import ston

uri = "bolt://localhost:7687"
user = "neo4j"
password = "neofourj"

ston = ston.STON(uri, user, password)

# ston.neograph.delete_all()
# ston.create_map("/home/rougny/insulin.sbgn", "id1")

query = 'MATCH (process:Process), (process)-[consumption: CONSUMES]-(reactant:Macromolecule), (process)-[production: PRODUCES]-(product: Macromolecule), (catalyzer)-[catalysis: CATALYZES]-(process), (reactant)-[:HAS_STATE_VARIABLE]-(sv_reactant), (product)-[:HAS_STATE_VARIABLE]-(sv_product) WHERE sv_reactant.value IS NULL AND sv_product.value = "P" AND (sv_reactant.variable IS NULL AND sv_product.variable IS NULL OR sv_reactant.variable = sv_product.variable) RETURN catalysis'

ston.query_to_sbgnfile(query, "/home/rougny/res.sbgn", merge_records = False)
