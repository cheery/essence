class Intron(Box):
    def __init__(self, source, generator, control=None):
        self.source    = source
        self.generator = generator
        self.control   = control
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

#    def pick(self, (x,y), hits=None):
#        if hits == None:
#            hits = []
#        if 0 <= x - self.left < self.width and 0 <= y - self.top < self.height:
#            hits.append(self)
#        return self.node.pick((x,y), hits)
#
#    def subintrons(self, res=None):
#        if res == None:
#            return self.node.subintrons([])
#        else:
#            res.append(self)
#            return res
#
#    def find_context(self, intron):
#        if intron == self:
#            return ()
#        for subintron in self.subintrons():
#            match = subintron.find_context(intron)
#            if match is not None:
#                return (self,) + match
#
#    def traverse(self, res, cond):
#        if cond(self):
#            res.append(self)
#        return self.node.traverse(res, cond)
#
    def selection_rect(self, start, stop):
        x0 = (0, self.width)[start]
        x1 = (0, self.width)[stop]
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
