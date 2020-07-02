from math import atan2, pi
from collections import defaultdict

import libsbgnpy.libsbgn as libsbgn

from py2neo import NodeMatcher, RelationshipMatcher

from stonpy.sbgn import cast_map

def match(subgraph, nodes=None, rtype=None):
    relationships = set([])
    if subgraph is None:
        return relationships
    elif nodes is None and rtype is None:
        return subgraph.relationships
    for relationship in subgraph.relationships:
        if rtype is not None and type(relationship).__name__ != rtype:
            continue
        if len(nodes) >= 1 and nodes[0] is not None and relationship.start_node != nodes[0]:
            continue
        if len(nodes) == 2 and nodes[1] is not None and relationship.end_node != nodes[1]:
            continue
        relationships.add(relationship)
    return relationship

def match_one(subgraph, nodes=None, rtype=None):
    if subgraph is None:
        return None
    for relationship in subgraph.relationships:
        if rtype is not None and type(relationship).__name__ != rtype:
            continue
        if len(nodes) >= 1 and nodes[0] is not None and relationship.start_node != nodes[0]:
            continue
        if len(nodes) == 2 and nodes[1] is not None and relationship.end_node != nodes[1]:
            continue
        return relationship
    return None

def subgraph_union(subgraph1, subgraph2):
    if subgraph1 is not None:
        if subgraph2 is not None:
            return subgraph1 | subgraph2
        else:
            return subgraph1
    elif subgraph2 is not None:
        return subgraph2
    else:
        return None

def print_subgraph(subgraph):
    if not subgraph.nodes and not subgraph.relationships:
        print("Empty subgraph")
    for n in subgraph.nodes:
        print(n)
    for r in subgraph.relationships:
        print(r)

def map_to_sbgn_file(sbgnmap, sbgn_file):
    sbgn = libsbgn.sbgn()
    sbgn.set_map(sbgnmap)
    sbgn.write_file(sbgn_file)
    with open(sbgn_file) as f:
        s = f.read()
        s = s.replace("sbgn:","")
        s = s.replace(' xmlns:sbgn="http://sbgn.org/libsbgn/0.2"', "")
        s = s.replace('."', '.0"')
    with open(sbgn_file, 'w') as f:
        f.write(s)

def sbgn_file_to_map(sbgn_file):
    sbgn = libsbgn.parse(sbgn_file, silence = True)
    sbgnmap = sbgn.get_map()
    return sbgnmap

def match_node(node, graph):
    matches = set([])
    n_matcher = NodeMatcher(graph)
    for match in n_matcher.match(*node.labels, **dict(node)):
        matches.add(match)
    return matches

def match_relationship(relationship, graph):
    matches = set([])
    start_node = relationship.start_node
    end_node = relationship.end_node
    matched_start = set([])
    for matched_node in match_node(start_node, graph):
        matched_start.add(matched_node)
    matched_end = set([])
    for matched_node in match_node(end_node, graph):
        matched_end.add(matched_node)
    r_matcher = RelationshipMatcher(graph)
    for start_node in matched_start:
        for end_node in matched_end:
            for match in r_matcher.match((start_node, end_node), type(relationship).__name__, **dict(relationship)):
                matches.add(match)
    return matches

def match_subgraph(subgraph, graph, exact=False):
    dmatched = {}
    matched_subgraph = None
    for node in subgraph.nodes:
        matched_nodes = set([])
        for matched_node in match_node(node, graph):
            matched_nodes.add(matched_node)
            matched_subgraph = subgraph_union(matched_subgraph, matched_node)
        if exact and not matched_nodes:
            return None
        dmatched[node] = matched_nodes
    r_matcher = RelationshipMatcher(graph)
    for relationship in subgraph.relationships:
        matched_relationships = set([])
        start_node = relationship.start_node
        end_node = relationship.end_node
        if start_node not in dmatched:
            matched_start = set([])
            for matched_node in match_node(start_node, graph):
                matched_start.add(matched_node)
        else:
            matched_start = dmatched[start_node]
        if exact and not matched_start:
            return None
        if end_node not in dmatched:
            matched_end = set([])
            for matched_node in match_node(end_node, graph):
                matched_end.add(matched_node)
        else:
            matched_end = dmatched[end_node]
        if exact and not matched_end:
            return None
        for start_node in matched_start:
            for end_node in matched_end:
                for matched_relationship in r_matcher.match((start_node, end_node), type(relationship).__name__, **dict(relationship)):
                    matched_relationships.add(matched_relationship)
                    matched_subgraph = subgraph_union(matched_subgraph, matched_relationship)
        if exact and not matched_relationships:
            return None
    return matched_subgraph

def exists_subgraph(subgraph, graph):
    return match_subgraph(subgraph, graph, exact = True) is not None

def node_to_cypher(node, name=None):
    if name is None:
        name = ""
    labels = ""
    for label in node.labels:
        labels += ":{}".format(label)
    if node:
        l = []
        for prop, val in node.items():
            if isinstance(val, bool) or isinstance(val, int):
                item = '{}: {}'.format(prop, val)
            else:
                item = '{}: "{}"'.format(prop, val)
            l.append(item)
        props = " {{{}}}".format(", ".join(l))
    else:
        props = ""
    s = "({}{}{})".format(name, labels, props)
    return s

def reduce_compartments_of_map(sbgnmap, margin=10):
    dcompartments = defaultdict(list)
    for glyph in sbgnmap.get_glyph():
        if glyph.compartmentRef is not None:
            bbox = glyph.get_bbox()
            compartment_id = glyph.compartmentRef
            if compartment_id not in dcompartments:
                dcompartments[compartment_id] = {
                    "min_x": bbox.get_x(),
                    "min_y": bbox.get_y(),
                    "max_x": bbox.get_x() + bbox.get_w(),
                    "max_y": bbox.get_y() + bbox.get_h()}
            else:
                if dcompartments[compartment_id]["min_x"] > bbox.get_x():
                    dcompartments[compartment_id]["min_x"] = bbox.get_x()
                if dcompartments[compartment_id]["min_y"] > bbox.get_y():
                    dcompartments[compartment_id]["min_y"] = bbox.get_y()
                if dcompartments[compartment_id]["max_x"] < bbox.get_x() + \
                        bbox.get_w():
                    dcompartments[compartment_id]["max_x"] = bbox.get_x() + \
                        bbox.get_w()
                if dcompartments[compartment_id]["max_y"] < bbox.get_y() + \
                        bbox.get_h():
                    dcompartments[compartment_id]["max_x"] = bbox.get_y() + \
                        bbox.get_h()
            for subglyph in glyph.get_glyph():
                bbox = subglyph.get_bbox()
                if dcompartments[compartment_id]["min_x"] > bbox.get_x():
                    dcompartments[compartment_id]["min_x"] = bbox.get_x()
                if dcompartments[compartment_id]["min_y"] > bbox.get_y():
                    dcompartments[compartment_id]["min_y"] = bbox.get_y()
                if dcompartments[compartment_id]["max_x"] < bbox.get_x() + \
                        bbox.get_w():
                    dcompartments[compartment_id]["max_x"] = bbox.get_x() + \
                        bbox.get_w()
                if dcompartments[compartment_id]["max_y"] < bbox.get_y() + \
                        bbox.get_h():
                    dcompartments[compartment_id]["max_x"] = bbox.get_y() + \
                        bbox.get_h()
    for glyph in sbgnmap.get_glyph():
        if glyph.get_class().name == "COMPARTMENT":
            min_x = dcompartments[glyph.get_id()]["min_x"] - margin
            min_y = dcompartments[glyph.get_id()]["min_y"] - margin
            max_x = dcompartments[glyph.get_id()]["max_x"] + margin
            max_y = dcompartments[glyph.get_id()]["max_y"] + margin
            bbox = glyph.get_bbox()
            bbox.set_x(min_x)
            bbox.set_y(min_y)
            bbox.set_w(max_x - min_x)
            bbox.set_h(max_y - min_y)

def map_to_top_left(sbgnmap):

    def _find_mins(sbgnmap):
        min_x = None
        min_y = None
        for glyph in sbgnmap.get_glyph():
            bbox = glyph.get_bbox()
            if bbox is not None:
                if min_x is None or bbox.get_x() < min_x:
                    min_x = bbox.get_x()
                if min_y is None or bbox.get_y() < min_y:
                    min_y = bbox.get_y()
            for subglyph in glyph.get_glyph():
                bbox = subglyph.get_bbox()
                if min_x is None or bbox.get_x() < min_x:
                    min_x = bbox.get_x()
                if min_y is None or bbox.get_y() < min_y:
                    min_y = bbox.get_y()
        return min_x, min_y

    def _glyph_to_top_left(glyph, min_x, min_y):
        bbox = glyph.get_bbox()
        if bbox is not None:
            bbox.set_x(bbox.get_x() - min_x)
            bbox.set_y(bbox.get_y() - min_y)
        for subglyph in glyph.get_glyph():
            _glyph_to_top_left(subglyph, min_x, min_y)

    def _arc_to_top_left(arc, min_x, min_y):
        points = [arc.get_start(), arc.get_end()] + arc.get_next()
        for point in points:
            point.set_x(point.get_x() - min_x)
            point.set_y(point.get_y() - min_y)

    def _arcgroup_to_top_left(arcgroup, min_x, min_y):
        for glyph in arcgroup.get_glyph():
            _glyph_to_top_left(glyph, min_x, min_y)
        for arc in arcgroup.get_arc():
            _arc_to_top_left(arc, min_x, min_y)

    min_x, min_y = _find_mins(sbgnmap)
    for glyph in sbgnmap.get_glyph():
        _glyph_to_top_left(glyph, min_x, min_y)
    for arc in sbgnmap.get_arc():
        _arc_to_top_left(arc, min_x, min_y)
    for arcgroup in sbgnmap.get_arcgroup():
        _arcgroup_to_top_left(arcgroup, min_x, min_y)

def atan2pi(y, x):
    a = atan2(y, x)
    if a < 0:
        a = a + 2 * pi
    return a

def are_maps_equal(map1, map2):
    return cast_map(map1) == cast_map(map2)
