import math

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

    def __mul__(self, i):
        return vec2(self.x * i, self.y * i)

    @property
    def magnitude(self):
        return math.sqrt(self.x*self.x + self.y*self.y)

    @property
    def normal(self):
        mag = self.magnitude
        if mag > 0.0:
            return vec2(self.x / mag, self.y / mag)
        return None

    def dot(self, other):
        return self.x*other.x + self.y*other.y

    def maximum(self, (x,y)):
        return vec2(max(self.x, x), max(self.y, y))

    def minimum(self, (x,y)):
        return vec2(min(self.x, x), min(self.y, y))

    def mix(self, (x,y), mask):
        return vec2(
            self.x if mask & 1 else x,
            self.y if mask & 2 else y
        )

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

    def offset(self, (left, top, right, bottom)):
        return rectangle(
            self.base - (left, top),
            self.size + (left+right, top+bottom)
        )

    def inset(self, (left, top, right, bottom)):
        return rectangle(
            self.base + (left, top),
            self.size - (left+right, top+bottom)
        )

    def inside(self, pos):
        x, y = pos - self.base
        w, h = self.size
        return 0 <= x < w and 0 <= y < h

    def move_inside(self, space, x=0.5, y=0.5):
        excess = space.size - self.size
        self.base = space.base + vec2(excess.x * x, excess.y * y)
        return self

def clamp(low, high, value):
    if value <= low:
        return low
    if value >= high:
        return high
    return value
