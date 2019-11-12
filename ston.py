from enum import Enum

from py2neo.data import walk
from py2neo import Database, Graph, Node, Relationship, Subgraph

import libsbgnpy.libsbgn as libsbgn

class STONEnum(Enum):
    #Labels
    EPN = "Epn"
    SUBUNIT = "Subunit"
    LOGICAL_OPERATOR = "LogicalOperator"
    COMPARTMENT = "Compartment"
    UNSPECIFIED_ENTITY = "UnspecifiedEntity"
    SIMPLE_CHEMICAL = "SimpleChemical"
    MACROMOLECULE = "Macromolecule"
    NUCLEIC_ACID_FEATURE = "NucleicAcidFeature"
    COMPLEX = "Complex"
    SIMPLE_CHEMICAL_MULTIMER = "SimpleChemicalMultimer"
    MACROMOLECULE_MULTIMER = "MacromoleculeMultimer"
    NUCLEIC_ACID_FEATURE_MULTIMER = "NucleicAcidFeatureMultimer"
    COMPLEX_MULTIMER = "ComplexMultimer"
    SOURCE_AND_SINK = "EmptySet"
    PERTURBING_AGENT = "PerturbingAgent"
    PROCESS = "Process"
    OMITTED_PROCESS = "OmittedProcess"
    UNCERTAIN_PROCESS  = "UncertainProcess"
    ASSOCIATION = "Association"
    DISSOCIATION  = "Dissociation"
    PHENOTYPE = "Phenotype"
    OR = "OrOperator"
    AND = "AndOperator"
    NOT = "NotOperator"
    STATE_VARIABLE = "StateVariable"
    UNIT_OF_INFORMATION = "UnitOfInformation"
    UNSPECIFIED_ENTITY_SUBUNIT = "UnspecifiedEntitySubunit"
    SIMPLE_CHEMICAL_SUBUNIT = "SimpleChemicalSubunit"
    MACROMOLECULE_SUBUNIT = "MacromoleculeSubunit"
    NUCLEIC_ACID_FEATURE_SUBUNIT = "NucleicAcidFeatureSubunit"
    COMPLEX_SUBUNIT = "ComplexSubunit"
    SIMPLE_CHEMICAL_MULTIMER_SUBUNIT = "SimpleChemicalMultimerSubunit"
    MACROMOLECULE_MULTIMER_SUBUNIT = "MacromoleculeMultimerSubunit"
    NUCLEIC_ACID_FEATURE_MULTIMER_SUBUNIT = "NucleicAcidFeatureMultimerSubunit"
    COMPLEX_MULTIMER_SUBUNIT = "ComplexMultimerSubunit"
    PORT = "Port"
    BBOX = "Bbox"
    TAG = "Tag"
    TERMINAL = "Terminal"
    SUBMAP = "Submap"
    #Relation types
    CATALYSIS  = "CATALYZES"
    MODULATION = "MODULATES"
    STIMULATION  = "STIMULATES"
    INHIBITION  = "INHIBITS"
    NECESSARY_STIMULATION  = "NECESSARY_STIMULATES"
    CONSUMPTION = "CONSUMES"
    PRODUCTION = "PRODUCES"
    HAS_SUBUNIT = "HAS_SUBUNIT"
    HAS_STATE_VARIABLE = "HAS_STATE_VARIABLE"
    HAS_UNIT_OF_INFORMATION = "HAS_UNIT_OF_INFORMATION"
    LOGIC_ARC = "IS_INPUT_OF"
    EQUIVALENCE_ARC = "IS_INPUT_OF"
    HAS_PORT = "HAS_PORT"
    HAS_BBOX = "HAS_BBOX"
    HAS_TERMINAL = "HAS_TERMINAL"
    IS_IN_COMPARTMENT = "IS_IN_COMPARTMENT"
    #Property names
    LABEL = "label"
    ID = "id"
    CLASS = "class"
    SOURCE = "source"
    TARGET = "target"
    CLONE = "clone"
    CLONE_LABEL = "cloneLabel"
    VALUE = "value"
    VARIABLE = "variable"
    PREFIX = "prefix"
    COMPARTMENT_ORDER = "compartmentOrder"
    LANGUAGE = "language"
    MAP_ID = "mapId"
    X = "x"
    Y = "y"
    W = "w"
    H = "h"
    START = "start"
    END = "end"
    ORIENTATION = "orientation"

# SBGNGlyphs = set(["COMPARTMENT", "UNSPECIFIED_ENTITY", "SIMPLE_CHEMICAL", "MACROMOLECULE", "NUCLEIC_ACID_FEATURE", "COMPLEX", "SIMPLE_CHEMICAL_MULTIMER", "MACROMOLECULE_MULTIMER", "NUCLEIC_ACID_FEATURE_MULTIMER", "COMPLEX_MULTIMER", "SOURCE_AND_SINK", "PERTURBING_AGENT", "PROCESS", "OMITTED_PROCESS", "UNCERTAIN_PROCESS", "ASSOCIATION", "DISSOCIATION", "PHENOTYPE", "OR", "AND", "NOT", "STATE_VARIABLE", "UNIT_OF_INFORMATION", "UNSPECIFIED_ENTITY_SUBUNIT", "SIMPLE_CHEMICAL_SUBUNIT", "MACROMOLECULE_SUBUNIT", "NUCLEIC_ACID_FEATURE_SUBUNIT", "COMPLEX_SUBUNIT", "SIMPLE_CHEMICAL_MULTIMER_SUBUNIT", "MACROMOLECULE_MULTIMER_SUBUNIT", "NUCLEIC_ACID_FEATURE_MULTIMER_SUBUNIT", "COMPLEX_MULTIMER_SUBUNIT", "TERMINAL", "TAG", "SUBMAP", "STATE_VARIABLE", "UNIT_OF_INFORMATION"])
#
# SBGNArcs = set(["CATALYSIS", "MODULATION", "STIMULATION", "INHIBITION", "NECESSARY_STIMULATION", "CONSUMPTION", "PRODUCTION", "LOGIC_ARC", "EQUIVALENCE_ARC"])

def sbgnfile_to_subgraph(sbgnfile):
    sbgn = libsbgn.parse(sbgnfile, silence = True)
    sbgnmap = sbgn.get_map()
    subgraph = map_to_subgraph(sbgnmap, sbgnfile)
    return subgraph

def map_to_subgraph(sbgnmap, map_id):
    dids = {}
    language = sbgnmap.get_language().value
    subgraph = None
    for glyph in sbgnmap.get_glyph():
        if glyph.get_class().name == "COMPARTMENT":
            node, glyph_subgraph = glyph_to_subgraph(glyph, file_name, language, dids)
            if not subgraph:
                subgraph = glyph_subgraph
            else:
                subgraph |= glyph_subgraph
            dids[glyph.get_id()] = node
    for glyph in sbgnmap.get_glyph():
        if glyph.get_class().name != "COMPARTMENT":
            node, glyph_subgraph = glyph_to_subgraph(glyph, file_name, language, dids)
            if not subgraph:
                subgraph = glyph_subgraph
            else:
                subgraph |= glyph_subgraph
    for arc in sbgnmap.get_arc():
        relationship = arc_to_relationship(arc, file_name, language, dids)
        subgraph |= relationship
    return subgraph

def glyph_to_subgraph(glyph, map_id, language, dids):
    node = Node()
    subgraph = node
    node.add_label(STONEnum[glyph.get_class().name].value)
    node[STONEnum["MAP_ID"].value] = file_name
    node[STONEnum["LANGUAGE"].value] = language
    node[STONEnum["ID"].value] = glyph.get_id()
    node[STONEnum["CLASS"].value] = glyph.get_class().value
    if glyph.get_label():
        if glyph.get_label().get_text():
            node[STONEnum["LABEL"].value] = glyph.get_label().get_text()
    if glyph.get_clone():
        node[STONEnum["CLONE"].value] = True
        if glyph.get_clone().get_label():
            if glyph.get_clone().get_label().get_text():
                node[STONEnum["CLONE_LABEL"].value] = glyph.get_clone().get_label().get_text()
    else:
        node[STONEnum["CLONE"].value] = False
    node[STONEnum["COMPARTMENT_ORDER"].value] = glyph.get_compartmentOrder()
    if glyph.get_compartmentRef():
        is_in_compartment = Relationship(node, STONEnum["IS_IN_COMPARTMENT"].value, dids[glyph.get_compartmentRef()])
        subgraph |= is_in_compartment
    if glyph.get_bbox():
        bbox_node = bbox_to_node(glyph.get_bbox(), map_id, language)
        subgraph |= bbox_node
        has_bbox = Relationship(node, STONEnum["HAS_BBOX"].value, bbox_node)
        subgraph |= has_bbox
    if glyph.orientation:
        node[STONEnum["ORIENTATION"].value] = glyph.orientation
    for subglyph in glyph.get_glyph():
        if subglyph.get_class().name == "UNIT_OF_INFORMATION":
            ui_node, ui_subgraph = unit_of_information_to_subgraph(subglyph, map_id, language)
            subgraph |= ui_subgraph
            has_ui = Relationship(node, STONEnum["HAS_UNIT_OF_INFORMATION"].value, ui_node)
            subgraph |= has_ui
        elif subglyph.get_class().name == "STATE_VARIABLE":
            sv_node, sv_subgraph = state_variable_to_subgraph(subglyph, map_id, language)
            subgraph |= sv_subgraph
            has_sv = Relationship(node, STONEnum["HAS_STATE_VARIABLE"].value, sv_node)
            subgraph |= has_sv
        elif subglyph.get_class().name == "TERMINAL":
            terminal_node, terminal_subgraph = glyph_to_subgraph(subglyph, file_name, language, dids)
            subgraph |= terminal_subgraph
            has_terminal = Relationship(node, STONEnum["HAS_TERMINAL"].value, terminal_node)
            subgraph |= has_terminal
        else:
            subunit_node, subunit_subgraph = glyph_to_subgraph(subglyph, file_name, language, dids)
            subgraph |= subunit_subgraph
            has_subunit = Relationship(node, STONEnum["HAS_SUBUNIT"].value, subunit_node)
            subgraph |= has_subunit
    for port in glyph.get_port():
        port_node = port_to_node(port, language)
        subgraph |= port_node
        has_port = Relationship(node, STONEnum["HAS_PORT"].value, port_node)
        subgraph |= has_port
        dids[port.get_id()] = node
    dids[glyph.get_id()] = node
    return node, subgraph

def bbox_to_node(bbox, map_id, language):
    node = Node()
    node.add_label(STONEnum["BBOX"].value)
    node[STONEnum["X"].value] = bbox.get_x()
    node[STONEnum["Y"].value] = bbox.get_y()
    node[STONEnum["W"].value] = bbox.get_w()
    node[STONEnum["H"].value] = bbox.get_h()
    node[STONEnum["MAP_ID"].value] = map_id
    node[STONEnum["LANGUAGE"].value] = language
    return node

def unit_of_information_to_subgraph(glyph, map_id, language):
    node = Node()
    subgraph = node
    node.add_label(STONEnum["UNIT_OF_INFORMATION"].value)
    node[STONEnum["ID"].value] = glyph.get_id()
    node[STONEnum["CLASS"].value] = glyph.get_class().value
    node[STONEnum["MAP_ID"].value] = map_id
    node[STONEnum["LANGUAGE"].value] = language
    if glyph.get_label():
        if glyph.get_label().get_text():
            label = glyph.get_label().get_text()
            if ':' in label:
                node[STONEnum["PREFIX"].value] = label.split(':')[0]
                node[STONEnum["VALUE"].value] = label.split(':')[1]
            else:
                node[STONEnum["VALUE"].value] = label
    if glyph.get_bbox():
        bbox_node = bbox_to_node(glyph.get_bbox(), map_id, language)
        has_bbox = Relationship(node, STONEnum["HAS_BBOX"].value, bbox_node)
        subgraph |= has_bbox
        subgraph |= bbox_node
    return node, subgraph

def state_variable_to_subgraph(glyph, map_id, language):
    node = Node()
    subgraph = node
    node.add_label(STONEnum["STATE_VARIABLE"].value)
    node[STONEnum["ID"].value] = glyph.get_id()
    node[STONEnum["CLASS"].value] = glyph.get_class().value
    node[STONEnum["MAP_ID"].value] = map_id
    node[STONEnum["LANGUAGE"].value] = language
    if glyph.get_state():
        node[STONEnum["VALUE"].value] = glyph.get_state().get_value()
        node[STONEnum["VARIABLE"].value] = glyph.get_state().get_variable()
    if glyph.get_bbox():
        bbox_node = bbox_to_node(glyph.get_bbox(), map_id, language)
        has_bbox = Relationship(node, STONEnum["HAS_BBOX"].value, bbox_node)
        subgraph |= has_bbox
        subgraph |= bbox_node
    return node, subgraph

def port_to_node(port, language):
    node = Node()
    node.add_label(STONEnum["PORT"].value)
    node[STONEnum["ID"].value] = port.get_id()
    node[STONEnum["X"].value] = port.get_x()
    node[STONEnum["Y"].value] = port.get_y()
    node[STONEnum["LANGUAGE"].value] = language
    return node

def arc_to_relationship(arc, map_id, language, dids):
    rtype = STONEnum[arc.get_class().name].value
    start_node = dids[arc.get_source()]
    end_node = dids[arc.get_target()]
    properties = {
        STONEnum["ID"].value: arc.get_id(),
        STONEnum["CLASS"].value: arc.get_class().value,
        STONEnum["MAP_ID"].value: map_id,
        STONEnum["LANGUAGE"].value: language,
        STONEnum["SOURCE"].value: arc.get_source(),
        STONEnum["TARGET"].value: arc.get_target(),
        STONEnum["START"].value: "{},{}".format(arc.get_start().get_x(), arc.get_start().get_y()),
        STONEnum["END"].value: "{},{}".format(arc.get_end().get_x(), arc.get_end().get_y())
    }
    if arc.get_class().name == "CONSUMPTION":
        relationship = Relationship(end_node, rtype, start_node, **properties)
    else:
        relationship = Relationship(start_node, rtype, end_node, **properties)
    return relationship

def subgraph_to_sbgnfile(subgraph, sbgnfile):
    sbgnmap = subgraph_to_map(subgraph)
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

def subgraph_to_map(subgraph):
    dobjects = {}
    glyphs = set([])
    arcs = set([])
    language = None
    for relationship in subgraph.relationships:
        subgraph |= relationship.start_node
        subgraph |= relationship.end_node
    for node in subgraph.nodes:
        for label in node.labels:
            if label == STONEnum["BBOX"].value:
                bbox = node_to_bbox(node)
                dobjects[node] = bbox
                break
            elif label == STONEnum["PORT"].value:
                port = node_to_port(node)
                dobjects[node] = port
                break
            else:
                glyph = node_to_glyph(node)
                dobjects[node] = glyph
                glyphs.add(glyph)
                if not language:
                    language = libsbgn.Language(node[STONEnum["LANGUAGE"].value])
    for relationship in subgraph.relationships:
        if type(relationship).__name__ == STONEnum["HAS_BBOX"].value:
            dobjects[relationship.start_node].set_bbox(dobjects[relationship.end_node])
    for relationship in subgraph.relationships:
        if type(relationship).__name__ == STONEnum["HAS_BBOX"].value:
            pass
        elif type(relationship).__name__ == STONEnum["HAS_PORT"].value:
            dobjects[relationship.start_node].add_port(dobjects[relationship.end_node])
        elif type(relationship).__name__ == STONEnum["IS_IN_COMPARTMENT"].value:
            dobjects[relationship.start_node].set_compartmentRef(dobjects[relationship.end_node].get_id())
        elif type(relationship).__name__ == STONEnum["HAS_SUBUNIT"].value or type(relationship).__name__ == STONEnum["HAS_STATE_VARIABLE"].value or type(relationship).__name__ == STONEnum["HAS_UNIT_OF_INFORMATION"].value or type(relationship).__name__ == STONEnum["HAS_TERMINAL"].value:
            dobjects[relationship.start_node].add_glyph(dobjects[relationship.end_node])
            glyphs.remove(dobjects[relationship.end_node])
        else:
            arc = relationship_to_arc(relationship)
            arcs.add(arc)
    sbgnmap = libsbgn.map()
    for glyph in glyphs:
        sbgnmap.add_glyph(glyph)
    for arc in arcs:
        sbgnmap.add_arc(arc)
    sbgnmap.set_language(language)
    return sbgnmap

def relationship_to_arc(relationship):
    arc = libsbgn.arc()
    arc.set_id(relationship[STONEnum["ID"].value])
    arc.set_class(libsbgn.ArcClass(relationship[STONEnum["CLASS"].value]))
    arc.set_source(relationship[STONEnum["SOURCE"].value])
    arc.set_target(relationship[STONEnum["TARGET"].value])
    start = libsbgn.startType(relationship[STONEnum["START"].value].split(',')[0], relationship[STONEnum["START"].value].split(',')[1])
    end = libsbgn.endType(relationship[STONEnum["END"].value].split(',')[0], relationship[STONEnum["END"].value].split(',')[1])
    arc.set_start(start)
    arc.set_end(end)
    return arc

def node_to_glyph(node):
    glyph = libsbgn.glyph()
    glyph.set_id(node[STONEnum["ID"].value])
    glyph.set_class(libsbgn.GlyphClass(node[STONEnum["CLASS"].value]))
    for label in node.labels:
        if label == STONEnum["STATE_VARIABLE"].value:
            state = libsbgn.stateType()
            state.set_value(node[STONEnum["VALUE"].value])
            state.set_variable(node[STONEnum["VARIABLE"].value])
            glyph.set_state(state)
            break
        elif label == STONEnum["UNIT_OF_INFORMATION"].value:
            label = libsbgn.label()
            text = node[STONEnum["VALUE"].value]
            if node[STONEnum["PREFIX"].value]:
                text = "{}:{}".format(node[STONEnum["PREFIX"].value], text)
            label.set_text(text)
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

def node_to_bbox(node):
    bbox = libsbgn.bbox()
    bbox.set_x(node[STONEnum["X"].value])
    bbox.set_y(node[STONEnum["Y"].value])
    bbox.set_h(node[STONEnum["H"].value])
    bbox.set_w(node[STONEnum["W"].value])
    return bbox

def node_to_port(node):
    port = libsbgn.port()
    port.set_id(node[STONEnum["ID"].value])
    port.set_x(node[STONEnum["X"].value])
    port.set_y(node[STONEnum["Y"].value])
    return port

if __name__ == '__main__':
    # file_name = "/home/rougny/essai.sbgn"
    file_name = "/home/rougny/research/sbgn/pd/newv2/examples/sources/insulin.sbgn"

    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "neofourj"

    g = Graph(uri = uri, user = user, password = password)

    subgraph = sbgnfile_to_subgraph(file_name)
    g.delete_all()

    tx = g.begin()
    tx.create(subgraph)
    tx.commit()

    tx = g.begin()
    cursor = tx.run("MATCH (n {{{}: '{}'}})-[r]-(m) RETURN r".format(STONEnum["MAP_ID"].value, file_name))
    # query = 'MATCH (process:Process), (process)-[consumption: CONSUMES]-(reactant:Macromolecule), (process)-[production: PRODUCES]-(product: Macromolecule), (catalyzer)-[catalysis: CATALYZES]-(process), (reactant)-[:HAS_STATE_VARIABLE]-(sv_reactant), (product)-[:HAS_STATE_VARIABLE]-(sv_product) WHERE sv_reactant.value IS NULL AND sv_product.value = "P" AND (sv_reactant.variable IS NULL AND sv_product.variable IS NULL OR sv_reactant.variable = sv_product.variable) RETURN process;'
    # cursor = tx.run(query)
    tx.commit()
    subgraph = cursor.to_subgraph()

    subgraph_to_sbgnfile(subgraph, "/home/rougny/res.sbgn")
