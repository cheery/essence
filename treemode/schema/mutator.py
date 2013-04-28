from base import Struct, Constant
from proxy import Proxy

class Mutator(object):
    def __init__(self, struct, index):
        self.struct = struct
        self.index  = index

    @property
    def which(self):
        obj = self.struct[self.index]
        if isinstance(obj, Struct):
            return 'struct'
        if isinstance(obj, Constant):
            return 'constant'
        if isinstance(obj, list):
            return 'list'
        if isinstance(obj, unicode):
            return 'string'
        if isinstance(obj, str):
            return 'buffer'
        raise Exception("Unknown mutateable")

    def replace(self, data):
        removed = self.struct[self.index]
        self.struct[self.index] = data
        Proxy.reproxy(self.struct.proxy, self.index, data)
        return removed

    def splice(self, start, stop, data):
        which = self.which
        if which in ('string', 'buffer'):
            immutable = self.struct[self.index]
            removed = immutable[start:stop]
            self.struct[self.index] = immutable[:start] + data + immutable[stop:]
        elif which == 'list':
            removed = self.struct[self.index][start:stop]
            self.struct[self.index][start:stop] = data
        else:
            raise Exception("Cannot splice %s" % which)
        Proxy.reproxy(self.struct.proxy, self.index, self.struct[self.index])
        return removed

class Selection(object):
    def __init__(self, mutator, head, tail=None):
        self.mutator = mutator
        self.head = head
        self.tail = head if tail is None else tail
    
    @property
    def struct(self):
        return self.mutator.struct

    @property
    def index(self):
        return self.mutator.index

    @property
    def which(self):
        return self.mutator.which

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
        removed = self.mutator.splice(self.start, self.stop, data)
        self.stop = len(data) + self.start
        return removed
