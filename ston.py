class STON(object):

    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri
        self.user = user
        self.password = password
        self.neograph = Graph(uri = uri, user = user, password = password)

    def has_map(sbgnmap):
        #file or libsbgn.Map or id

    def create_map(sbgnmap):
        #file or libsbgn.Map

    def get_map(mapid):
        #id

    def remove_map(mapid):
        #file or libsbgn.Map or id

    def query_to_map(query, complete=True, merge_records=True):

    def query_to_sbgnfile(query, sbgnfile, complete=True, merge_records=True):
        sbgnmaps = self.query_to_map(query, complete)

    def map_to_sbgnfile(sbgnmap, sbgnfile):

