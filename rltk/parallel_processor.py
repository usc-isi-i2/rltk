import multiprocessing as mp
import threading
import queue
from typing import Callable


class OutputThread(threading.Thread):
    """
    Handle output in main process.
    Create a thread and call ParallelProcessor.get_output().
    """
    def __init__(self, instance, output_handler):
        super(OutputThread, self).__init__()
        self.output_handler = output_handler
        self.instance = instance

    def run(self):
        for o in self.instance.get_output():
            self.output_handler(*o)


class ParallelProcessor(object):
    """
    Args:
        input_handler (Callable): Computational function. 
        num_of_processor (int): Number of processes to use. 
        max_size_per_input_queue (int): Maximum size of input queue for one process.
                                    If it's full, the corresponding process will be blocked.
                                    0 by default means unlimited.
        max_size_per_output_queue (int): Maximum size of output queue for one process.
                                    If it's full, the corresponding process will be blocked.
                                    0 by default means unlimited.
        output_handler (Callable): If the output data needs to be get in main process (another thread), 
                                set this handler, the arguments are same to the return from input_handler.
                                The return result is one by one, order is arbitrary.
    """

    # Command format in queue. Represent in tuple.
    # The first element of tuple will be command, the rests are arguments or data.
    # (CMD_XXX, args...)
    CMD_DATA = 0
    CMD_STOP = 1

    def __init__(self, input_handler: Callable, num_of_processor: int,
                 max_size_per_input_queue: int = 0, max_size_per_output_queue: int = 0,
                 output_handler: Callable = None):
        self.num_of_processor = num_of_processor
        self.input_queues = [mp.Queue(maxsize=max_size_per_input_queue) for _ in range(num_of_processor)]
        self.output_queues = [mp.Queue(maxsize=max_size_per_output_queue) for _ in range(num_of_processor)]
        self.processes = [mp.Process(target=self.run, args=(i, self.input_queues[i], self.output_queues[i]))
                          for i in range(num_of_processor)]
        self.input_handler = input_handler
        self.output_handler = output_handler
        self.input_queue_index = 0
        self.output_queue_index = 0

        # output can be handled in each process or in main process after merging (output_handler needs to be set)
        # if output_handler is set, output needs to be handled in main process; otherwise, it assumes there's no output.
        if output_handler:
            self.output_thread = OutputThread(self, output_handler)

    def start(self):
        """
        Start processes and threads.
        """
        if self.output_handler:
            self.output_thread.start()
        for p in self.processes:
            p.start()

    def join(self):
        """
        Block until processes and threads return.
        """
        for p in self.processes:
            p.join()
        if self.output_handler:
            self.output_thread.join()

    def task_done(self):
        """
        Indicate that all resources which need to compute are added to processes.
        (main process, blocked)
        """
        for q in self.input_queues:
            q.put((ParallelProcessor.CMD_STOP,))

    def compute(self, *args, **kwargs):
        """
        Add data to one of the input queues.
        (main process, unblocked, using round robin to find next available queue)
        """
        while True:
            q = self.input_queues[self.input_queue_index]
            self.input_queue_index = (self.input_queue_index + 1) % self.num_of_processor
            try:
                q.put_nowait((ParallelProcessor.CMD_DATA, args, kwargs))
                return  # put in
            except queue.Full:
                continue  # find next available

    def run(self, idx: int, input_queue: mp.Queue, output_queue: mp.Queue):
        """
        Process’s activity. It handles queue IO and invokes user's input handler.
        (subprocess, blocked, only two queues can be used to communicate with main process)
        """
        while True:
            data = input_queue.get()
            if data[0] == ParallelProcessor.CMD_STOP:
                # print(idx, 'stop')
                if self.output_handler:
                    output_queue.put((ParallelProcessor.CMD_STOP,))
                return
            elif data[0] == ParallelProcessor.CMD_DATA:
                args, kwargs = data[1], data[2]
                # print(idx, 'data')
                result = self.input_handler(*args, **kwargs)
                if not isinstance(result, tuple):  # output must represent as tuple
                    result = (result,)
                if self.output_handler:
                    output_queue.put((ParallelProcessor.CMD_DATA, result))

    def get_output(self):
        """
        Get data from output queue sequentially.
        (main process, unblocked, using round robin to find next available queue)
        """
        if not self.output_handler:
            return
        while True:
            # print(self.output_queues)
            q = self.output_queues[self.output_queue_index]
            try:
                data = q.get_nowait()  # get out
                if data[0] == ParallelProcessor.CMD_STOP:
                    del self.output_queues[self.output_queue_index]  # remove queue if it's finished
                elif data[0] == ParallelProcessor.CMD_DATA:
                    yield data[1]
            except queue.Empty:
                continue  # find next available
            finally:
                if len(self.output_queues) == 0:  # all finished
                    return
                self.output_queue_index = (self.output_queue_index + 1) % len(self.output_queues)
