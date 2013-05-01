def clamp(low, high, value):
    return min(high, max(low, value))

class Box(object):
    # some Box objects are ordinal references to an intron.
    reference = None

    def __init__(self, (left, top, width, height), style):
        self.left   = left
        self.top    = top
        self.width  = width
        self.height = height
        self.style  = style

    def flowline(self, edge, which):
        if edge in ('top', 'bottom'):
            return self.width  * (0.0, 0.5, 1.0)[which]
        if edge in ('left', 'right'):
            return self.height * (0.0, 0.5, 1.0)[which]

    def measure(self, parent):
        pass

    def arrange(self, parent, (left, top)):
        self.left = left
        self.top  = top

    def render(self, context):
        renderer = self.style['renderer']
        if renderer:
            renderer(context, self)
        for child in self:
            child.render(context)

    @property
    def rect(self):
        return (self.left, self.top, self.width, self.height)

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def inside(self, (x,y)):
        return 0 <= x - self.left < self.width and 0 <= y - self.top < self.height

    def in_range(self, start, stop):
        "Check if this box falls inside range as a reference."
        if self.reference is None:
            return False
        _start, _stop = self.reference
        return start <= _stop and stop >= _start

    def scan_offset(self, (x,y)):
        "Find nearest 'caret' for position"
        if self.reference is None:
            raise Exception("This object does not have reference")
        _start, _stop = self.reference
        left   = self.left
        right  = self.left + self.width
        top    = self.top
        bottom = self.top + self.height
        b0 = (x - left)**2  + (y - top)**2
        b1 = (x - right)**2 + (y - bottom)**2
        b  = (x - clamp(left, right, x))**2 + (y - clamp(top, bottom, y))**2
        if b0 < b1:
            return _start, b
        else:
            return _stop, b

    def selection_marker(self, start, stop):
        _start, _stop = self.reference
        x0 = (0, self.width)[min(1,max(0, start - _start))]
        x1 = (0, self.width)[min(1,max(0, stop  - _start))]
        return (self.left + x0 - 1, self.top, x1-x0 +2, self.height)

    def pick(self, pos, hits=None):
        "retrieve list of boxes that hit the cursor"
        hits = [] if hits is None else hits
        if self.inside(pos):
            hits.append(self)
        for subnode in self:
            hits = subnode.pick(pos, hits)
        return hits

    def references(self, res=None):
        "retrieve list of boxes that are references, excluding itself."
        res = [] if res is None else res
        for box in self:
            if box.reference is None:
                res = box.references(res)
            else:
                res.append(box)
        return res
