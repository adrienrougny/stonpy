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
        if sbgnmaps:
            sbgnmap = sbgnmaps.pop()[0]
        else:
            return None
        return sbgnmap

    def get_map_to_sbgnfile(self, map_id, sbgnfile):
        sbgnmap = self.get_map(map_id)
        utils.map_to_sbgnfile(sbgnmap, sbgnfile)

    def remove_map(self, map_id, sbgnmap):
        pass
        #file or libsbgn.Map or id

    def query_to_map(self, query, complete=True, merge_records=True):
        sbgnmaps = set([])
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
            sbgnmaps |= converter.subgraph_to_map(subgraph)
        return sbgnmaps

    def query_to_sbgnfile(
            self, query, sbgnfile, complete=True, merge_records=True):
        sbgnmaps = self.query_to_map(
                query, complete = complete, merge_records = merge_records)
        if len(sbgnmaps) > 1:
            ext = "sbgn"
            l = sbgnfile.split('.')
            if len(l) > 1:
                ext = l[-1]
                root = ''.join(l[:-1])
            else:
                root = sbgnfile
            for i, sbgnmap in enumerate(sbgnmaps):
                utils.map_to_sbgnfile(sbgnmap[0], "{}_{}.{}".format(root, i, ext))
        elif len(sbgnmaps) == 1:
            sbgnmap = sbgnmaps.pop()
            utils.map_to_sbgnfile(sbgnmap[0], sbgnfile)
