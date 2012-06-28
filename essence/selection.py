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
from document import element, copy, copyList, splice, build, collapse, modify
from random import randint
from util import makelist

class Selection(object):
    def __init__(self, buffer, finger, cursor, tail):
        self.buffer = buffer
        self.finger = finger
        self.cursor = cursor
        self.tail = tail

    @property
    def start(self):
        return min(self.cursor, self.tail)

    @property
    def stop(self):
        return max(self.cursor, self.tail)

    @property
    def top(self):
        return self.buffer.document.context(self.finger)[-1]

    @property
    def ascendable(self):
        return len(self.finger) > 0

    def descendable(self, index):
        top = self.top
        return isinstance(top[index], element)

    @property
    def yank(self):
        return copyList(self.top[self.start:self.stop])

    @property
    @makelist
    def frame_context(self):
        current = self.buffer.visual
        it = iter(self.finger)
        while current is not None:
            yield current
            index = it.next()
            next = None
            for frame in current.find():
                base, _ = frame.range
                if base == index:
                    next = frame
            current = next

        

#class Selection(object):
#    def __init__(self, buf):
#        self.buf = buf
#        self.document = buf.document
#        self.finger = ()
#        self.cursor = 0
#        self.tail = 0
#
#    def _get_start(self):
#        return min(self.cursor, self.tail)
#    def _get_stop(self):
#        return max(self.cursor, self.tail)
#    def _set_start(self, value):
#        if self.cursor < self.tail:
#            self.cursor = value
#        else:
#            self.tail = value
#
#    def _set_stop(self, value):
#        if self.cursor < self.tail:
#            self.tail = value
#        else:
#            self.cursor = value
#
#    start = property(_get_start, _set_start)
#    stop = property(_get_stop, _set_stop)
#    top = property(lambda self: self.document.traverse(self.finger))
#    context = property(lambda self: self.document.context(self.finger))
#
#    def isinside(self, index):
#        return 0 <= index <= len(self.top)
#
#    def can_descend(self, index):
#        return can_walk_down(self.document, self.finger, index)
#
#    def can_ascend(self):
#        return len(self.finger) > 0
#
#    def build(self, tag, uid=None):
#        uid = randint(1, 2**32) if uid is None else uid
#        sel = self
#        base = sel.start
#        sel.buf.do(sel.finger, build(sel.start, sel.stop, tag, randint(1, 10**10)))
#        sel.finger = sel.finger + (base,)
#        sel.cursor -= base
#        sel.tail -= base
#
#    def splice(self, blob):
#        self.buf.do(self.finger, splice(self.start, self.stop, blob))
#        self.tail = self.cursor = self.start + len(blob)
#
#    def __repr__(self):
#        return repr((self.start, self.stop))
