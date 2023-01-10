# StonPy

StonPy is a package that allows users to store SBGN maps into a Neo4j database, query the database, and convert query results back to valid SBGN maps.

## Installation

StonPy can be installed using `pip`:

```
pip install stonpy
```

## Quickstart

```python
from stonpy.core import STON

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
```

## Documentation

A complete documentation is available [here](https://stonpy.readthedocs.io/en/latest/).
