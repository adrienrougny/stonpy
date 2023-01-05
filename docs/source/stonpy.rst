stonpy package
==============

Installation
------------

StonPy can be installed using `pip`:

.. code-block:: bash

    pip install stonpy

You may also install the `Neo4j APOC core Library <https://neo4j.com/docs/apoc/current/>`_, which is an optional dependency for StonPy.
When installed, the library will make the `get_map function` of the :doc:`/stonpy.core` significantly faster.


Quickstart
----------

The following snippet of code will make you started with StonPy.
For a more complete tutorial, a Jupyter Notebook is available `here <https://github.com/adrienrougny/stonpy/blob/master/notebooks/demo.ipynb>`_.

.. code-block:: python

   from stonpy import STON

   ston = STON("URI", "USER", "PASSWORD")
   ston.create_map(sbgn_map="my_sbgn_file.sbgn", map_id="my_map_id")
   my_query = """
       MATCH (m:Map {id: 'my_map_id'})-[r:HAS_GLYPH]->(p:StoichiometricProcess)
       RETURN p
   """
   sbgn_files = ston.query_to_sbgn_file(
       query=my_query,
       sbgn_file="my_query_result.sbgn",
       merge_records=False
   )

   print(sbgn_files)


Package documentation
---------------------

Following is the documentation for the different modules of the package.
The main module of the package is the :doc:`/stonpy.core`; the other modules offer functions and classes used by this main module.

.. toctree::
   :maxdepth: 0

   stonpy.core
   stonpy.conversion
   stonpy.completion
   stonpy.model
   stonpy.sbgn
   stonpy.utils

Completion
----------------

When the result of a query is a subgraph (including a unique node or relationship), it may be completed to form a “complete subgraph” using the :doc:`/stonpy.completion`.
The documentation for the completion algorithm used in this module can be found :doc:`here <completion_rules>`.

Command line interface
----------------------

The StonPy package includes a command line interface (CLI) which allows users to perform all the operations supported by the library.
StonPy's CLI is installed with the package, and may be executed with the `stonpy` command:

.. code-block:: shell

   stonpy --help

The complete documentation for the CLI can be found :doc:`here <cli>`.
