class Config(object):
    def __init__(self, parent, current):
        self.parent  = parent
        self.current = current

    def inherit(self, *a, **kw):
        properties = {}
        properties.update(kw)
        for o in a:
            properties.update(o)
        return self.__class__(self, properties)

    def __getitem__(self, key):
        if key in self.current:
            return self.current[key]
        return self.parent[key]
