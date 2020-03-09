import stonpy

uri = "bolt://localhost:7687"
user = "neo4j"
password = "neofourj"

ston = stonpy.STON(uri, user, password)

# ston.graph.delete_all()
# ston.create_map("insulin.sbgn", "id1")
# ston.get_map_to_sbgn_file("id1", "insulin_exported.sbgn")

query1 = 'MATCH (p)-[:CONSUMES]->(n {label:"IRS1-4"}) RETURN p'
# query1 = 'MATCH (b)<-[hb:HAS_BBOX]-(p)-[c:CONSUMES]->(n {label:"IRS1-4"}), (m:Map)-[hg:HAS_GLYPH]->(p), (m)-[hg] RETURN p, b, m'

ston.query_to_sbgn_file(query1, "query1.sbgn", complete=True)
