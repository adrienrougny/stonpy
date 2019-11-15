from enum import Enum

from py2neo.data import walk
from py2neo import Database, Graph, Node, Relationship, Subgraph

import libsbgnpy.libsbgn as libsbgn

class STONEnum(Enum):
    #Labels
    MAP = "Map"
    EPN = "Epn"
    GLYPH = "Glyph"
    ARC = "Arc"
    ARCGROUP = "Arcgroup"
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
    DELAY = "DelayOperator"
    EQUIVALENCE = "EquivalenceOperator"
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
    BIOLOGICAL_ACTIVITY = "BiologicalActivity"
    START = "Start"
    END = "End"
    NEXT = "Next"
    CATALYSIS  = "Catalyzis"
    MODULATION = "Modulation"
    STIMULATION  = "Stimulation"
    INHIBITION  = "Inhibition"
    NECESSARY_STIMULATION  = "NecessaryStimulation"
    CONSUMPTION = "Consumption"
    PRODUCTION = "Production"
    LOGIC_ARC = "LogicArc"
    EQUIVALENCE_ARC = "EquivalenceArc"
    NEGATIVE_INFLUENCE = "NegativeInfluence"
    POSITIVE_INFLUENCE = "PositiveInfluence"
    UNKNOWN_INFLUENCE = "UnknownInfluence"
    EXISTENCE = "Existence"
    LOCATION = "Location"
    VARIABLE_VALUE = "VariableValue"
    ENTITY = "Entity"
    INTERACTION = "Interaction"
    ASSIGNMENT = "Assignment"
    OUTCOME = "OUTCOME"
    #Relation types
    CATALYSIS_SHORTCUT  = "CATALYZES"
    MODULATION_SHORTCUT = "MODULATES"
    STIMULATION_SHORTCUT  = "STIMULATES"
    INHIBITION_SHORTCUT  = "INHIBITS"
    NECESSARY_STIMULATION_SHORTCUT  = "NECESSARY_STIMULATES"
    CONSUMPTION_SHORTCUT = "CONSUMES"
    PRODUCTION_SHORTCUT = "PRODUCES"
    HAS_SUBUNIT = "HAS_SUBUNIT"
    HAS_STATE_VARIABLE = "HAS_STATE_VARIABLE"
    HAS_UNIT_OF_INFORMATION = "HAS_UNIT_OF_INFORMATION"
    LOGIC_ARC_SHORTCUT = "IS_INPUT_OF"
    EQUIVALENCE_ARC_SHORTCUT = "IS_INPUT_OF"
    HAS_PORT = "HAS_PORT"
    HAS_BBOX = "HAS_BBOX"
    HAS_TERMINAL = "HAS_TERMINAL"
    IS_IN_COMPARTMENT = "IS_IN_COMPARTMENT"
    NEGATIVE_INFLUENCE_SHORTCUT = "NEGATIVELY_INFLUENCES"
    POSITIVE_INFLUENCE_SHORTCUT = "POSITIVELY_INFLUENCES"
    UNKNOWN_INFLUENCE_SHORTCUT = "INFLUENCES"
    HAS_CARDINALITY = "HAS_CARDINALITY"
    HAS_OUTCOME = "HAS_OUTCOME"
    HAS_SOURCE = "HAS_SOURCE"
    HAS_TARGET = "HAS_TARGET"
    HAS_START = "HAS_START"
    HAS_END = "HAS_END"
    HAS_NEXT = "HAS_NEXT"
    HAS_VALUE = "HAS_VALUE"
    HAS_GLYPH = "HAS_GLYPH"
    HAS_ARC = "HAS_ARC"
    HAS_ARCGROUP = "HAS_ARCGROUP"
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
    MAP_ID = "id"
    X = "x"
    Y = "y"
    W = "w"
    H = "h"
    ORIENTATION = "orientation"
    CARDINALITY = "cardinality"
    UI_TYPE = "type"

# SBGNGlyphs = set(["COMPARTMENT", "UNSPECIFIED_ENTITY", "SIMPLE_CHEMICAL", "MACROMOLECULE", "NUCLEIC_ACID_FEATURE", "COMPLEX", "SIMPLE_CHEMICAL_MULTIMER", "MACROMOLECULE_MULTIMER", "NUCLEIC_ACID_FEATURE_MULTIMER", "COMPLEX_MULTIMER", "SOURCE_AND_SINK", "PERTURBING_AGENT", "PROCESS", "OMITTED_PROCESS", "UNCERTAIN_PROCESS", "ASSOCIATION", "DISSOCIATION", "PHENOTYPE", "OR", "AND", "NOT", "STATE_VARIABLE", "UNIT_OF_INFORMATION", "UNSPECIFIED_ENTITY_SUBUNIT", "SIMPLE_CHEMICAL_SUBUNIT", "MACROMOLECULE_SUBUNIT", "NUCLEIC_ACID_FEATURE_SUBUNIT", "COMPLEX_SUBUNIT", "SIMPLE_CHEMICAL_MULTIMER_SUBUNIT", "MACROMOLECULE_MULTIMER_SUBUNIT", "NUCLEIC_ACID_FEATURE_MULTIMER_SUBUNIT", "COMPLEX_MULTIMER_SUBUNIT", "TERMINAL", "TAG", "SUBMAP", "STATE_VARIABLE", "UNIT_OF_INFORMATION"])
#
# SBGNArcs = set(["CATALYSIS", "MODULATION", "STIMULATION", "INHIBITION", "NECESSARY_STIMULATION", "CONSUMPTION", "PRODUCTION", "LOGIC_ARC", "EQUIVALENCE_ARC"])

def sbgnfile_to_subgraph(sbgnfile, map_id):
    sbgn = libsbgn.parse(sbgnfile, silence = True)
    sbgnmap = sbgn.get_map()
    if not map_id:
        map_id = sbgnfile
    subgraph = map_to_subgraph(sbgnmap, map_id)
    return subgraph

def map_to_subgraph(sbgnmap, map_id):
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
            glyph_node, glyph_subgraph = glyph_to_subgraph(glyph, dids, dpids)
            if not subgraph:
                subgraph = glyph_subgraph
            else:
                subgraph |= glyph_subgraph
            dids[glyph.get_id()] = glyph_node
            subgraph |= Relationship(map_node, STONEnum["HAS_GLYPH"].value, glyph_node)
    for glyph in sbgnmap.get_glyph():
        if glyph.get_class().name != "COMPARTMENT":
            glyph_node, glyph_subgraph = glyph_to_subgraph(glyph, dids, dpids)
            if not subgraph:
                subgraph = glyph_subgraph
            else:
                subgraph |= glyph_subgraph
            subgraph |= Relationship(map_node, STONEnum["HAS_GLYPH"].value, glyph_node)
    for arc in sbgnmap.get_arc():
        if arc.get_class().name == "ASSIGNMENT" or arc.get_class().name == "INTERACTION":
            arc_node, arc_subgraph = arc_to_subgraph(arc, dids, dpids)
            subgraph |= arc_subgraph
            subgraph |= Relationship(map_node, STONEnum["HAS_ARC"].value, arc_node)
            dids[arc.get_id()] = arc_node
    for arc in sbgnmap.get_arc():
        if arc.get_class().name != "ASSIGNMENT" and arc.get_class().name != "INTERACTION":
            arc_node, arc_subgraph = arc_to_subgraph(arc, dids, dpids)
            subgraph |= arc_subgraph
            subgraph |= Relationship(map_node, STONEnum["HAS_ARC"].value, arc_node)
    for arcgroup in sbgnmap.get_arcgroup():
        arcgroup_node, arcgroup_subgraph = arcgroup_to_subgraph(arcgroup, dids, dpids)
        subgraph |= arcgroup_subgraph
        subgraph |= Relationship(map_node, STONEnum["HAS_ARCGROUP"].value, arcgroup_node)
    return subgraph

def glyph_to_subgraph(glyph, dids, dpids):
    node = Node()
    subgraph = node
    node.add_label(STONEnum[glyph.get_class().name].value)
    node.add_label(STONEnum["GLYPH"].value)
    node[STONEnum["CLASS"].value] = glyph.get_class().value
    node[STONEnum["ID"].value] = glyph.get_id()
    if glyph.get_label():
        label = glyph.get_label().get_text()
        if glyph.get_class().name == "UNIT_OF_INFORMATION":
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
                node[STONEnum["CLONE_LABEL"].value] = glyph.get_clone().get_label().get_text()
    else:
        node[STONEnum["CLONE"].value] = False
    if glyph.get_compartmentRef():
        node[STONEnum["COMPARTMENT_ORDER"].value] = glyph.get_compartmentOrder()
    if glyph.get_compartmentRef():
        is_in_compartment = Relationship(node, STONEnum["IS_IN_COMPARTMENT"].value, dids[glyph.get_compartmentRef()])
        subgraph |= is_in_compartment
    if glyph.get_bbox():
        bbox_node = bbox_to_node(glyph.get_bbox())
        subgraph |= bbox_node
        has_bbox = Relationship(node, STONEnum["HAS_BBOX"].value, bbox_node)
        subgraph |= has_bbox
    if glyph.orientation:
        node[STONEnum["ORIENTATION"].value] = glyph.orientation
    if glyph.get_state():
        node[STONEnum["VALUE"].value] = glyph.get_state().get_value()
        node[STONEnum["VARIABLE"].value] = glyph.get_state().get_variable()
    if glyph.get_entity():
        node[STONEnum["UI_TYPE"].value] = glyph.get_entity().name
    for subglyph in glyph.get_glyph():
        subglyph_node, subglyph_subgraph = glyph_to_subgraph(subglyph, dids, dpids)
        subgraph |= subglyph_subgraph
        dids[subglyph.get_id()] = subglyph_node
        if subglyph.get_class().name == "UNIT_OF_INFORMATION":
            subgraph |= Relationship(node, STONEnum["HAS_UNIT_OF_INFORMATION"].value, subglyph_node)
        elif subglyph.get_class().name == "STATE_VARIABLE":
            subgraph |= Relationship(node, STONEnum["HAS_STATE_VARIABLE"].value, subglyph_node)
        elif subglyph.get_class().name == "TERMINAL":
            subgraph |= Relationship(node, STONEnum["HAS_TERMINAL"].value, subglyph_node)
        elif subglyph.get_class().name == "OUTCOME":
            subgraph |= Relationship(node, STONEnum["HAS_OUTCOME"].value, subglyph_node)
        else:
            subgraph |= Relationship(node, STONEnum["HAS_SUBUNIT"].value, subglyph_node)
    for port in glyph.get_port():
        port_node = port_to_node(port)
        subgraph |= port_node
        subgraph |= Relationship(node, STONEnum["HAS_PORT"].value, port_node)
        dids[port.get_id()] = port_node
        dpids[port.get_id()] = node
    dids[glyph.get_id()] = node
    return node, subgraph

def bbox_to_node(bbox):
    node = Node()
    node.add_label(STONEnum["BBOX"].value)
    node[STONEnum["X"].value] = bbox.get_x()
    node[STONEnum["Y"].value] = bbox.get_y()
    node[STONEnum["W"].value] = bbox.get_w()
    node[STONEnum["H"].value] = bbox.get_h()
    return node

def port_to_node(port):
    node = Node()
    node.add_label(STONEnum["PORT"].value)
    node[STONEnum["ID"].value] = port.get_id()
    node[STONEnum["X"].value] = port.get_x()
    node[STONEnum["Y"].value] = port.get_y()
    return node

def arc_to_subgraph(arc, dids, dpids):
    node = Node()
    node.add_label(STONEnum[arc.get_class().name].value)
    node.add_label(STONEnum["ARC"].value)
    node[STONEnum["CLASS"].value] = arc.get_class().value
    node[STONEnum["ID"].value] = arc.get_id()
    subgraph = node
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
        subgraph |= Relationship(prev_node, STONEnum["HAS_NEXT"].value, next_node)
        prev_node = next_node
    if prev_node != start:
        subgraph |= Relationship(prev_node, STONEnum["HAS_NEXT"].value, end)
    for glyph in arc.get_glyph():
        glyph_node, glyph_subgraph = glyph_to_subgraph(glyph, dids, dpids)
        subgraph |= glyph_subgraph
        if glyph.get_class().name == "CARDINALITY":
            subgraph |= Relationship(node, STONEnum["HAS_CARDINALITY"].value, glyph_node)
        elif glyph.get_class().name == "OUTCOME":
            subgraph |= Relationship(node, STONEnum["HAS_OUTCOME"].value, glyph_node)
    for port in arc.get_port():
        port_node = port_to_node(port)
        subgraph |= port_node
        subgraph |= Relationship(node, STONEnum["HAS_PORT"].value, port_node)
        dids[port.get_id()] = port_node
        dpids[port.get_id()] = node
    return node, subgraph

def arcgroup_to_subgraph(arcgroup, dids, dpids):
    node = Node()
    if arcgroup.get_class() == "interaction": # class interaction is just a string for arcgroups
        node.add_label(STONEnum["INTERACTION"].value)
    else:
        node.add_label(STONEnum[arcgroup.get_class().name].value)
    node.add_label(STONEnum["ARCGROUP"].value)
    if arcgroup.get_class() == "interaction": # class interaction is just a string for arcgroups
        node[STONEnum["CLASS"].value] = arcgroup.get_class()
    else:
        node[STONEnum["CLASS"].value] = arcgroup.get_class().value
    subgraph = node
    for glyph in arcgroup.get_glyph():
        glyph_node, glyph_subgraph = glyph_to_subgraph(glyph, dids, dpids)
        subgraph |= glyph_subgraph
        subgraph |= Relationship(node, STONEnum["HAS_GLYPH"].value, glyph_node)
    for arc in arcgroup.get_arc():
        arc_node, arc_subgraph = arc_to_subgraph(arc, dids, dpids)
        subgraph |= arc_subgraph
        subgraph |= Relationship(node, STONEnum["HAS_ARC"].value, arc_node)
    return node, subgraph

def map_to_sbgnfile(sbgnmap, sbgnfile):
    print(sbgnfile)
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

def subgraph_to_sbgnfile(subgraph, sbgnfile):
    sbgnmaps = subgraph_to_map(subgraph)
    if len(sbgnmaps) > 1:
        ext = "sbgn"
        l = sbgnfile.split('.')
        if len(l) > 1:
            ext = l[-1]
            root = ''.join(l[:-1])
        else:
            root = sbgnfile
        for i, sbgnmap in enumerate(sbgnmaps):
            map_to_sbgnfile(sbgnmap, "{}_{}.{}".format(root, i, ext))
    elif len(sbgnmaps) == 1:
        sbgnmap = sbgnmaps.pop()
        map_to_sbgnfile(sbgnmap, sbgnfile)

def subgraph_to_map(subgraph):
    dobjects = {}
    sbgnmaps = set([])
    for node in subgraph.nodes:
        if node.has_label(STONEnum["MAP"].value):
            sbgnmap = libsbgn.map()
            language = node[STONEnum["LANGUAGE"].value]
            sbgnmap.set_language(libsbgn.Language(language))
            sbgnmaps.add(sbgnmap)
            dobjects[node] = sbgnmap
        if node.has_label(STONEnum["BBOX"].value):
            bbox = bbox_from_node(node)
            dobjects[node] = bbox
        elif node.has_label(STONEnum["PORT"].value):
            port = port_from_node(node)
            dobjects[node] = port
        elif node.has_label(STONEnum["GLYPH"].value):
            glyph = glyph_from_node(node)
            dobjects[node] = glyph
        elif node.has_label(STONEnum["ARC"].value):
            arc = arc_from_node(node)
            dobjects[node] = arc
        elif node.has_label(STONEnum["START"].value):
            start = sart_from_node(node)
            dobjects[node] = start
        elif node.has_label(STONEnum["END"].value):
            end = end_from_node(node)
            dobjects[node] = end
        elif node.has_label(STONEnum["NEXT"].value):
            nextt = next_from_node(node)
            dobjects[node] = nextt
        elif node.has_label(STONEnum["ARCGROUP"].value):
            arcgroup = arcgroup_from_node(node)
            dobjects[node] = arcgroup
    for relationship in subgraph.relationships:
        rtype = type(relationship).__name__
        if rtype == STONEnum["HAS_BBOX"].value:
            dobjects[relationship.start_node].set_bbox(dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_PORT"].value:
            dobjects[relationship.start_node].add_port(dobjects[relationship.end_node])
        elif rtype == STONEnum["IS_IN_COMPARTMENT"].value:
            dobjects[relationship.start_node].set_compartmentRef(dobjects[relationship.end_node].get_id())
        elif rtype == STONEnum["HAS_START"].value:
            dobjects[relationship.start_node].set_start(dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_END"].value:
            dobjects[relationship.start_node].set_end(dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_SOURCE"].value:
            dobjects[relationship.start_node].set_source(dobjects[relationship.end_node].get_id())
        elif rtype == STONEnum["HAS_TARGET"].value:
            dobjects[relationship.start_node].set_target(dobjects[relationship.end_node].get_id())
        elif rtype == STONEnum["HAS_GLYPH"].value or rtype == STONEnum["HAS_SUBUNIT"].value or rtype == STONEnum["HAS_STATE_VARIABLE"].value or rtype == STONEnum["HAS_UNIT_OF_INFORMATION"].value or rtype == STONEnum["HAS_TERMINAL"].value or rtype == STONEnum["HAS_OUTCOME"].value or rtype == STONEnum["HAS_CARDINALITY"].value:
            dobjects[relationship.start_node].add_glyph(dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_ARC"].value:
            dobjects[relationship.start_node].add_arc(dobjects[relationship.end_node])
        elif rtype == STONEnum["HAS_ARCGROUP"].value:
            dobjects[relationship.start_node].add_arcgroup(dobjects[relationship.end_node])
    return sbgnmaps

def glyph_from_node(node):
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

def bbox_from_node(node):
    bbox = libsbgn.bbox()
    bbox.set_x(node[STONEnum["X"].value])
    bbox.set_y(node[STONEnum["Y"].value])
    bbox.set_h(node[STONEnum["H"].value])
    bbox.set_w(node[STONEnum["W"].value])
    return bbox

def port_from_node(node):
    port = libsbgn.port()
    port.set_id(node[STONEnum["ID"].value])
    port.set_x(node[STONEnum["X"].value])
    port.set_y(node[STONEnum["Y"].value])
    return port

def sart_from_node(node):
    start = libsbgn.startType(node[STONEnum["X"].value], node[STONEnum["Y"].value])
    return start

def end_from_node(node):
    end = libsbgn.endType(node[STONEnum["X"].value], node[STONEnum["Y"].value])
    return end

def next_from_node(node):
    nextt = libsbgn.endType(node[STONEnum["X"].value], node[STONEnum["Y"].value])
    return nextt

def arc_from_node(node):
    arc = libsbgn.arc()
    arc.set_id(node[STONEnum["ID"].value])
    arc.set_class(libsbgn.ArcClass(node[STONEnum["CLASS"].value]))
    return arc

def arcgroup_from_node(node):
    arcgroup = libsbgn.arcgroup()
    # arcgroup.set_id(node[STONEnum["ID"].value]) # argroup has no ID
    if node[STONEnum["CLASS"].value] == "interaction": # class interaction is just a string for arcgroups
        arcgroup.set_class(node[STONEnum["CLASS"].value])
    else:
        arcgroup.set_class(libsbgn.ArcClass(node[STONEnum["CLASS"].value]))
    return arcgroup

def complete_subgraph(subgraph, neograph):
    completed = set([])
    for node in subgraph.nodes:
        if node not in completed:
            if node.has_label(STONEnum["GLYPH"].value):
                subgraph |= complete_subgraph_with_glyph_node(subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["ARC"].value):
                subgraph |= complete_subgraph_with_arc_node(subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["ARCGROUP"].value):
                subgraph |= complete_subgraph_with_arcgroup_node(subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["BBOX"].value):
                subgraph |= complete_subgraph_with_bbox_node(subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["MAP"].value):
                subgraph |= complete_subgraph_with_map_node(subgraph, node, completed, neograph)
            elif node.has_label(STONEnum["PORT"].value):
                subgraph |= complete_subgraph_with_port_node(subgraph, node, completed, neograph)
    # print_subgraph(subgraph)
    return subgraph

def complete_subgraph_with_glyph_node(subgraph, node, completed, neograph):
    completed.add(node)
    #BBOX
    relationship = match_one(subgraph, (node,), STONEnum["HAS_BBOX"].value)
    if relationship is None:
        relationship = neograph.match_one((node,), STONEnum["HAS_BBOX"].value)
    if relationship is not None:
        subgraph |= relationship
        subgraph |= relationship.end_node
    #PORTs only of node is a process or a logical operator
    if node.has_label(STONEnum["PROCESS"].value) or node.has_label(STONEnum["UNCERTAIN_PROCESS"].value) or node.has_label(STONEnum["OMITTED_PROCESS"].value) or node.has_label(STONEnum["ASSOCIATION"].value) or node.has_label(STONEnum["DISSOCIATION"].value) or node.has_label(STONEnum["AND"].value) or node.has_label(STONEnum["OR"].value) or node.has_label(STONEnum["NOT"].value) or node.has_label(STONEnum["DELAY"].value) or node.has_label(STONEnum["EQUIVALENCE"].value):
        relationships = neograph.match((node,), STONEnum["HAS_PORT"].value)
        for relationship in relationships:
            port_node = relationship.end_node
            subgraph |= relationship
            subgraph |= port_node
            if port_node not in completed:
                subgraph |= complete_subgraph_with_port_node(subgraph, port_node, completed, neograph)
    #STATE_VARIABLEs, UNIT_OF_INFORMATIONs, SUBUNITs, OUTCOMEs, TERMINALS
    for name in ["HAS_STATE_VARIABLE", "HAS_UNIT_OF_INFORMATION", "HAS_SUBUNIT", "HAS_OUTCOME", "HAS_TERMINAL"]:
        relationships = neograph.match((node,), STONEnum[name].value)
        for relationship in relationships:
            subglyph_node = relationship.end_node
            subgraph |= relationship
            subgraph |= subglyph_node
            if subglyph_node not in completed:
                subgraph |= complete_subgraph_with_glyph_node(subgraph, subglyph_node, completed, neograph)
    #MAP
    relationship = match_one(subgraph, (None, node), STONEnum["HAS_GLYPH"].value)
    if relationship is None:
        relationship = neograph.match_one((None, node), STONEnum["HAS_GLYPH"].value)
    if relationship is not None:
        sbgnmap = relationship.start_node
        subgraph |= relationship
        subgraph |= sbgnmap
    #STATE_VARIABLE, UNIT_OF_INFORMATION, SUBUNIT, OR OUTCOME OWNER
    for name in ["HAS_STATE_VARIABLE", "HAS_UNIT_OF_INFORMATION", "HAS_SUBUNIT", "HAS_OUTCOME"]:
        relationship = match_one(subgraph, (None, node), STONEnum[name].value)
        if relationship is None:
            relationship = neograph.match_one((None, node), STONEnum[name].value)
        if relationship is not None:
            owner = relationship.start_node
            subgraph |= relationship
            subgraph |= owner
            if owner not in completed:
                if owner.has_label(STONEnum["GLYPH"].value):
                    subgraph |= complete_subgraph_with_glyph_node(subgraph, owner, completed, neograph)
                elif owner.has_label(STONEnum["ARC"].value):
                    subgraph |= complete_subgraph_with_arc_node(subgraph, owner, completed, neograph)
    return subgraph

def complete_subgraph_with_port_node(subgraph, port_node, completed, neograph):
    completed.add(port_node)
    #OWNER
    relationship = match_one(subgraph, (None, port_node), STONEnum["HAS_PORT"].value)
    if relationship is None:
        relationship = neograph.match_one((None, port_node), STONEnum["HAS_PORT"].value)
    if relationship is not None:
        owner = relationship.start_node
        subgraph |= relationship
        subgraph |= owner
        if owner not in completed:
            if owner.has_label(STONEnum["GLYPH"].value):
                subgraph |= complete_subgraph_with_glyph_node(subgraph, owner, completed, neograph)
            elif owner.has_label(STONEnum["ARC"].value):
                subgraph |= complete_subgraph_with_arc_node(subgraph, owner, completed, neograph)
    #SOURCE OF
    relationships = neograph.match((None, port_node), STONEnum["HAS_SOURCE"].value)
    for relationship in relationships:
        arc_node = relationship.start_node
        subgraph |= relationship
        subgraph |= arc_node
        if arc_node not in completed:
            subgraph |= complete_subgraph_with_arc_node(subgraph, arc_node, completed, neograph)
    #TARGET OF
    relationships = neograph.match((None, port_node), STONEnum["HAS_TARGET"].value)
    for relationship in relationships:
        arc_node = relationship.start_node
        subgraph |= relationship
        subgraph |= arc_node
        if arc_node not in completed:
            subgraph |= complete_subgraph_with_arc_node(subgraph, arc_node, completed, neograph)
    return subgraph

def complete_subgraph_with_bbox_node(subgraph, bbox_node, completed, neograph):
    #OWNER
    completed.add(bbox_node)
    relationship = match_one(subgraph, (None, bbox_node), STONEnum["HAS_BBOX"].value)
    if relationship is None:
        relationship = neograph.match_one((None, bbox_node), STONEnum["HAS_BBOX"].value)
    if relationship is not None:
        owner = relationship.start_node
        subgraph |= relationship
        subgraph |= owner
        if owner not in completed:
            subgraph |= complete_subgraph_with_glyph_node(subgraph, owner, completed, neograph)
    print_subgraph(subgraph)
    return subgraph

def complete_subgraph_with_arc_node(subgraph, node, completed, neograph):
    completed.add(node)
    #PORTs
    relationships = neograph.match((node,), STONEnum["HAS_PORT"].value)
    for relationship in relationships:
        port_node = relationship.end_node
        subgraph |= relationship
        subgraph |= port_node
    #OUTCOMEs
    relationships = neograph.match((node,), STONEnum["HAS_OUTCOME"].value)
    for relationship in relationships:
        subglyph_node = relationship.end_node
        subgraph |= relationship
        subgraph |= subglyph_node
        if subglyph_node not in completed:
            subgraph |= complete_subgraph_with_glyph_node(subgraph, subglyph_node, completed, neograph)
    #MAP
    relationship = match_one(subgraph, (None, node), STONEnum["HAS_ARC"].value)
    if relationship is None:
        relationship = neograph.match_one((None, node), STONEnum["HAS_ARC"].value)
    if relationship is not None:
        sbgnmap = relationship.start_node
        subgraph |= relationship
        subgraph |= sbgnmap
    #CARDINALITY
    relationship = match_one(subgraph, (node,), STONEnum["HAS_CARDINALITY"].value)
    if relationship is None:
        relationship = neograph.match_one((node,), STONEnum["HAS_CARDINALITY"].value)
    if relationship is not None:
        cardinality = relationship.end_node
        subgraph |= relationship
        subgraph |= cardinality
        if cardinality not in completed:
            subgraph |= complete_subgraph_with_glyph_node(subgraph, cardinality, completed, neograph)
    #SOURCE
    relationship = match_one(subgraph, (node,), STONEnum["HAS_SOURCE"].value)
    if relationship is None:
        relationship = neograph.match_one((node,), STONEnum["HAS_SOURCE"].value)
    if relationship is not None:
        source = relationship.end_node
        subgraph |= relationship
        subgraph |= source
        if source not in completed:
            if source.has_label(STONEnum["PORT"].value):
                subgraph |= complete_subgraph_with_port_node(subgraph, source, completed, neograph)
            else:
                subgraph |= complete_subgraph_with_glyph_node(subgraph, source, completed, neograph)
    #TARGET
    relationship = match_one(subgraph, (node,), STONEnum["HAS_TARGET"].value)
    if relationship is None:
        relationship = neograph.match_one((node,), STONEnum["HAS_TARGET"].value)
    if relationship is not None:
        target = relationship.end_node
        subgraph |= relationship
        subgraph |= target
        if target not in completed:
            if target.has_label(STONEnum["PORT"].value):
                subgraph |= complete_subgraph_with_port_node(subgraph, target, completed, neograph)
            else:
                subgraph |= complete_subgraph_with_glyph_node(subgraph, target, completed, neograph)
    #START
    relationship = match_one(subgraph, (node,), STONEnum["HAS_START"].value)
    if relationship is None:
        relationship = neograph.match_one((node,), STONEnum["HAS_START"].value)
    if relationship is not None:
        start = relationship.end_node
        subgraph |= relationship
        subgraph |= start 
    #END
    relationship = match_one(subgraph, (node,), STONEnum["HAS_END"].value)
    if relationship is None:
        relationship = neograph.match_one((node,), STONEnum["HAS_END"].value)
    if relationship is not None:
        end = relationship.end_node
        subgraph |= relationship
        subgraph |= end
    return subgraph

def complete_subgraph_with_arcgroup_node(subgraph, node, completed, neograph):
    #ARCs
    relationships = neograph.match((node,), STONEnum["HAS_ARC"].value)
    for relationship in relationships:
        arc_node = relationship.end_node
        subgraph |= relationship
        subgraph |= arc_node
        if arc_node not in completed:
            subgraph |= complete_subgraph_with_arc_node(subgraph, arc_node, completed, neograph)
    #GLYPHs
    relationships = neograph.match((node,), STONEnum["HAS_GLYPH"].value)
    for relationship in relationships:
        glyph_node = relationship.end_node
        subgraph |= relationship
        subgraph |= glyph_node
        if glyph_node not in completed:
            subgraph |= complete_subgraph_with_glyph_node(subgraph, glyph_node, completed, neograph)
    #MAP
    relationship = match_one(subgraph, (None, node), STONEnum["HAS_ARCGROUP"].value)
    if relationship is None:
        relationship = neograph.match_one((None, node), STONEnum["HAS_ARCGROUP"].value)
    if relationship is not None:
        sbgnmap = relationship.start_node
        subgraph |= relationship
        subgraph |= sbgnmap
    return subgraph

def complete_subgraph_with_map_node(subgraph, node, completed, neograph):
    #ARCs
    relationships = neograph.match((node,), STONEnum["HAS_ARC"].value)
    for relationship in relationships:
        arc_node = relationship.end_node
        subgraph |= relationship
        subgraph |= arc_node
        if arc_node not in completed:
            subgraph |= complete_subgraph_with_arc_node(subgraph, arc_node, completed, neograph)
    #GLYPHs
    relationships = neograph.match((node,), STONEnum["HAS_GLYPH"].value)
    for relationship in relationships:
        glyph_node = relationship.end_node
        subgraph |= relationship
        subgraph |= glyph_node
        if glyph_node not in completed:
            subgraph |= complete_subgraph_with_glyph_node(subgraph, glyph_node, completed, neograph)
    #ARCGROUPs
    relationships = neograph.match((node,), STONEnum["HAS_ARCGROUP"].value)
    for relationship in relationships:
        arcgroup_node = relationship.end_node
        subgraph |= relationship
        subgraph |= arcgroup_node
        if arcgroup_node not in completed:
            subgraph |= complete_subgraph_with_arcgroup_node(subgraph, arcgroup_node, completed, neograph)
    return subgraph
 
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

def create_map(sbgnfile, map_id):
    subgraph = sbgnfile_to_subgraph(sbgnfile, map_id)
    tx = g.begin()
    tx.create(subgraph)
    tx.commit()

if __name__ == '__main__':
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "neofourj"

    g = Graph(uri = uri, user = user, password = password)

    g.delete_all()

    # create_map("/home/rougny/essai.sbgn", "id1")
    create_map("/home/rougny/research/sbgn/pd/newv2/examples/sources/insulin.sbgn", "id2")

    tx = g.begin()
    # query = 'MATCH (n:Port {id: "arc2.0"}) RETURN n'
    # query = 'MATCH (n:Process {id: "glyph3"}) RETURN n'
    query = 'MATCH p=(n1:Map {id: "id2"})-[*]->() RETURN p'
    # query = 'MATCH (process:Process), (process)-[consumption: CONSUMES]-(reactant:Macromolecule), (process)-[production: PRODUCES]-(product: Macromolecule), (catalyzer)-[catalysis: CATALYZES]-(process), (reactant)-[:HAS_STATE_VARIABLE]-(sv_reactant), (product)-[:HAS_STATE_VARIABLE]-(sv_product) WHERE sv_reactant.value IS NULL AND sv_product.value = "P" AND (sv_reactant.variable IS NULL AND sv_product.variable IS NULL OR sv_reactant.variable = sv_product.variable) RETURN process;'
    cursor = tx.run(query)
    tx.commit()
    subgraph = cursor.to_subgraph()
    subgraph = complete_subgraph(subgraph, g)
    subgraph_to_sbgnfile(subgraph, "/home/rougny/res.sbgn")
