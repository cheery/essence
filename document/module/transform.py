import core

class flat(object):
    def __init__(self, dtype, data):
        self.dtype = dtype
        self.data = data

class segment(object):
    def __init__(self, left, data, right):
        self.left = left
        self.right = right
        self.data = data

def make_contiguous(document, start, stop):
    base, start, stop = find_base(document, start, stop)
    path0 = traverse_finger(base, start)
    # path_collapse(path0)
    path1 = traverse_finger(base, stop)
    # path_collapse(path1)

    # while at it, return some interesting information.

def splice(document, start, stop, data):
    _ = make_contiguous(document, start, stop)
    # take apart the area you're going to work on.
    # apply 'removal' and retrieve returning flat/segment
    # apply 'insertion' and stitch the area back together.

def retag(document, start, stop):
    pass
    # find the block marked by range.
    # retag it.

def wrap(document, start, stop):
    pass
    # find the shards marked by range.
    # wrap them back together.

def collapse(document, start, stop):
    pass
    # find the block marked by range.
    # collapse it.
