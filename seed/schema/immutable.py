# When object is being edited, it follows different structure.
# Programs that are evaluated hold more raw structures with language proxies in them.
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

    def __repr__(self):
        return self.uid

class Proxy(object):
    """
    This is the feature of immutable module.
    Proxy identifies the location of the node,
    which lets one to construct error reports
    with reliable location data.

    If they end up inside resulting module,
    they should be copied along. For this
    there's .to -field in every proxy.
    """
    def __init__(self, parent, index):
        self.parent = parent
        self.index  = index
        self.to     = None

    def unroll(self):
        if self.parent is None:
            return None
        info, path = self.parent.unroll()
        path.append(self.index)
        return info, path

class RootProxy(object):
    def __init__(self, info):
        self.info = info
        self.to   = None

    def unroll(self):
        return self.info, []

def link_proxies(this, children, start=0):
    out = []
    for index, obj in enumerate(children, start):
        if isinstance(obj, (Struct, List)):
            if not (obj.proxy.parent is None or this is None):
                print obj, this, children
            assert obj.proxy.parent is None or this is None
            obj.proxy.parent = this
            obj.proxy.index  = index
        out.append(obj)
    return out

# there's no constant type, constant is a struct with zero arity.
class Struct(object):
    __slots__ = ('type', 'proxy', 'data')
    def __init__(self, type, data):
        self.type   = type
        self.proxy  = Proxy(None, 0)
        self.data   = link_proxies(self.proxy, data, 0)

    def index(self, obj):
        return self.data.index(obj)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __getattr__(self, name):
        if name in self.type.labels:
            return self[self.type.labels.index(name)]
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name not in Struct.__slots__ and name in self.type.labels:
            self[self.type.labels.index(name)] = value
        else:
            object.__setattr__(self, name, value)

    def __repr__(self):
        return "Struct(%r, %r)" % (self.type, self.data)

class List(object):
    def __init__(self, data):
        self.proxy = Proxy(None, 0)
        self.data = link_proxies(self.proxy, data, 0)

    def index(self, obj):
        return self.data.index(obj)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __repr__(self):
        return "List(%r)" % self.data

def String(data):
    return unicode(data)

def Buffer(data):
    return str(data)

class Document(object):
    def __init__(self, objects):
        self.objects = objects
        self.proxy = RootProxy(None)
        self.data = link_proxies(self.proxy, objects, 0)

    def set_info(self, info):
        self.proxy.info = info

    def index(self, obj):
        return self.objects.index(obj)

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)

    def __getitem__(self, index):
        return self.objects[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __repr__(self):
        return "Document(%r)" % self.objects

def getdata(obj):
    """
        Specific function defined for Strings and Buffers
        which converts them into encodeable format.
    """
    return obj

def isstruct(obj):
    return isinstance(obj, Struct)

def isstring(obj):
    return isinstance(obj, unicode)

def isbuffer(obj):
    return isinstance(obj, str)

def islist(obj):
    return isinstance(obj, List)
