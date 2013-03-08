from essence3.util import clamp

class Align(object):
    def __init__(self, h, v = None):
        self.h = h
        self.v = h if v is None else v

    def __call__(self, node, edge):
        if edge in ('top', 'bottom'):
            return node.width  * self.h
        if edge in ('left', 'right'):
            return node.height * self.v

class FlowAlign(object):
    def __init__(self, h, v = None):
        self.h = h
        self.v = h if v is None else v

    def __call__(self, node, edge):
        if edge in ('top', 'bottom'):
            return node.flowline(edge, self.h)
        if edge in ('left', 'right'):
            return node.flowline(edge, self.v)

def flow_simple(node, (low, high), edge, which):
    if which == 0:
        return low + node.offset1[0] + node[0].flowline(edge, which)
    if which == 2:
        return low + node.offset1[-2] + node[-1].flowline(edge, which)
    i = len(node) / 2
    if which == 1:
        if len(node) % 2 == 1:
            return low + node.offset1[i] + node[i].flowline(edge, which)
        else:
            return low + (node.offset0[i] + node.offset1[i])*0.5

class Box(object):
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

    def arrange(self, parent, (left,top)):
        self.left = left
        self.top  = top

    def render(self):
        background = self.style['background']
        if background:
            background(self)

    def pick(self, (x,y), hits):
        return hits

    def subintrons(self, res):
        return res

    def traverse(self, res, cond):
        if cond(self):
            res.append(self)
        return res

class Slate(Box):
    def __init__(self, (width, height), style):
        Box.__init__(self, (0, 0, width, height), style)

class Label(Box):
    def __init__(self, source, style):
        self.source = source
        Box.__init__(self, (0, 0, 0, 0), style)
        self.offsets = None 

    def flowline(self, edge, which):
        left, top, right, bottom = self.style['padding']
        if edge in ('top', 'bottom'):
            return self.width  * (0.0, 0.5, 1.0)[which] + left
        if edge in ('left', 'right'):
            if which == 0:
                return top
            if which == 1:
                return top + self.style['font'].mathline * self.style['font_size']
            if which == 2:
                return top + self.style['font'].baseline * self.style['font_size']

    def measure(self, parent):
        left, top, right, bottom = self.style['padding']
        self.offsets = self.style['font'].measure(self.source, self.style['font_size'])
        self.width  = left + right + self.offsets[-1]
        self.height = top + bottom + self.style['font'].lineheight * self.style['font_size']

    def arrange(self, parent, (left,top)):
        self.left = left
        self.top  = top

    def render(self):
        background = self.style['background']
        if background:
            background(self)
        self.style['font'](self)

    def selection_rect(self, start, stop):
        left, top, right, bottom = self.style['padding']
        x0 = self.offsets[start]
        x1 = self.offsets[stop]
        return (self.left + left + x0 - 1, self.top, x1-x0 + 2, self.height)

    def scan_offset(self, (x,y)):
        left, top, right, bottom = self.style['padding']
        x -= self.left + left
        k = 0
        best = abs(x - 0)
        for index, offset in enumerate(self.offsets):
            v = abs(x - offset)
            if v <= best:
                best = v
                k = index
        return k, best ** 2.0 + abs(y - clamp(self.top, self.top + self.height, y)) ** 2.0

class Container(Box):
    def __init__(self, nodes, style):
        self.nodes = nodes
        self.offset0 = [0] * (len(nodes) + 1)
        self.offset1 = [0] * (len(nodes) + 1)
        self.flow0 = [0] * len(nodes)
        self.flow1 = [0] * len(nodes)
        self.base0 = 0 
        self.base1 = 0
        Box.__init__(self, (0, 0, 0, 0), style)

    def __getitem__(self, i):
        return self.nodes[i]

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def render(self):
        background = self.style['background']
        if background:
            background(self)
        for node in self:
            node.render()

    def pick(self, (x,y), hits):
        for node in self:
            res = node.pick((x,y), hits)
        return hits

    def subintrons(self, res):
        for node in self:
            res = node.subintrons(res)
        return res

    def traverse(self, res, cond):
        if cond(self):
            res.append(self)
        for node in self:
            res = node.traverse(res, cond)
        return res

class HBox(Container):
    def flowline(self, edge, which):
        left, top, right, bottom = self.style['padding']
        if edge == 'left':
            return top + self.base0 - self.flow0[0]  + self[0].flowline(edge, which)
        elif edge == 'right':
            return top + self.base1 - self.flow1[-1] + self[-1].flowline(edge, which)
        else:
            return self.style['flow'](self, (left, self.width-right), edge, which)

    def measure(self, parent):
        offset = cap = 0
        low = org = high = 0
        for i, node in enumerate(self):
            node.measure(self)
            self.offset0[i] = cap
            self.offset1[i] = offset
            self.flow0[i] = f0 = self.style['align'](node, 'left')
            self.flow1[i] = f1 = self.style['align'](node, 'right')
            low  = min(low,  0           - f0)
            high = max(high, node.height - f0)
            low  += f0 - f1
            org  += f0 - f1
            high += f0 - f1
            cap     = offset + node.width
            offset += node.width + self.style['spacing']
        self.offset0[len(self)] = self.offset1[len(self)] = cap
        self.base0 = org - low
        self.base1 = 0 - low
        left, top, right, bottom = self.style['padding']
        self.width = cap         + left + right
        self.height = high - low + top  + bottom

    def arrange(self, parent, (left,top)):
        self.left = left
        self.top  = top
        left, top, right, bottom = self.style['padding']
        base_x = self.left + left
        base_y = self.base0 + self.top + top
        for i, node in enumerate(self):
            node.arrange(self, (base_x + self.offset1[i], base_y - self.flow0[i]))
            base_y += self.flow1[i] - self.flow0[i]

    def get_spacer(self, i):
        left, top, right, bottom = self.style['padding']
        x0 = self.offset0[i]
        x1 = self.offset1[i]
        return self.left + left+x0, self.top + top, x1-x0, self.height-bottom-top

class VBox(Container):
    def flowline(self, edge, which):
        left, top, right, bottom = self.style['padding']
        if edge == 'top':
            return left + self.base0 - self.flow0[0]  + self[0].flowline(edge, which)
        elif edge == 'bottom':
            return left + self.base1 - self.flow1[-1] + self[-1].flowline(edge, which)
        else:
            return self.style['flow'](self, (top, self.height-bottom), edge, which)

    def measure(self, parent):
        offset = cap = 0
        low = org = high = 0
        for i, node in enumerate(self):
            node.measure(self)
            self.offset0[i] = cap
            self.offset1[i] = offset
            self.flow0[i] = f0 = self.style['align'](node, 'top')
            self.flow1[i] = f1 = self.style['align'](node, 'bottom')
            low  = min(low,  0          - f0)
            high = max(high, node.width - f0)
            low  += f0 - f1
            org  += f0 - f1
            high += f0 - f1
            cap     = offset + node.height
            offset += node.height + self.style['spacing']
        self.offset0[len(self)] = self.offset1[len(self)] = cap
        self.base0 = org - low
        self.base1 = 0 - low
        left, top, right, bottom = self.style['padding']
        self.height = cap        + top  + bottom
        self.width  = high - low + left + right

    def arrange(self, parent, (left,top)):
        self.left = left
        self.top  = top
        left, top, right, bottom = self.style['padding']
        base_x = self.base0 + self.left + left
        base_y = self.top   + top
        for i, node in enumerate(self):
            node.arrange(self, (base_x - self.flow0[i], base_y + self.offset1[i]))
            base_x += self.flow1[i] - self.flow0[i]

    def get_spacer(self, i):
        left, top, right, bottom = self.style['padding']
        y0 = self.offset0[i]
        y1 = self.offset1[i]
        return self.left + left, self.top + y0+top, self.width - right-left, y1-y0

class Intron(Box):
    def __init__(self, source, index, generator):
        self.source    = source
        self.index     = index
        self.generator = generator
        self.rebuild()

    def rebuild(self):
        self.node, self.style = self.generator(self.source)

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

    def render(self):
        background = self.style['background']
        if background:
            background(self)
        self.node.render()

    def pick(self, (x,y), hits=None):
        if hits == None:
            hits = []
        if 0 <= x - self.left < self.width and 0 <= y - self.top < self.height:
            hits.append(self)
        return self.node.pick((x,y), hits)

    def subintrons(self, res=None):
        if res == None:
            return self.node.subintrons([])
        else:
            res.append(self)
            return res

    def find_context(self, intron):
        if intron == self:
            return ()
        for subintron in self.subintrons():
            match = subintron.find_context(intron)
            if match is not None:
                return (self,) + match

    def traverse(self, res, cond):
        if cond(self):
            res.append(self)
        return self.node.traverse(res, cond)

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

def solve(root, (left, top)):
    root.measure(None)
    root.arrange(None, (left, top))
