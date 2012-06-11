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
