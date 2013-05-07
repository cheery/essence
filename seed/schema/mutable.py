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
        assert obj.parent is None
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

class Document(object):
    def __init__(self, objects):
        self.objects = reparent(self, objects)

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)

    def replace(self, this, that):
        raise Exception("implement replace first")

    def splice(self, container, start, stop, data):
        raise Exception("implement splice first")

class Selection(object):
    def __init__(self, container, head, tail=None):
        self.container = container
        self.head      = head
        self.tail      = head if tail is None else tail

    last = property(lambda self: len(self.struct[self.index]))
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

def normalize(obj, pole=True):
    if isinstance(obj, Document):
        return Selection(obj, len(obj)*pole, len(obj)*(not pole)) 
    elif isinstance(obj, Selection):
        return obj
    elif isinstance(obj.parent, List):
        index = obj.parent.index(obj)
        return Selection(obj.parent, index+pole, index+(not pole))

def get_object(obj):
    if isinstance(obj, Selection):
        return obj.container
    return obj
