.. rltk documentation master file, created by
   sphinx-quickstart on Thu Feb 23 13:46:31 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RLTK's documentation
=====================

Record Linkage ToolKit.

Getting Start
--------------

Installation (need to upload to PYPI later)::

   pip install rltk

Example 1::

   >>> import rltk
   >>> rltk.levenshtein_distance('abc', 'abd')
   1

In RLTK, you can simply load the the resource you need and give it name, then reuse it by name in later methods.

Example 2::

   >>> import rltk
   >>>
   >>> edit_distance_cost = {'insert': {'c':50}, 'insert_default':100, 'delete_default':100, 'substitute_default':100}
   >>>
   >>> tk = rltk.init()
   >>> tk.load_edit_distance_table('A1', edit_distance_cost) # load resource
   >>> tk.levenshtein_distance('a', 'abc')
   >>> 2
   >>> tk.levenshtein_distance('a', 'abc', name='A1')
   >>> 150
   >>> tk.normalized_levenshtein_distance('a', 'abc', name='A1')
   >>> 50.0


API Reference
--------------

.. toctree::
   :maxdepth: 2

   modules.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
