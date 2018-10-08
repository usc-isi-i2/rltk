Remote
======

RLTK's remote module is based on `Dask's distributed <https://distributed.dask.org/en/latest/>`_. It has `scheduler` which coordinates the actions of several `worker` s spread across multiple machines and the concurrent requests of several clients.

To start scheduler, do:

.. code-block:: bash

    python -m rltk remote.scheduler --port <port>

Then on worker machines, do

.. code-block:: bash

    python -m rltk remote.worker <scheduler ip>:<scheduler port> --nprocs <processors>

Dask provides a web UI to monitor scheduler and worker status, detailed explanation is `here <http://distributed.dask.org/en/latest/web.html>`_.

Remote
------

.. automodule:: rltk.remote.remote
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __init__

Task
----

.. automodule:: rltk.remote.task
    :members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __init__