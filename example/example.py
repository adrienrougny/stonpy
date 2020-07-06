import stonpy

uri = "bolt://localhost:7687"
user = "neo4j"
password = "neofourj"

ston = stonpy.STON(uri, user, password)

sbgn_file = "insulin.sbgn"

ston.graph.delete_all()
ston.create_map(sbgn_file, "id1")

assert ston.has_map("id1") is True
assert ston.has_map(sbgn_map=sbgn_file) is True
assert ston.has_map(map_id="id1", sbgn_map=sbgn_file) is True
assert ston.has_map(map_id="id2", sbgn_map=sbgn_file) is False

ston.get_map_to_sbgn_file("id1", "insulin_exported.sbgn")

query1 = 'MATCH (p)-[:CONSUMES]->(n {label:"IRS1-4"}) RETURN p'

query2 = '''MATCH (process)-[:CONSUMES]->(reactant),
    (process)-[:PRODUCES]->(product),
    (reactant)-[:HAS_STATE_VARIABLE]-(reactant_sv),
    (product)-[:HAS_STATE_VARIABLE]-(product_sv)
    WHERE reactant.label = product.label
    AND reactant_sv.value IS NULL
    AND product_sv.value = "P"
    AND (product_sv.variable IS NULL
        AND reactant_sv.variable IS NULL
        AND product_sv.order = reactant_sv.order
        OR product_sv.variable = reactant_sv.variable)
    RETURN process;'''

ston.query_to_sbgn_file(query1, "query1.sbgn", complete=True)
ston.query_to_sbgn_file(query2, "query2.sbgn", complete=True, merge_records=True)
ston.query_to_sbgn_file(query2, "query2_no_merge.sbgn", complete=True, merge_records=False, to_top_left=True)
