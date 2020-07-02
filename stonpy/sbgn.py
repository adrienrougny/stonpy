from enum import Enum

from functools import total_ordering

def read(file_name):
    sbgn = libsbgn.parse(file_name, silence=True)
    return cast_map(sbgn.get_map())

def cast_map(old):
    dids = {}
    new = Map()
    new.language = Language[old.get_language().name]
    for g in old.get_glyph():
        if g.get_class().name == "COMPARTMENT":
            newg = cast_glyph(g, dids)
            new.add_glyph(newg)
            dids[g.get_id()] = newg
    for g in old.get_glyph():
        if g.get_class().name != "COMPARTMENT":
            newg = cast_glyph(g, dids)
            new.add_glyph(newg)
            dids[g.get_id()] = newg
    for a in old.get_arcgroup():
        new.add_arcgroup(cast_arcgroup(a, dids))
    for a in old.get_arc():
        if a.get_class().name == "INTERACTION" \
                or a.get_class().name == "ASSIGNMENT":
            newa = cast_arc(a, dids)
            new.add_arc(newa)
            dids[a.get_id()] = newa
    for a in old.get_arc():
        if a.get_class().name != "INTERACTION" \
                and a.get_class().name != "ASSIGNMENT":
            newa = cast_arc(a, dids)
            new.add_arc(newa)
            dids[a.get_id()] = newa
    return new

def cast_glyph(old, dids):
    new = Glyph()
    new.id = old.get_id()
    new.clazz = GlyphClass[old.get_class().name]
    if old.get_label() is not None:
        new.label = cast_label(old.get_label())
    if old.get_clone() is not None:
        new.clone = cast_clone(old.get_clone())
    if old.get_bbox() is not None:
        new.bbox = cast_bbox(old.get_bbox())
    # if old.get_orientation() is not None:
        # new.orientation = Orientation[old.get_orientation().name]
    if old.orientation is not None: # two previous lines do not work because of a libsbgn bug
        new.orientation = Orientation(old.orientation)
    for g in old.get_glyph():
        newg = cast_glyph(g, dids)
        new.add_glyph(newg)
        dids[g.get_id()] = newg
    for p in old.get_port():
        newp = cast_port(p)
        new.add_port(newp)
        dids[p.get_id()] = newp
    if old.get_compartmentRef() is not None:
        new.compartmentRef = dids[old.get_compartmentRef()]
    if old.get_compartmentOrder() is not None:
        new.compartmentOrder = old.get_compartmentOrder()
    if old.get_entity() is not None:
        new.entity = EntityClass(old.get_entity().name)
    return new

def cast_arc(old, dids):
    new = Arc()
    new.id = old.get_id()
    new.clazz = ArcClass[old.get_class().name]
    print(old.get_id(), old.get_source(), old.get_target())
    new.source = dids[old.get_source()]
    new.target = dids[old.get_target()]
    new.start = cast_start(old.get_start())
    new.end = cast_end(old.get_end())
    for n in old.get_next():
        new.add_next(cast_next(n))
    for p in old.get_port():
        new.add_port(cast_port(p))
    for g in old.get_glyph():
        new.add_glyph(cast_glyph(g))
    return new

def cast_arcgroup(old, dids):
    new = Arcgroup()
    new.clazz = ArcgroupClass[old.get_class().name]
    for g in old.get_glyph():
        newg = cast_glyph(g, dids)
        new.add_glyph(newg)
        dids[g.get_id()] = newg
    for a in old.get_arc():
        newa = cast_glyph(a, dids)
        new.add_arc(newa)
        dids[a.get_id()] = newa
    return new

def cast_label(old):
    new = Label()
    if old.get_bbox() is not None:
        new.bbox = cast_bbox(old.get_bbox())
    new.text = old.get_text()
    return new

def cast_bbox(old):
    new = Bbox()
    new.x = old.get_x()
    new.y = old.get_y()
    new.w = old.get_w()
    new.h = old.get_h()
    return new

def cast_clone(old):
    new = Clone()
    if old.get_label():
        new.label = cast_label(old.get_label())
    return new

def cast_point(old):
    new = Point()
    new.x = old.get_x()
    new.y = old.get_y()
    return new

def cast_port(old):
    new = Port()
    new.id = old.get_id()
    new.x = old.get_x()
    new.y = old.get_y()
    return new

def cast_end(old):
    new = End()
    new.x = old.get_x()
    new.y = old.get_y()
    # for point in old.get_point():
    #     new.add_point(cast_point(point))
    return new

def cast_start(old):
    new = Start()
    new.x = old.get_x()
    new.y = old.get_y()
    # for point in old.get_point():
    #     new.add_point(cast_point(point))
    return new

def cast_next(old):
    new = Next()
    new.x = old.get_x()
    new.y = old.get_y()
    # for point in old.get_point():
    #     new.add_point(cast_point(point))
    return new

@total_ordering
class Map(object):
    def __init__(
            self, id=None, language=None, glyphs=None, arcs=None,
            arcgroups=None):
        self.id = id
        self.language = language
        self.glyphs = glyphs if glyphs is not None else []
        self.arcs = arcs if arcs is not None else []
        self.arcgroups = arcgroups if arcgroups is not None else []

    def add_glyph(self, glyph):
        self.glyphs.append(glyph)

    def add_arc(self, arc):
        self.arcs.append(arc)

    def add_arcgroup(self, arcgroup):
        self.arcgroups.append(arcgroup)

    def to_tuple(self):
        return (self.language, sorted(self.glyphs),
            sorted(self.arcs), sorted(self.arcgroups))

    def __eq__(self, other):
        return  isinstance(other, Map) and self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        if isinstance(other, Map):
            return self.to_tuple() < other.to_tuple()
        else:
            return TypeError


@total_ordering
class Glyph(object):
    def __init__(
            self, id=None, clazz=None, label=None, clone=None, bbox=None,
            orientation=None, glyphs=None, ports=None, compartmentRef=None,
            compartmentOrder=None, entity=None):
        self.id = id
        self.clazz = clazz
        self.label = label
        self.clone = clone
        self.bbox = bbox
        self.orientation = orientation
        self.glyphs = glyphs if glyphs is not None else []
        self.ports = ports if ports is not None else []
        self.compartmentRef = compartmentRef
        self.compartmentOrder = compartmentOrder
        self.entity = entity

    @property
    def svs(self):
        return [g for g in self.glyphs if g.clazz.name == "STATE_VARIABLE"]

    @property
    def uis(self):
        return [g for g in self.glyphs
            if g.clazz.name == "UNIT_OF_INFORMATION"]

    @property
    def tags(self):
        return [g for g in self.glyphs if g.clazz.name == "TAG"]

    @property
    def subunits(self):
        return [
            g for g in self.glyphs if g.clazz.name != "TAG"
                and g.clazz.name != "STATE_VARIABLE"
                and g.clazz.name != "UNIT_OF_INFORMATION"
            ]

    def add_port(self, port):
        self.ports.append(port)
        port.owner = self

    def add_glyph(self, glyph):
        self.glyphs.append(glyph)
        glyph.owner = self

    def to_tuple(self):
        return (self.clazz, self.label,
            self.clone, self.bbox,
            self.orientation, sorted(self.glyphs),
            sorted(self.ports), self.compartmentRef,
            self.compartmentOrder)

    def __eq__(self, other):
        return isinstance(other, Glyph) and self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        if isinstance(other, Glyph):
            return self.to_tuple() < other.to_tuple()
        else:
            return TypeError


@total_ordering
class Arc(object):
    def __init__(
            self, id=None, clazz=None, source=None, target=None, start=None,
            end=None, nexts=None, glyphs=None, ports=None):
        self.id = id
        self.clazz = clazz
        self.source = source
        self.target = target
        self.start = start
        self.end = end
        self.nexts = nexts if nexts is not None else []
        self.glyphs = glyphs if glyphs is not None else []
        self.ports = ports if ports is not None else []

    def add_port(self, port):
        self.ports.append(port)
        port.owner = self

    def add_glyph(self, glyph):
        self.glyphs.append(glyph)
        glyph.owner = self

    def add_next(self, next_):
        self.nexts.append(next_)

    @property
    def cardinality(self):
        for g in self.glyphs:
            if g.clazz.name == "CARDINALITY":
                return g
        return None

    def to_tuple(self):
        return (self.clazz, self.source,
            self.target, self.start, self.end, sorted(self.nexts),
            sorted(self.ports), sorted(self.glyphs))

    def __eq__(self, other):
        return isinstance(other, Arc) and self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        if isinstance(other, Arc):
            return self.to_tuple() < other.to_tuple()
        else:
            return TypeError

@total_ordering
class Arcgroup(object):
    def __init__(self, clazz=None, glyphs=None, arcs=None):
        self.clazz = clazz
        self.glyphs = glyphs if glyphs is not None else []
        self.arcs = arcs if arcs is not None else []

    def add_glyph(self, glyph):
        self.glyphs.append(glyph)

    def add_arc(self, arc):
        self.arcs.append(arc)

    def to_tuple(self):
        return (sorted(self.glyphs), sorted(self.arcs))

    def __eq__(self, other):
        return isinstance(other, Arcgroup) and self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        if isinstance(other, Arcgroup):
            return self.to_tuple() < other.to_tuple()
        else:
            return TypeError


@total_ordering
class Label(object):
    def __init__(self, text=None, bbox=None):
        self.text = text
        self.bbox = bbox

    def to_tuple(self):
        return (self.text, self.bbox)

    def __eq__(self, other):
        return isinstance(other, Label) and  self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        if isinstance(other, Label):
            return self.to_tuple() < other.to_tuple()
        else:
            return TypeError


@total_ordering
class Bbox(object):
    def __init__(self, x=None, y=None, w=None, h=None):
        self.x = x
        self.y = y
        self.h = h
        self.w = w

    def to_tuple(self):
        return (self.x, self.y, self.w, self.h)

    def __eq__(self, other):
        return isinstance(other, Bbox) and self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        if isinstance(other, Bbox):
            return self.to_tuple() < other.to_tuple()
        else:
            return TypeError


@total_ordering
class Clone(object):
    def __init__(self, label=None):
        self.label = label

    def to_tuple(self):
        return (self.label)

    def __eq__(self, other):
        return isinstance(other, Clone) and self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        if isinstance(other, Clone):
            return self.to_tuple() < other.to_tuple()
        else:
            return TypeError


@total_ordering
class Point(object):
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def to_tuple(self):
        return (self.x, self.y)

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__ and self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        if isinstance(other, Point):
            return self.to_tuple() < other.to_tuple()
        else:
            return TypeError


class Port(Point):
    def __init__(self, id=None, x=None, y=None, owner=None):
        super().__init__(x, y)
        self.id = id
        self.owner = owner


class ArcPoint(Point):
    def __init__(self, x=None, y=None, points=None):
        super().__init__(x, y)
        self.points = points if points is not None else []

    def add_point(self, point):
        self.points.append(point)

class End(ArcPoint):
    pass


class Start(ArcPoint):
    pass


class Next(ArcPoint):
    pass

# Following enums are copied from lisbgn-python, written by Matthias König


class Language(Enum):
    """
    Enum representing the three languages of SBGN.
    """
    AF = "activity flow"
    ER = "entity relationship"
    PD = "process description"

    def __lt__(self, other):
        return self.value < other.value


class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"

    def __lt__(self, other):
        return self.value < other.value



class GlyphClass(Enum):
    """
    Enumeration with all possible values for the class attribute of Glyphs in SBGN-ML.
    This includes both top-level glyphs and sub-glyphs.
    """
    # glyphs
    UNSPECIFIED_ENTITY = "unspecified entity"
    SIMPLE_CHEMICAL = "simple chemical"
    MACROMOLECULE = "macromolecule"
    NUCLEIC_ACID_FEATURE = "nucleic acid feature"
    SIMPLE_CHEMICAL_MULTIMER = "simple chemical multimer"
    MACROMOLECULE_MULTIMER = "macromolecule multimer"
    NUCLEIC_ACID_FEATURE_MULTIMER = "nucleic acid feature multimer"
    COMPLEX = "complex"
    COMPLEX_MULTIMER = "complex multimer"
    SOURCE_AND_SINK = "source and sink"
    PERTURBATION = "perturbation"
    BIOLOGICAL_ACTIVITY = "biological activity"
    PERTURBING_AGENT = "perturbing agent"
    COMPARTMENT = "compartment"
    SUBMAP = "submap"
    TAG = "tag"
    TERMINAL = "terminal"
    PROCESS = "process"
    OMITTED_PROCESS = "omitted process"
    UNCERTAIN_PROCESS = "uncertain process"
    ASSOCIATION = "association"
    DISSOCIATION = "dissociation"
    PHENOTYPE = "phenotype"
    AND = "and"
    OR = "or"
    NOT = "not"
    STATE_VARIABLE = "state variable"
    UNIT_OF_INFORMATION = "unit of information"
    # @deprecated
    # By mistake, we used STOICHIOMETRY in instead of {@link CARDINALITY} in LibSBGN M1.
    # We keep this constant here to support reading old documents.
    # This constant will be removed in LibSBGN M3.
    STOICHIOMETRY = "stoichiometry"
    ENTITY = "entity"
    OUTCOME = "outcome"
    # @deprecated
    # Observable was used in old versions of SBGN, but has been replaced with {@link PHENOTYPE}.
    # However, because older versions of SBGN are supported by LibSBGN, this constant will never be removed.
    OBSERVABLE = "observable"
    INTERACTION = "interaction"
    ANNOTATION = "annotation"
    VARIABLE_VALUE = "variable value"
    IMPLICIT_XOR = "implicit xor"
    DELAY = "delay"
    EXISTENCE = "existence"
    LOCATION = "location"
    CARDINALITY = "cardinality"

    def __lt__(self, other):
        return self.value < other.value

class ArcClass(Enum):
    """
    Enumeration with all possible values for the class attribute of Arcs in SBGN-ML.
    """
    PRODUCTION = "production"
    CONSUMPTION = "consumption"
    CATALYSIS = "catalysis"
    MODULATION = "modulation"
    STIMULATION = "stimulation"
    INHIBITION = "inhibition"
    ASSIGNMENT = "assignment"
    INTERACTION = "interaction"
    ABSOLUTE_INHIBITION = "absolute inhibition"
    ABSOLUTE_STIMULATION = "absolute stimulation"
    POSITIVE_INFLUENCE = "positive influence"
    NEGATIVE_INFLUENCE = "negative influence"
    UNKNOWN_INFLUENCE = "unknown influence"
    EQUIVALENCE_ARC = "equivalence arc"
    NECESSARY_STIMULATION = "necessary stimulation"
    LOGIC_ARC = "logic arc"

    def __lt__(self, other):
        return self.value < other.value

class Arcgroup(Enum):
    """
    Enumeration with all possible values for the class attribute of Arcs in SBGN-ML.
    """
    INTERACTION = "interaction"

    def __lt__(self, other):
        return self.value < other.value


