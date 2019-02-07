import multiprocessing as mp
import queue
from typing import Callable
import sys
import logging


logger = logging.getLogger('RLTK - MapReduce')
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stdout_handler)


class ReduceContext(object):
    def __init__(self):
        raise NotImplementedError

    def merge(self, ctx):
        raise NotImplementedError


class MapReduce(object):

    CMD_NO_NEW_DATA = 1  # no more new user data
    CMD_MAPPER_FINISH = 2  # mapper finished
    CMD_REDUCER_WAITING = 3  # reducer is waiting
    CMD_NO_RUNNING_MAPPER = 4  # no mapper is running
    CMD_REDUCER_AWAKE = 5  # awake a reducer
    CMD_REDUCER_KILL = 6  # kill a reducer
    CMD_REDUCER_FINISH = 7  # reducer finished

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

        # start manager, mapper and reducer processes
        self._manager_process.start()
        for m in self._mapper_process:
            m.start()
        for r in self._reducer_process:
            r.start()

    def add_task(self, *args, **kwargs):
        self._mapper_queue.put( (args, kwargs) )

    def join(self):
        # no more user data
        self._manager_cmd_queue.put( (self.__class__.CMD_NO_NEW_DATA,) )

        # wait until all child processes exited
        for m in self._mapper_process:
            m.join()
        for r in self._reducer_process:
            r.join()
        self._manager_process.join()

        # return context
        return self._reducer_queue.get()

    def _run_manager(self):
        running_mapper = [1 for _ in range(self._num_of_process)]  # running mappers, 1 is running
        running_reducer = [1 for _ in range(self._num_of_process)]  # running reducers, 1 is running
        waiting_reducer = [0 for _ in range(self._num_of_process)]  # waiting reducers, 1 is waiting
        killing_reducer = [0 for _ in range(self._num_of_process)]  # killing reducers, 1 is asked to kill

        # only return the index where mask shows 1
        def apply_mask(mask):
            for idx, m in enumerate(mask):
                if m == 1:
                    yield idx

        while True:
            try:
                cmd = self._manager_cmd_queue.get(timeout=0.1)

                # no more user data, notify all mappers
                if cmd[0] == self.__class__.CMD_NO_NEW_DATA:
                    for q in self._mapper_cmd_queue:
                        q.put( (self.__class__.CMD_NO_NEW_DATA,) )

                # a mapper finished
                elif cmd[0] == self.__class__.CMD_MAPPER_FINISH:
                    idx = cmd[1]
                    running_mapper[idx] = 0
                    # notify reducers if all mappers are finished
                    if sum(running_mapper) == 0:
                        for r in self._reducer_cmd_queue:
                            r.put( (self.__class__.CMD_NO_RUNNING_MAPPER,) )

                # a reducer is waiting
                # if all reducers are waiting,
                # ask half of them to kill themselves and release held resources (context),
                # after being killed, wake up rest of the reducers
                elif cmd[0] == self.__class__.CMD_REDUCER_WAITING:
                    idx = cmd[1]
                    waiting_reducer[idx] = 1
                    logger.info('waiting reducer #%d', idx)

                    # total num of running reducers
                    running_reducer_num = len(list(apply_mask(running_reducer)))
                    logger.info('running reducer num %d', running_reducer_num)

                    # only one reducer and nothing to reduce anymore
                    if running_reducer_num == 1:
                        # kill last reducer
                        idx = next(apply_mask(running_reducer))
                        self._reducer_cmd_queue[idx].put( (self.__class__.CMD_REDUCER_KILL,) )
                        return

                    # total num of waiting reducers
                    waiting_reducer_num = len(list(filter(lambda x: x > 0,
                                    [waiting_reducer[idx] for idx in apply_mask(running_reducer)])))
                    logger.info('waiting reducer num %d', waiting_reducer_num)
                    logger.info('waiting reducer status %s', str(waiting_reducer))

                    # need to kill half of the reducers and release resources
                    if running_reducer_num == waiting_reducer_num:
                        # reset waiting reducer (for next round)
                        waiting_reducer = [0 for _ in range(self._num_of_process)]
                        # pick half of them to kill, notify these reducers
                        kill_reducer_num = running_reducer_num - int(running_reducer_num / 2)
                        notified_kill_reducer_num = 0
                        for idx in apply_mask(running_reducer):
                            self._reducer_cmd_queue[idx].put( (self.__class__.CMD_REDUCER_KILL,) )
                            killing_reducer[idx] = 1
                            notified_kill_reducer_num += 1
                            logging.info('killing reducer #%d', idx)
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
                                # reset state for killed reducer
                                running_reducer[idx] = 0
                                killing_reducer[idx] = 0
                                logger.info('reducer killed #%d', idx)

                                # all killed, wake up rest of the reducers
                                if sum(killing_reducer) == 0:
                                    for idx in apply_mask(running_reducer):
                                        logger.info('awaking reducer #%d', idx)
                                        self._reducer_cmd_queue[idx].put( (self.__class__.CMD_REDUCER_AWAKE,) )
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
                # no more new data, mapper finishes
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
                if isinstance(m, ReduceContext):  # merge two contexts
                    context.merge(m)
                else:  # merge context and data
                    self._reducer(context, m)
            except queue.Empty:
                # there are still some alive mapper, wait for their output
                if not no_running_mapper:
                    continue

                # no data in reducer queue, ask manager and wait for further action
                self._manager_cmd_queue.put( (self.__class__.CMD_REDUCER_WAITING, idx) )
                cmd = self._reducer_cmd_queue[idx].get()
                # awake
                if cmd[0] == self.__class__.CMD_REDUCER_AWAKE:
                    continue
                # kill itself, put context back to reducer queue
                elif cmd[0] == self.__class__.CMD_REDUCER_KILL:
                    self._reducer_queue.put(context)
                    self._manager_cmd_queue.put( (self.__class__.CMD_REDUCER_FINISH, idx) )
                    return



