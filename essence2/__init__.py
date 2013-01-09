class vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __repr__(self):
        return "vec2(%s)" % ', '.join(repr(scalar) for scalar in self)

    def __add__(self, (x,y)):
        return vec2(self.x + x, self.y + y)

    def __sub__(self, (x,y)):
        return vec2(self.x - x, self.y - y)

class rgba(object):
    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __iter__(self):
        return iter((self.r, self.g, self.b, self.a))

    def __repr__(self):
        return "rgba(%s)" % ', '.join(repr(channel) for channel in self)

class rectangle(object):
    def __init__(self, base, size):
        self.base = base
        self.size = size

    def __iter__(self):
        return iter((self.base, self.size))

    def __repr__(self):
        return "rectangle(%s)" % ', '.join(repr(channel) for channel in self)

    def valid(self):
        x, y = self.size
        return x >= 0 and y >= 0

def clamp(low, high, value):
    if value <= low:
        return low
    if value >= high:
        return high
    return value
