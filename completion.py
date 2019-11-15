class CompletionEnum(Enum):
    MAP = {
        "OWNED_BY": {},
        "OWNS": {
            "HAS_GLYPH": {"multi": True, "recursive": True},
            "HAS_ARC": {"multi": True, "recursive": True}
            "HAS_ARCGROUP": {"multi": True, "recursive": True}
        }
    }
    GLYPH = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
        }
    }
    ARC = "Arc"
    ARCGROUP = "Arcgroup"
    SUBUNIT = "Subunit"
    LOGICAL_OPERATOR = "LogicalOperator"
    COMPARTMENT = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True}
        }
    }
    UNSPECIFIED_ENTITY = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
        }
    }
    SIMPLE_CHEMICAL = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True},
            "HAS_STATE_VARIABLE": {"multi": True, "recursive": True},
        }
    }
    MACROMOLECULE = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True},
            "HAS_STATE_VARIABLE": {"multi": True, "recursive": True},
        }
    }
    NUCLEIC_ACID_FEATURE = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True},
            "HAS_STATE_VARIABLE": {"multi": True, "recursive": True},
        }
    }
    COMPLEX = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True},
            "HAS_STATE_VARIABLE": {"multi": True, "recursive": True},
            "HAS_SUBUNIT": {"multi": True, "recursive": True},
        }
    }
    SIMPLE_CHEMICAL_MULTIMER = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True},
            "HAS_STATE_VARIABLE": {"multi": True, "recursive": True},
        }
    }
    MACROMOLECULE_MULTIMER = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True},
            "HAS_STATE_VARIABLE": {"multi": True, "recursive": True},
        }
    }
    NUCLEIC_ACID_FEATURE_MULTIMER = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True},
            "HAS_STATE_VARIABLE": {"multi": True, "recursive": True},
        }
    }
    COMPLEX_MULTIMER = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True},
            "HAS_STATE_VARIABLE": {"multi": True, "recursive": True},
            "HAS_SUBUNIT": {"multi": True, "recursive": True},
        }
    }
    SOURCE_AND_SINK = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
        }
    }
    PERTURBING_AGENT = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_UNIT_OF_INFORMATION": {"multi": True, "recursive": True},
        }
    }
    PROCESS = {
        "OWNED_BY": {
            "HAS_GLYPH": {"multi": False, "recursive": False}
        },
        "OWNS": {
            "HAS_BBOX": {"multi": False, "recursive": False},
            "HAS_PORT": {"multi": True, "recursive": True},
        }
    }
    OMITTED_PROCESS = "OmittedProcess"
    UNCERTAIN_PROCESS  = "UncertainProcess"
    ASSOCIATION = "Association"
    DISSOCIATION  = "Dissociation"
    PHENOTYPE = "Phenotype"
    OR = "OrOperator"
    AND = "AndOperator"
    NOT = "NotOperator"
    DELAY = "Delay"
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
    CATALYSIS  = "Catalysis"
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


