"""The module for converting SBGN maps to a subgraphs and vice-versa."""

from py2neo import Graph, Node, Relationship, Subgraph

import rdflib

import libsbgnpy.libsbgn as libsbgn
import libsbgnpy.libsbgnSubs as libsbgnSubs

from stonpy.model import STONEnum, ontologies
import stonpy.utils as utils


def map_to_subgraph(sbgn_map, map_id=None, make_shortcuts=True, make_sbml_annotations=True, verbose=False):
    """Convert an SBGN map to a subgraph and return it.

    :param sbgn_map: the SBGN map
    :type sbgn_map: `libsbgnpy.libsbgn.map`
    :param map_id: the ID of the SBGN map, default is `None`
    :type map_id: `str`, optional
    :param make_shortcuts: if set to `True`, \
            shortcut relationships will be added. Defaults to `True`.
    :type make_shortcuts: `bool`, optional
    :param make_sbml_annotations: if set to `True`, \
            SBML annotations inside extensions will be added as nodes and \
            relationships. Defaults to `True`.
    :type make_sbml_annotations: `bool`, optional
    :param verbose: if set to `True`, prints operations to stdout. \
            Defaults to `True`.
    :type verbose: `bool`, optional
    :return: the resulting subgraph
    :rtype: `py2neo.Subgraph`
    """
    dids = {}
    dpids = {}
    nodes = set([])
    relationships = set([])
    language = sbgn_map.get_language().value
    ontology = ontologies[language]

    map_node = Node()
    nodes.add(map_node)
    map_node.add_label(STONEnum["MAP"].value)
    map_node[STONEnum["LANGUAGE"].value] = language
    map_node[STONEnum["MAP_ID"].value] = map_id
    if sbgn_map.get_extension() is not None:
        map_node[STONEnum["EXTENSION"].value] = str(sbgn_map.get_extension())
        if make_sbml_annotations and _extension_has_sbml_annotation(sbgn_map.get_extension()):
            annotation_nodes, annotation_other_nodes, annotation_relationships = _extension_as_sbml_annotation_to_subgraph(
                sbgn_map.get_extension())
            nodes |= annotation_nodes
            nodes |= annotation_other_nodes
            relationships |= annotation_relationships
            for annotation_node in annotation_nodes:
                relationships.add(Relationship(
                    map_node, STONEnum["HAS_ANNOTATION"].value, annotation_node))
    if sbgn_map.get_notes() is not None:
        map_node[STONEnum["NOTES"].value] = str(utils.decode_notes_and_extension(sbgn_map.get_notes()))

    for glyph in sbgn_map.get_glyph():
        if glyph.get_class().name == "COMPARTMENT":
            glyph_node, glyph_other_nodes, glyph_relationships = _glyph_to_subgraph(
                glyph, dids, dpids, ontology, make_sbml_annotations=make_sbml_annotations)
            nodes.add(glyph_node)
            nodes |= glyph_other_nodes
            relationships |= glyph_relationships
            relationships.add(Relationship(
                map_node, STONEnum["HAS_GLYPH"].value, glyph_node))
            dids[glyph.get_id()] = glyph_node

    for glyph in sbgn_map.get_glyph():
        if glyph.get_class().name != "COMPARTMENT":
            glyph_node, glyph_other_nodes, glyph_relationships = _glyph_to_subgraph(
                glyph, dids, dpids, ontology, make_sbml_annotations=make_sbml_annotations)
            nodes.add(glyph_node)
            nodes |= glyph_other_nodes
            relationships |= glyph_relationships
            relationships.add(Relationship(
                map_node, STONEnum["HAS_GLYPH"].value, glyph_node))
            dids[glyph.get_id()] = glyph_node
    for arc in sbgn_map.get_arc():
        if arc.get_class().name == "ASSIGNMENT" or \
                arc.get_class().name == "INTERACTION":
            arc_node, arc_other_nodes, arc_relationships = _arc_to_subgraph(
                arc, dids, dpids, ontology, make_shortcuts, make_sbml_annotations)
            nodes.add(arc_node)
            nodes |= arc_other_nodes
            relationships |= arc_relationships
            dids[arc.get_id()] = arc_node
            relationships.add(Relationship(
                map_node, STONEnum["HAS_ARC"].value, arc_node))
            dids[arc.get_id()] = arc_node

    for arc in sbgn_map.get_arc():
        if arc.get_class().name != "ASSIGNMENT" and \
                arc.get_class().name != "INTERACTION":
            arc_node, arc_other_nodes, arc_relationships = _arc_to_subgraph(
                arc, dids, dpids, ontology, make_shortcuts, make_sbml_annotations)
            nodes.add(arc_node)
            nodes |= arc_other_nodes
            relationships |= arc_relationships
            dids[arc.get_id()] = arc_node
            relationships.add(Relationship(
                map_node, STONEnum["HAS_ARC"].value, arc_node))
            dids[arc.get_id()] = arc_node

    for arcgroup in sbgn_map.get_arcgroup():
            arcgroup_node, arcgroup_other_nodes, arcgroup_relationships = _arcgroup_to_subgraph(
                arcgroup, dids, dpids, ontology, make_shortcuts, make_sbml_annotations)
            nodes.add(arcgroup_node)
            nodes |= arcgroup_other_nodes
            relationships |= arcgroup_relationships
            dids[arcgroup.get_id()] = arcgroup_node
            relationships.add(Relationship(
                map_node, STONEnum["HAS_ARCGROUP"].value, arcgroup_node))
            dids[arcgroup.get_id()] = arcgroup_node
    subgraph = Subgraph(nodes, relationships)
    return subgraph


def _extension_has_sbml_annotation(extension):
    rdf_string = _get_rdf_from_string(str(extension))
    if rdf_string:
        return True
    else:
        return False


def _get_rdf_from_string(s):
    while not s.startswith("<rdf:RDF") and len(s) > 0:
        s = s[1:]
    while not s.endswith("</rdf:RDF>") and len(s) > 0:
        s = s[:-1]
    return s
    #
    # in_rdf = False
    # rdf_string = ""
    # for line in str(s).split("\n"):
    #     line = line.lstrip(" ")
    #     if line.startswith("<rdf:RDF"):
    #         in_rdf = True
    #     elif line.startswith("</rdf:RDF"):
    #         rdf_string += "{}\n".format(line)
    #         in_rdf = False
    #     if in_rdf:
    #         rdf_string += "{}\n".format(line)
    # return rdf_string


def _extension_as_sbml_annotation_to_subgraph(extension):
    nodes = set([])
    relationships = set([])
    annotation_nodes = set([])
    rdf_string = _get_rdf_from_string(str(extension))
    if len(rdf_string) > 0:
        rdf_graph = rdflib.Graph()
        rdf_graph.parse(data=rdf_string, format="application/rdf+xml")
        dnodes = {}
        for s, p, o in rdf_graph:
            if isinstance(s, rdflib.term.URIRef) and isinstance(o, rdflib.term.BNode):
                annotation_node = Node()
                annotation_node.add_label(STONEnum["ANNOTATION"].value)
                annotation_node[STONEnum["QUALIFIER_URI"].value] = str(p)
                l = str(p).split("/")
                qualifier = l[-1]
                qualifier_ns = "/".join(l[:-1])
                annotation_node[STONEnum["QUALIFIER_NS"].value] = qualifier_ns
                annotation_node[STONEnum["QUALIFIER"].value] = qualifier
                dnodes[str(o)] = annotation_node
                annotation_nodes.add(annotation_node)
        for s, p, o in rdf_graph:
            if isinstance(o, rdflib.term.URIRef) and isinstance(s, rdflib.term.BNode) and not str(p).endswith("#type"):
                resource_node = Node()
                resource_node.add_label(STONEnum["RESOURCE"].value)
                resource_node[STONEnum["URI"].value] = str(o)
                if str(o).startswith("urn"):
                    l = str(o).split(":")
                    collection_ns = ":".join(l[:-1])
                else:
                    l = str(o).split("/")
                    collection_ns = "/".join(l[:-1])
                id = l[-1]
                resource_node[STONEnum["COLLECTION_NS"].value] = collection_ns
                resource_node["id"] = id
                nodes.add(resource_node)
                relationship = Relationship(
                    dnodes[str(s)], STONEnum["HAS_RESOURCE"].value, resource_node)
                relationships.add(relationship)
    return annotation_nodes, nodes, relationships


def _glyph_to_subgraph(glyph, dids, dpids, ontology, subunit=False, order=None, make_sbml_annotations=True):
    node = Node()
    nodes = set([])
    relationships = set([])
    ston_type = glyph.get_class().name
    if ston_type == "INTERACTION":
        ston_type = "{}_GLYPH".format(ston_type)
    elif ston_type == "PROCESS":
        ston_type = "GENERIC_{}".format(ston_type)
    if subunit:
        ston_type = "{}_SUBUNIT".format(ston_type)

    for elements in ontology:
        if ston_type in elements.value:
            node.add_label(STONEnum[elements.name].value)
    node.add_label(STONEnum[ston_type].value)

    node[STONEnum["CLASS"].value] = glyph.get_class().value
    node[STONEnum["ID"].value] = glyph.get_id()
    if glyph.get_notes():
        node[STONEnum["NOTES"].value] = str(glyph.get_notes())
    if glyph.get_extension() is not None:
        node[STONEnum["EXTENSION"].value] = str(glyph.get_extension())
        if make_sbml_annotations and _extension_has_sbml_annotation(glyph.get_extension()):
            annotation_nodes, annotation_other_nodes, annotation_relationships = _extension_as_sbml_annotation_to_subgraph(
                glyph.get_extension())
            nodes |= annotation_nodes
            nodes |= annotation_other_nodes
            relationships |= annotation_relationships
            for annotation_node in annotation_nodes:
                relationships.add(Relationship(
                    node, STONEnum["HAS_ANNOTATION"].value, annotation_node))

    if order is not None:
        node[STONEnum["ORDER"].value] = order

    if glyph.get_label() is not None:
        label = glyph.get_label()
        label_text = label.get_text()
        if ston_type == "UNIT_OF_INFORMATION":
            if ':' in label_text:
                node[STONEnum["PREFIX"].value] = label_text.split(':')[0]
                node[STONEnum["VALUE"].value] = label_text.split(':')[1]
            else:
                node[STONEnum["VALUE"].value] = label_text
        else:
            node[STONEnum["LABEL_PROP"].value] = label_text
        label_node, label_other_nodes, label_relationships = _label_to_subgraph(label)
        nodes.add(label_node)
        nodes |= label_other_nodes
        relationships |= label_relationships
        has_label = Relationship(node, STONEnum["HAS_LABEL"].value, label_node)
        relationships.add(has_label)

    if glyph.get_clone():
        node[STONEnum["CLONE"].value] = True
        if glyph.get_clone().get_label():
            if glyph.get_clone().get_label().get_text():
                node[STONEnum["CLONE_LABEL"].value] = \
                    glyph.get_clone().get_label().get_text()
    else:
        node[STONEnum["CLONE"].value] = False

    if glyph.get_compartmentOrder():
        node[STONEnum["COMPARTMENT_ORDER"].value] = \
            glyph.get_compartmentOrder()
    if glyph.get_compartmentRef():
        is_in_compartment = Relationship(node,
                                         STONEnum["IS_IN_COMPARTMENT"].value,
                                         dids[glyph.get_compartmentRef()])
        relationships.add(is_in_compartment)

    if glyph.get_bbox():
        bbox = glyph.get_bbox()
        bbox_node = _bbox_to_node(bbox)
        nodes.add(bbox_node)
        has_bbox = Relationship(node, STONEnum["HAS_BBOX"].value, bbox_node)
        relationships.add(has_bbox)

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
        svs = sorted(svs, key=lambda g: utils.atan2pi(
            -(g.get_bbox().get_y() + g.get_bbox().get_h() / 2 - center[1]),
            g.get_bbox().get_x() + g.get_bbox().get_w() / 2 - center[0]))
    for i, subglyph in enumerate(svs):
        if all_bbox:
            order = i
        else:
            order = None
        subglyph_node, subglyph_other_nodes, subglyph_relationships = _glyph_to_subgraph(
            subglyph, dids, dpids, ontology, subunit=False, order=order, make_sbml_annotations=make_sbml_annotations)
        nodes.add(subglyph_node)
        nodes |= subglyph_other_nodes
        relationships |= subglyph_relationships
        dids[subglyph.get_id()] = subglyph_node
        relationships.add(Relationship(
            node, STONEnum["HAS_STATE_VARIABLE"].value, subglyph_node))

    for subglyph in glyph.get_glyph() + svs:
        sub_ston_type = subglyph.get_class().name
        if sub_ston_type == "UNIT_OF_INFORMATION" or \
                sub_ston_type == "TERMINAL" or \
                sub_ston_type == "OUTCOME" or \
                sub_ston_type == "EXISTENCE" or \
                sub_ston_type == "LOCATION":
            subglyph_node, subglyph_other_nodes, subglyph_relationships = _glyph_to_subgraph(
                subglyph, dids, dpids, ontology, make_sbml_annotations=make_sbml_annotations)
            r_type = "HAS_{}".format(sub_ston_type)
        elif sub_ston_type == "STATE_VARIABLE":
            continue
        else:
            subglyph_node, subglyph_other_nodes, subglyph_relationships = _glyph_to_subgraph(
                subglyph, dids, dpids, ontology, subunit=True, make_sbml_annotations=make_sbml_annotations)
            r_type = "HAS_SUBUNIT"
        nodes.add(subglyph_node)
        nodes |= subglyph_other_nodes
        relationships |= subglyph_relationships
        dids[subglyph.get_id()] = subglyph_node
        relationships.add(Relationship(
            node, STONEnum[r_type].value, subglyph_node))

    for port in glyph.get_port():
        port_node = _port_to_node(port)
        nodes.add(port_node)
        relationships.add(Relationship(
            node, STONEnum["HAS_PORT"].value, port_node))
        dids[port.get_id()] = port_node
        dpids[port.get_id()] = node
    dids[glyph.get_id()] = node

    return node, nodes, relationships


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

def _label_to_subgraph(label):
    node = Node()
    nodes = set([])
    relationships = set([])
    node.add_label(STONEnum["LABEL"].value)
    if label.get_text() is not None:
        node[STONEnum["TEXT"].value] = label.get_text()
    if label.get_bbox() is not None:
        bbox = label.get_bbox()
        bbox_node = _bbox_to_node(bbox)
        nodes.add(bbox_node)
        has_bbox = Relationship(node, STONEnum["HAS_BBOX"].value, bbox_node)
        relationships.add(has_bbox)
    return node, nodes, relationships


def _arc_to_subgraph(arc, dids, dpids, ontology, make_shortcuts=True, make_sbml_annotations=True):
    node = Node()
    nodes = set([])
    relationships = set([])

    ston_type = arc.get_class().name
    for elements in ontology:
        if ston_type in elements.value:
            node.add_label(STONEnum[elements.name].value)
    node.add_label(STONEnum[ston_type].value)

    node[STONEnum["CLASS"].value] = arc.get_class().value
    node[STONEnum["ID"].value] = arc.get_id()
    if arc.get_notes():
        node[STONEnum["NOTES"].value] = str(arc.get_notes())
    if arc.get_extension() is not None:
        node[STONEnum["EXTENSION"].value] = str(arc.get_extension())
        if make_sbml_annotations and _extension_has_sbml_annotation(arc.get_extension()):
            annotation_nodes, annotation_other_nodes, annotation_relationships = _extension_as_sbml_annotation_to_subgraph(
                arc.get_extension())
            nodes |= annotation_nodes
            nodes |= annotation_other_nodes
            relationships |= annotation_relationships
            for annotation_node in annotation_nodes:
                relationships.add(Relationship(
                    node, STONEnum["HAS_ANNOTATION"].value, annotation_node))

    source = dids[arc.get_source()]
    relationships.add(Relationship(node, STONEnum["HAS_SOURCE"].value, source))
    target = dids[arc.get_target()]
    relationships.add(Relationship(node, STONEnum["HAS_TARGET"].value, target))

    start = Node()
    start.add_label(STONEnum["START"].value)
    start[STONEnum["X"].value] = arc.get_start().get_x()
    start[STONEnum["Y"].value] = arc.get_start().get_y()
    nodes.add(start)
    relationships.add(Relationship(node, STONEnum["HAS_START"].value, start))
    end = Node()
    end.add_label(STONEnum["END"].value)
    end[STONEnum["X"].value] = arc.get_end().get_x()
    end[STONEnum["Y"].value] = arc.get_end().get_y()
    nodes.add(end)
    relationships.add(Relationship(node, STONEnum["HAS_END"].value, end))
    for i, nextt in enumerate(arc.get_next()):
        next_node = Node()
        next_node.add_label(STONEnum["NEXT"].value)
        next_node[STONEnum["X"].value] = nextt.get_x()
        next_node[STONEnum["Y"].value] = nextt.get_y()
        next_node[STONEnum["ORDER"].value] = i
        relationships.add(Relationship(
            node,
            STONEnum["HAS_NEXT"].value,
            next_node))

    cardinality = None
    for glyph in arc.get_glyph():
        glyph_node, glyph_other_nodes, glyph_relationships = _glyph_to_subgraph(
            glyph, dids, dpids, ontology, make_sbml_annotations=make_sbml_annotations)
        nodes.add(glyph_node)
        nodes |= glyph_other_nodes
        relationships |= glyph_relationships
        if glyph.get_class().name == "CARDINALITY":
            relationships.add(Relationship(
                node, STONEnum["HAS_CARDINALITY"].value, glyph_node))
            cardinality = glyph.get_label().get_text()
        elif glyph.get_class().name == "OUTCOME":
            relationships.add(Relationship(
                node, STONEnum["HAS_OUTCOME"].value, glyph_node))

    for port in arc.get_port():
        port_node = _port_to_node(port)
        nodes.add(port_node)
        relationships.add(Relationship(
            node, STONEnum["HAS_PORT"].value, port_node))
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
                start_node = target_node
                end_node = source_node
            else:
                start_node = source_node
                end_node = target_node

            relationships.add(Relationship(
                start_node,
                STONEnum["{}_{}".format(ston_type, "SHORTCUT")].value,
                end_node,
                **props))
    return node, nodes, relationships


def _arcgroup_to_subgraph(arcgroup, dids, dpids, ontology, make_shortcuts=True, make_sbml_annotations=True):
    node = Node()
    nodes = set([])
    relationships = set([])
    if arcgroup.get_class() == "interaction":
        ston_type = "INTERACTION"
    else:
        ston_type = arcgroup.get_class().name
    if ston_type == "INTERACTION":
        ston_type = "{}_ARCGROUP".format(ston_type)

    for elements in ontology:
        if ston_type in elements.value:
            node.add_label(STONEnum[elements.name].value)
    node.add_label(STONEnum[ston_type].value)

    if ston_type == "INTERACTION_ARCGROUP":  # class interaction is just a string for arcgroups
        node[STONEnum["CLASS"].value] = arcgroup.get_class()
    else:
        node[STONEnum["CLASS"].value] = arcgroup.get_class().value

    if arcgroup.get_notes():
        node[STONEnum["NOTES"].value] = str(utils.decode_notes_and_extension(arcgroup.get_notes()))
    if arcgroup.get_extension():
        node[STONEnum["EXTENSION"].value] = str(arcgroup.get_extension())
        if make_sbml_annotations and _extension_has_sbml_annotation(arcgroup.get_extension()):
            annotation_nodes, annotation_other_nodes, annotation_relationship = _extension_as_sbml_annotation_to_subgraph(
                arcgroup.get_extension())
            nodes |= annotation_nodes
            nodes |= annotation_other_nodes
            relationships |= annotation_relationships
            for annotation_node in annotation_nodes:
                relationships.add(Relationship(
                    node, STONEnum["HAS_ANNOTATION"].value, annotation_node))

    for glyph in arcgroup.get_glyph():
        glyph_node, glyph_other_nodes, glyph_relationships = _glyph_to_subgraph(
            glyph, dids, dpids, ontology, make_sbml_annotations=make_sbml_annotations)
        nodes.add(glyph_node)
        nodes |= glyph_other_nodes
        relationships |= glyph_relationships
        relationships.add(Relationship(
            node, STONEnum["HAS_GLYPH"].value, glyph_node))
    for arc in arcgroup.get_arc():
        arc_node, arc_other_nodes, arc_relationship = _arc_to_subgraph(
            arc, dids, dpids, ontology, make_shortcuts, make_sbml_annotations)
        nodes.add(arc_node)
        nodes |= arc_other_nodes
        relationships |= arc_relationships
        relationships.add(Relationship(
            node, STONEnum["HAS_ARC"].value, arc_node))
    return node, nodes, relationships


def subgraph_to_map(subgraph):
    """Convert a subgraph to zero or more SBGN maps and return them.

    :param subgraph: the subgraph
    :type subgraph: `py2neo.Subgraph`
    :return: the resulting SBGN maps, under the form of a generator. Each returned element is a tuple of the form (map, map_id).
    :rtype: `Iterator[(`libsbgnpy.libsbgn.map`, `str`)]`
    """
    dobjects = {}
    sbgn_maps = set([])
    if subgraph is None:
        return sbgn_maps
    for node in subgraph.nodes:
        if node.has_label(STONEnum["MAP"].value):
            sbgn_map = libsbgn.map()
            language = node[STONEnum["LANGUAGE"].value]
            map_id = node[STONEnum["ID"].value]
            sbgn_map.set_language(libsbgn.Language(language))
            if node[STONEnum["NOTES"].value]:
                sbgn_map.set_notes(libsbgnSubs.Notes(
                    node[STONEnum["NOTES"].value]))
            if node[STONEnum["EXTENSION"].value]:
                sbgn_map.set_extension(libsbgnSubs.Extension(
                    node[STONEnum["EXTENSION"].value]))
            sbgn_maps.add((sbgn_map, map_id))
            dobjects[node.identity] = sbgn_map
        if node.has_label(STONEnum["BBOX"].value):
            bbox = _bbox_from_node(node)
            dobjects[node.identity] = bbox
        elif node.has_label(STONEnum["PORT"].value):
            port = _port_from_node(node)
            dobjects[node.identity] = port
        elif node.has_label(STONEnum["GLYPH"].value):
            glyph = _glyph_from_node(node)
            dobjects[node.identity] = glyph
        elif node.has_label(STONEnum["ARC"].value):
            arc = _arc_from_node(node)
            dobjects[node.identity] = arc
        elif node.has_label(STONEnum["START"].value):
            start = _start_from_node(node)
            dobjects[node.identity] = start
        elif node.has_label(STONEnum["END"].value):
            end = _end_from_node(node)
            dobjects[node.identity] = end
        elif node.has_label(STONEnum["NEXT"].value):
            nextt = _next_from_node(node)
            dobjects[node.identity] = nextt
        elif node.has_label(STONEnum["ARCGROUP"].value):
            arcgroup = _arcgroup_from_node(node)
            dobjects[node.identity] = arcgroup
        elif node.has_label(STONEnum["LABEL"].value):
            label = _label_from_node(node)
            dobjects[node.identity] = label
    for relationship in subgraph.relationships:
        rtype = type(relationship).__name__
        if rtype == STONEnum["HAS_BBOX"].value:
            dobjects[relationship.start_node.identity].set_bbox(
                dobjects[relationship.end_node.identity])
        elif rtype == STONEnum["HAS_LABEL"].value:
            dobjects[relationship.start_node.identity].set_label(
                dobjects[relationship.end_node.identity])
        elif rtype == STONEnum["HAS_PORT"].value:
            dobjects[relationship.start_node.identity].add_port(
                dobjects[relationship.end_node.identity])
        elif rtype == STONEnum["IS_IN_COMPARTMENT"].value:
            dobjects[relationship.start_node.identity].set_compartmentRef(
                dobjects[relationship.end_node.identity].get_id())
        elif rtype == STONEnum["HAS_START"].value:
            dobjects[relationship.start_node.identity].set_start(
                dobjects[relationship.end_node.identity])
        elif rtype == STONEnum["HAS_END"].value:
            dobjects[relationship.start_node.identity].set_end(
                dobjects[relationship.end_node.identity])
        elif rtype == STONEnum["HAS_NEXT"].value:
            arc = dobjects[relationship.start_node.identity]
            order = relationship.end_node[STONEnum["ORDER"].value]
            while order >= len(arc.get_next()):
                arc.add_next(None)
            arc.next[order] = dobjects[relationship.end_node.identity]
        elif rtype == STONEnum["HAS_SOURCE"].value:
            dobjects[relationship.start_node.identity].set_source(
                dobjects[relationship.end_node.identity].get_id())
        elif rtype == STONEnum["HAS_TARGET"].value:
            dobjects[relationship.start_node.identity].set_target(
                dobjects[relationship.end_node.identity].get_id())
        elif rtype == STONEnum["HAS_GLYPH"].value or \
                rtype == STONEnum["HAS_SUBUNIT"].value or \
                rtype == STONEnum["HAS_STATE_VARIABLE"].value or \
                rtype == STONEnum["HAS_EXISTENCE"].value or \
                rtype == STONEnum["HAS_LOCATION"].value or \
                rtype == STONEnum["HAS_UNIT_OF_INFORMATION"].value or \
                rtype == STONEnum["HAS_TERMINAL"].value or \
                rtype == STONEnum["HAS_OUTCOME"].value or \
                rtype == STONEnum["HAS_CARDINALITY"].value:
            dobjects[relationship.start_node.identity].add_glyph(
                dobjects[relationship.end_node.identity])
        elif rtype == STONEnum["HAS_ARC"].value:
            dobjects[relationship.start_node.identity].add_arc(
                dobjects[relationship.end_node.identity])
        elif rtype == STONEnum["HAS_ARCGROUP"].value:
            dobjects[relationship.start_node.identity].add_arcgroup(
                dobjects[relationship.end_node.identity])
    for sbgn_map in sbgn_maps:
        yield sbgn_map


def _glyph_from_node(node):
    glyph = libsbgn.glyph()
    glyph.set_id(node[STONEnum["ID"].value])
    glyph.set_class(libsbgn.GlyphClass(node[STONEnum["CLASS"].value]))
    if node[STONEnum["NOTES"].value]:
        glyph.set_notes(libsbgnSubs.Notes(node[STONEnum["NOTES"].value]))
    if node[STONEnum["EXTENSION"].value]:
        glyph.set_extension(libsbgnSubs.Extension(
            node[STONEnum["EXTENSION"].value]))

    if node.has_label(STONEnum["STATE_VARIABLE"].value):
        state = libsbgn.stateType()
        state.set_value(node[STONEnum["VALUE"].value])
        state.set_variable(node[STONEnum["VARIABLE"].value])
        glyph.set_state(state)
    elif node.has_label(STONEnum["UNIT_OF_INFORMATION"].value):
        if node[STONEnum["UI_TYPE"].value]:
            entity = libsbgn.entityType(node[STONEnum["UI_TYPE"].value])
            glyph.set_entity(entity)
    if node[STONEnum["CLONE"].value]:
        clone = libsbgn.cloneType()
        glyph.set_clone(clone)
    if node[STONEnum["ORIENTATION"].value]:
        glyph.orientation = node[STONEnum["ORIENTATION"].value]
    if node[STONEnum["COMPARTMENT_ORDER"].value]:
        glyph.set_compartmentOrder(node[STONEnum["COMPARTMENT_ORDER"].value])
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

def _label_from_node(node):
    label = libsbgn.label()
    if node[STONEnum["TEXT"].value] is not None:
        label.set_text(node[STONEnum["TEXT"].value])
    return label

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
    if node[STONEnum["NOTES"].value]:
        arc.set_notes(libsbgnSubs.Notes(node[STONEnum["NOTES"].value]))
    if node[STONEnum["EXTENSION"].value]:
        arc.set_extension(libsbgnSubs.Extension(
            node[STONEnum["EXTENSION"].value]))
    return arc


def _arcgroup_from_node(node):
    arcgroup = libsbgn.arcgroup()
    # arcgroup.set_id(node[STONEnum["ID"].value]) # argroup has no ID
    # class interaction is just a string for arcgroups
    if node[STONEnum["CLASS"].value] == "interaction":
        arcgroup.set_class(node[STONEnum["CLASS"].value])
    else:
        arcgroup.set_class(libsbgn.ArcClass(node[STONEnum["CLASS"].value]))
    arcgroup.set_notes(libsbgnSubs.Notes(node[STONEnum["NOTES"].value]))
    arcgroup.set_extension(libsbgnSubs.Extension(
        node[STONEnum["EXTENSION"].value]))
    return arcgroup
