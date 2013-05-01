from container import Container

class Row(Container):
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

    def spacer_rect(self, i):
        left, top, right, bottom = self.style['padding']
        x0 = self.offset0[i]
        x1 = self.offset1[i]
        return self.left + left+x0, self.top + top, x1-x0, self.height-bottom-top
