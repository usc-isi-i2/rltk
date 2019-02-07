import multiprocessing as mp
import queue
from typing import Callable


class ReduceContext(object):
    def __init__(self):
        raise NotImplementedError

    def merge(self, ctx):
        raise NotImplementedError


class MapReduce(object):

    CMD_NO_NEW_DATA = 1
    CMD_MAPPER_FINISH = 2
    CMD_REDUCER_WAITING = 3
    CMD_NO_RUNNING_MAPPER = 4
    CMD_REDUCER_CONTINUE = 5
    CMD_REDUCER_KILL = 6
    CMD_REDUCER_FINISH = 7

    def __init__(self, num_of_process: int, mapper: Callable, reducer: Callable, context_class: type):
        self._mapper_queue = mp.Queue()
        self._reducer_queue = mp.Queue()
        self._mapper_cmd_queue = [mp.Queue() for _ in range(num_of_process)]
        self._reducer_cmd_queue = [mp.Queue() for _ in range(num_of_process)]
        self._manager_cmd_queue = mp.Queue()

        self._manager_process = mp.Process(target=self._run_manager)
        self._mapper_process = [mp.Process(target=self._run_mapper, args=(i, ))
                          for i in range(num_of_process)]
        self._reducer_process = [mp.Process(target=self._run_reducer, args=(i, ))
                          for i in range(num_of_process)]

        self._mapper = mapper
        self._reducer = reducer
        self._context_class = context_class
        self._num_of_process = num_of_process

        self._manager_process.start()
        for m in self._mapper_process:
            m.start()
        for r in self._reducer_process:
            r.start()

    def add_task(self, *args, **kwargs):
        self._mapper_queue.put( (args, kwargs) )

    def join(self):
        self._manager_cmd_queue.put( (self.__class__.CMD_NO_NEW_DATA,) )
        for m in self._mapper_process:
            m.join()
        for r in self._reducer_process:
            r.join()
        self._manager_process.join()
        return self._reducer_queue.get()

    def _run_manager(self):
        running_mapper = [1 for _ in range(self._num_of_process)]
        running_reducer = [1 for _ in range(self._num_of_process)]
        waiting_reducer = [0 for _ in range(self._num_of_process)]
        killing_reducer = [0 for _ in range(self._num_of_process)]

        def apply_mask(mask):
            for idx, m in enumerate(mask):
                if m == 1:
                    yield idx

        while True:
            try:
                cmd = self._manager_cmd_queue.get(timeout=0.1)
                # no new user data, notify mappers
                if cmd[0] == self.__class__.CMD_NO_NEW_DATA:
                    for q in self._mapper_cmd_queue:
                        q.put( (self.__class__.CMD_NO_NEW_DATA,) )
                # a mapper finished, notify reducers if all mappers finished
                elif cmd[0] == self.__class__.CMD_MAPPER_FINISH:
                    idx = cmd[1]
                    running_mapper[idx] = 0
                    if sum(running_mapper) == 0:
                        for r in self._reducer_cmd_queue:
                            r.put( (self.__class__.CMD_NO_RUNNING_MAPPER,) )
                # a reducer is waiting, if all waiting,
                # ask some of the reducers to kill themselves and release resource,
                # after killing, wake up rest of the reducers
                elif cmd[0] == self.__class__.CMD_REDUCER_WAITING:
                    idx = cmd[1]
                    waiting_reducer[idx] = 1
                    # print('reducer waiting', idx)

                    running_reducer_num = len(list(apply_mask(running_reducer)))
                    # print('running num', running_reducer_num)
                    # nothing to reduce anymore
                    if running_reducer_num == 1:
                        # kill last reducer
                        idx = next(apply_mask(running_reducer))
                        self._reducer_cmd_queue[idx].put( (self.__class__.CMD_REDUCER_KILL,) )
                        return

                    # need to kill some reducers
                    waiting_reducer_num = len(list(filter(lambda x: x > 0,
                                    [waiting_reducer[idx] for idx in apply_mask(running_reducer)])))
                    # print('waiting num', waiting_reducer_num, waiting_reducer)
                    if running_reducer_num == waiting_reducer_num:
                        # reset waiting reducer
                        waiting_reducer = [0 for _ in range(self._num_of_process)]
                        # kill half of them, notify these reducers
                        kill_reducer_num = running_reducer_num - int(running_reducer_num / 2)
                        notified_kill_reducer_num = 0
                        for idx in apply_mask(running_reducer):
                            self._reducer_cmd_queue[idx].put( (self.__class__.CMD_REDUCER_KILL,) )
                            killing_reducer[idx] = 1
                            notified_kill_reducer_num += 1
                            # print('reducer killing', idx)
                            if kill_reducer_num == notified_kill_reducer_num:
                                break
                        # make sure these reducers are killed
                        while True:
                            cmd = self._manager_cmd_queue.get()
                            # other command, put it back
                            if cmd[0] != self.__class__.CMD_REDUCER_FINISH:
                                self._manager_cmd_queue.put(cmd)
                            else:
                                idx = cmd[1]
                                running_reducer[idx] = 0
                                killing_reducer[idx] = 0
                                # print('reducer killed', idx)
                                # all killed, wake up rest of the reducers
                                if sum(killing_reducer) == 0:
                                    for idx in apply_mask(running_reducer):
                                        # print('reducer continuing', idx)
                                        self._reducer_cmd_queue[idx].put( (self.__class__.CMD_REDUCER_CONTINUE,) )
                                    break

            except queue.Empty:
                continue

    def _run_mapper(self, idx):
        no_new_data = False

        while True:
            # cmd
            try:
                cmd = self._mapper_cmd_queue[idx].get_nowait()
                if cmd[0] == self.__class__.CMD_NO_NEW_DATA:
                    no_new_data = True
            except queue.Empty:
                pass

            # data
            try:
                data = self._mapper_queue.get(timeout=0.1)
                args, kwargs = data[0], data[1]
                result = self._mapper(*args, **kwargs)
                self._reducer_queue.put(result)
            except queue.Empty:
                if no_new_data:
                    self._manager_cmd_queue.put( (self.__class__.CMD_MAPPER_FINISH, idx) )
                    return
                continue

    def _run_reducer(self, idx):
        context = self._context_class()
        no_running_mapper = False

        while True:
            # cmd
            try:
                cmd = self._reducer_cmd_queue[idx].get_nowait()
                if cmd[0] == self.__class__.CMD_NO_RUNNING_MAPPER:
                    no_running_mapper = True
            except queue.Empty:
                pass

            # data
            try:
                m = self._reducer_queue.get(timeout=0.1)
                if isinstance(m, ReduceContext):
                    context.merge(m)
                else:
                    self._reducer(context, m)
            except queue.Empty:
                # wait for mapper
                if not no_running_mapper:
                    continue

                # if waiting, ask manager and wait for further command
                self._manager_cmd_queue.put( (self.__class__.CMD_REDUCER_WAITING, idx) )
                cmd = self._reducer_cmd_queue[idx].get()
                if cmd[0] == self.__class__.CMD_REDUCER_CONTINUE:
                    continue
                elif cmd[0] == self.__class__.CMD_REDUCER_KILL:
                    self._reducer_queue.put(context)
                    self._manager_cmd_queue.put( (self.__class__.CMD_REDUCER_FINISH, idx) )
                    return



