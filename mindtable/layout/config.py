class Config(object):
    def __init__(self, parent, current):
        self.parent  = parent
        self.current = current

    def inherit(self, **kw):
        return self.__class__(self, kw)

    def __getitem__(self, key):
        if key in self.current:
            return self.current[key]
        return self.parent[key]
