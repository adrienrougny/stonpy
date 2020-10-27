import os.path

import libsbgnpy.libsbgn as libsbgn

from py2neo import Graph

import stonpy.utils as utils
import stonpy.converter as converter
import stonpy.completer as completer
from stonpy.model import STONEnum

class STON(object):
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri
        self.user = user
        self.password = password
        self.graph = Graph(uri = uri, user = user, password = password)
        # self.graph.run(
        #     'CREATE CONSTRAINT ON (m:{}) \
        #     ASSERT m.{} IS UNIQUE'.format(STONEnum["MAP"].value, STONEnum["ID"].value))

    def has_map(self, map_id=None, sbgn_map=None):
        """Check whether the database contains a given SBGN map

        If only a map ID is provided, checks whether the database contains a map with that ID.
        If only an SBGN map is provided, checks whether the database contains this map.
        If both a map ID and an SBGN map are provided, checks whether the database contains this map with this ID.

        :param map_id: the ID of the SBGN map, default is `None`
        :type map_id: `str`, optional
        :param sbgn_map: the SBGN map, either a path to an SBGN-ML file or an SBGN map object, default is `None`
        :type sbgn_map: `str` or `libsbgnpy.libsbgn.map`
        :return: `True` if the database contains the SBGN map, `False` otherwise
        :rtype: `bool`
        """
        if sbgn_map is None:
            if map_id is None:
                return False
            else:
                tx = self.graph.begin()
                query = 'MATCH (m:{} {{{}: "{}"}}) RETURN m'.format(
                    STONEnum["MAP"].value, STONEnum["ID"].value, map_id)
                res = tx.evaluate(query)
                tx.commit()
                if res is None:
                    return False
                else:
                    return True
        else:
            if isinstance(sbgn_map, str):
                if os.path.isfile(sbgn_map):
                    sbgn_map = utils.sbgn_file_to_map(sbgn_map)
            if map_id is not None:
                # query = 'MATCH p=(m:{} {{{}: "{}"}})-[*]->() RETURN p'.format(
                #     STONEnum["MAP"].value, STONEnum["ID"].value, map_id)
                # maps_to_test = list(self.query_to_map(query, merge_records=True, complete=False))
                # FOLLOWING SEEMS FASTER THAN ABOVE, TO TEST FURTHER
                query = 'MATCH (m:{} {{{}: "{}"}}) RETURN m'.format(
                    STONEnum["MAP"].value, STONEnum["ID"].value, map_id)
                maps_to_test = list(self.query_to_map(query, complete=True))


            else:
                maps_to_test = []
                subgraph = converter.map_to_subgraph(sbgn_map)
                # we get the Map node and one node in rel with the Map node
                node = None
                for relationship in subgraph.relationships:
                    if relationship.start_node.has_label(STONEnum["MAP"].value) and \
                            type(relationship).__name__ == STONEnum["HAS_GLYPH"].value:
                        node = relationship.end_node
                        break
                if node is not None: # i.e. the map is not empty
                    query = 'MATCH (m:{})-[{}]->{} RETURN id(m)'.format(
                        STONEnum["MAP"].value, STONEnum["HAS_GLYPH"].value,
                        utils.node_to_cypher(node))
                    cursor = self.graph.run(query)
                    for record in cursor:
                        neo_id = record["id(m)"]
                        # query = 'MATCH p=(m:{})-[*]->() WHERE id(m) = {} \
                        #     RETURN p'.format(STONEnum["MAP"].value, neo_id)
                        # maps_to_test += list(self.query_to_map(query, merge_records=True, complete=False))
                        # FOLLOWING SEEMS FASTER THAN ABOVE, TO TEST FURTHER
                        query = 'MATCH (m:{}) WHERE id(m) = {} \
                            RETURN m'.format(STONEnum["MAP"].value, neo_id)
                        maps_to_test += list(self.query_to_map(query, complete=True))
            for sbgn_map2 in maps_to_test:
                if utils.are_maps_equal(sbgn_map, sbgn_map2[0]):
                    return True
            return False


    def create_map(self, sbgn_map, map_id):
        """Add an SBGN map to the database (with the CREATE instruction).

        :param sbgn_map: the SBGN map, either a path to an SBGN-ML file or an SBGN map object
        :type sbgn_map: `str` or `libsbgnpy.libsbgn.map`
        :param map_id: the ID of the SBGN map
        :type map_id: `str`, optional
        """
        if os.path.isfile(sbgn_map):
            sbgn_file = sbgn_map
            sbgn_map = utils.sbgn_file_to_map(sbgn_file)
        subgraph = converter.map_to_subgraph(sbgn_map, map_id)
        tx = self.graph.begin()
        tx.create(subgraph)
        tx.commit()


    def merge_map(self, sbgn_map, map_id):
        """Add an SBGN map to the database (with the MERGE instruction).

        :param sbgn_map: the SBGN map, either a path to an SBGN-ML file or an SBGN map object
        :type sbgn_map: `str` or `libsbgnpy.libsbgn.map`
        :param map_id: the ID of the SBGN map, default is `None`
        :type map_id: `str`, optional
        """
        if os.path.isfile(sbgn_map):
            sbgn_file = sbgn_map
            sbgn_map = utils.sbgn_file_to_map(sbgn_file)
        subgraph = converter.map_to_subgraph(sbgn_map, map_id)
        tx = self.graph.begin()
        tx.merge(subgraph)
        tx.commit()


    def delete_map(self, map_id=None, sbgn_map=None):
        """Delete an SBGN map from the database.

        If only a map ID is provided, deletes all maps with this ID from the database.
        If only an SBGN map is provided, deletes this map from the database.
        If both a map ID and an SBGN map are provided, deletes the map from the database onlty if it has this ID.

        :param map_id: the ID of the SBGN map, default is `None`
        :type map_id: `str`, optional
        :param sbgn_map: the SBGN map, either a path to an SBGN-ML file or an SBGN map object
        :type sbgn_map: `str` or `libsbgnpy.libsbgn.map`
        """
        if sbgn_map is None and map_id is not None:
            tx = self.graph.begin()
            query = 'MATCH p=(m:{} {{id: "{}"}})-[*]->() \
                    FOREACH(n IN nodes(p) | DETACH DELETE n'.format(
                        STONEnum["MAP"].value, map_id)
            cursor = tx.run(query)
            tx.commit()
        elif sbgn_map is not None:
            if isinstance(sbgn_map, str):
                if os.path.isfile(sbgn_map):
                    sbgn_map = utils.sbgn_file_to_map(sbgn_map)
            subgraph = converter.map_to_subgraph(sbgn_map, map_id=map_id)
            return utils.exists_subgraph(subgraph, self.graph)
        else:
            return False


    def get_map(self, map_id):
        """Retrieve an SBGN map with given ID from the database and returns it.

        If no map is retrieved, returns `None`.
        If multiple maps are retrieved, only the first one is returned.

        :param map_id: the ID of the SBGN map to retrieve
        :type map_id: `str`
        :return: the SBGN map or `None`
        :rtype: `libsbgnpy.libsbgn.map` or `None`
        """
        tx = self.graph.begin()
        query = 'MATCH (m:{} {{id: "{}"}}) \
                CALL apoc.path.subgraphAll(m, {{relationshipFilter: ">"}}) \
                YIELD nodes, relationships \
                RETURN m, nodes, relationships'.format(
                    STONEnum["MAP"].value, map_id)
        cursor = tx.run(query)
        tx.commit()
        for record in cursor:
            subgraph = record["m"]
            for node in record["nodes"]:
                subgraph = subgraph | node
            for relationship in record["relationships"]:
                subgraph = subgraph | relationship
        sbgn_maps = converter.subgraph_to_map(subgraph)
        try:
            return next(sbgn_maps)
        except:
            return None

    def get_map_to_sbgn_file(self, map_id, sbgn_file):
        """Retrieve a map with given ID from the database and write it to the given SBGN-ML file.

        Nothing is done if no map is retrieved.
        If multiple maps are retrieved, only the first one is written to the SBGN-ML file.

        :param map_id: the ID of the SBGN map to retrieve
        :type map_id: `str`
        :param sbgn_file: the path of the the SBGN-ML where to write the retrieved map
        :type sbgn_file: `str`
        """
        sbgn_map = self.get_map(map_id)
        if sbgn_map is not None:
            utils.map_to_sbgn_file(sbgn_map[0], sbgn_file)
        else:
            raise Exception("No map found")


    def query_to_map(self, query, complete=True, merge_records=False, to_top_left=False):
        """Run a cypher query against the database and return the resulting SBGN maps.

        By default, each record resulting from the query is transformed to zero or more SBGN maps, one for each Map node it contains.
        The resulting SBGN maps are then returned one by one. Only distinct SBGN maps are returned.
        When `merge_records` is set to `True`, records are merged before being transformed to SBGN maps.
        When `complete` is set to `True`, records are completed before being transformed; a node or a relationship of a record is always completed by the Map node it belongs to, and by all other nodes and relationships that are ultimately necessary to form a valid map from it.
        Hence if `complete` is set to `True`, at least one valid SBGN map will be returned as long as at least one record contains a node or a relationship.

        :param query: the cypher query
        :type query: `str`
        :param complete: if set to `True`, the nodes and relationships of every record are completed
        :type complete: `bool`, optional
        :param merge_records: if set to `True`, the records of the result are merged
        :type merge_records: `bool`, optional
        :param to_top_left: if set to `True`, each resulting map is moved to the top left of its canvas
        :type to_top_left: bool, optional
        :return: the resulting SBGN maps, under the form of a generator. Each returned element is a tuple of the form (map, map_id).
        :rtype: `Iterator[(`libsbgnpy.libsbgn.map`, `str`)]`
        """
        tx = self.graph.begin()
        cursor = tx.run(query)
        tx.commit()
        subgraphs = set([])
        if merge_records:
            subgraphs.add(cursor.to_subgraph())
        else:
            for record in cursor:
                subgraphs.add(record.to_subgraph())
        i = 0
        for subgraph in subgraphs:
            if complete:
                subgraph = completer.complete_subgraph(subgraph, self.graph)
            sbgn_maps = converter.subgraph_to_map(subgraph)
            for sbgn_map in sbgn_maps:
                if to_top_left:
                    utils.map_to_top_left(sbgn_map[0])
                yield sbgn_map

    def query_to_sbgn_file(
            self, query, sbgn_file, complete=True, merge_records=True, to_top_left=False):
        """Run a cypher query against the database and write the resulting SBGN maps to one or more SBGN-ML files.

        By default, each record resulting from the query is transformed to zero or more SBGN maps, one for each Map node it contains, and each SBGN map is written to a distinct SBGN-ML file.
        When `merge_records` is set to `True`, records are merged before being transformed to SBGN maps.
        When `complete` is set to `True`, records are completed before being transformed; a node or a relationship of a record is always completed by the Map node it belongs to, and by all other nodes and relationships that are ultimately necessary to form a valid map from it.
        Hence if `complete` is set to `True`, at least one valid SBGN map will be written as long as at least one record contains a node or a relationship.
        If there is only one resulting SBGN map, it is written to sbgn_file.
        If there are multiple resulting SBGN maps, each distinct SBGN map is written to a different file formatted as follows: the ith distinct SBGN map is written to file <name>-i.<ext> if `sbgn_file` is of the form <name>.<ext>, and to file `sbgn_file`-i.sbgn otherwise.

        :param query: the cypher query
        :type query: `str`
        :param sbgn_file: the file name where to write the resulting SBGN maps
        :param complete: if set to `True`, the nodes and relationships of every record are completed
        :type complete: bool, optional
        :param merge_records: if set to `True`, the records of the result are merged
        :type merge_records: `bool`, optional
        :param to_top_left: if set to `True`, each resulting map is moved to the top left of its canvas
        :type to_top_left: `bool`, optional
        """

        sbgn_maps = self.query_to_map(
                query, complete=complete, merge_records=merge_records, to_top_left = to_top_left)
        try:
            sbgn_map1 = next(sbgn_maps)
        except:
            pass
        else:
            try:
                sbgn_map2 = next(sbgn_maps)
            except:
                utils.map_to_sbgn_file(sbgn_map1[0], sbgn_file)
            else:
                ext = "sbgn"
                l = sbgn_file.split('.')
                if len(l) > 1:
                    ext = l[-1]
                    root = ''.join(l[:-1])
                else:
                    root = sbgn_file
                utils.map_to_sbgn_file(sbgn_map1[0], "{}_1.{}".format(root, ext))
                utils.map_to_sbgn_file(sbgn_map2[0], "{}_2.{}".format(root, ext))
                for i, sbgn_map in enumerate(sbgn_maps):
                    utils.map_to_sbgn_file(sbgn_map[0], "{}_{}.{}".format(root, i + 3, ext))
