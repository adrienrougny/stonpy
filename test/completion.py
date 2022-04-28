#!/bin/python

import stonpy

from credentials import URI, USER, PASSWORD

ston = stonpy.ston.STON(URI, USER, PASSWORD)

query_process = """MATCH (m:Map {id: "neuronal_muscle_signalling.sbgn"})-[:HAS_GLYPH]->(p:Process {id: "glyph19"})
RETURN p
"""

query_terminal = """MATCH (t:Terminal) RETURN t"""

query_epn = """MATCH (m:Map {id: "activated_stat1alpha_induction_of_the_irf1_gene.sbgn"})-[HAS_GLYPH]->(e:Epn {id: "glyph13"}) RETURN e"""

query_entity = """MATCH (m:Map {id: "regulation_of_calcium_calmoduline_kinase_ii_effect_on_synaptic_plasticity.sbgn"})-[HAS_GLYPH]->(e:Entity {id: "glyph0"}) RETURN e"""


ston.query_to_sbgn_file(query_process, "maps_completion/query_process_no_modulations.sbgn", complete=True, to_top_left=True)
ston.query_to_sbgn_file(query_process, "maps_completion/query_process_modulations.sbgn", complete=True, to_top_left=True, complete_process_modulations=True)

ston.query_to_sbgn_file(query_terminal, "maps_completion/query_terminal.sbgn", complete=True, to_top_left=True)

ston.query_to_sbgn_file(query_epn, "maps_completion/query_epn.sbgn", complete=True, to_top_left=True)

ston.query_to_sbgn_file(query_entity, "maps_completion/query_entity.sbgn", complete=True, to_top_left=True)
