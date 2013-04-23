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
