Scaling and Optimization
========================

One important feature of RLTK is scalability. It can either work with very limited resources or utilize large amount of resources.

Set proper arguments
--------------------

Some of the methods have optional / required arguments about buffer size, chunk size, queue size, etc. Giving them proper values according to your machine's specification can reduce a lot of unnecessary memory-disk swap operations.

Parallel processing
-------------------

If you have some compute-intensive procedures and your machine has more than one CPU core, `rltk.ParallelProcessor` is a tool to try. You can find more detailed information in its documentation, but in general, it encapsulates multiprocessing and multithreading to do parallel computing. More detailed usage is in API documentation :doc:`mod_parallel_processor`.

.. code-block:: python

    result = []

    def heavy_calculation(x, y):
        return x * x, y + 5

    def output_handler(r1, r2):
        result.append(r1 if r1 > r2 else r2)

    pp = rltk.ParallelProcessor(heavy_calculation, 8, output_handler=output_handler)
    pp.start()

    for i in range(8):
        pp.compute(i, i + 1)

    pp.task_done()
    pp.join()

    print(result)

Distributed computing (experimental)
-------------------------------

.. note::

    It's not true that running RLTK on one machine is slower than on cluster, performance depends on requirement, data and code. If you only have tiny datasets and light task, Parallel computing is also not needed, creating processes and thread context switching all have costs. Similarly, distributed computing has more cost on IO (especially network) and it's more hard to do debugging, use it when you really need it. For most of the time, refactor code may have a boosting effect.

If you have an extremely heavy computation work or very large datasets, and you also have multiple idle machines, you may consider to use distributed computing. More detailed usage is in API documentation :doc:`mod_remote`.

First you need to set up a cluster. Cluster is formed by one scheduler and a bunch of workers.

To start a scheduler, do

.. code-block:: bash

    python -m rltk remote.scheduler

Then on worker machines, do

.. code-block:: bash

    python -m rltk remote.worker <scheduler ip>:8786 --nprocs <processors>

Second, change a bit of your code and run it. The API for distributed computing is really like `rltk.ParallelProcessor`. But you need a `rltk.remote.Remote` object which connects to the scheduler and an instance of `rltk.remote.Task` which has a input and a output handler.

.. code-block:: python

    remote = rltk.remote.Remote('127.0.0.1:8786')
    task = rltk.remote.Task(remote, input_handler=heavy_calculation, output_handler=output_handler)
    task.start()

    for i in range(8):
        task.compute(i, i + 1)

    task.task_done()
    task.join()
