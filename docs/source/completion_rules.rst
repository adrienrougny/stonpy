.. _completion:

Completion rules
================

When the result of a query is a subgraph (including a unique node or relationship), it may be completed to form a "complete subgraph" using the :ref:`stonpy-completion`.
The "complete subgraph" can then be converted to a valid SBGN map using the :ref:`stonpy-conversion`.
To form the "complete subgraph", the completion algorithm runs through all relationships and nodes of the input subgraph and completes them (i.e. adds nodes and relationships to the subgraph) following the completion rules described below.
Completion may be recursive: a completion rule may add a node or a relationship to the list of nodes to be completed.

Relationships
-------------

A relationship will be completed by its source and target nodes, which will themselves be completed.
A relationship modelling an arc (such as CATALYZES, INHIBITS, PRODUCES, etc.) will also be completed with the graph node modelling the same arc, which will itself be completed.
For example, in the figure below, the relationship CATALYZES (in green) will be completed by the node labelled Catalysis (also in green), which will itself be completed.

.. image:: data_model/build/figure_completion.png
   :width: 600

Nodes
-----

Nodes are completed following the rules given in the table below.
A completion rule is applied to a given node only if that node includes the label given in the "Node" column.
If it is the case, the Neo4j database will be queried for all relationships having the type given in the "Relationship type" column and having the node as its source or target, depending on the value in the "Node role" column.
The node will be completed with the resulting relationships, which will themselves not be completed.
The node will also be completed with the "other node" of each relationship (i.e. the target node if the node to be completed is the source of the relationship, and the source node otherwise), which will itself be completed if the value of the "Recursive" column is "Yes".

For example, the first rule states that any node that models a glyph (i.e. that includes the "Glyph" label) should be completed with all relationships in the Neo4j graph whose type is "HAS_LABEL" and whose source is the node.
Furthermore, the target of such relationships should also be completed.

.. raw:: html
   :file: data_model/build/completion.html
