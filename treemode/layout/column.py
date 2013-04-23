from container import Container

class Column(Container):
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

    def spacer_rect(self, i):
        left, top, right, bottom = self.style['padding']
        y0 = self.offset0[i]
        y1 = self.offset1[i]
        return self.left + left, self.top + y0+top, self.width - right-left, y1-y0
