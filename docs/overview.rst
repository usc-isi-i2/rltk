Overview
=================

What's Record Linkage
---------------------

Record linkage (RL) is the task of finding records in a data set that refer to the same entity across different data sources (e.g., data files, books, websites, and databases). -- Wikipedia

Assume we have two following tables:

.. image:: images/overview-tables.png
   :scale: 60 %

It's obvious that both of them have *id* ``A04`` and these two belong to the same entity. Then we know that "David's id is A04 and he is a male".

But real world situations are more complex:

* Typos: “Joh” vs “John”
* OCR errors: “J0hn” vs “John”
* Formatting conventions: “03/17” vs “March 17”
* Abbreviations: “J. K. Rowling” vs “Joanne Rowling”
* Nick names: “John” vs “Jock”
* Word order: “Sargent, John S.” vs “John S. Sargent”

Record Linkage Toolkit (RLTK) is designed to give a easy to use, scalable and extensible way of resolving these problems.

Basic Components & Data Flow
----------------------------

The first step of using RLTK is to create ``Dataset``.

.. image:: images/overview-dataflow.png
   :scale: 60 %

In RLTK, every "row" in table is called ``Record``. Notice "row" here is a logical concept: for a csv file it's a csv object (can be formed by multiple lines); for a json lines file, it's a line object; for a query from DBMS, it's one row; for some self-defined stream, it's a minimal entity.

``Dataset`` is a "table", or more precise, a collection of ``Record`` s.

``Reader`` is used to handle heterogeneous input. For each "row", the return of the ``Reader`` is represented in a Python dictionary, named ``raw_object`` (shown as grey ``{...}`` in figure). ``Record`` is generated based on ``raw_object``: user need to extend base ``Record`` class and add properties for later usage.

``Adapter`` is where all ``Record`` s get stored. It can be either in memory or persistent.

So, the data flow is: in order to create ``Dataset``, use ``Reader`` to read from input source and convert entity by entity to ``raw_object`` which is used to construct ``Record``, then store ``Record`` in ``Adapter``.

Obviously, generating ``Record`` is really time consuming if the dataset is large, but if the concrete ``Adapter`` is a persistent one (e.g., ``HBaseAdapter``), then next time, ``Dataset`` can be loaded directly from this ``Adapter`` instead of regenerating again from raw input.

Minimal Workflow
----------------

Now we have two ``Datasets`` and we need to find pairs (If it's de-duplication problem, only one ``Dataset`` is needed).

.. image:: images/overview-basic-workflow.png
   :scale: 60 %

Simply using RLTK's API to get all possible combinations of candidate pairs and implement your only "magical function" to find if two ``Record`` s are the same.

Let's look at an example input datasets and minimal implementation.

.. image:: images/overview-inputs.png
   :scale: 60 %

.. code-block:: python

	import rltk

	class Record1(rltk.Record):
	    @property
	    def id(self):
	        return self.raw_object['doc_id']

	    @property
	    def value(self):
	        return self.raw_object['doc_value']

	class Record2(rltk.Record):
	    @rltk.cached_property
	    def id(self):
	        return self.raw_object['ident']

	    @rltk.cached_property
	    def value(self):
	        v = self.raw_object.get('values', list())
	        return v[0] if len(v) > 0 else 'empty'


	ds1 = rltk.Dataset(reader=rltk.CSVReader('ds1.csv'),
	                   record_class=Record1, adapter=rltk.MemoryAdapter())
	ds2 = rltk.Dataset(reader=rltk.JsonLinesReader('ds2.jl'),
	                   record_class=Record2, adapter=rltk.DBMAdapter('file_index'))

	pairs = rltk.get_record_pairs(ds1, ds2)
	for r1, r2 in pairs:
	    print('-------------')
	    print(r1.id, r1.value, '\t', r2.id, r2.value)
	    print('levenshtein_distance:', rltk.levenshtein_distance(r1.value, r2.value))
	    print('levenshtein_similarity:', rltk.levenshtein_similarity(r1.value, r2.value))

Evaluation
----------


Blocking
--------


Optimization
------------
