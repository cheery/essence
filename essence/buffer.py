# This file is part of Essential Editor Research Project (EERP)
#
# EERP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EERP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EERP.  If not, see <http://www.gnu.org/licenses/>.
from document import deserialize, serialize

class Buffer(object):
    def __init__(self, document, history, view=None, sel=None, filename=None):
        self.document = document
        self.history = history
        self.view = view
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

    def do(self, finger, operation):
        assert self.sel.finger == finger # don't do this later >:-(
        sel = self.sel
        location = sel.finger, sel.cursor, sel.tail
        self.document.traverse(finger)
        reverse = self.moid, finger, operation(self.document.traverse(finger)), location
        h0, h1 = self.history
        h0.append(reverse)
        self.history = h0, []
        self.view = None # less destructive update might be in place later.
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
        self.view = None

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
        self.view = None
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
