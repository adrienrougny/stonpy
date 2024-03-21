from enum import Enum


class STONEnum(Enum):
    """The Enum for the labels, relationship types and properties names used
    in stonpy's data model
    """

    # Labels
    COLLECTION = "Collection"
    MAP = "Map"
    ACTIVITY = "Activity"
    EPN = "Epn"
    MULTIMER = "Multimer"
    GLYPH = "Glyph"
    ARC = "Arc"
    ARCGROUP = "Arcgroup"
    SUBUNIT = "Subunit"
    LOGICAL_OPERATOR = "LogicalOperator"
    PROCESS = "Process"
    STOICHIOMETRIC_PROCESS = "StoichiometricProcess"
    INFLUENCE = "Influence"
    FLUX_ARC = "FluxArc"
    AUXILLIARY_UNIT = "AuxilliaryUnit"
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
    GENERIC_PROCESS = "GenericProcess"
    OMITTED_PROCESS = "OmittedProcess"
    UNCERTAIN_PROCESS = "UncertainProcess"
    ASSOCIATION = "Association"
    DISSOCIATION = "Dissociation"
    PHENOTYPE = "Phenotype"
    OR = "OrOperator"
    AND = "AndOperator"
    NOT = "NotOperator"
    DELAY = "DelayOperator"
    EQUIVALENCE = "EquivalenceOperator"
    ENTITY = "Entity"
    VARIABLE_VALUE = "VariableValue"
    EXISTENCE = "Existence"
    LOCATION = "Location"
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
    PHENOTYPE_SUBUNIT = (
        "PhenotypeSubunit"  # for compatibility with some CD maps out there
    )
    PORT = "Port"
    BBOX = "Bbox"
    TAG = "Tag"
    TERMINAL = "Terminal"
    SUBMAP = "Submap"
    BIOLOGICAL_ACTIVITY = "BiologicalActivity"
    START = "Start"
    END = "End"
    NEXT = "Next"
    CATALYSIS = "Catalyzis"
    MODULATION = "Modulation"
    STIMULATION = "Stimulation"
    ABSOLUTE_STIMULATION = "AsboluteStimulation"
    INHIBITION = "Inhibition"
    ABSOLUTE_INHIBITION = "AsboluteInhibition"
    NECESSARY_STIMULATION = "NecessaryStimulation"
    CONSUMPTION = "Consumption"
    PRODUCTION = "Production"
    LOGIC_ARC = "LogicArc"
    EQUIVALENCE_ARC = "EquivalenceArc"
    NEGATIVE_INFLUENCE = "NegativeInfluence"
    POSITIVE_INFLUENCE = "PositiveInfluence"
    UNKNOWN_INFLUENCE = "UnknownInfluence"
    INTERACTION = "Interaction"
    INTERACTION_GLYPH = "InteractionGlyph"
    INTERACTION_ARCGROUP = "InteractionArcgroup"
    ASSIGNMENT = "Assignment"
    OUTCOME = "Outcome"
    CARDINALITY = "Cardinality"
    ANNOTATION = "Annotation"
    RESOURCE = "Resource"
    INTERACTOR = "Interactor"
    RELATIONSHIP = "Relationship"
    STATEMENT = "Statement"
    ENTITY_NODE = "EntityNode"
    IMPLICIT_XOR = "ImplicitXor"
    LABEL = "Label"
    # Relation types
    HAS_SUBUNIT = "HAS_SUBUNIT"
    HAS_STATE_VARIABLE = "HAS_STATE_VARIABLE"
    HAS_UNIT_OF_INFORMATION = "HAS_UNIT_OF_INFORMATION"
    HAS_PORT = "HAS_PORT"
    HAS_BBOX = "HAS_BBOX"
    HAS_TERMINAL = "HAS_TERMINAL"
    IS_IN_COMPARTMENT = "IS_IN_COMPARTMENT"
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
    HAS_RESOURCE = "HAS_RESOURCE"
    HAS_ANNOTATION = "HAS_ANNOTATION"
    HAS_EXISTENCE = "HAS_EXISTENCE"
    HAS_LOCATION = "HAS_LOCATION"
    HAS_LABEL = "HAS_LABEL"
    HAS_MAP = "HAS_MAP"
    # Relationships shortcut
    CATALYSIS_SHORTCUT = "CATALYZES"
    MODULATION_SHORTCUT = "MODULATES"
    STIMULATION_SHORTCUT = "STIMULATES"
    INHIBITION_SHORTCUT = "INHIBITS"
    NECESSARY_STIMULATION_SHORTCUT = "NECESSARY_STIMULATES"
    CONSUMPTION_SHORTCUT = "CONSUMES"
    PRODUCTION_SHORTCUT = "PRODUCES"
    LOGIC_ARC_SHORTCUT = "HAS_INPUT"
    EQUIVALENCE_ARC_SHORTCUT = "HAS_INPUT"
    NEGATIVE_INFLUENCE_SHORTCUT = "NEGATIVELY_INFLUENCES"
    POSITIVE_INFLUENCE_SHORTCUT = "POSITIVELY_INFLUENCES"
    UNKNOWN_INFLUENCE_SHORTCUT = "INFLUENCES"
    ASSIGNMENT_SHORTCUT = "IS_ASSIGNED_TO"
    INTERACTION_SHORTCUT = "INTERACTS_WITH"
    ABSOLUTE_INHIBITION_SHORTCUT = "ABSOLUTE_INHIBITS"
    ABSOLUTE_STIMULATION_SHORTCUT = "ABSOLUTE_STIMULATES"
    # Property names
    LABEL_PROP = "label"
    ID = "id"
    NAME = "name"
    CLASS = "class"
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
    CARDINALITY_PROP = "cardinality"
    UI_TYPE = "type"
    ORDER = "order"
    NOTES = "notes"
    EXTENSION = "extension"
    QUALIFIER_URI = "qualifier_uri"
    QUALIFIER = "qualifier"
    QUALIFIER_NS = "qualifier_ns"
    URI = "uri"
    COLLECTION_NS = "collection_ns"
    TEXT = "text"


class OntologyPD(Enum):
    """The ontology for PD"""

    SUBUNIT = set(
        [
            "UNSPECIFIED_ENTITY_SUBUNIT",
            "SIMPLE_CHEMICAL_SUBUNIT",
            "MACROMOLECULE_SUBUNIT",
            "NUCLEIC_ACID_FEATURE_SUBUNIT",
            "COMPLEX_SUBUNIT",
            "SIMPLE_CHEMICAL_MULTIMER_SUBUNIT",
            "MACROMOLECULE_MULTIMER_SUBUNIT",
            "NUCLEIC_ACID_FEATURE_MULTIMER_SUBUNIT",
            "COMPLEX_MULTIMER_SUBUNIT",
            "PHENOTYPE_SUBUNIT",
        ]
    )
    AUXILLIARY_UNIT = SUBUNIT | set(
        ["STATE_VARIABLE", "UNIT_OF_INFORMATION", "CARDINALITY", "TERMINAL"]
    )
    MULTIMER = set(
        [
            "SIMPLE_CHEMICAL_MULTIMER",
            "MACROMOLECULE_MULTIMER",
            "NUCLEIC_ACID_FEATURE_MULTIMER",
            "COMPLEX_MULTIMER",
        ]
    )
    EPN = MULTIMER | set(
        [
            "UNSPECIFIED_ENTITY",
            "SIMPLE_CHEMICAL",
            "MACROMOLECULE",
            "NUCLEIC_ACID_FEATURE",
            "COMPLEX",
            "SOURCE_AND_SINK",
            "PERTURBING_AGENT",
        ]
    )
    STOICHIOMETRIC_PROCESS = set(
        [
            "GENERIC_PROCESS",
            "OMITTED_PROCESS",
            "UNCERTAIN_PROCESS",
            "ASSOCIATION",
            "DISSOCIATION",
        ]
    )
    PROCESS = STOICHIOMETRIC_PROCESS | set(["PHENOTYPE"])
    STIMULATION = set(["STIMULATION", "NECESSARY_STIMULATION", "CATALYSIS"])
    INHIBITION = set(["INHIBITION"])
    MODULATION = STIMULATION | INHIBITION | set(["MODULATION"])
    FLUX_ARC = set(["CONSUMPTION", "PRODUCTION"])
    LOGICAL_OPERATOR = set(["AND", "OR", "NOT", "DELAY"])
    GLYPH = (
        EPN
        | AUXILLIARY_UNIT
        | PROCESS
        | LOGICAL_OPERATOR
        | set(["COMPARTMENT", "EQUIVALENCE", "SUBMAP", "TAG"])
    )
    ARC = MODULATION | FLUX_ARC | set(["LOGIC_ARC", "EQUIVALENCE_ARC"])


class OntologyAF(Enum):
    """The ontology for AF"""

    ACTIVITY = set(["BIOLOGICAL_ACTIVITY", "PHENOTYPE"])
    AUXILLIARY_UNIT = set(["UNIT_OF_INFORMATION", "TERMINAL"])
    INFLUENCE = set(
        [
            "POSITIVE_INFLUENCE",
            "NEGATIVE_INFLUENCE",
            "UNKNOWN_INFLUENCE",
            "NECESSARY_STIMULATION",
        ]
    )
    LOGICAL_OPERATOR = set(["AND", "OR", "NOT", "DELAY"])
    GLYPH = (
        AUXILLIARY_UNIT
        | LOGICAL_OPERATOR
        | ACTIVITY
        | set(["COMPARTMENT", "SUBMAP", "TAG"])
    )
    ARC = INFLUENCE | set(["LOGIC_ARC", "EQUIVALENCE_ARC"])


class OntologyER(Enum):
    """The ontology for ER"""

    STATE_VARIABLE = set(["EXISTENCE", "LOCATION", "STATE_VARIABLE"])
    AUXILLIARY_UNIT = STATE_VARIABLE | set(
        ["UNIT_OF_INFORMATION", "TERMINAL", "CARDINALITY"]
    )
    STIMULATION = set(
        ["STIMULATION", "NECESSARY_STIMULATION", "ABSOLUTE_STIMULATION"]
    )
    INHIBITION = set(["INHIBITION", "ABSOLUTE_INHIBITION"])
    INFLUENCE = STIMULATION | INHIBITION | set(["MODULATION"])
    LOGICAL_OPERATOR = set(["AND", "OR", "NOT", "DELAY"])
    INTERACTOR = set(["ENTITY", "OUTCOME"])
    ENTITY_NODE = LOGICAL_OPERATOR | INTERACTOR | set(["PERTURBING_AGENT"])
    GLYPH = (
        AUXILLIARY_UNIT
        | LOGICAL_OPERATOR
        | ENTITY_NODE
        | set(
            [
                "SUBMAP",
                "TAG",
                "INTERACTION_GLYPH",
                "VARIABLE_VALUE",
                "PHENOTYPE",
                "IMPLICIT_XOR",
            ]
        )
    )
    ARC = INFLUENCE | set(
        ["ASSIGNMENT", "INTERACTION", "LOGIC_ARC", "EQUIVALENCE_ARC"]
    )
    STATEMENT = set(["ASSIGNMENT", "INTERACTION", "PHENOTYPE"])
    RELATIONSHIP = STATEMENT | INFLUENCE


ontologies = {
    "process description": OntologyPD,
    "activity flow": OntologyAF,
    "entity relationship": OntologyER,
}
