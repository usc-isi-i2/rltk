"""
This module is designed for breaking the restriction of Python Global Interpreter Lock (GIL): It uses multi-processing (compute-intensive operations) and multi-threading (return data collecting) to accelerate computing.
Once it's initialized, it creates a sub process pool, all the added data will be dispatched to different sub processes for parallel computing. The result sends back and consumes in another thread in current main process. The Inter Process Communication (IPC) between main process and sub processes is based on queue.

Example::

    result = []
    
    def dummy_computation_with_input(x):
        time.sleep(0.0001)
        return x * x, x + 5
    
    def output_handler(r1, r2):
        result.append(r1 if r1 > r2 else r2)
    
    pp = ParallelProcessor(dummy_computation_with_input, 8, output_handler=output_handler)
    pp.start()
    
    for i in range(8):
        pp.compute(i)
    
    pp.task_done()
    pp.join()
    
    print(result)
"""

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
        max_size_per_input_queue (int, optional): Maximum size of input queue for one process.
                                    If it's full, the corresponding process will be blocked.
                                    0 by default means unlimited.
        max_size_per_output_queue (int, optional): Maximum size of output queue for one process.
                                    If it's full, the corresponding process will be blocked.
                                    0 by default means unlimited.
        output_handler (Callable, optional): If the output data needs to be get in main process (another thread),
                                set this handler, the arguments are same to the return from input_handler.
                                The return result is one by one, order is arbitrary.
        enable_process_id (bool, optional): If it's true, an additional argument `_idx` (process id) will be
                                passed to `input_handler`. It defaults to False.
    
    
    Note:
        Do NOT implement heavy compute-intensive operations in output_handler, they should be in input_handler.
    """

    # Command format in queue. Represent in tuple.
    # The first element of tuple will be command, the rests are arguments or data.
    # (CMD_XXX, args...)
    CMD_DATA = 0
    CMD_STOP = 1

    def __init__(self, input_handler: Callable, num_of_processor: int,
                 max_size_per_input_queue: int = 0, max_size_per_output_queue: int = 0,
                 output_handler: Callable = None, enable_process_id: bool = False,
                 input_batch_size: int = 1, output_batch_size: int = 1):
        self.num_of_processor = num_of_processor
        self.input_queues = [mp.Queue(maxsize=max_size_per_input_queue) for _ in range(num_of_processor)]
        self.output_queues = [mp.Queue(maxsize=max_size_per_output_queue) for _ in range(num_of_processor)]
        self.processes = [mp.Process(target=self.run, args=(i, self.input_queues[i], self.output_queues[i]))
                          for i in range(num_of_processor)]
        self.input_handler = input_handler
        self.output_handler = output_handler
        self.input_queue_index = 0
        self.output_queue_index = 0
        self.enable_process_id = enable_process_id
        self.input_batch_size = input_batch_size
        self.output_batch_size = output_batch_size
        self.input_batch = []
        self.output_batch = []

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
        if len(self.input_batch) > 0:
            self._compute(self.input_batch)
            self.input_batch = []

        for q in self.input_queues:
            q.put( (ParallelProcessor.CMD_STOP,) )

    def compute(self, *args, **kwargs):
        """
        Add data to one of the input queues.
        (main process, unblocked, using round robin to find next available queue)
        """
        self.input_batch.append( (args, kwargs) )

        if len(self.input_batch) == self.input_batch_size:
            self._compute(self.input_batch)
            self.input_batch = []  # reset buffer

    def _compute(self, batched_args):
        while True:
            q = self.input_queues[self.input_queue_index]
            self.input_queue_index = (self.input_queue_index + 1) % self.num_of_processor
            try:
                q.put_nowait( (ParallelProcessor.CMD_DATA, batched_args) )
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
                    output_queue.put( (ParallelProcessor.CMD_STOP,) )
                return
            elif data[0] == ParallelProcessor.CMD_DATA:
                for d in data[1]:
                    args, kwargs = d[0], d[1]
                    # print(idx, 'data')
                    result = self.input_handler(*args, **kwargs, _idx=idx) if self.enable_process_id \
                        else self.input_handler(*args, **kwargs)
                    if self.output_handler:
                        if not isinstance(result, tuple):  # output must represent as tuple
                            result = (result,)
                        output_queue.put( (ParallelProcessor.CMD_DATA, result) )

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
