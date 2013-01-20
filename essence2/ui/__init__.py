from essence2 import vec2, rectangle

class List(object):
    background = None
    padding = 0, 0, 0, 0
    spacing = 0
    min_size = vec2(32, 0)
    extend = 0
    align = 0.5, 0.5
    def __init__(self, children, field=None, slot=None):
        self.children = children
        self.field = field
        self.slot = slot

    def dup(self):
        return self.__class__(
            list(child.dup() for child in self.children),
            self.field,
            self.slot
        )

    def layout0(self, font):
        self.offsets = []
        min_size = vec2(0, 0)
        self.layout_extend = 0
        self._extend = 0
        current = 0
        for child in self.children:
            stop = current
            current += self.spacing if len(self.offsets) > 0 else 0
            self.offsets.append((stop, current))
            size, extend = child.layout0(font)
            current += size.y
            min_size.x = max(min_size.x, size.x)
            min_size.y = current
            self._extend |= extend
        self.offsets.append((current, current))
        self.outer = rectangle(vec2(0,0), min_size).offset(self.padding)
        self._min_size0 = self.min_size.maximum(self.outer.size)
        self._min_size1 = min_size
        return self._min_size0, self._extend | self.extend

    def layout1(self, space):
        self.outer.size = space.size.mix(self._min_size0, self._extend | self.extend)
        self.outer.move_inside(space, *self.align)
        outinner = self.outer.inset(self.padding)
        base, size = outinner
        inner = rectangle(vec2(0, 0), outinner.size.mix(self._min_size1, self._extend))
        base, size = inner.move_inside(outinner, *self.align)
        for index, child in enumerate(self.children):
            start = self.offsets[index  ][1]
            stop  = self.offsets[index+1][0]
            subspace = rectangle(
                vec2(base.x, base.y + start),
                vec2(size.x, stop - start)
            )
            child.layout1(subspace)

    def draw(self, screen):
        if self.background:
            screen(self.background, self.outer)
        for child in self.children:
            child.draw(screen)

    def locate_offset(self, index):
        offset0 = self.offsets[0][0]
        offset1 = None
        for i, child in enumerate(self.children):
            if child.slot != None:
                if child.slot < index:
                    offset0 = self.offsets[i+1][0]
                if index <= child.slot and offset1 == None:
                    offset1 = self.offsets[i][1]
        if offset1 == None:
            offset1 = self.offsets[i+1][1]
        return offset0, offset1

    def selection(self, start, stop):
        inner = self.outer.inset(self.padding)
        y0 = self.locate_offset(start)[1] - 1
        y1 = self.locate_offset(stop)[0] + 1
        base = inner.base + (-1, y0)
        size = vec2(inner.size.x + 1, y1 - y0)
        return rectangle(base, size)

    def caret(self, index):
        inner = self.outer.inset(self.padding)
        y0 = self.locate_offset(index)[0] - 1
        y1 = self.locate_offset(index)[1] + 1
        base = inner.base + (-1, y0)
        size = vec2(inner.size.x + 1, y1 - y0)
        return rectangle(base, size)

    def nearest_index(self, position):
        inner = self.outer.inset(self.padding)
        delta = position - inner.base
        d0 = abs(delta.y - 0)
        index = 0
        for index, (offset0, offset1) in enumerate(self.offsets):
            d1 = abs(delta.y - offset0)
            if d0 < d1:
                return index - 1
            d0 = abs(delta.y - offset1)
        return index

    def nearest_caret(self, position):
        nearest = self.nearest_index(position)
        slot = 0
        for index, child in enumerate(self.children):
            if nearest <= index:
                return slot
            if child.slot != None:
                slot = child.slot + 1
        return slot + 1

class Label(object):
    background = None
    padding = 0, 0, 0, 0
    extend = 0
    min_size = vec2(8, 12)
    align = 0.5, 0.5
    blend = None
    def __init__(self, field='', slot=None):
        self.field = field
        self.slot = slot

    def dup(self):
        return self.__class__(self.field, self.slot)

    def layout0(self, font):
        self.surface = font(str(self.field))
        self.outer = self.surface.geometry.offset(self.padding)
        self._min_size = self.min_size.maximum(self.outer.size)
        self._extend = self.extend
        if self.blend:
            self.surface(self.blend)
        return self._min_size, self._extend

    def layout1(self, space):
        self.outer.size = space.size.mix(self._min_size, self._extend | self.extend)
        self.outer.move_inside(space, *self.align)
        outinner = self.outer.inset(self.padding)
        self.surface.geometry.move_inside(outinner, *self.align)

    def draw(self, screen):
        if self.background:
            screen(self.background, self.outer)
        screen(self.surface)

    def selection(self, start, stop):
        return self.surface.selection(start, stop)

    def caret(self, index):
        if len(self.field) == 0:
            caret = rectangle(vec2(0, 0), vec2(1, 8))
            caret.move_inside(self.outer.inset(self.padding), *self.align)
            return caret
        return self.surface.caret(index)

    def nearest_caret(self, position):
        return self.surface.nearest_caret(position)
