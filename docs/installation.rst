Installation
============

.. note::

    RLTK only supports Python 3 and it's tested under Python 3.7+.


pip
----

Using pip to install::

    pip install rltk

If you want to update RLTK::

    pip install -U rltk

Generally, it's recommended to install packages in a virtual environment::

    virtualenv rltk_env
    source activate rltk_env
    pip install rltk


Install from source
-------------------

The other way to install RLTK is to clone from GitHub repository and build it from source::

    git clone https://github.com/usc-isi-i2/rltk.git
    cd rltk

    virtualenv rltk_env
    source activate rltk_env
    pip install -e .

Run tests
---------

RLTK uses `pytest <https://pytest.org/>`_ for unit tests. To run them, simply do following command from the root of rltk package::

    pytest

If you need more detailed information, do::

    pytest -v --color=yes

Build documentation
-------------------

Additional dependencies for building documentation should be installed first:

    pip install -r requirements_docs.txt

Documentation is powered by `Sphinx <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_ , to generate it on your local, please run::

    cd docs
    make html # the generated doc is located at _build/html/index.html
