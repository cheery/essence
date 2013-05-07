import os

class rgba(object):
    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __iter__(self):
        return iter((self.r, self.g, self.b, self.a))

    def __repr__(self):
        return "rgba(%s)" % ', '.join(str(c) for c in self)

def mix(a, b, t):
    s = 1 - t
    return type(a)(*(type(i)(i*s + j*t) for i, j in zip(a, b)))

def in_module(path):
    return os.path.join(os.path.dirname(__file__), path)
