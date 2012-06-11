from document import can_walk_down, copy

class Selection(object):
    def __init__(self, buf):
        self.buf = buf
        self.document = buf.document
        self.finger = ()
        self.cursor = 0
        self.tail = 0

    def _get_start(self):
        return min(self.cursor, self.tail)
    def _get_stop(self):
        return max(self.cursor, self.tail)
    def _set_start(self, value):
        if self.cursor < self.tail:
            self.cursor = value
        else:
            self.tail = value

    def _set_stop(self, value):
        if self.cursor < self.tail:
            self.tail = value
        else:
            self.cursor = value

    start = property(_get_start, _set_start)
    stop = property(_get_stop, _set_stop)
    top = property(lambda self: self.document.traverse(self.finger))
    context = property(lambda self: self.document.context(self.finger))

    def isinside(self, index):
        return 0 <= index <= len(self.top)

    def can_descend(self, index):
        return can_walk_down(self.document, self.finger, index)

    def can_ascend(self):
        return len(self.finger) > 0

    def yank(self):
        return copy(self.document.traverse(self.finger)[self.start:self.stop])
