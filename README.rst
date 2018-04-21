RLTK: Record Linkage ToolKit
============================

.. begin-intro
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://raw.githubusercontent.com/usc-isi-i2/rltk/master/LICENSE
    :alt: License

.. image:: https://api.travis-ci.org/usc-isi-i2/rltk.svg?branch=master
    :target: https://travis-ci.org/usc-isi-i2/rltk
    :alt: Travis

.. image:: https://readthedocs.org/projects/rltk/badge/?version=latest
    :target: http://rltk.readthedocs.io/en/latest
    :alt: Documents

We are actively developing a new version of RLTK. If you are curious, check out the v2  branch:
https://github.com/usc-isi-i2/rltk/tree/v2

The Record Linkage ToolKit (RLTK) is a general-purpose open-source record linkage platform that allows users to build powerful Python programs that link records (represented as arbitrarily structured JSON documents) referring to the same underlying entity. Record linkage is an extremely important problem that shows up in domains extending from social networks to bibliographic data and biomedicine. Current open platforms for record linkage have problems scaling even to moderately sized datasets, or are just not easy to use (even by experts). RLTK attempts to address all of these issues.

RLTK supports a full, scalable record linkage pipeline, including multi-core algorithms for blocking, profiling data, computing a wide variety of features (including string, token, numeric, phonetic and time-series features), and training and applying machine learning classifiers based on Python’s sklearn library. An end-to-end RLTK pipeline can be jumpstarted with only a few lines of code. However, RLTK is also designed to be extensible and customizable, allowing users arbitrary degrees of control over many of the individual components. You can add new features to RLTK (e.g. a custom string similarity) very easily.

Although easy to use, RLTK also contains advanced modules that allow you to automate record linkage by giving you access to state-of-the-art algorithms that were only published recently and have no other open-source implementations we are aware of. Some of these algorithms have been applied to extremely difficult domains such as Dark Web and human trafficking data. Last but not least, RLTK gives you easy facilities to convert your native data format (such as CSV, natural language documents, XML, RDF, graph formats etc.) into JSON so you have to invest minimal manual labor to get started.

RLTK is being built by the information integration group at `USC/ISI <http://usc-isi-i2.github.io/>`_, with funding from multiple projects funded by the DARPA LORELEI and MEMEX programs and the IARPA CAUSE program.
RLTK is under active maintenance and we expect to keep adding new features and state-of-the-art record linkage algorithms in the foreseeable future, in addition to continuously supporting our adopters to integrate the platform into their applications.

.. end-intro

Documentation
-------------

* `Tutorials <http://rltk.readthedocs.io>`_
* `API Reference <http://rltk.readthedocs.io/en/latest/modules.html>`_
