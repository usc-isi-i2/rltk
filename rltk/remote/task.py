from threading import Semaphore
from typing import Callable

from rltk.remote.remote import Remote


class Task(object):

    def __init__(self, remote: Remote, input_handler: Callable, output_handler: Callable,
                 chunk_size: int = 1000, max_queue_size: int = 10):
        self.remote = remote
        self.input_handler = input_handler
        self.output_handler = output_handler

        self.chunk_data = []  # buffer
        self.chunk_size = chunk_size  # buffer size
        self.future_semaphore = Semaphore(value=max_queue_size)  # max num of un-return futures
        self.all_futures = set([])  # all un-return future objects
        self.done = False

    def start(self):
        pass

    @staticmethod
    def _parse_input(input_handler, data):
        return [input_handler(*args, **kwargs) for args, kwargs in data]

    def _parse_output(self, future):
        if future.done():
            for r in future.result():
                self.output_handler(*r)

        # release resources no matter what condition that future gets
        self.all_futures.remove(future)
        self.future_semaphore.release()

    def compute(self, *args, **kwargs):
        if self.done:
            return

        if len(self.chunk_data) < self.chunk_size:
            self.chunk_data.append(([*args], {**kwargs}))
        if len(self.chunk_data) == self.chunk_size:
            self._submit()

    def _submit(self):
        self.future_semaphore.acquire()

        # scatter input data (scatter first if data is large)
        data_future = self.remote.scatter(self.chunk_data)

        # input and output must be staticmethod, create wrappers to bypass restriction
        future = self.remote.submit(Task._parse_input, self.input_handler, data_future)
        Task._parse_output_wrapper = lambda ft: Task._parse_output(self, ft)

        # add listener
        future.add_done_callback(Task._parse_output_wrapper)
        self.all_futures.add(future)

        self.chunk_data = []

    def task_done(self):
        self.done = True
        self._submit()  # force flush buffer

    def join(self):
        while len(self.all_futures) != 0:
            pass
