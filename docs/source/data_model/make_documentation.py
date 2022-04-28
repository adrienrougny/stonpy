import os
from csv import reader, list_dialects
from dataclasses import dataclass, field
from typing import Optional

CSV_SEP = ";"
CSV_ENDLINE = "\n"
CSV_QUOTE = '"'
NODES_FILE = "nodes.csv"
RELATIONSHIPS_FILE = "relationships.csv"
COMPLETION_FILE = "completion_rules.csv"
BUILD_DIR = "build/"
SBGN_LANGUAGES = ["PD", "AF", "ER"]

@dataclass
class Model(object):
    nodes: Optional[list["Node"]] = field(default_factory=list)
    relationships: Optional[list["Relationship"]] = field(default_factory=list)
    completion_rules: Optional[list["CompletionRule"]] = field(default_factory=list)

    def get_node(self, label, language):
        for node in self.nodes:
            if node.label == label and node.language == language:
                return node
        return None

@dataclass
class Relationship(object):
    _model: Optional[Model] = None
    description: Optional[str] = None
    language: Optional[str] = None
    rtype: Optional[str] = None
    source_types: list[str, str] = field(default_factory=list)
    target_types: list[str, str] = field(default_factory=list)
    source_arity: Optional[str] = None
    target_arity: Optional[str] = None

    def all_source_types(self, non_abstract_only=False):
        source_types = []
        for source_type in self.source_types:
            node = self._model.get_node(source_type, self.language)
            if not non_abstract_only or not node.abstract:
                source_types.append(node.label)
            source_types += [descendant.label for descendant in node.descendants(non_abstract_only=non_abstract_only)]
        return source_types

    def all_target_types(self, non_abstract_only=False):
        target_types = []
        for target_type in self.target_types:
            node = self._model.get_node(target_type, self.language)
            if not non_abstract_only or not node.abstract:
                target_types.append(node.label)
            target_types += [descendant.label for descendant in node.descendants(non_abstract_only=non_abstract_only)]
        return target_types

    def to_html_for_node_page(self, with_source=True, with_target=True, non_abstract_only=False):
        if with_source:
            source_types = self.all_source_types(non_abstract_only=non_abstract_only)
        else:
            source_types = None
        if with_target:
            target_types = self.all_target_types(non_abstract_only=non_abstract_only)
        else:
            target_types = None
        s = ""
        if source_types is not None:
            if len(source_types) <= 3:
                s += f" {' or '.join([get_a_link(source_type) for source_type in source_types])}"
            else:
                s += f" [...]"
        s += f"-({self.source_arity})-{get_a_link(self.rtype)}-({self.target_arity})->"
        if target_types is not None:
            if len(target_types) <= 3:
                s += f" {' or '.join([get_a_link(target_type) for target_type in target_types])}"
            else:
                s += " [...]"
        return s

    def to_html(self):
        s = f"<div class='relationship' id='{self.rtype}'>\n"
        s += f"<h3>{self.description}</h3>\n"

        s += f"<h4>Type</h4>\n"
        s += f"<ul>\n"
        s += f"<li>{self.rtype}</i></li>\n"
        s += f"</ul>\n"

        s += f"<h4>Source arity</h4>\n"
        s += f"<ul>\n"
        if self.source_arity == "*":
            source_arity = "any"
        else:
            source_arity = self.source_arity
        s += f"<li>{source_arity}</i></li>\n"
        s += f"</ul>\n"

        s += f"<h4>Source types</h4>\n"
        s += f"<ul>\n"
        for source_type in self.all_source_types(non_abstract_only=True):
            s += f"<li>{get_a_link(source_type)}</i></li>\n"
        s += f"</ul>\n"

        s += f"<h4>Target arity</h4>\n"
        s += f"<ul>\n"
        if self.target_arity == "*":
            target_arity = "any"
        else:
            target_arity = self.target_arity
        s += f"<li>{source_arity}</i></li>\n"
        s += f"</ul>\n"

        s += f"<h4>Target types</h4>\n"
        s += f"<ul>\n"
        for target_type in self.all_target_types(non_abstract_only=True):
            s += f"<li>{get_a_link(target_type)}</i></li>\n"
        s += f"</ul>\n"

        s += "</div>"
        return s


@dataclass
class Node(object):
    _model: Optional[Model] = None
    description: Optional[str] = None
    abstract: bool = False
    language: Optional[str] = None
    label: Optional[str] = None
    inherits: Optional["Node"] = None
    comments: Optional[str] = None
    attributes: list[str] = field(default_factory=list)

    def outgoing_relationships(self):
        outgoing_relationships = []
        for relationship in self._model.relationships:
            if self.language == relationship.language and self.label in relationship.all_source_types():
                outgoing_relationships.append(relationship)
        return outgoing_relationships

    def ingoing_relationships(self):
        ingoing_relationships = []
        for relationship in self._model.relationships:
            if self.language == relationship.language and self.label in relationship.all_target_types():
                ingoing_relationships.append(relationship)
        return ingoing_relationships

    def inherited_attributes(self):
        if self.inherits is not None:
            return self._inherits_node().all_attributes()
        else:
            return []

    def inherited_labels(self):
        if self.inherits is not None:
            return self._inherits_node().all_labels()
        else:
            return []

    def inherited_ingoing_relationships(self):
        if self.inherits is not None:
            return self._inherits_node().all_ingoing_relationships()
        else:
            return []

    def inherited_outgoing_relationships(self):
        if self.inherits is not None:
            return self._inherits_node().all_outgoing_relationships()
        else:
            return []

    def _inherits_node(self):
        return self._model.get_node(self.inherits, self.language)

    def all_labels(self):
        return [self.label] + self.inherited_labels()

    def all_attributes(self):
        return self.attributes + self.inherited_attributes()

    def all_ingoing_relationships(self):
        return self.ingoing_relationships() + self.inherited_ingoing_relationships()

    def all_outgoing_relationships(self):
        return self.outgoing_relationships() + self.inherited_outgoing_relationships()

    def descendants(self, non_abstract_only=False):
        descendants = []
        for node in self._model.nodes:
            if node.inherits == self.label and node.language == self.language:
                descendants.append(node)
                descendants += node.descendants(non_abstract_only=non_abstract_only)
        if non_abstract_only:
            descendants = [node for node in descendants if not node.abstract]
        return descendants

    def to_html(self):
        s = f"<div class='node' id='{self.label}'>\n"
        s += f"<h3>{self.description}</h3>\n"

        s += f"<h4>Labels</h4>\n"
        s += f"<ul>\n"
        for label in self.all_labels():
            node = self._model.get_node(label, self.language)
            if node.abstract:
                s += f"<li><i>{label}</i></li>\n"
            else:
                s += f"<li>{label}</li>\n"
        s += f"</ul>\n"

        s += f"<h4>Attributes</h4>\n"
        s += f"<ul>\n"
        for attribute in self.all_attributes():
            s += f"<li>{attribute}</li>\n"
        s += f"</ul>\n"

        s += f"<h4>Relationships</h4>\n"

        s += f"<ul>\n"
        for relationship in self.outgoing_relationships():
            s += f"<li>. {relationship.to_html_for_node_page(with_target=True, with_source=False, non_abstract_only=True)}</li>\n"
        s += f"</ul>\n"

        s += f"<ul>\n"
        for relationship in self.ingoing_relationships():
            s += f"<li>{relationship.to_html_for_node_page(with_target=False, with_source=True, non_abstract_only=True)} .</li>\n"
        s += f"</ul>\n"

        if self.comments is not None:
            s += "<h4>Comments</h4>\n"
            s += f"{self.comments}"
        s += "</div>"
        return s

@dataclass
class CompletionRule(object):
    _model: Optional[Model] = None
    node: Optional[str] = None
    rtype: Optional[str] = None
    node_role: Optional[str] = None
    recursive: Optional[str] = None

    def to_html(self):
        s = "<tr>\n"
        for attr in ["node", "rtype", "node_role", "recursive"]:
            s += f"<td>{getattr(self, attr)}</td>\n"
        s += "</tr>\n"
        return s

def make_model():
    model = Model()
    nodes_table = return_table_from_csv_file(NODES_FILE)
    for node_row in nodes_table:
        nodes = make_nodes_from_row(node_row)
        for node in nodes:
            model.nodes.append(node)
            node._model = model
    relationships_table = return_table_from_csv_file(RELATIONSHIPS_FILE)
    for relationship_row in relationships_table:
        relationships = make_relationships_from_row(relationship_row)
        for relationship in relationships:
            model.relationships.append(relationship)
            relationship._model = model
    completion_rules_table = return_table_from_csv_file(COMPLETION_FILE)
    for completion_rule_row in completion_rules_table:
        completion_rule = make_completion_rule_from_row(completion_rule_row)
        model.completion_rules.append(completion_rule)
        completion_rule._model = model

    return model

def make_nodes_from_row(node_row):
    nodes = []
    languages = node_row["Language"]
    if languages == "All":
        languages = SBGN_LANGUAGES
    else:
        languages = languages.split(", ")
    description = node_row["Description"]
    attributes = node_row["Attributes"]
    comments = node_row["Comment"]
    label = node_row["Label"]
    inherits = node_row["Inherits"]
    abstract = node_row["Abstract"]
    if abstract == "1":
        abstract = True
    else:
        abstract = False
    for language in languages:
        node = Node()
        node.description = description
        node.language = language
        if attributes is not None:
            node.attributes = attributes
        node.comments = comments
        node.label = label
        node.inherits = inherits
        node.abstract = abstract
        nodes.append(node)
    return nodes

def make_relationships_from_row(relationship_row):
    relationships = []
    languages = relationship_row["Language"]
    if languages == "All":
        languages = SBGN_LANGUAGES
    else:
        languages = languages.split(", ")
    rtype = relationship_row["Relationship"]
    description = rtype
    for language in languages:
        relationship = Relationship()
        relationship.language = language
        relationship.description = description
        relationship.rtype = rtype
        source_types = relationship_row[f"Source {language}"]
        assert source_types is not None
        source_types = source_types.split(" or ")
        l = source_types[-1].split(" ")
        source_types[-1] = l[0]
        source_arity = l[1][1:-1]
        relationship.source_types = source_types
        relationship.source_arity = source_arity
        target_types = relationship_row[f"End {language}"]
        assert target_types is not None
        target_types = target_types.split(" or ")
        l = target_types[-1].split(" ")
        target_types[-1] = l[0]
        target_arity = l[1][1:-1]
        relationship.target_types = target_types
        relationship.target_arity = target_arity
        relationships.append(relationship)
    return relationships

def make_completion_rule_from_row(completion_rule_row):
    completion_rule = CompletionRule()
    completion_rule.node = completion_rule_row["Node"]
    completion_rule.node_role = completion_rule_row["Node role"]
    completion_rule.rtype = completion_rule_row["Relationship"]
    completion_rule.recursive = completion_rule_row["Recursive"]
    return completion_rule

def _unquote(s):
    return s.lstrip(CSV_QUOTE).rstrip(CSV_QUOTE)


def return_table_from_csv_file(file_name):
    table = [] # list of dicts, keys are the header
    with open(file_name) as f:
        line = f.readline()
        line = line.rstrip(CSV_ENDLINE)
        cells = [_unquote(cell) for cell in line.split(CSV_SEP)]
        header = []
        types = []
        for cell in cells:
            header.append(" ".join(cell.split(" ")[:-1]))
            types.append(cell.split(" ")[-1][1:-1])
        file_content = f.read()
    in_cell = False
    cell = ""
    n_cell = 0
    row = {}
    for c in file_content:
        if c == CSV_QUOTE:
            if in_cell:
                in_cell = False
                if multiline_cell:
                    cell = cell.split(CSV_ENDLINE)
                if types[n_cell] == "list" and not isinstance(cell, list):
                    cell = [cell]
                row[header[n_cell]] = cell
            else:
                in_cell = True
                multiline_cell = False
        elif c == CSV_ENDLINE:
            if in_cell:
                multiline_cell = True
                cell += c
            else:
                n_cell = 0
                table.append(row)
                for key in header:
                    if key not in row:
                        row[key] = None
                row = {}
                cell = ""
        elif c == CSV_SEP:
            n_cell += 1
            cell = ""
        else:
            cell += c
    return table

def get_file_name(element_type, language, with_base_dir=False):
    if language is not None:
        file_name = f"{element_type}_{language}.html"
    else:
        file_name = f"{element_type}.html"
    if with_base_dir:
        return os.path.join(BUILD_DIR, file_name)
    else:
        return file_name

def get_a_link(element, base_url=None):
    if base_url is None:
        base_url = ""
    url = f"{base_url}#{element}"
    s = f"<a href='{url}'>{element}</a>"
    return s

def make_nodes_page(language, model):
    nodes = sorted(model.nodes, key=lambda node: node.label)
    file_name = get_file_name("nodes", language, with_base_dir=True)
    with open(file_name, "w") as f:
        f.write("<!DOCTYPE html>\n<html>\n<body>\n")
        f.write("<h2>Nodes</h2>\n")
        for node in nodes:
            if node.language == language and not node.abstract:
                f.write(node.to_html())
                f.write("\n")
        f.write("</body>\n</html>")

def make_relationships_page(language, model):
    file_name = get_file_name("relationships", language, with_base_dir=True)
    with open(file_name, "w") as f:
        # f.write("<!DOCTYPE html>\n<html>\n<body>\n")
        f.write("<h2>Relationships</h2>\n")
        for relationship in model.relationships:
            if relationship.language == language:
                f.write(relationship.to_html())
                f.write("\n")
        f.write("</body>\n</html>")

def make_completion_page(model):
    file_name = get_file_name("completion", None, with_base_dir=True)
    with open(file_name, "w") as f:
        # f.write("<!DOCTYPE html>\n<html>\n<body>\n")
        # f.write("<h2>Relationships</h2>\n")
        # f.write("<h2>Nodes</h2>\n")
        f.write("<table>\n")
        f.write("<tr>\n")
        for attr in ["Node", "Relationship type", "Node role", "Recursive"]:
            f.write(f"<td><b>{attr}</b></td>\n")
        f.write("</tr>\n")
        for completion_rule in model.completion_rules:
            f.write(completion_rule.to_html())
            f.write("\n")
        f.write("</table>\n")
        # f.write("</body>\n</html>")

if __name__ == "__main__":
    os.makedirs(BUILD_DIR, exist_ok=True)
    model = make_model()
    for language in SBGN_LANGUAGES:
        make_nodes_page(language, model)
        make_relationships_page(language, model)
        make_completion_page(model)
