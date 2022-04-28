stonpy's data model
==============

Stonpy’s data model was built following the SBGN-ML data model.
The figure below shows an excerpt of a Neo4j graph built from an SBGN PD map using stonpy.

.. image:: data_model/build/figure_completion.png
   :width: 600

stonpy's data model is as follows:

* Each element of a map, as well as the map itself, is modelled using a graph node

* A graph node is labelled based on the class and superclasses of the element it models

* Attributes of elements are modelled in two ways:

    - attributes that are of a simple type (e.g. a string, a float) are directly set as attributes of the node they belong to

    - attributes that are of an element type (e.g. a (sub-)glyph, an arc) are modelled using a graph relationship between the node modelling the main element and the one modelling the attribute

* Containment of a sub-element inside an element is modelled using a relationship between the node modelling the container element and the one modelling the subelement

* A graph relationship is typed based on the name of the attribute it models or on the type of the contained subelement


In our model, SBGN arcs are modelled using Neo4j nodes.
This structure is required since arcs may contain subelements (such as (sub-)glyphs or ports) that are themselves modelled using nodes.
It has however two drawbacks: first, it moves our model away from the representation of maps itself, where arcs are links between nodes, and makes it less intuitive; second, it makes more difficult for the user to write queries focusing on the biological concepts only, without taking into account their specific representation.
Hence:

* Each arc is additionally modelled using a graph relationship from the node modelling its source to the one modelling its target

* Such a graph relationship is labelled based on the class of the arc it models.
  For example, the relationship modelling a catalysis arc will be labelled with CATALYZES.
  Such relationships are coloured in green in the figure above.

All nodes and relationships used to model maps of each SBGN language are described in details below.

Languages
----------

.. toctree::
   :maxdepth: 4

   stonpy_model_PD
   stonpy_model_AF
   stonpy_model_ER
