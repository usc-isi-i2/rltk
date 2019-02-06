import multiprocessing as mp
import queue
from typing import Callable


class MapReduce(object):

    CMD_DATA = 0
    CMD_STOP = 1

    def __init__(self, num_of_process: int, mapper: Callable, reducer: Callable):
        self._mapper_queue = mp.Queue(maxsize=100)
        self._reducer_queue = mp.Queue(maxsize=100)
        self._mapper_process = [mp.Process(target=self._run_mapper, args=(i, ))
                          for i in range(num_of_process)]
        self._reducer_process = [mp.Process(target=self._run_reducer, args=(i, ))
                          for i in range(num_of_process)]
        self._mapper = mapper
        self._reducer = reducer

        # start mappers
        for m in self._mapper_process:
            m.start()

    def map(self, *args, **kwargs):
        self._mapper_queue.put((self.__class__.CMD_DATA, args, kwargs))

    def _run_mapper(self, idx):
        while True:
            data = self._mapper_queue.get()
            if data[0] == self.__class__.CMD_STOP:
                self._mapper_queue.put(data)  # put it back to queue
                return
            elif data[0] == self.__class__.CMD_DATA:
                args, kwargs = data[1], data[2]
                result = self._mapper(*args, **kwargs)
                self._reducer_queue.put(result)

    def reduce(self):
        # stop mappers
        self._mapper_queue.put((self.__class__.CMD_STOP,))
        for m in self._mapper_process:
            m.join()
        # start reducers
        for r in self._reducer_process:
            r.start()
        # wait until reducers finish
        for r in self._reducer_process:
            r.join()
        return self._reducer_queue.get()

    def _run_reducer(self, idx):
        while True:
            try:
                m1 = self._reducer_queue.get(timeout=0.01)
            except queue.Empty:  # excess reducer
                return
            try:
                m2 = self._reducer_queue.get(timeout=0.01)
            except queue.Empty:  # excess reducer
                self._reducer_queue.put(m1)  # put m1 back to queue
                return
            result = self._reducer(m1, m2)
            self._reducer_queue.put(result)
