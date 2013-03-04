class Color(object):
    def __init__(self, item):
        self.item = item

    s = property(lambda self: float(self.item.x+2) / self.item.atlas.width)
    t = property(lambda self: float(self.item.y+2) / self.item.atlas.height)

    def __call__(self, emit, (left, top, width, height), shade=None):
        shade = shade or self.item.atlas.white
        emit(left,       top,        self.s, self.t, shade.s, shade.t)
        emit(left+width, top,        self.s, self.t, shade.s, shade.t)
        emit(left+width, top+height, self.s, self.t, shade.s, shade.t)
        emit(left,       top+height, self.s, self.t, shade.s, shade.t)

