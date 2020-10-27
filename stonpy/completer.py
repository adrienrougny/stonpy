from stonpy.model import STONEnum

import stonpy.utils as utils

def complete_subgraph(subgraph, db_graph):
    """Completes a subgraph w.r.t to a graph and returns it.

    A relationship is completed by its start node and its end node (by default, in subgraphs).
    A shortucut relationship is also completed by the Arc node it corresponds to.
    In the following, when a node is completed by another node is shares a relationship with, the node is also completed by this relationship.
    A Map node is completed with all the Glyph, Arc and Arcgroup nodes it owns, which are themselves completed recursively.
    A Glyph node is completed with all its decorating Auxiliary unit and subglyph nodes, which are themselves completed recursively, with its Bbox node, with all its Port nodes, which are not completed recursively (except for the Process, Logical operator and Equivalence nodes, for which they are completed recursively), and with its owning Map node (if it is not a subglyph of another glyph or arcgroup).
    Among the Glyph nodes, the EPN and Activity nodes are also completed by the Compartment node they belong to, which is itself completed recursively.
    An Arc node is completed with its source, target, Start, End, Next and Cardinality nodes, the latter being completed recursively, and with its owning Map node (if it is not a subglyph of an arcgroup).
    An Arcgroup node is completed with all the Glyph and Arc nodes it owns, which are themselves completed recursively.
    Finally, a Port node is completed with the Glyph or Arc node that owns it, and with the Arc nodes whom it is a source or target node of.

    :param subgraph: the subgraph to complete
    :type subgraph: `py2neo.Subgraph`
    :param db_graph: the neo4j graph where to look for the completion
    :type db_graph: `py2neo.Graph`
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
            if node.has_label(STONEnum["GLYPH"].value):
                subgraph = _complete_subgraph_with_glyph_node(
                    node, subgraph, db_graph, completed)
            elif node.has_label(STONEnum["ARC"].value):
                subgraph = _complete_subgraph_with_arc_node(
                    node, subgraph, db_graph, completed)
            elif node.has_label(STONEnum["ARCGROUP"].value):
                subgraph = _complete_subgraph_with_arcgroup_node(
                    node, subgraph, db_graph, completed)
            elif node.has_label(STONEnum["BBOX"].value):
                subgraph = _complete_subgraph_with_bbox_node(
                    node, subgraph, db_graph, completed)
            elif node.has_label(STONEnum["MAP"].value):
                subgraph = _complete_subgraph_with_map_node(
                    node, subgraph, db_graph, completed)
            elif node.has_label(STONEnum["PORT"].value):
                subgraph = _complete_subgraph_with_port_node(
                    node, subgraph, db_graph, completed)

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
                    subgraph |= record["arc"]
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
        complete_end_node=False):

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
            subgraph |= relationship
            new_end_node = relationship.end_node
            new_start_node = relationship.start_node
            if end_node is None:
                subgraph |= new_end_node
            if start_node is None:
                subgraph |= new_start_node
            to_complete = []
            if complete_start_node and new_start_node not in completed:
                to_complete.append(new_start_node)
            if complete_end_node and new_end_node not in completed:
                to_complete.append(new_end_node)
            for node in to_complete:
                if node.has_label(STONEnum["GLYPH"].value):
                    subgraph =  _complete_subgraph_with_glyph_node(
                            node, subgraph, db_graph, completed)
                elif node.has_label(STONEnum["PORT"].value):
                    subgraph =  _complete_subgraph_with_port_node(
                            node, subgraph, db_graph, completed)
                elif node.has_label(STONEnum["ARC"].value):
                    subgraph =  _complete_subgraph_with_arc_node(
                            node, subgraph, db_graph, completed)
                elif node.has_label(STONEnum["BBOX"].value):
                    subgraph =  _complete_subgraph_with_bbox_node(
                            node, subgraph, db_graph, completed)
    return subgraph


def _complete_subgraph_with_glyph_node(node, subgraph, db_graph, completed):
    completed.add(node)

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
    if node.has_label(STONEnum["EPN"].value) or \
            node.has_label(STONEnum["ACTIVITY"].value):
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

    # STATE_VARIABLEs, UNIT_OF_INFORMATIONs, SUBUNITs, OUTCOMEs, TERMINALs
    if node.has_label(STONEnum["EPN"].value) or \
            node.has_label(STONEnum["ENTITY"].value) or \
            node.has_label(STONEnum["ACTIVITY"].value) or \
            node.has_label(STONEnum["SUBUNIT"].value) or \
            node.has_label(STONEnum["INTERACTION_GLYPH"].value) or \
            node.has_label(STONEnum["SUBMAP"].value):
        for r_name in ["HAS_STATE_VARIABLE",
                     "HAS_UNIT_OF_INFORMATION",
                     "HAS_SUBUNIT",
                     "HAS_OUTCOME",
                     "HAS_TERMINAL"]:
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

    # GLYPH's OWNING MAP
    if node.has_label(STONEnum["EPN"].value) or \
            node.has_label(STONEnum["ENTITY"].value) or \
            node.has_label(STONEnum["ACTIVITY"].value) or \
            node.has_label(STONEnum["COMPARTMENT"].value) or \
            node.has_label(STONEnum["SUBMAP"].value) or \
            node.has_label(STONEnum["VALUE"].value) or \
            node.has_label(STONEnum["LOGICAL_OPERATOR"].value) or \
            node.has_label(STONEnum["STOICHIOMETRIC_PROCESS"].value) or \
            node.has_label(STONEnum["INTERACTION_ARCGROUP"].value) or \
            node.has_label(STONEnum["EQUIVALENCE"].value):
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

    # STATE_VARIABLE, UNIT_OF_INFORMATION, SUBUNIT, OR OUTCOME OWNING GLYPH
    node_label = None
    if node.has_label(STONEnum["STATE_VARIABLE"].value):
        node_label = "STATE_VARIABLE"
    elif node.has_label(STONEnum["UNIT_OF_INFORMATION"].value):
        node_label = "UNIT_OF_INFORMATION"
    elif node.has_label(STONEnum["SUBUNIT"].value):
        node_label = "SUBUNIT"
    elif node.has_label(STONEnum["OUTCOME"].value):
        node_label = "OUTCOME"
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


def _complete_subgraph_with_port_node(node, subgraph, db_graph, completed):
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


def _complete_subgraph_with_bbox_node(node, subgraph, db_graph, completed):
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


def _complete_subgraph_with_arc_node(node, subgraph, db_graph, completed):
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


def _complete_subgraph_with_arcgroup_node(node, subgraph, db_graph, completed):
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

    # MAP
    subgraph = _find_relationship_and_complete_subgraph(
        "HAS_MAP",
        subgraph,
        db_graph,
        completed,
        nary = False,
        start_node = None,
        end_node = node,
        complete_start_node = False,
        complete_end_node = False)
    return subgraph


def _complete_subgraph_with_map_node(node, subgraph, db_graph, completed):
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
