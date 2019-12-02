from py2neo import Database, Graph, Node, Relationship, Subgraph

import libsbgnpy.libsbgn as libsbgn

from ston.model import *
import ston.utils as utils

def map_to_subgraph(sbgnmap, map_id=None, make_shortcuts=True):
    dids = {}
    dpids = {}
    map_node = Node()

    map_node.add_label(STONEnum["MAP"].value)
    language = sbgnmap.get_language().value
    map_node[STONEnum["LANGUAGE"].value] = language
    map_node[STONEnum["MAP_ID"].value] = map_id

    subgraph = None
    for glyph in sbgnmap.get_glyph():
        if glyph.get_class().name == "COMPARTMENT":
            glyph_node, glyph_subgraph = _glyph_to_subgraph(glyph, dids, dpids)
            subgraph = utils.subgraph_union(subgraph, glyph_subgraph)
            dids[glyph.get_id()] = glyph_node
            subgraph |= Relationship(
                map_node, STONEnum["HAS_GLYPH"].value, glyph_node)

    for glyph in sbgnmap.get_glyph():
        if glyph.get_class().name != "COMPARTMENT":
            glyph_node, glyph_subgraph = _glyph_to_subgraph(glyph, dids, dpids)
            subgraph = utils.subgraph_union(subgraph, glyph_subgraph)
            subgraph |= Relationship(
                map_node, STONEnum["HAS_GLYPH"].value, glyph_node)

    for arc in sbgnmap.get_arc():
        if arc.get_class().name == "ASSIGNMENT" or \
                arc.get_class().name == "INTERACTION":
            arc_node, arc_subgraph = _arc_to_subgraph(arc, dids, dpids)
            subgraph |= arc_subgraph
            subgraph |= Relationship(
                map_node, STONEnum["HAS_ARC"].value, arc_node)
            dids[arc.get_id()] = arc_node

    for arc in sbgnmap.get_arc():
        if arc.get_class().name != "ASSIGNMENT" and \
                arc.get_class().name != "INTERACTION":
            arc_node, arc_subgraph = _arc_to_subgraph(
                    arc, dids, dpids, make_shortcuts)
            subgraph |= arc_subgraph
            subgraph |= Relationship(
                map_node, STONEnum["HAS_ARC"].value, arc_node)

    for arcgroup in sbgnmap.get_arcgroup():
        arcgroup_node, arcgroup_subgraph = _arcgroup_to_subgraph(
            arcgroup, dids, dpids, make_shortcuts)
        subgraph |= arcgroup_subgraph
        subgraph |= Relationship(
            map_node,
            STONEnum["HAS_ARCGROUP"].value,
            arcgroup_node)

    return subgraph


def _glyph_to_subgraph(glyph, dids, dpids, subunit=False, order=None):
    node = Node()
    subgraph = node
    ston_type = glyph.get_class().name
    if ston_type == "INTERACTION":
        ston_type = "{}_GLYPH".format(ston_type)
    elif ston_type == "PROCESS":
        ston_type = "GENERIC_{}".format(ston_type)
    if subunit:
        ston_type = "{}_SUBUNIT".format(ston_type)

    for ontology in Ontologies:
        if ston_type in ontology.value:
            node.add_label(STONEnum[ontology.name].value)
    node.add_label(STONEnum[ston_type].value)

    node[STONEnum["CLASS"].value] = glyph.get_class().value
    node[STONEnum["ID"].value] = glyph.get_id()

    if order is not None:
        node[STONEnum["ORDER"].value] = order

    if glyph.get_label():
        label = glyph.get_label().get_text()
        if ston_type == "UNIT_OF_INFORMATION":
            if ':' in label:
                node[STONEnum["PREFIX"].value] = label.split(':')[0]
                node[STONEnum["VALUE"].value] = label.split(':')[1]
            else:
                node[STONEnum["VALUE"].value] = label
        else:
            node[STONEnum["LABEL"].value] = label

    if glyph.get_clone():
        node[STONEnum["CLONE"].value] = True
        if glyph.get_clone().get_label():
            if glyph.get_clone().get_label().get_text():
                node[STONEnum["CLONE_LABEL"].value] = \
                        glyph.get_clone().get_label().get_text()
    else:
        node[STONEnum["CLONE"].value] = False

    if glyph.get_compartmentRef():
        node[STONEnum["COMPARTMENT_ORDER"].value] = \
                glyph.get_compartmentOrder()
    if glyph.get_compartmentRef():
        is_in_compartment = Relationship(node,
                                         STONEnum["IS_IN_COMPARTMENT"].value,
                                         dids[glyph.get_compartmentRef()])
        subgraph |= is_in_compartment

    if glyph.get_bbox():
        bbox = glyph.get_bbox()
        bbox_node = _bbox_to_node(bbox)
        subgraph |= bbox_node
        has_bbox = Relationship(node, STONEnum["HAS_BBOX"].value, bbox_node)
        subgraph |= has_bbox

    if glyph.orientation:
        node[STONEnum["ORIENTATION"].value] = glyph.orientation

    if glyph.get_state():
        value = glyph.get_state().get_value()
        if value == "":
            value = None
        variable = glyph.get_state().get_variable()
        if variable == "":
            variable = None
        node[STONEnum["VALUE"].value] = value
        node[STONEnum["VARIABLE"].value] = variable
    if glyph.get_entity():
        node[STONEnum["UI_TYPE"].value] = glyph.get_entity().name

    # If the glyph and all its svs have a bbox, we order the svs following
    # their angular placement on the border of the glyph (counter clock-wise).
    # This is useful when multiple svs have undefined variables.
    # If the glyph or one of the svs do not have a bbox, we do not order the
    # svs.
    svs = []
    bbox = glyph.get_bbox()
    all_bbox = bbox is not None
    for subglyph in glyph.get_glyph():
        sub_ston_type = subglyph.get_class().name
        if sub_ston_type == "STATE_VARIABLE":
            if subglyph.get_bbox() is None:
                all_bbox = False
            svs.append(subglyph)
    if all_bbox:
        center = (bbox.get_x() + bbox.get_w() / 2,
                bbox.get_y() + bbox.get_h() / 2)
        svs = sorted(svs, key = lambda g: utils.atan2pi(
                -(g.get_bbox().get_y() + g.get_bbox().get_h() / 2 - center[1]),
                g.get_bbox().get_x() + g.get_bbox().get_w() / 2 - center[0]))
    for i, subglyph in enumerate(svs):
        if all_bbox:
            order = i
        else:
            order = None
        subglyph_node, subglyph_subgraph = _glyph_to_subgraph(
                subglyph, dids, dpids, subunit = False, order = order)
        subgraph |= subglyph_subgraph
        dids[subglyph.get_id()] = subglyph_node
        subgraph |= Relationship(
            node, STONEnum["HAS_STATE_VARIABLE"].value, subglyph_node)

    for subglyph in glyph.get_glyph() + svs:
        sub_ston_type = subglyph.get_class().name
        if sub_ston_type == "UNIT_OF_INFORMATION" or \
                sub_ston_type == "TERMINAL" or \
                sub_ston_type == "OUTCOME":
            subglyph_node, subglyph_subgraph = _glyph_to_subgraph(
                subglyph, dids, dpids)
            r_type = "HAS_{}".format(sub_ston_type)
        elif sub_ston_type == "STATE_VARIABLE":
            continue
        else:
            subglyph_node, subglyph_subgraph = _glyph_to_subgraph(
                subglyph, dids, dpids, subunit = True)
            r_type = "HAS_SUBUNIT"
        subgraph |= subglyph_subgraph
        dids[subglyph.get_id()] = subglyph_node
        subgraph |= Relationship(
            node, STONEnum[r_type].value, subglyph_node)

    for port in glyph.get_port():
        port_node = _port_to_node(port)
        subgraph |= port_node
        subgraph |= Relationship(node, STONEnum["HAS_PORT"].value, port_node)
        dids[port.get_id()] = port_node
        dpids[port.get_id()] = node
    dids[glyph.get_id()] = node

    return node, subgraph


def _bbox_to_node(bbox):
    node = Node()
    node.add_label(STONEnum["BBOX"].value)
    node[STONEnum["X"].value] = bbox.get_x()
    node[STONEnum["Y"].value] = bbox.get_y()
    node[STONEnum["W"].value] = bbox.get_w()
    node[STONEnum["H"].value] = bbox.get_h()
    return node


def _port_to_node(port):
    node = Node()
    node.add_label(STONEnum["PORT"].value)
    node[STONEnum["ID"].value] = port.get_id()
    node[STONEnum["X"].value] = port.get_x()
    node[STONEnum["Y"].value] = port.get_y()
    return node


def _arc_to_subgraph(arc, dids, dpids, make_shortcuts=True):
    node = Node()
    subgraph = node

    ston_type = arc.get_class().name
    for ontology in Ontologies:
        if ston_type in ontology.value:
            node.add_label(STONEnum[ontology.name].value)
    node.add_label(STONEnum[ston_type].value)

    node[STONEnum["CLASS"].value] = arc.get_class().value
    node[STONEnum["ID"].value] = arc.get_id()

    source = dids[arc.get_source()]
    subgraph |= Relationship(node, STONEnum["HAS_SOURCE"].value, source)
    target = dids[arc.get_target()]
    subgraph |= Relationship(node, STONEnum["HAS_TARGET"].value, target)

    start = Node()
    start.add_label(STONEnum["START"].value)
    start[STONEnum["X"].value] = arc.get_start().get_x()
    start[STONEnum["Y"].value] = arc.get_start().get_y()
    subgraph |= start
    subgraph |= Relationship(node, STONEnum["HAS_START"].value, start)
    end = Node()
    end.add_label(STONEnum["END"].value)
    end[STONEnum["X"].value] = arc.get_end().get_x()
    end[STONEnum["Y"].value] = arc.get_end().get_y()
    subgraph |= end
    subgraph |= Relationship(node, STONEnum["HAS_END"].value, end)
    prev_node = start
    for nextt in arc.get_next():
        next_node = Node()
        next_node.add_label(STONEnum["NEXT"].value)
        next_node[STONEnum["X"].value] = nextt.get_x()
        next_node[STONEnum["Y"].value] = nextt.get_y()
        subgraph |= next_node
        subgraph |= Relationship(
            prev_node,
            STONEnum["HAS_NEXT"].value,
            next_node)
        prev_node = next_node
    if prev_node != start:
        subgraph |= Relationship(prev_node, STONEnum["HAS_NEXT"].value, end)

    cardinality = None
    for glyph in arc.get_glyph():
        glyph_node, glyph_subgraph = _glyph_to_subgraph(glyph, dids, dpids)
        subgraph |= glyph_subgraph
        if glyph.get_class().name == "CARDINALITY":
            subgraph |= Relationship(
                node, STONEnum["HAS_CARDINALITY"].value, glyph_node)
            cardinality = glyph.get_label().get_text()
        elif glyph.get_class().name == "OUTCOME":
            subgraph |= Relationship(
                node, STONEnum["HAS_OUTCOME"].value, glyph_node)

    for port in arc.get_port():
        port_node = _port_to_node(port)
        subgraph |= port_node
        subgraph |= Relationship(node, STONEnum["HAS_PORT"].value, port_node)
        dids[port.get_id()] = port_node
        dpids[port.get_id()] = node

    if make_shortcuts:
        if "{}_{}".format(ston_type, "SHORTCUT") in \
                [attr.name for attr in STONEnum]:
            source_id = arc.get_source()
            if source_id in dpids:
                source_node = dpids[source_id]
            else:
                source_node = dids[source_id]
            target_id = arc.get_target()
            if target_id in dpids:
                target_node = dpids[target_id]
            else:
                target_node = dids[target_id]
            if cardinality is not None:
                props = {STONEnum["CARDINALITY_PROP"].value: cardinality}
            else:
                props = {}
            if ston_type == "CONSUMPTION" or \
                    ston_type == "LOGIC_ARC" or \
                    ston_type == "EQUIVALENCE_ARC":
                left_node = target_node
                right_node = source_node
            else:
                left_node = source_node
                right_node = target_node

            subgraph |= Relationship(
                    left_node,
                    STONEnum["{}_{}".format(ston_type, "SHORTCUT")].value,
                    right_node,
                    **props)
    return node, subgraph


def _arcgroup_to_subgraph(arcgroup, dids, dpids, make_shortcuts=True):
    node = Node()
    subgraph = node
    if arcgroup.get_class() == "interaction":
        ston_type = "INTERACTION"
    else:
        ston_type = arcgroup.get_class().name
    if ston_type == "INTERACTION":
        ston_type = "{}_ARCGROUP".format(ston_type)
    for ontology in Ontologies:
        if ston_type in ontology.value:
            node.add_label(STONEnum[ontology.name].value)
    node.add_label(STONEnum[ston_type].value)

    if ston_type == "INTERACTION_ARCGROUP":  # class interaction is just a string for arcgroups
        node[STONEnum["CLASS"].value] = arcgroup.get_class()
    else:
        node[STONEnum["CLASS"].value] = arcgroup.get_class().value
    for glyph in arcgroup.get_glyph():
        glyph_node, glyph_subgraph = _glyph_to_subgraph(glyph, dids, dpids)
        subgraph |= glyph_subgraph
        subgraph |= Relationship(node, STONEnum["HAS_GLYPH"].value, glyph_node)
    for arc in arcgroup.get_arc():
        arc_node, arc_subgraph = _arc_to_subgraph(
                arc, dids, dpids, make_shortcuts)
        subgraph |= arc_subgraph
        subgraph |= Relationship(node, STONEnum["HAS_ARC"].value, arc_node)
    return node, subgraph


def subgraph_to_map(subgraph):
    dobjects = {}
    sbgnmaps = set([])
    if subgraph is None:
        return sbgnmaps
    for node in subgraph.nodes:
        if node.has_label(STONEnum["MAP"].value):
            sbgnmap = libsbgn.map()
            language = node[STONEnum["LANGUAGE"].value]
            map_id = node[STONEnum["ID"].value]
            sbgnmap.set_language(libsbgn.Language(language))
            sbgnmaps.add((sbgnmap, map_id))
            dobjects[node] = sbgnmap
        if node.has_label(STONEnum["BBOX"].value):
            bbox = _bbox_from_node(node)
            dobjects[node] = bbox
        elif node.has_label(STONEnum["PORT"].value):
            port = _port_from_node(node)
            dobjects[node] = port
        elif node.has_label(STONEnum["GLYPH"].value):
            glyph = _glyph_from_node(node)
            dobjects[node] = glyph
        elif node.has_label(STONEnum["ARC"].value):
            arc = _arc_from_node(node)
            dobjects[node] = arc
        elif node.has_label(STONEnum["START"].value):
            start = _start_from_node(node)
            dobjects[node] = start
        elif node.has_label(STONEnum["END"].value):
            end = _end_from_node(node)
            dobjects[node] = end
        elif node.has_label(STONEnum["NEXT"].value):
            nextt = _next_from_node(node)
            dobjects[node] = nextt
        elif node.has_label(STONEnum["ARCGROUP"].value):
            arcgroup = _arcgroup_from_node(node)
            dobjects[node] = arcgroup
    for relationship in subgraph.relationships:
        rtype = type(relationship).__name__
        if rtype == STONEnum["HAS_BBOX"].value:
            dobjects[relationship.start_node].set_bbox(
                dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_PORT"].value:
            dobjects[relationship.start_node].add_port(
                dobjects[relationship.end_node])
        elif rtype == STONEnum["IS_IN_COMPARTMENT"].value:
            dobjects[relationship.start_node].set_compartmentRef(
                dobjects[relationship.end_node].get_id())
        elif rtype == STONEnum["HAS_START"].value:
            dobjects[relationship.start_node].set_start(
                dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_END"].value:
            dobjects[relationship.start_node].set_end(
                dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_SOURCE"].value:
            dobjects[relationship.start_node].set_source(
                dobjects[relationship.end_node].get_id())
        elif rtype == STONEnum["HAS_TARGET"].value:
            dobjects[relationship.start_node].set_target(
                dobjects[relationship.end_node].get_id())
        elif rtype == STONEnum["HAS_GLYPH"].value or \
                rtype == STONEnum["HAS_SUBUNIT"].value or \
                rtype == STONEnum["HAS_STATE_VARIABLE"].value or \
                rtype == STONEnum["HAS_UNIT_OF_INFORMATION"].value or \
                rtype == STONEnum["HAS_TERMINAL"].value or \
                rtype == STONEnum["HAS_OUTCOME"].value or \
                rtype == STONEnum["HAS_CARDINALITY"].value:
            dobjects[relationship.start_node].add_glyph(
                dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_ARC"].value:
            dobjects[relationship.start_node].add_arc(
                dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_ARCGROUP"].value:
            dobjects[relationship.start_node].add_arcgroup(
                dobjects[relationship.end_node])
    for sbgnmap in sbgnmaps:
        yield sbgnmap

def _glyph_from_node(node):
    glyph = libsbgn.glyph()
    glyph.set_id(node[STONEnum["ID"].value])
    glyph.set_class(libsbgn.GlyphClass(node[STONEnum["CLASS"].value]))
    if node.has_label(STONEnum["STATE_VARIABLE"].value):
        state = libsbgn.stateType()
        state.set_value(node[STONEnum["VALUE"].value])
        state.set_variable(node[STONEnum["VARIABLE"].value])
        glyph.set_state(state)
    elif node.has_label(STONEnum["UNIT_OF_INFORMATION"].value):
        label = libsbgn.label()
        text = node[STONEnum["VALUE"].value]
        if node[STONEnum["PREFIX"].value]:
            text = "{}:{}".format(node[STONEnum["PREFIX"].value], text)
        label.set_text(text)
        glyph.set_label(label)
        if node[STONEnum["UI_TYPE"].value]:
            entity = libsbgn.entityType(node[STONEnum["UI_TYPE"].value])
            glyph.set_entity(entity)
    if node[STONEnum["LABEL"].value]:
        label = libsbgn.label()
        label.set_text(node[STONEnum["LABEL"].value])
        glyph.set_label(label)
    if node[STONEnum["CLONE"].value]:
        clone = libsbgn.cloneType()
        glyph.set_clone(clone)
    if node[STONEnum["ORIENTATION"].value]:
        glyph.orientation = node[STONEnum["ORIENTATION"].value]
    return glyph


def _bbox_from_node(node):
    bbox = libsbgn.bbox()
    bbox.set_x(node[STONEnum["X"].value])
    bbox.set_y(node[STONEnum["Y"].value])
    bbox.set_h(node[STONEnum["H"].value])
    bbox.set_w(node[STONEnum["W"].value])
    return bbox


def _port_from_node(node):
    port = libsbgn.port()
    port.set_id(node[STONEnum["ID"].value])
    port.set_x(node[STONEnum["X"].value])
    port.set_y(node[STONEnum["Y"].value])
    return port


def _start_from_node(node):
    start = libsbgn.startType(
        node[STONEnum["X"].value], node[STONEnum["Y"].value])
    return start


def _end_from_node(node):
    end = libsbgn.endType(node[STONEnum["X"].value], node[STONEnum["Y"].value])
    return end


def _next_from_node(node):
    nextt = libsbgn.endType(
        node[STONEnum["X"].value], node[STONEnum["Y"].value])
    return nextt


def _arc_from_node(node):
    arc = libsbgn.arc()
    arc.set_id(node[STONEnum["ID"].value])
    arc.set_class(libsbgn.ArcClass(node[STONEnum["CLASS"].value]))
    return arc


def _arcgroup_from_node(node):
    arcgroup = libsbgn.arcgroup()
    # arcgroup.set_id(node[STONEnum["ID"].value]) # argroup has no ID
    # class interaction is just a string for arcgroups
    if node[STONEnum["CLASS"].value] == "interaction":
        arcgroup.set_class(node[STONEnum["CLASS"].value])
    else:
        arcgroup.set_class(libsbgn.ArcClass(node[STONEnum["CLASS"].value]))
    return arcgroup
