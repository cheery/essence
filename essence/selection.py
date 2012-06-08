class Selection(object):
    def __init__(self, buf):
        self.buf = buf
        self.document = buf.document
        self.finger = ()
        self.cursor = 0
        self.tail = 0

    start = property(lambda self: min(self.cursor, self.tail))
    stop = property(lambda self: max(self.cursor, self.tail))
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
