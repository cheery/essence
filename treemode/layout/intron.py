from box import Box
from label import Label

def clamp(low, high, value):
    return min(high, max(low, value))

def subintrons(node, out):
    if isinstance(node, Intron):
        out.append(node)
    else:
        for subnode in node:
            out = subintrons(subnode, out)
    return out

class Intron(Box):
    "Generator gets called with (intron, *args), it must provide intron.node, intron.style, and maybe intron.controller"
    def __init__(self, generator, *args):
        Box.__init__(self, (0,0,0,0), None)
        self.node       = None
        self.controller = None
        self.generator  = generator
        self.args       = args
        self.rebuild()

    def rebuild(self):
        self.node  = None
        self.style = None
        self.generator(self, *self.args)
        assert self.node  != None
        assert self.style != None

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
#
#    def pick(self, pos, hits=None):
#        hits = [] if hits is None else hits
#        if self.inside(pos):
#            hits.append(self)
#        for subnode in self:
#            hits = pickbox(subnode, pos, hits)
#        return hits

    def subintrons(self, out=None):
        out = [] if out is None else out
        for subnode in self:
            out = subintrons(subnode, out)
        return out

#    def labels(self, out=None):
#        out = [] if out is None else out
#        for subnode in self:
#            out = labels(subnode, out)
#        return out

##    def find_context(self, source):
##        if source == self.source:
##            return ()
##        for subintron in self.subintrons():
##            match = subintron.find_context(source)
##            if match is not None:
##                return (self,) + match
##
##    def find(self, source):
##        if self.source == source:
##            return self
##        for subintron in self.subintrons():
##            match = subintron.find(source)
##            if match is not None:
##                return match
#
#    def traverse(self, res, cond):
#        if cond(self):
#            res.append(self)
#        return self.node.traverse(res, cond)
#
#    def selection_rect(self, start, stop):
#        x0 = (0, self.width)[min(1,max(0, start - self.index))]
#        x1 = (0, self.width)[min(1,max(0, stop  - self.index))]
#        return (self.left + x0 - 1, self.top, x1-x0 +2, self.height)

#    def in_range(self, start, stop):
#        x0 = self.index
#        x1 = self.index + 1
#        return start <= x1 and stop >= x0
    def pick_offset(self, pos):
        k = 0
        best = None
        for box in self.references():
            i, v = box.scan_offset(pos)
            if v <= best or best is None:
                k = i
                best = v
        return k

    def __iter__(self):
        return iter((self.node,))
