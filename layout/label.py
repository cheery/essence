from box import Box

class Label(Box):
    def __init__(self, source, style):
        self.source  = source
        self.offsets = None 
        Box.__init__(self, (0, 0, 0, 0), style)

    def flowline(self, edge, which):
        left, top, right, bottom = self.style['padding']
        if edge in ('top', 'bottom'):
            return self.width  * (0.0, 0.5, 1.0)[which] + left
        if edge in ('left', 'right'):
            if which == 0:
                return top
            if which == 1:
                return top + self.style['font'].baseline * 0.5
            if which == 2:
                return top + self.style['font'].baseline

    def measure(self, parent):
        left, top, right, bottom = self.style['padding']
        self.offsets = self.style['font'].measure(self.source)
        self.width  = left + right + self.offsets[-1]
        self.height = top + bottom + self.style['font'].height * self.style['line_height']

    def arrange(self, parent, (left,top)):
        self.left = left
        self.top  = top

    @property
    def baseline_pos(self):
        left, top, right, bottom = self.style['padding']
        font = self.style['font']
        return (self.left + left, self.top + top + font.baseline)

    def selection_rect(self, start, stop):
        left, top, right, bottom = self.style['padding']
        x0 = self.offsets[start]
        x1 = self.offsets[stop]
        return (self.left + left + x0 - 1, self.top, x1-x0 + 2, self.height)

#    def scan_offset(self, (x,y)):
#        left, top, right, bottom = self.style['padding']
#        x -= self.left + left
#        k = 0
#        best = abs(x - 0)
#        for index, offset in enumerate(self.offsets):
#            v = abs(x - offset)
#            if v <= best:
#                best = v
#                k = index
#        return k, best ** 2.0 + abs(y - clamp(self.top, self.top + self.height, y)) ** 2.0
