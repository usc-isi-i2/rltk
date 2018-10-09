Remote
======

RLTK's remote module is based on `Dask's distributed <https://distributed.dask.org/en/latest/>`_. It has `scheduler` which coordinates the actions of several `worker` s spread across multiple machines and the concurrent requests of several clients.

To start scheduler, do:

.. code-block:: bash

    python -m rltk remote.scheduler --port <port>

Then on worker machines, do

.. code-block:: bash

    python -m rltk remote.worker <scheduler-ip>:<scheduler-port> --nprocs <processors>

Authentication is supported through Privacy Enhanced Mail (PEM) files. You can either get them from CA (Certificate Authority) or generate self-signed PEM locally. Here's an example of generating PEM by using `OpenSSL <https://www.openssl.org/docs/manmaster/man1/openssl-req.html>`_:

.. code-block:: bash

    openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout key.pem -out cert.pem

Then provide these PEM files while starting scheduler and workers. If you don't have CA certificate, set `tls-ca-file` same to `tls-cert`.

.. code-block:: bash

    # scheduler
    python -m rltk remote.scheduler --port <port> --tls-ca-file cert.pem --tls-cert cert.pem --tls-key key.pem

    # worker, specify protocol TLS in scheduler's address
    python -m rltk remote.worker tls://<scheduler-ip>:<scheduler-port> --tls-ca-file cert.pem --tls-cert cert.pem --tls-key key.pem

Dask provides a web UI to monitor scheduler and worker status, detailed usage can be found `here <http://distributed.dask.org/en/latest/web.html>`_.

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