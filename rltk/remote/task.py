from threading import Semaphore
from typing import Callable

from rltk.remote.remote import Remote


class Task(object):
    """
    Remote task. It has similar API to :meth:`rltk.ParallelProcessor`. 
    But do not use :meth:`rltk.ParallelProcessor` if this module is used. If you still want multiprocessing, 
    please give each worker more processes.
    
    Args:
        remote (Remote): Remote object.
        input_handler (Callable): Input handler.
        output_handler (Callable): Output handler. It accepts same number of arguments to `input_handler` 's return values.
        chunk_size (int, optional): Size of the each data chunk. Defaults to 1000.
        max_queue_size (int, optional): How many chunks can be in the queue. Defaults to 10.
    """

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
        """
        Start listening.
        """
        pass

    @staticmethod
    def _parse_input(input_handler, data):
        return [input_handler(*args, **kwargs) for args, kwargs in data]

    def _parse_output(self, future):
        if future.done():
            for r in future.result():
                if not isinstance(r, tuple):
                    r = (r,)
                self.output_handler(*r)

        # release resources no matter what condition that future gets
        self.all_futures.remove(future)
        self.future_semaphore.release()

    def compute(self, *args, **kwargs):
        """
        Add data to compute.
        """
        if self.done:
            return

        if len(self.chunk_data) < self.chunk_size:
            self.chunk_data.append(([*args], {**kwargs}))
        if len(self.chunk_data) == self.chunk_size:
            self._submit()

    def _submit(self):
        if len(self.chunk_data) == 0:
            return

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
        """
        Indicate that all resources which need to compute are added.
        """
        self.done = True
        self._submit()  # force flush buffer

    def join(self):
        """
        Block until all tasks are done.
        """
        while len(self.all_futures) != 0:
            pass
