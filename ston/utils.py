import libsbgnpy.libsbgn as libsbgn

from py2neo import NodeMatcher, RelationshipMatcher

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
    for n in subgraph.nodes:
        print(n)
    for r in subgraph.relationships:
        print(r)

def map_to_sbgnfile(sbgnmap, sbgnfile):
    sbgn = libsbgn.sbgn()
    sbgn.set_map(sbgnmap)
    sbgn.write_file(sbgnfile)
    with open(sbgnfile) as f:
        s = f.read()
        s = s.replace("sbgn:","")
        s = s.replace(' xmlns:sbgn="http://sbgn.org/libsbgn/0.2"', "")
        s = s.replace('."', '.0"')
    with open(sbgnfile, 'w') as f:
        f.write(s)
    print("Written map to {}".format(sbgnfile))

def sbgnfile_to_map(sbgnfile):
    sbgn = libsbgn.parse(sbgnfile, silence = True)
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
