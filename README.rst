RLTK: Record Linkage ToolKit
============================

.. begin-intro
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://raw.githubusercontent.com/usc-isi-i2/rltk/master/LICENSE
    :alt: License

.. image:: https://api.travis-ci.org/usc-isi-i2/rltk.svg?branch=master
    :target: https://travis-ci.org/usc-isi-i2/rltk
    :alt: Travis

.. image:: https://badge.fury.io/py/rltk.svg
    :target: https://badge.fury.io/py/rltk
    :alt: pypi

.. image:: https://readthedocs.org/projects/rltk/badge/?version=latest
    :target: http://rltk.readthedocs.io/en/latest
    :alt: Documents

The Record Linkage ToolKit (RLTK) is a general-purpose open-source record linkage platform that allows users to build powerful Python programs that link records referring to the same underlying entity. Record linkage is an extremely important problem that shows up in domains extending from social networks to bibliographic data and biomedicine. Current open platforms for record linkage have problems scaling even to moderately sized datasets, or are just not easy to use (even by experts). RLTK attempts to address all of these issues.

RLTK supports a full, scalable record linkage pipeline, including multi-core algorithms for blocking, profiling data, computing a wide variety of features, and training and applying machine learning classifiers based on Python’s sklearn library. An end-to-end RLTK pipeline can be jump-started with only a few lines of code. However, RLTK is also designed to be extensible and customizable, allowing users arbitrary degrees of control over many of the individual components. You can add new features to RLTK (e.g. a custom string similarity) very easily.

RLTK is being built by the `Center on Knowledge Graphs <http://usc-isi-i2.github.io/>`_ at `USC/ISI <https://isi.edu/>`_, with funding from multiple projects funded by the DARPA LORELEI and MEMEX programs and the IARPA CAUSE program.
RLTK is under active maintenance and we expect to keep adding new features and state-of-the-art record linkage algorithms in the foreseeable future, in addition to continuously supporting our adopters to integrate the platform into their applications.

.. end-intro

Datasets & Experiments
----------------------
* `rltk-experimentation <https://github.com/usc-isi-i2/rltk-experimentation>`_

Documentation
-------------

* `Tutorials <http://rltk.readthedocs.io>`_
* `API Reference <http://rltk.readthedocs.io/en/latest/modules.html>`_
