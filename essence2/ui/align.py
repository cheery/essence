def center(parent, child, axis):
    box = parent.inset
    if axis == 'x':
        return (box.left + box.right  == child.box.left + child.box.right)
    if axis == 'y':
        return (box.top  + box.bottom == child.box.top  + child.box.bottom)
    raise Exception("bad axis %r" % axis)

def left(parent, child, axis):
    box = parent.inset
    if axis == 'x':
        return (box.left == child.box.left)
    raise Exception("bad axis %r" % axis)

def right(parent, child, axis):
    box = parent.inset
    if axis == 'x':
        return (box.right == child.box.right)
    raise Exception("bad axis %r" % axis)

def top(parent, child, axis):
    box = parent.inset
    if axis == 'y':
        return (box.top == child.box.top)
    raise Exception("bad axis %r" % axis)

def bottom(parent, child, axis):
    box = parent.inset
    if axis == 'y':
        return (box.bottom == child.box.bottom)
    raise Exception("bad axis %r" % axis)

def low(parent, child, axis):
    box = parent.inset
    if axis == 'x':
        fork0, fork1 = parent.hfork, child.hfork
    elif axis == 'y':
        fork0, fork1 = parent.vfork, child.vfork
    else:
        raise Exception("bad axis %r" % axis)
    return (fork0.low == fork1.low)

def middle(parent, child, axis):
    box = parent.inset
    if axis == 'x':
        fork0, fork1 = parent.hfork, child.hfork
    elif axis == 'y':
        fork0, fork1 = parent.vfork, child.vfork
    else:
        raise Exception("bad axis %r" % axis)
    return (fork0.middle == fork1.middle)

def high(parent, child, axis):
    box = parent.inset
    if axis == 'x':
        fork0, fork1 = parent.hfork, child.hfork
    elif axis == 'y':
        fork0, fork1 = parent.vfork, child.vfork
    else:
        raise Exception("bad axis %r" % axis)
    return (fork0.high == fork1.high)
