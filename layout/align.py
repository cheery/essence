class Align(object):
    def __init__(self, h, v = None):
        self.h = h
        self.v = h if v is None else v

    def __call__(self, node, edge):
        if edge in ('top', 'bottom'):
            return node.width  * self.h
        if edge in ('left', 'right'):
            return node.height * self.v
