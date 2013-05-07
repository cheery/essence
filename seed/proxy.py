class StructType(object):
    def __init__(self, uid):
        labels = uid.split(':')
        self.name   = labels[0]
        self.labels = labels[1:]
        self.uid    = uid

    def __hash__(self):
        return hash(self.uid)

    def __cmp__(self, other):
        return cmp(self.uid, other.uid)

# The source points out the location in original file.
class Source(object):
    def __init__(self, parent, index):
        self.parent = parent
        self.index  = index

# this thing has the fancy getattr and so on..
class Struct(object):
    def __init__(self, type, data):
        self.type = type
        self.data = data
        self.source = None

class List(object):
    def __init__(self, data):
        self.data = data
        self.source = None
