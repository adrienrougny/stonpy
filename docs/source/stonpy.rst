stonpy package
==============

Quickstart
----------

.. code-block:: python

   from stonpy.ston import STON

   ston = STON("URI", "USER", "PASSWORD")
   ston.create_map(sbgn_map="my_sbgn_file.sbgn", map_id="my_map_id")
   my_query = """
       MATCH (m:Map {id: 'my_map_id'})-[r:HAS_GLYPH]->(p:StoichiometricProcess)
       RETURN p
   """
   sbgn_files = ston.query_to_sbgn_file(
       query=my_query,
       sbgn_file="my_query_result.sbgn",
       complete=True,
       merge_records=False
   )

   print(sbgn_files)

Submodules
----------

.. toctree::
   :maxdepth: 4

   stonpy.ston
   stonpy.converter
   stonpy.completor
   stonpy.model
   stonpy.sbgn
   stonpy.utils

Completion
----------
.. toctree::
   :maxdepth: 4

   completion_rules


