"""The module for completing subgraphs to form complete subgraphs that can be 
converted to SBGN maps."""

from stonpy.model import STONEnum

import stonpy.utils as utils

def _choose_node_completion_function(node):
    for label in node.labels:
        name = STONEnum(label).name
        if name in _node_completion_functions:
            return _node_completion_functions[name]
    raise Exception(f"No completion function for node {node}")


def complete_subgraph(subgraph, db_graph, complete_process_modulations=False):
    """Complete a subgraph w.r.t to a graph and returns it.

    See :ref:`completion` for more details.

    :param subgraph: the subgraph to complete
    :type subgraph: `py2neo.Subgraph`
    :param db_graph: the neo4j graph where to look for the completion
    :type db_graph: `py2neo.Graph`
    :param complete_process_modulations: option to complete processes with the modulations targetting it, default is `False`
    :type complete_process_modulations: `bool`
    :return: the completed subgraph
    :rtype: `py2neo.Subgraph`
    """
    completed = set([])
    for relationship in subgraph.relationships:
        if relationship not in completed:
            subgraph = _complete_subgraph_with_relationship(
                relationship, subgraph, db_graph, completed)
    for node in subgraph.nodes:
        if node not in completed:
            subgraph = _complete_subgraph_with_node(node, subgraph, db_graph,
                                                    completed,
                                                    complete_process_modulations)
    return subgraph

def _complete_subgraph_with_node(node, subgraph, db_graph, completed,
                                 complete_process_modulations):
    completion_func = _choose_node_completion_function(node)
    subgraph = completion_func(node, subgraph, db_graph, completed,
                               complete_process_modulations)
    return subgraph


def _complete_subgraph_with_relationship(
        relationship, subgraph, db_graph, completed):
    completed.add(relationship)

    shortcut = "_SHORTCUT"
    r_type = type(relationship).__name__
    if STONEnum(r_type).name.endswith(shortcut):
        start_node = relationship.start_node
        end_node = relationship.end_node
        arc_label = STONEnum[STONEnum(r_type).name[:-len(shortcut)]].value
        if r_type == STONEnum["CONSUMPTION_SHORTCUT"].value or \
                r_type == STONEnum["EQUIVALENCE_ARC_SHORTCUT"].value or \
                r_type == STONEnum["LOGIC_ARC_SHORTCUT"].value:
            source_id = end_node.identity
            target_id = start_node.identity
        else:
            source_id = start_node.identity
            target_id = end_node.identity
        queries = []
        queries.append(
                """OPTIONAL MATCH (arc:{arc_label})-[:{has_source}]->(source),
                (arc)-[:{has_target}]->(target)
                WHERE id(source) = {source_id} AND id(target) = {target_id}
                RETURN arc""".format(
                    arc_label =  arc_label,
                    has_source = STONEnum["HAS_SOURCE"].value,
                    has_target =  STONEnum["HAS_TARGET"].value,
                    source_id = source_id,
                    target_id = target_id))
        queries.append(
                """OPTIONAL MATCH (arc:{arc_label})-[:{has_source}]->(source_port),
                (source)-[:{has_port}]->(source_port),
                (arc)-[:{has_target}]->(target)
                WHERE id(source) = {source_id} AND id(target) = {target_id}
                RETURN arc""".format(
                    arc_label =  arc_label,
                    has_source = STONEnum["HAS_SOURCE"].value,
                    has_port = STONEnum["HAS_PORT"].value,
                    has_target =  STONEnum["HAS_TARGET"].value,
                    source_id = source_id,
                    target_id = target_id))
        queries.append(
                """OPTIONAL MATCH (arc:{arc_label})-[:{has_source}]->(source),
                (arc)-[:{has_target}]->(target_port),
                (target)-[:{has_port}]->(target_port)
                WHERE id(source) = {source_id} AND id(target) = {target_id}
                RETURN arc""".format(
                    arc_label =  arc_label,
                    has_source = STONEnum["HAS_SOURCE"].value,
                    has_port = STONEnum["HAS_PORT"].value,
                    has_target =  STONEnum["HAS_TARGET"].value,
                    source_id = source_id,
                    target_id = target_id))
        queries.append(
                """OPTIONAL MATCH (arc:{arc_label})-[:{has_source}]->(source_port),
                (source)-[:{has_port}]->(source_port),
                (arc)-[:{has_target}]->(target_port),
                (target)-[:{has_port}]->(target_port)
                WHERE id(source) = {source_id} AND id(target) = {target_id}
                RETURN arc""".format(
                    arc_label =  arc_label,
                    has_source = STONEnum["HAS_SOURCE"].value,
                    has_port = STONEnum["HAS_PORT"].value,
                    has_target =  STONEnum["HAS_TARGET"].value,
                    source_id = source_id,
                    target_id = target_id))
        stop = False
        for query in queries:
            cursor = db_graph.run(query)
            for record in cursor:
                if record["arc"] is not None:
                    subgraph = subgraph | record["arc"]
                    stop = True
                    break
            if stop:
                break
    return subgraph

def _find_relationship_and_complete_subgraph(
        r_name,
        subgraph,
        db_graph,
        completed,
        nary=False,
        start_node=None,
        end_node=None,
        complete_start_node=False,
        complete_end_node=False,
        complete_process_modulations=False):

    if not nary:
        relationship = utils.match_one(
            subgraph, (start_node, end_node), STONEnum[r_name].value)
        if relationship is None:
            relationship = db_graph.match_one(
                    (start_node, end_node), STONEnum[r_name].value)
        relationships = [relationship]
    elif nary:
        relationships = db_graph.match(
                (start_node, end_node), STONEnum[r_name].value)
    for relationship in relationships:
        if relationship is not None and relationship not in completed:
            completed.add(relationship)
            subgraph = subgraph | relationship
            new_end_node = relationship.end_node
            new_start_node = relationship.start_node
            if end_node is None:
                subgraph = subgraph | new_end_node
            if start_node is None:
                subgraph = subgraph | new_start_node
            to_complete = []
            if complete_start_node and new_start_node not in completed:
                to_complete.append(new_start_node)
            if complete_end_node and new_end_node not in completed:
                to_complete.append(new_end_node)
            for node in to_complete:
                subgraph = _complete_subgraph_with_node(
                    node,
                    subgraph,
                    db_graph,
                    completed,
                    complete_process_modulations
                )

    return subgraph


def _complete_subgraph_with_glyph_node(node, subgraph, db_graph, completed, complete_process_modulations):
    completed.add(node)

    # LABEL
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_LABEL",
        subgraph,
        db_graph,
        completed,
        nary = False,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = True)


    # BBOX
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_BBOX",
        subgraph,
        db_graph,
        completed,
        nary = False,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = False)

    # COMPARTMENT
    subgraph = _find_relationship_and_complete_subgraph(
        "IS_IN_COMPARTMENT",
        subgraph,
        db_graph,
        completed,
        nary = False,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = True)

    # PORTs only if node is a process or a logical/equivalence operator
    if node.has_label(STONEnum["STOICHIOMETRIC_PROCESS"].value) or \
            node.has_label(STONEnum["LOGICAL_OPERATOR"].value) or \
            node.has_label(STONEnum["EQUIVALENCE"].value):

        subgraph = _find_relationship_and_complete_subgraph(
            "HAS_PORT",
            subgraph,
            db_graph,
            completed,
            nary = True,
            start_node = node,
            end_node = None,
            complete_start_node = False,
            complete_end_node = True)

    # MODULATION ARCS targetting a process, only if node is a process and complete_process_modulations is True
    if node.has_label(STONEnum["STOICHIOMETRIC_PROCESS"].value) and complete_process_modulations:
        subgraph = _find_relationship_and_complete_subgraph(
            "HAS_TARGET",
            subgraph,
            db_graph,
            completed,
            nary = True,
            start_node = None,
            end_node = node,
            complete_start_node = True,
            complete_end_node = False)

    # AUXILLIARY UNITS
    for r_name in ["HAS_STATE_VARIABLE",
                 "HAS_UNIT_OF_INFORMATION",
                 "HAS_SUBUNIT",
                 "HAS_OUTCOME",
                 "HAS_TERMINAL",
                 "HAS_EXISTENCE",
                 "HAS_LOCATION"]:
        subgraph = _find_relationship_and_complete_subgraph(
            r_name,
            subgraph,
            db_graph,
            completed,
            nary = True,
            start_node = node,
            end_node = None,
            complete_start_node = False,
            complete_end_node = True)

    # GLYPH's OWNING MAP IF NOT AUXILLIARY UNIT
    if not node.has_label(STONEnum["AUXILLIARY_UNIT"].value):
        subgraph = _find_relationship_and_complete_subgraph(
            "HAS_GLYPH",
            subgraph,
            db_graph,
            completed,
            nary = False,
            start_node = None,
            end_node = node,
            complete_start_node = False,
            complete_end_node = False)

    # STATE_VARIABLE, UNIT_OF_INFORMATION, SUBUNIT, OUTCOME OWNING GLYPH OR TERMINAL
    node_labels = [
        "EXISTENCE",
        "LOCATION",
        "STATE_VARIABLE",
        "UNIT_OF_INFORMATION",
        "SUBUNIT",
        "OUTCOME",
        "TERMINAL"
    ]
    node_label = None
    for label in node_labels:
        if node.has_label(STONEnum[label].value):
            node_label = label
            break
    if node_label is not None:
        subgraph = _find_relationship_and_complete_subgraph(
            "HAS_{}".format(node_label),
            subgraph,
            db_graph,
            completed,
            nary = False,
            start_node = None,
            end_node = node,
            complete_start_node = True,
            complete_end_node = False)
    return subgraph


def _complete_subgraph_with_port_node(node, subgraph, db_graph, completed, complete_process_modulations):
    completed.add(node)

    # OWNER GLYPH
    subgraph = _find_relationship_and_complete_subgraph(
            "HAS_PORT",
            subgraph,
            db_graph,
            completed,
            nary = False,
            start_node = None,
            end_node = node,
            complete_start_node = True,
            complete_end_node = False)

    # SOURCE OF ARC, TARGET OF ARC
    for r_name in ["HAS_SOURCE", "HAS_TARGET"]:
        subgraph = _find_relationship_and_complete_subgraph(
            r_name,
            subgraph,
            db_graph,
            completed,
            nary = True,
            start_node = None,
            end_node = node,
            complete_start_node = True,
            complete_end_node = False)
    return subgraph


def _complete_subgraph_with_bbox_node(node, subgraph, db_graph, completed, complete_process_modulations):
    completed.add(node)

    # OWNER GLYPH
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_BBOX",
        subgraph,
        db_graph,
        completed,
        nary = False,
        start_node = None,
        end_node = node,
        complete_start_node = True,
        complete_end_node = False)
    return subgraph

def _complete_subgraph_with_arc_point_node(node, subgraph, db_graph, completed, complete_process_modulations):
    completed.add(node)

    # OWNER GLYPH
    if node.has_label(STONEnum["END"].value):
        r_type = STONEnum["HAS_END"].value
    elif node.has_label(STONEnum["START"].value):
        r_type = STONEnum["HAS_START"].value
    elif node.has_label(STONEnum["NEXT"].value):
        r_type = STONEnum["HAS_NEXT"].value
    subgraph = _find_relationship_and_complete_subgraph(
        r_type,
        subgraph,
        db_graph,
        completed,
        nary = False,
        start_node = None,
        end_node = node,
        complete_start_node = True,
        complete_end_node = False)
    return subgraph


def _complete_subgraph_with_label_node(node, subgraph, db_graph, completed, complete_process_modulations):
    completed.add(node)

    # OWNER GLYPH
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_LABEL",
        subgraph,
        db_graph,
        completed,
        nary = False,
        start_node = None,
        end_node = node,
        complete_start_node = True,
        complete_end_node = False)
    return subgraph


def _complete_subgraph_with_arc_node(node, subgraph, db_graph, completed, complete_process_modulations):
    completed.add(node)

    # PORTs
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_PORT",
        subgraph,
        db_graph,
        completed,
        nary = True,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = False)

    # OUTCOMEs
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_OUTCOME",
        subgraph,
        db_graph,
        completed,
        nary = True,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = True)

    # MAP
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_ARC",
        subgraph,
        db_graph,
        completed,
        nary = False,
        start_node = None,
        end_node = node,
        complete_start_node = False,
        complete_end_node = False)

    # CARDINALITY, SOURCE, TARGET
    for r_name in ["HAS_CARDINALITY", "HAS_SOURCE", "HAS_TARGET"]:
        subgraph = _find_relationship_and_complete_subgraph(
            r_name,
            subgraph,
            db_graph,
            completed,
            nary = False,
            start_node = node,
            end_node = None,
            complete_start_node = False,
            complete_end_node = True)

    # START, END
    for r_name in ["HAS_START", "HAS_END"]:
        subgraph = _find_relationship_and_complete_subgraph(
            r_name,
            subgraph,
            db_graph,
            completed,
            nary = False,
            start_node = node,
            end_node = None,
            complete_start_node = False,
            complete_end_node = False)

    # NEXT
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_NEXT",
        subgraph,
        db_graph,
        completed,
        nary = True,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = False)
    return subgraph


def _complete_subgraph_with_arcgroup_node(node, subgraph, db_graph, completed, complete_process_modulations):
    completed.add(node)

    # ARCs
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_ARC",
        subgraph,
        db_graph,
        completed,
        nary = True,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = True)

    # OWNING MAP
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_ARCGROUP",
        subgraph,
        db_graph,
        completed,
        nary = False,
        start_node = None,
        end_node = node,
        complete_start_node = False,
        complete_end_node = False)
    return subgraph


def _complete_subgraph_with_map_node(node, subgraph, db_graph, completed, complete_process_modulations):
    completed.add(node)

    # ARCs
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_ARC",
        subgraph,
        db_graph,
        completed,
        nary = True,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = True)

    # GLYPHs
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_GLYPH",
        subgraph,
        db_graph,
        completed,
        nary = True,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = True)

    # ARCGROUPs
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_ARCGROUP",
        subgraph,
        db_graph,
        completed,
        nary = True,
        start_node = node,
        end_node = None,
        complete_start_node = False,
        complete_end_node = True)
    return subgraph

_node_completion_functions = {
    "GLYPH": _complete_subgraph_with_glyph_node,
    "ARC": _complete_subgraph_with_arc_node,
    "ARCGROUP": _complete_subgraph_with_arcgroup_node,
    "BBOX": _complete_subgraph_with_bbox_node,
    "MAP": _complete_subgraph_with_map_node,
    "PORT": _complete_subgraph_with_port_node,
    "LABEL": _complete_subgraph_with_label_node,
    "NEXT": _complete_subgraph_with_arc_point_node,
    "END": _complete_subgraph_with_arc_point_node,
    "START": _complete_subgraph_with_arc_point_node
}


