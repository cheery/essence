from box import Box
from label import Label

def clamp(low, high, value):
    return min(high, max(low, value))

def pickbox(node, pos, hits):
    if isinstance(node, Intron):
        return node.pick(pos, hits)
    for subnode in node:
        hits = pickbox(subnode, pos, hits)
    return hits

def subintrons(node, out):
    if isinstance(node, Intron):
        out.append(node)
    else:
        for subnode in node:
            out = subintrons(subnode, out)
    return out

def labels(node, out):
    if isinstance(node, Label):
        out.append(node)
    for subnode in node:
        out = labels(subnode, out)
    return out

class Intron(Box):
    def __init__(self, source, generator, control=None, index=None):
        self.source    = source
        self.generator = generator
        self.control   = control
        self.index     = index
        self.rebuild()

    def rebuild(self):
        self.node = self.generator(self, self.source)

    def flowline(self, edge, which):
        left, top, right, bottom = self.style['padding']
        if edge in ('left', 'right'):
            x0 = top
        if edge in ('top', 'bottom'):
            x0 = left
        return x0 + self.node.flowline(edge, which)

    def measure(self, parent):
        left, top, right, bottom = self.style['padding']
        min_width  = self.style['min_width']
        min_height = self.style['min_height']
        self.node.measure(self)
        self.width  = max(min_width,  self.node.width  + left + right)
        self.height = max(min_height, self.node.height + top + bottom)

    def arrange(self, parent, (left, top)):
        self.left = left
        self.top  = top
        left, top, right, bottom = self.style['padding']
        inner_width  = self.width  - left - right
        inner_height = self.height - top - bottom
        x = self.left + left + (inner_width  - self.node.width)*0.5
        y = self.top  + top  + (inner_height - self.node.height)*0.5
        self.node.arrange(self, (x,y))

    def pick(self, pos, hits=None):
        hits = [] if hits is None else hits
        if self.inside(pos):
            hits.append(self)
        for subnode in self:
            hits = pickbox(subnode, pos, hits)
        return hits

    def subintrons(self, out=None):
        out = [] if out is None else out
        for subnode in self:
            out = subintrons(subnode, out)
        return out

    def labels(self, out=None):
        out = [] if out is None else out
        for subnode in self:
            out = labels(subnode, out)
        return out

    def find_context(self, source):
        if source == self.source:
            return ()
        for subintron in self.subintrons():
            match = subintron.find_context(source)
            if match is not None:
                return (self,) + match
#
#    def traverse(self, res, cond):
#        if cond(self):
#            res.append(self)
#        return self.node.traverse(res, cond)
#
    def selection_rect(self, start, stop):
        x0 = (0, self.width)[min(1,max(0, start - self.index))]
        x1 = (0, self.width)[min(1,max(0, stop  - self.index))]
        return (self.left + x0 - 1, self.top, x1-x0 +2, self.height)

    def scan_offset(self, (x,y)):
        left   = self.left
        right  = self.left + self.width
        top    = self.top
        bottom = self.top + self.height
        b0 = (x - left)**2  + (y - top)**2
        b1 = (x - right)**2 + (y - bottom)**2
        b  = (x - clamp(left, right, x))**2 + (y - clamp(top, bottom, y))**2
        if b0 < b1:
            return self.index, b
        else:
            return self.index+1, b

    def in_range(self, start, stop):
        x0 = self.index
        x1 = self.index + 1
        return start <= x1 and stop >= x0

    def pick_offset(self, pos):
        k = 0
        best = None
        for intron in self.subintrons():
            if intron.index is None:
                continue
            i, v = intron.scan_offset(pos)
            if v <= best or best is None:
                k = i
                best = v
        for label in self.labels():
            if label.source is not self.source:
                continue
            i, v = label.scan_offset(pos)
            if v <= best or best is None:
                k = i
                best = v
        return k

    def __iter__(self):
        return iter((self.node,))
