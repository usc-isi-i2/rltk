.. rltk documentation master file, created by
   sphinx-quickstart on Thu Feb 23 13:46:31 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RLTK: Record Linkage ToolKit
============================

.. include:: ./../README.rst
      :start-after: begin-intro
      :end-before: end-intro


Getting Started
---------------

Installation::

   pip install -U rltk

Example::

   >>> import rltk
   >>> rltk.levenshtein_distance('abc', 'abd')
   1

Tutorial
-------------

.. toctree::
   :maxdepth: 2

   overview.rst


API Reference
-------------

.. toctree::
   :maxdepth: 2

   modules.rst
