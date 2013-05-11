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

def reparent(this, children):
    out = []
    for obj in children:
        if not (obj.parent is None or this is None):
            print obj, this, children
        assert obj.parent is None or this is None
        obj.parent = this
        out.append(obj)
    return out

# there's no constant type, constant is a struct with zero arity.
class Struct(object):
    def __init__(self, type, data):
        self.type   = type
        self.data   = reparent(self, data)
        self.parent = None

    def index(self, obj):
        return self.data.index(obj)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        assert value.parent is None
        self.data[index].parent = None
        self.data[index] = value
        value.parent = self

class List(object):
    def __init__(self, data):
        self.data = reparent(self, data)
        self.parent = None

    def index(self, obj):
        return self.data.index(obj)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        assert value.parent is None
        self.data[index].parent = None
        self.data[index] = value
        value.parent = self

    def _splice(self, start, stop, value):
        removed = reparent(None, self.data[start:stop])
        self.data[start:stop] = reparent(self, value)
        return removed
#
#class Buffer(object):
#    def __init__(self, data):
#        self.data   = data
#        self.parent = None
#
class String(object):
    def __init__(self, data):
        self.data   = data
        self.parent = None

    def __len__(self):
        return len(self.data)

    def __getitem__(self, what):
        return self.data[what]

    def _splice(self, start, stop, value):
        assert isinstance(value, unicode)
        removed = self.data[start:stop]
        self.data = self.data[:start] + value + self.data[stop:]
        return removed

class Document(object):
    def __init__(self, objects):
        self.objects = reparent(self, objects)
        self.listeners = set()

    def index(self, obj):
        return self.objects.index(obj)

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)

    def __getitem__(self, index):
        return self.objects[index]

    def __setitem__(self, index, value):
        assert value.parent is None
        self.objects[index].parent = None
        self.objects[index] = value
        value.parent = self

    def replace(self, this, that):
        parent = this.parent
        index  = parent.index(this)
        parent[index] = that
        for listener in self.listeners:
            listener.on_replace(parent, index, this, that)

    def splice(self, container, start, stop, data):
        removed = container._splice(start, stop, data)
        for listener in self.listeners:
            listener.on_splice(container, start, stop, data, removed)
        return removed

    def _splice(self, start, stop, value):
        removed = reparent(None, self.objects[start:stop])
        self.objects[start:stop] = reparent(self, value)
        return removed

class Selection(object):
    def __init__(self, container, head, tail=None):
        self.container = container
        self.head      = head
        self.tail      = head if tail is None else tail

    last = property(lambda self: len(self.container))
    def _get_start(self):
        if self.head < self.tail:
            return self.head
        else:
            return self.tail
    def _set_start(self, value):
        if self.head < self.tail:
            self.head = value
        else:
            self.tail = value
    start = property(_get_start, _set_start)

    def _get_stop(self):
        if self.head < self.tail:
            return self.tail
        else:
            return self.head
    def _set_stop(self, value):
        if self.head < self.tail:
            self.tail = value
        else:
            self.head = value
    stop = property(_get_stop, _set_stop)

    def splice(self, data):
        document = get_document(self.container)
        document.splice(self.container, self.start, self.stop, data)
        self.stop = self.start + len(data)

def normalize(obj, pole=True):
    if isinstance(obj, Document):
        return Selection(obj, len(obj)*pole, len(obj)*(not pole)) 
    elif isinstance(obj, Selection):
        return obj
    elif isinstance(obj.parent, (List, Document)):
        index = obj.parent.index(obj)
        return Selection(obj.parent, index+pole, index+(not pole))
    else:
        return obj

def get_object(obj):
    if isinstance(obj, Selection):
        return obj.container
    return obj

def get_document(obj):
    while not isinstance(obj, Document):
        obj = obj.parent
    return obj

def get_pole(obj):
    if isinstance(obj, Selection):
        return obj.head >= obj.tail
    return False

def extend(selection):
    if isinstance(selection, Selection):
        if selection.start > 0 or selection.stop < selection.last:
            selection = Selection(selection.container, selection.head, selection.tail)
            selection.start = 0
            selection.stop  = selection.last
            return selection
        else:
            return normalize(selection.container, get_pole(selection))
    else:
        return normalize(selection.parent)

def getdata(obj):
    """
        Specific function defined for Strings and Buffers
        which converts them into encodeable format.
    """
    return obj.data

def isstruct(obj):
    return isinstance(obj, Struct)

def isstring(obj):
    return isinstance(obj, String)

def isbuffer(obj):
    return False

def islist(obj):
    return isinstance(obj, List)

def istype(obj, uid):
    if isinstance(uid, (tuple, list)):
        return isstruct(obj) and obj.type.uid in uid
    return isstruct(obj) and obj.type.uid == uid

def isinside(obj, uid):
    obj = get_object(obj)
    if isinstance(obj, Document):
        return False
    return istype(obj.parent, uid)

def iscont(obj):
    return isinstance(obj, (Document, List))
