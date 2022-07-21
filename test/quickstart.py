import os

from stonpy.core import STON

from credentials import URI, USER, PASSWORD

ston = STON(URI, USER, PASSWORD)
ston.graph.delete_all()

ston.create_map(
    sbgn_map="maps/mapk_cascade.sbgn",
    map_id="my_id"
)

my_query = """
   MATCH (m:Map {id: 'my_id'})-[r:HAS_GLYPH]->(p:StoichiometricProcess)
   RETURN p
"""

sbgn_files = ston.query_to_sbgn_file(
    query=my_query,
    sbgn_file="my_query_result.sbgn",
    complete=True,
    merge_records=False
)

print(sbgn_files)
