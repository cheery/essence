class AlignByFlow(object):
    def __init__(self, h, v = None):
        self.h = h
        self.v = h if v is None else v

    def __call__(self, node, edge):
        if edge in ('top', 'bottom'):
            return node.flowline(edge, self.h)
        if edge in ('left', 'right'):
            return node.flowline(edge, self.v)

def simple(node, (low, high), edge, which):
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
