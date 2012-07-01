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
from util import makelist, pull, push

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
        return index < len(top) and isinstance(top[index], element)

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

    def splice(self, data):
        length = len(data)
        operation = splice(self.start, self.stop, data)
        self.buffer.do(self.finger, operation)
        return Selection(
            self.buffer,
            self.finger,
            self.start + length,
            self.start + length,
        )
        # SPLICE (text, elements, range)

    def move(self, offset, selection=False, relative=True):
        cursor = self.top.clamp(relative*self.cursor + offset)
        tail = self.tail if selection else cursor
        return Selection(self.buffer, self.finger, cursor, tail)

    @property
    def ascend(self):
        finger, cursor = pull(self.finger)
        return Selection(self.buffer, finger, self.cursor, self.tail).grasp(cursor, cursor+1)

    def descend(self, base):
        finger = push(self.finger, base)
        start, stop = 0, len(self.top[base])
        return Selection(self.buffer, finger, self.cursor, self.tail).grasp(start,stop)

    def build(self, outside=False, kw=None):
        kw = {'which':'scratch'} if kw is None else kw
        start = self.start
        stop = self.stop
        operation = build(start, stop, kw)
        self.buffer.do(self.finger, operation)
        if outside:
            finger = self.finger
            stop = start + 1
        else:
            finger = push(self.finger, start)
            start -= start
            stop -= start
        return Selection(self.buffer, finger, self.cursor, self.tail).grasp(start, stop)
        # BUILD (with selection and type)

    def collapse(self):
        finger, base = pull(self.finger)
        start = self.start + base
        stop = self.stop + base
        operation = collapse(base)
        self.buffer.do(finger, operation)
        return Selection(self.buffer, finger, start, stop)
        # COLLAPSE
        
    def modify(self, kw):
        self.buffer.do(self.finger, modify(kw))
        return self
        # MODIFY

    @property
    def bounds(self):
        top = self.top
        cursor = self.cursor - 1

        while cursor > 0:
            if isinstance(top[cursor], element):
                break
            if isinstance(top[cursor-1], element):
                break
            cursor -= 1
        start = cursor

        cursor = self.cursor + 1
        while cursor < len(top):
            if isinstance(top[cursor], element):
                break
            if isinstance(top[cursor-1], element):
                break
            cursor += 1
        stop = cursor

        return start, stop

    @property
    def textbounds(self):
        top = self.top
        cursor = self.cursor
        while cursor > 0:
            if isinstance(top[cursor-1], element):
                break
            cursor -= 1
        start = cursor

        while cursor < len(top):
            if isinstance(top[cursor], element):
                break
            cursor += 1
        stop = cursor

        return start, stop

    def walk_backward(self):
        top = self.top
        cursor = self.cursor
        if cursor == 0:
            if self.ascendable:
                finger, cursor = pull(self.finger)
                return Selection(self.buffer, finger, cursor, cursor)
            return self
        elif isinstance(top[cursor-1], element):
            finger = push(self.finger, cursor-1)
            cursor = len(top[cursor-1])
            return Selection(self.buffer, finger, cursor, cursor)
        else:
            cursor = self.bounds[0]
            return Selection(self.buffer, self.finger, cursor, cursor)

    def walk_forward(self):
        top = self.top
        cursor = self.cursor
        if cursor >= len(top):
            if self.ascendable:
                finger, cursor = pull(self.finger)
                return Selection(self.buffer, finger, cursor+1, cursor+1)
            return self
        elif isinstance(top[cursor], element):
            finger = push(self.finger, cursor)
            cursor = 0
            return Selection(self.buffer, finger, cursor, cursor)
        else:
            cursor = self.bounds[1]
            return Selection(self.buffer, self.finger, cursor, cursor)
        # NAVIGATE (UP, DOWN, LEFT+[SH], RIGHT+[SH], LB, RB)

    def grasp(self, start, stop):
        if self.cursor < self.tail:
            cursor, tail = start, stop
        else:
            tail, cursor = start, stop
        return Selection(self.buffer, self.finger, cursor, tail)
