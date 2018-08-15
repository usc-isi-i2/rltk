import time

from rltk.parallel_processor import ParallelProcessor


def test_basic():
    def dummy_computation():
        time.sleep(0.0001)

    pp = ParallelProcessor(dummy_computation, 8)
    pp.start()

    for i in range(1000):
        pp.compute()

    pp.task_done()
    pp.join()


def test_with_input():
    def dummy_computation_with_input(x):
        time.sleep(0.0001)

    pp = ParallelProcessor(dummy_computation_with_input, 8)
    pp.start()

    for i in range(1000):
        pp.compute(i)

    pp.task_done()
    pp.join()


def test_with_multiple_input():
    def dummy_computation_with_input(x, y):
        assert x * 2 == y
        time.sleep(0.0001)

    pp = ParallelProcessor(dummy_computation_with_input, 8)
    pp.start()

    for i in range(1000):
        pp.compute(i, y=i*2)

    pp.task_done()
    pp.join()


def test_with_output():
    result = []

    def dummy_computation_with_input(x):
        time.sleep(0.0001)
        return x * x

    def output_handler(r):
        result.append(r)

    pp = ParallelProcessor(dummy_computation_with_input, 8, output_handler=output_handler)
    pp.start()

    for i in range(8):
        pp.compute(i)

    pp.task_done()
    pp.join()

    for i in [0, 1, 4, 9, 16, 25, 36, 49]:
        assert i in result


def test_with_multiple_output():
    result = []

    def dummy_computation_with_input(x):
        time.sleep(0.0001)
        return x * x, x * x

    def output_handler(r1, r2):
        result.append(r1)

    pp = ParallelProcessor(dummy_computation_with_input, 8, output_handler=output_handler)
    pp.start()

    for i in range(8):
        pp.compute(i)

    pp.task_done()
    pp.join()

    for i in [0, 1, 4, 9, 16, 25, 36, 49]:
        assert i in result
