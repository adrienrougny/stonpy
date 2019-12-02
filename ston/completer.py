from ston.model import STONEnum

import ston.utils as utils


def complete_subgraph(subgraph, neograph):
    completed = set([])
    for relationship in subgraph.relationships:
        subgraph |= complete_subgraph_with_relationship(
            subgraph, relationship, completed, neograph)
    for node in subgraph.nodes:
        if node not in completed:
            if node.has_label(STONEnum["GLYPH"].value):
                subgraph |= complete_subgraph_with_glyph_node(
                    subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["ARC"].value):
                subgraph |= complete_subgraph_with_arc_node(
                    subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["ARCGROUP"].value):
                subgraph |= complete_subgraph_with_arcgroup_node(
                    subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["BBOX"].value):
                subgraph |= complete_subgraph_with_bbox_node(
                    subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["MAP"].value):
                subgraph |= complete_subgraph_with_map_node(
                    subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["PORT"].value):
                subgraph |= complete_subgraph_with_port_node(
                    subgraph, node, completed, neograph)
    return subgraph


def complete_subgraph_with_relationship(
        subgraph, relationship, completed, neograph):
    completed.add(relationship)
    start_node = relationship.start_node
    end_node = relationship.end_node
    subgraph |= start_node
    subgraph |= end_node
    r_type = type(relationship).__name__
    shortcut = "_SHORTCUT"
    if STONEnum(r_type).name.endswith(shortcut):
        arc_label = STONEnum[STONEnum(r_type).name[:-len(shortcut)]].value
        if r_type == STONEnum["CONSUMPTION_SHORTCUT"].value or \
                r_type == STONEnum["EQUIVALENCE_ARC_SHORTCUT"].value:
            source = utils.node_to_cypher(end_node)
            target = utils.node_to_cypher(start_node)
        elif r_type == STONEnum["CATALYSIS_SHORTCUT"].value or \
                r_type == STONEnum["MODULATION_SHORTCUT"].value or \
                r_type == STONEnum["STIMULATION_SHORTCUT"].value or \
                r_type == STONEnum["INHIBITION_SHORTCUT"].value or \
                r_type == STONEnum["NECESSARY_STIMULATION_SHORTCUT"].value or \
                r_type == STONEnum["PRODUCTION_SHORTCUT"].value or \
                r_type == STONEnum["LOGIC_ARC_SHORTCUT"].value or \
                r_type == STONEnum["NEGATIVE_INFLUENCE_SHORTCUT"].value or \
                r_type == STONEnum["POSITIVE_INFLUENCE_SHORTCUT"].value or \
                r_type == STONEnum["UNKNOWN_INFLUENCE_SHORTCUT"].value or \
                r_type == STONEnum["ASSIGNMENT_SHORTCUT"].value or \
                r_type == STONEnum["INTERACTION_SHORTCUT"].value:
            source = utils.node_to_cypher(start_node)
            target = utils.node_to_cypher(end_node)
        queries = []
        queries.append(
            'OPTIONAL MATCH {source}<-[:{has_source}]-(arc:{arc_label})-[:{has_target}]-{target} RETURN arc'.format(
                **{
                    "source": source,
                    "has_source": STONEnum["HAS_SOURCE"].value,
                    "arc_label": arc_label,
                    "has_target": STONEnum["HAS_TARGET"].value,
                    "target": target}))
        queries.append(
            'OPTIONAL MATCH {source}-[:{has_port}]->()<-[:{has_source}]-(arc:{arc_label})-[:{has_target}]->{target} RETURN arc'.format(
                **{
                    "source": source,
                    "has_source": STONEnum["HAS_SOURCE"].value,
                    "arc_label": arc_label,
                    "has_target": STONEnum["HAS_TARGET"].value,
                    "target": target,
                    "has_port": STONEnum["HAS_PORT"].value}))
        queries.append(
            'OPTIONAL MATCH {source}<-[:{has_source}]-(arc:{arc_label})-[:{has_target}]->()<-[:{has_port}]-{target} RETURN arc'.format(
                **{
                    "source": source,
                    "has_source": STONEnum["HAS_SOURCE"].value,
                    "arc_label": arc_label,
                    "has_target": STONEnum["HAS_TARGET"].value,
                    "target": target,
                    "has_port": STONEnum["HAS_PORT"].value}))
        queries.append('OPTIONAL MATCH {source}-[:{has_port}]->()<-[:{has_source}]-(arc:{arc_label})-[:{has_target}]->()<-[:{has_port}]-{target} RETURN arc'.format(
            **{
                "source": source,
                "has_source": STONEnum["HAS_SOURCE"].value,
                "arc_label": arc_label,
                "has_target": STONEnum["HAS_TARGET"].value,
                "target": target,
                "has_port": STONEnum["HAS_PORT"].value
            }
        ))
        stop = False
        for query in queries:
            tx = neograph.begin()
            cursor = tx.run(query)
            tx.commit()
            for record in cursor:
                if record["arc"] is not None:
                    subgraph |= record["arc"]
                    stop = True
                    break
            if stop:
                break
    return subgraph


def complete_subgraph_with_glyph_node(subgraph, node, completed, neograph):
    completed.add(node)

    # BBOX, COMPARTMENT
    for name in ["HAS_BBOX", "IS_IN_COMPARTMENT"]:
        relationship = utils.match_one(
            subgraph, (node,), STONEnum[name].value)
        if relationship is None:
            relationship = neograph.match_one((node,), STONEnum[name].value)
        if relationship is not None:
            subglyph_node = relationship.end_node
            subgraph |= relationship
            subgraph |= subglyph_node
            if name == "IS_IN_COMPARTMENT" and subglyph_node not in completed:
                subgraph |= complete_subgraph_with_glyph_node(
                    subgraph,
                    subglyph_node,
                    completed,
                    neograph)

    # PORTs only of node is a process or a logical operator
    if node.has_label(STONEnum["STOICHIOMETRIC_PROCESS"].value) or \
            node.has_label(STONEnum["LOGICAL_OPERATOR"].value) or \
            node.has_label(STONEnum["EQUIVALENCE"].value):
        relationships = neograph.match((node,), STONEnum["HAS_PORT"].value)
        for relationship in relationships:
            port_node = relationship.end_node
            subgraph |= relationship
            subgraph |= port_node
            if port_node not in completed:
                subgraph |= complete_subgraph_with_port_node(
                    subgraph,
                    port_node,
                    completed,
                    neograph)

    # STATE_VARIABLEs, UNIT_OF_INFORMATIONs, SUBUNITs, OUTCOMEs, TERMINALS
    for name in ["HAS_STATE_VARIABLE",
                 "HAS_UNIT_OF_INFORMATION",
                 "HAS_SUBUNIT", "HAS_OUTCOME",
                 "HAS_TERMINAL"]:
        relationships = neograph.match((node,), STONEnum[name].value)
        for relationship in relationships:
            subglyph_node = relationship.end_node
            subgraph |= relationship
            subgraph |= subglyph_node
            if subglyph_node not in completed:
                subgraph |= complete_subgraph_with_glyph_node(
                    subgraph,
                    subglyph_node,
                    completed,
                    neograph)

    # MAP
    relationship = utils.match_one(
        subgraph, (None, node), STONEnum["HAS_GLYPH"].value)
    if relationship is None:
        relationship = neograph.match_one(
            (None, node), STONEnum["HAS_GLYPH"].value)
    if relationship is not None:
        sbgnmap = relationship.start_node
        subgraph |= relationship
        subgraph |= sbgnmap

    # STATE_VARIABLE, UNIT_OF_INFORMATION, SUBUNIT, OR OUTCOME OWNER
    for name in [
        "HAS_STATE_VARIABLE",
        "HAS_UNIT_OF_INFORMATION",
        "HAS_SUBUNIT",
            "HAS_OUTCOME"]:
        relationship = utils.match_one(
            subgraph, (None, node), STONEnum[name].value)
        if relationship is None:
            relationship = neograph.match_one(
                (None, node), STONEnum[name].value)
        if relationship is not None:
            owner = relationship.start_node
            subgraph |= relationship
            subgraph |= owner
            if owner not in completed:
                if owner.has_label(STONEnum["GLYPH"].value):
                    subgraph |= complete_subgraph_with_glyph_node(
                        subgraph, owner, completed, neograph)
                elif owner.has_label(STONEnum["ARC"].value):
                    subgraph |= complete_subgraph_with_arc_node(
                        subgraph, owner, completed, neograph)

    return subgraph


def complete_subgraph_with_port_node(subgraph, port_node, completed, neograph):
    completed.add(port_node)
    # OWNER
    relationship = utils.match_one(
        subgraph, (None, port_node), STONEnum["HAS_PORT"].value)
    if relationship is None:
        relationship = neograph.match_one(
            (None, port_node), STONEnum["HAS_PORT"].value)
    if relationship is not None:
        owner = relationship.start_node
        subgraph |= relationship
        subgraph |= owner
        if owner not in completed:
            if owner.has_label(STONEnum["GLYPH"].value):
                subgraph |= complete_subgraph_with_glyph_node(
                    subgraph, owner, completed, neograph)
            elif owner.has_label(STONEnum["ARC"].value):
                subgraph |= complete_subgraph_with_arc_node(
                    subgraph, owner, completed, neograph)
    # SOURCE OF
    relationships = neograph.match(
        (None, port_node), STONEnum["HAS_SOURCE"].value)
    for relationship in relationships:
        arc_node = relationship.start_node
        subgraph |= relationship
        subgraph |= arc_node
        if arc_node not in completed:
            subgraph |= complete_subgraph_with_arc_node(
                subgraph, arc_node, completed, neograph)
    # TARGET OF
    relationships = neograph.match(
        (None, port_node), STONEnum["HAS_TARGET"].value)
    for relationship in relationships:
        arc_node = relationship.start_node
        subgraph |= relationship
        subgraph |= arc_node
        if arc_node not in completed:
            subgraph |= complete_subgraph_with_arc_node(
                subgraph, arc_node, completed, neograph)
    return subgraph


def complete_subgraph_with_bbox_node(subgraph, bbox_node, completed, neograph):
    # OWNER
    completed.add(bbox_node)
    relationship = utils.match_one(
        subgraph, (None, bbox_node), STONEnum["HAS_BBOX"].value)
    if relationship is None:
        relationship = neograph.match_one(
            (None, bbox_node), STONEnum["HAS_BBOX"].value)
    if relationship is not None:
        owner = relationship.start_node
        subgraph |= relationship
        subgraph |= owner
        if owner not in completed:
            subgraph |= complete_subgraph_with_glyph_node(
                subgraph, owner, completed, neograph)
    return subgraph


def complete_subgraph_with_arc_node(subgraph, node, completed, neograph):
    completed.add(node)
    # PORTs
    relationships = neograph.match((node,), STONEnum["HAS_PORT"].value)
    for relationship in relationships:
        port_node = relationship.end_node
        subgraph |= relationship
        subgraph |= port_node
    # OUTCOMEs
    relationships = neograph.match((node,), STONEnum["HAS_OUTCOME"].value)
    for relationship in relationships:
        subglyph_node = relationship.end_node
        subgraph |= relationship
        subgraph |= subglyph_node
        if subglyph_node not in completed:
            subgraph |= complete_subgraph_with_glyph_node(
                subgraph, subglyph_node, completed, neograph)
    # MAP
    relationship = utils.match_one(
        subgraph, (None, node), STONEnum["HAS_ARC"].value)
    if relationship is None:
        relationship = neograph.match_one(
            (None, node), STONEnum["HAS_ARC"].value)
    if relationship is not None:
        sbgnmap = relationship.start_node
        subgraph |= relationship
        subgraph |= sbgnmap
    # CARDINALITY
    relationship = utils.match_one(
        subgraph, (node,), STONEnum["HAS_CARDINALITY"].value)
    if relationship is None:
        relationship = neograph.match_one(
            (node,), STONEnum["HAS_CARDINALITY"].value)
    if relationship is not None:
        cardinality = relationship.end_node
        subgraph |= relationship
        subgraph |= cardinality
        if cardinality not in completed:
            subgraph |= complete_subgraph_with_glyph_node(
                subgraph, cardinality, completed, neograph)
    # SOURCE
    relationship = utils.match_one(
        subgraph, (node,), STONEnum["HAS_SOURCE"].value)
    if relationship is None:
        relationship = neograph.match_one(
            (node,), STONEnum["HAS_SOURCE"].value)
    if relationship is not None:
        source = relationship.end_node
        subgraph |= relationship
        subgraph |= source
        if source not in completed:
            if source.has_label(STONEnum["PORT"].value):
                subgraph |= complete_subgraph_with_port_node(
                    subgraph, source, completed, neograph)
            else:
                subgraph |= complete_subgraph_with_glyph_node(
                    subgraph, source, completed, neograph)
    # TARGET
    relationship = utils.match_one(
        subgraph, (node,), STONEnum["HAS_TARGET"].value)
    if relationship is None:
        relationship = neograph.match_one(
            (node,), STONEnum["HAS_TARGET"].value)
    if relationship is not None:
        target = relationship.end_node
        subgraph |= relationship
        subgraph |= target
        if target not in completed:
            if target.has_label(STONEnum["PORT"].value):
                subgraph |= complete_subgraph_with_port_node(
                    subgraph, target, completed, neograph)
            else:
                subgraph |= complete_subgraph_with_glyph_node(
                    subgraph, target, completed, neograph)
    # START
    relationship = utils.match_one(
        subgraph, (node,), STONEnum["HAS_START"].value)
    if relationship is None:
        relationship = neograph.match_one((node,), STONEnum["HAS_START"].value)
    if relationship is not None:
        start = relationship.end_node
        subgraph |= relationship
        subgraph |= start
    # END
    relationship = utils.match_one(
        subgraph, (node,), STONEnum["HAS_END"].value)
    if relationship is None:
        relationship = neograph.match_one((node,), STONEnum["HAS_END"].value)
    if relationship is not None:
        end = relationship.end_node
        subgraph |= relationship
        subgraph |= end
    return subgraph


def complete_subgraph_with_arcgroup_node(subgraph, node, completed, neograph):
    # ARCs
    relationships = neograph.match((node,), STONEnum["HAS_ARC"].value)
    for relationship in relationships:
        arc_node = relationship.end_node
        subgraph |= relationship
        subgraph |= arc_node
        if arc_node not in completed:
            subgraph |= complete_subgraph_with_arc_node(
                subgraph, arc_node, completed, neograph)
    # GLYPHs
    relationships = neograph.match((node,), STONEnum["HAS_GLYPH"].value)
    for relationship in relationships:
        glyph_node = relationship.end_node
        subgraph |= relationship
        subgraph |= glyph_node
        if glyph_node not in completed:
            subgraph |= complete_subgraph_with_glyph_node(
                subgraph, glyph_node, completed, neograph)
    # MAP
    relationship = utils.match_one(
        subgraph, (None, node), STONEnum["HAS_ARCGROUP"].value)
    if relationship is None:
        relationship = neograph.match_one(
            (None, node), STONEnum["HAS_ARCGROUP"].value)
    if relationship is not None:
        sbgnmap = relationship.start_node
        subgraph |= relationship
        subgraph |= sbgnmap
    return subgraph


def complete_subgraph_with_map_node(subgraph, node, completed, neograph):
    # ARCs
    relationships = neograph.match((node,), STONEnum["HAS_ARC"].value)
    for relationship in relationships:
        arc_node = relationship.end_node
        subgraph |= relationship
        subgraph |= arc_node
        if arc_node not in completed:
            subgraph |= complete_subgraph_with_arc_node(
                subgraph, arc_node, completed, neograph)
    # GLYPHs
    relationships = neograph.match((node,), STONEnum["HAS_GLYPH"].value)
    for relationship in relationships:
        glyph_node = relationship.end_node
        subgraph |= relationship
        subgraph |= glyph_node
        if glyph_node not in completed:
            subgraph |= complete_subgraph_with_glyph_node(
                subgraph, glyph_node, completed, neograph)
    # ARCGROUPs
    relationships = neograph.match((node,), STONEnum["HAS_ARCGROUP"].value)
    for relationship in relationships:
        arcgroup_node = relationship.end_node
        subgraph |= relationship
        subgraph |= arcgroup_node
        if arcgroup_node not in completed:
            subgraph |= complete_subgraph_with_arcgroup_node(
                subgraph, arcgroup_node, completed, neograph)
    return subgraph
