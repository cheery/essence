class Buffer(object):
    def __init__(self, document, history, root_frame=None, sel=None, filename=None):
        self.document = document
        self.history = history
        self.root_frame = root_frame
        self.sel = sel
        self.filename = filename
        self.moid = self.prev_moid = 0
        self.next_moid = 1

    @property
    def caption(self):
        return (self.filename or "[No Name]") + (' [+]' if self.modified else '')

    @property
    def modified(self):
        return self.moid != self.prev_moid

    def __call__(self, screen, construct_frame):
        if self.root_frame is None:
            self.root_frame = construct_frame(self.document)
        return self.root_frame

    def do(self, finger, operation):
        assert self.sel.finger == finger # don't do this later >:-(
        sel = self.sel
        location = sel.finger, sel.cursor, sel.tail
        self.document.traverse(finger)
        reverse = self.moid, finger, operation(self.document.traverse(finger)), location
        h0, h1 = self.history
        h0.append(reverse)
        self.history = h0, []
        self.root_frame = None # less destructive update might be in place later.
        self.moid = self.next_moid
        self.next_moid += 1

    def undo(self):
        sel = self.sel
        location = sel.finger, sel.cursor, sel.tail
        h0, h1 = self.history
        moid, finger, operation, (sel.finger, sel.cursor, sel.tail) = h0.pop(-1)
        reverse = self.moid, finger, operation(self.document.traverse(finger)), location
        h1.append(reverse)
        self.moid = moid
        self.root_frame = None

    def redo(self):
        sel = self.sel
        location = sel.finger, sel.cursor, sel.tail
        h0, h1 = self.history
        if len(h1) == 0:
            return False
        moid, finger, operation, (sel.finger, sel.cursor, sel.tail) = h1.pop(-1)
        reverse = self.moid, finger, operation(self.document.traverse(finger)), location
        h0.append(reverse)
        self.moid = moid
        self.root_frame = None
        return True

    def save(self, path=None): # this saving method cannot be trusted, although it tries to not crash.
        path = self.filename if path is None else path
        if path is None:
            return False
        data = serialize(self.document)
        fd = open(path, 'w')
        fd.write(data)
        fd.close()
        if path == self.filename:
            self.prev_moid = self.moid
        return True
