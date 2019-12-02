import os.path

import libsbgnpy.libsbgn as libsbgn

from py2neo import Graph

import ston.utils as utils
import ston.converter as converter
import ston.completer as completer
from ston.model import STONEnum

class STON(object):
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri
        self.user = user
        self.password = password
        self.neograph = Graph(uri = uri, user = user, password = password)

    def has_map(self, map_id=None, sbgnmap=None):
        has_map = False
        if map_id is not None:
            tx = self.neograph.begin()
            query = 'MATCH (m:{} {{id: "{}"}}) RETURN m'.format(
                    STONEnum["MAP"].value, map_id)
            res = tx.evaluate(query)
            tx.commit()
            if res is None:
                return False
            else:
                has_map = True
        if isinstance(sbgnmap, str) and os.path.isfile(sbgnmap):
            sbgnmap = utils.sbgnfile_to_map(sbgnmap)
        if isinstance(sbgnmap, libsbgn.map):
            subgraph = converter.map_to_subgraph(sbgnmap)
            has_map = utils.exists_subgraph(subgraph, self.neograph)
        return has_map

    def create_map(self, sbgnmap, map_id=None):
        if os.path.isfile(sbgnmap):
            sbgnfile = sbgnmap
            sbgnmap = utils.sbgnfile_to_map(sbgnfile)
        subgraph = converter.map_to_subgraph(sbgnmap, map_id)
        tx = self.neograph.begin()
        tx.create(subgraph)
        tx.commit()

    def get_map(self, map_id):
        tx = self.neograph.begin()
        query = 'MATCH p=(m:{} {{id: "{}"}})-[*]->() RETURN p'.format(
                STONEnum["MAP"].value, map_id)
        cursor = tx.run(query)
        tx.commit()
        subgraph = cursor.to_subgraph()
        sbgnmaps = converter.subgraph_to_map(subgraph)
        try:
            return next(sbgnmaps)
        except:
            return None

    def get_map_to_sbgnfile(self, map_id, sbgnfile):
        sbgnmap = self.get_map(map_id)
        if sbgnmap is not None:
            utils.map_to_sbgnfile(sbgnmap[0], sbgnfile)

    def remove_map(self, map_id, sbgnmap):
        pass
        #file or libsbgn.Map or id

    def query_to_map(self, query, complete=True, merge_records=False, to_top_left=False):
        """Runs a cypher query against the database and returns the resulting SBGN maps

        Records resulting from the query are merged and transformed to zero or more SBGN maps that are returned.
        For an SBGN map to be returned, at least one of the resulting records must contain a Map node.
        Multiple maps can be returned if a resulting record contains multiple Map nodes, or if merge_records is set to `False` and at least two resulting records contain a Map node.
        Resulting records may be completed when complete is set to `True`.
        In this case, a node or a relationship of a record is always completed by the Map node it belongs to, and by all other nodes and relationships that are ultimately necessary to form a valid map from it.
        Hence if complete is set to `True`, at least one valid SBGN map will be returned as long as at least one record contains a node or a relationship.

        :param query: the cypher query
        :type query: string
        :param complete: if set to `True`, the nodes and relationships of every record will be completed
        :type complete: bool, optional
        :param merge_records: if set to `True`, the records of the result will be merged
        :type merge_records: bool, optional
        :param to_top_left: if set to `True`, the each of the resulting maps will be moved to the top left of its canvas
        :type to_top_left: bool, optional
        :return: the resulting SBGN maps, under the form of a generator. Each returned element is a tuple of the form (map, map_id).
        :rtype: Iterator[(:class:`libsbgnpy.libsbgn.map`, str)]
        """
        tx = self.neograph.begin()
        cursor = tx.run(query)
        tx.commit()
        subgraphs = set([])
        if merge_records:
            subgraphs.add(cursor.to_subgraph())
        else:
            for record in cursor:
                subgraphs.add(record.to_subgraph())
        for subgraph in subgraphs:
            if complete:
                subgraph = completer.complete_subgraph(subgraph, self.neograph)
            sbgnmaps = converter.subgraph_to_map(subgraph)
            for sbgnmap in sbgnmaps:
                if to_top_left:
                    utils.map_to_top_left(sbgnmap[0])
                yield sbgnmap

    def query_to_sbgnfile(
            self, query, sbgnfile, complete=True, merge_records=True, to_top_left=False):
        """Runs a cypher query against the database and writes the resulting SBGN maps to one or more SBGN-ML file

        For a resulting SBGN map to be written to an SBGN-ML file, at least one of the resulting records must contain a Map node.
        Multiple maps can be written if a resulting record contains multiple Map nodes, or if merge_records is set to `False` and at least two resulting records contain a Map node.
        Resulting records may be completed when complete is set to `True`.
        In this case, a node or a relationship of a record is always completed by the Map node it belongs to, and by all other nodes and relationships that are ultimately necessary to form a valid map from it.


        :param query: the cypher query
        :type query: string
        :param complete: if set to `True`, the nodes and relationships of every record will be completed
        :type complete: bool, optional
        :param merge_records: if set to `True`, the records of the result will be merged
        :type merge_records: bool, optional
        :param to_top_left: if set to `True`, the each of the resulting maps will be moved to the top left of its canvas
        :type to_top_left: bool, optional
        :return: the resulting SBGN maps, under the form of a generator. Each returned element is a tuple of the form (map, map_id).
        :rtype: Iterator[(:class:`libsbgnpy.libsbgn.map`, str)]
        """

        sbgnmaps = self.query_to_map(
                query, complete = complete, merge_records = merge_records, to_top_left = to_top_left)
        try:
            sbgnmap1 = next(sbgnmaps)
        except:
            pass
        else:
            try:
                sbgnmap2 = next(sbgnmaps)
            except:
                utils.map_to_sbgnfile(sbgnmap1[0], sbgnfile)
            else:
                ext = "sbgn"
                l = sbgnfile.split('.')
                if len(l) > 1:
                    ext = l[-1]
                    root = ''.join(l[:-1])
                else:
                    root = sbgnfile
                utils.map_to_sbgnfile(sbgnmap1[0], "{}_1.{}".format(root, ext))
                utils.map_to_sbgnfile(sbgnmap2[0], "{}_2.{}".format(root, ext))
                for i, sbgnmap in enumerate(sbgnmaps):
                    utils.map_to_sbgnfile(sbgnmap[0], "{}_{}.{}".format(root, i + 2, ext))
