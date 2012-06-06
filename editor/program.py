
class program(object):
    """
    For now the program is just a list. though it's obvious it will enjoy
    event hookups and such. so this class is for hooking up events later.
    """
    def __init__(self, listing):
        self.listing = list(listing)
        self.listeners = []

    def event(self, name, *args):
        for listener in self.listeners:
            getattr('on_'+listener, name)(*args)

    def splice(start, stop, data):
        res = self.listing[start:stop]
        self.listing[start:stop] = data
        self.event('splice', start, stop, data, res)
        return res

    def slice(start, stop):
        return self.listing[start:stop]

    def __iter__(self):
        return iter(self.listing)

class array(object):
    """
    Native python strings are immutable. bytes is a mutable "string".
    """
    def __init__(self, data):
        self.data = data

    def splice(start, stop, data):
        res = self.data[start:stop]
        self.data = self.data[:start] + self.data[stop:]
        return res

    def slice(start, stop):
        return self.data[start:stop]

    def copy(self):
        return array(self.data)

    isbytes = lambda self: True
    isOPN = lambda self: False
    isCLO = lambda self: False

class structuralnode(object):
    """
    The basetype is one of:

        'OPN'
        'CLO'

    structuralnode is an uneditable object.. much like a marker in fact.
    """
    def __init__(self, basetype):
        self.basetype = basetype

    isbytes = lambda self: False
    isOPN = lambda self: self.basetype == 'OPN'
    isCLO = lambda self: self.basetype == 'CLO'

OPN = structuralnode('OPN')
CLO = structuralnode('CLO')
