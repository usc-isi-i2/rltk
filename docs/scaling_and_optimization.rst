Scaling and Optimization
========================

One important feature of RLTK is scalability. It can either work with very limited resources or utilize large amount of resources.

Set proper arguments
--------------------

Some of the methods have optional / required arguments about buffer size, chunk size, queue size, etc. Giving them proper values according to your machine's specification can reduce a lot of unnecessary memory-disk swap operations.

Parallel processing
-------------------

General parallel processing
```````````````````````````

If you have some compute-intensive procedures and your machine has more than one CPU core, `rltk.ParallelProcessor` is a tool to try. You can find more detailed information in API documentation :doc:`mod_parallel_processor`, but in general, it encapsulates multiprocessing to do parallel computing and multithreading to do data collecting.

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


MapReduce
`````````

The above solution uses one thread (in main process) for collecting calculated data. If you want to do something like divide and conquer, especially when "conquer" needs heavy calculation, you may need `rltk.MapReduce` module. Detailed documentation can be found :doc:`mod_map_reduce`.

.. code-block:: python

    def mapper(x):
        time.sleep(0.0001)
        return x

    def reducer(r1, r2):
        return r1 + r2

    mr = rltk.MapReduce(8, mapper, reducer)
    for i in range(10000):
        mr.add_task(i)
    result = mr.join()
    print(result)

Distributed computing (Experimental)
------------------------------------

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

    def input_handler(r1, r2):
        return r1, r2, is_pair(r1, r2)

    def output_handler(r1, r2, label):
        print(r1.id, r2.id, label)

    remote = rltk.remote.Remote('127.0.0.1:8786')
    task = rltk.remote.Task(remote, input_handler=input_handler, output_handler=output_handler)
    task.start()

    for r1, r2 in rltk.get_record_pairs(ds1, ds2):
        task.compute(r1, r2)

    task.task_done()
    task.join()

If data is in shared data store (file systems or services), there's no need to transfer record data through scheduler to worker but record id. Then workers can get data directly from data store. So change your code to make `input_handler` accepts id as input and fetch the record data in it.

.. code-block:: python
    :emphasize-lines: 1,2,9

    def input_handler(id1, id2):
        r1, r2 = ds1.get(id1), ds2.get(id2)
        return is_pair(r1, r2)

    task = rltk.remote.Task(remote, input_handler=input_handler, output_handler=output_handler)
    task.start()

    for r1, r2 in rltk.get_record_pairs(ds1, ds2):
        task.compute(r1.id, r2.id)

    task.task_done()
    task.join()
