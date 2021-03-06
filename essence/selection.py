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
from document import editlength, star, dot, element, iselement, empty_template, filled_template, replace, copy, copyList, dotmarker, starmarker, holepartial
from random import randint
from util import makelist, pull, push

def clamp(star, base):
    return max(star.first, min(base, star.last))

def mark0(hole):
    if isinstance(hole, dot):
        return dotmarker(hole, False)
    if isinstance(hole, star):
        return starmarker(hole, 0, 0)
    if isinstance(hole, holepartial):
        return starmarker(hole.hole, hole.start, hole.start)

def mark1(hole):
    if isinstance(hole, dot):
        return dotmarker(hole, True)
    if isinstance(hole, star):
        cursor = hole.last
        return starmarker(hole, cursor, cursor)
    if isinstance(hole, holepartial):
        return starmarker(hole.hole, hole.stop, hole.stop)

def mark2(hole):
    if isinstance(hole, dot):
        return dotmarker(hole, True)
    if isinstance(hole, star):
        return starmarker(hole, hole.last, hole.first)
    if isinstance(hole, holepartial):
        return starmarker(hole.hole, hole.stop, hole.start)

def first_marker(obj):
    if iselement(obj) and len(obj.holes) > 0:
        return mark0(obj.holes[0])

def last_marker(obj):
    if iselement(obj) and len(obj.holes) > 0:
        return mark1(obj.holes[-1])

class Selection(object):
    def __init__(self, buffer, path, parent, marker):
        self.buffer = buffer
        self.path = list(path)
        self.parent = parent
        self.marker = marker

    def remove(self):
        if self.marker.dot:
            self.buffer.do(self.marker, replace([None]))
        else:
            self.replace([])

    def replace(self, data, branch_in=False):
        length = sum(editlength(obj) for obj in data)
        self.buffer.do(self.marker, replace(data))
        if self.marker.dot:
            self.marker = dotmarker(self.marker.hole, visited = not branch_in)
        else:
            cursor = self.marker.start + length * (not branch_in)
            self.marker = starmarker(self.marker.hole, cursor, cursor)
        if branch_in:
            self.walk()

    # works only if there's starmarker
    def move(self, offset, selection=False, relative=True):
        if not self.marker.dot:
            cursor = clamp(self.marker.hole, relative*self.marker.cursor + offset)
            tail = self.marker.tail if selection else cursor
            self.marker = starmarker(self.marker.hole, cursor, tail)

    @property
    def empty(self):
        marker = self.marker
        if isinstance(marker, starmarker):
            return marker.start == marker.stop
        return False

    @property
    def bounds(self):
        marker = self.marker
        start0, stop0 = marker.hole.last, marker.hole.first
        for partial in marker.hole.partials:
            start1, stop1 = partial.start, partial.stop
            if start1 <= marker.cursor <= stop1:
                start0 = min(start0, start1)
                stop0 = max(stop0, stop1)
        return start0, stop0

    def walk(self):
        marker = self.marker
        parent = self.parent
        if marker.dot and marker.at_top:
            new_marker = first_marker(marker.hole.a)
            if new_marker is not None:
                self.path.append((self.parent, marker.hole))
                self.parent = marker.hole.a
                self.marker = new_marker
                return
            marker = mark1(marker.hole)
        if marker.at_bottom:
            index = parent.holes.index(marker.hole)
            if index + 1 < len(self.parent.holes):
                self.marker = mark0(parent.holes[index + 1])
            elif len(self.path) > 0:
                parent, partial = self.path.pop(-1)
                self.parent = parent
                self.marker = mark1(partial)
            return
        if marker.dot:
            return
        for partial in marker.hole.partials:
            if partial.start <= marker.cursor < partial.stop:
                new_marker = first_marker(partial.a)
                if new_marker is None:
                    self.move(partial.stop, relative=False)
                    return
                else:
                    self.path.append((self.parent, partial))
                    self.parent = partial.a
                    self.marker = new_marker
                    return

    def walk_backwards(self):
        marker = self.marker
        parent = self.parent
        if marker.dot and marker.at_bottom:
            new_marker = last_marker(marker.hole.a)
            if new_marker is not None:
                self.path.append((self.parent, marker.hole))
                self.parent = marker.hole.a
                self.marker = new_marker
                return
            marker = mark0(marker.hole)
        if marker.at_top:
            index = parent.holes.index(marker.hole)
            if index > 0:
                self.marker = mark1(parent.holes[index - 1])
            elif len(self.path) > 0:
                parent, partial = self.path.pop(-1)
                self.parent = parent
                self.marker = mark0(partial)
            return
        for partial in marker.hole.partials:
            if partial.start < marker.cursor <= partial.stop:
                new_marker = last_marker(partial.a)
                if new_marker is None:
                    self.move(partial.start, relative=False)
                    return
                else:
                    self.path.append((self.parent, partial))
                    self.parent = partial.a
                    self.marker = new_marker
                    return

    def select_parent(self, mark=mark2):
        if len(self.path) > 0:
            self.parent, hole = self.path.pop(-1)
            self.marker = mark(hole)
            return True
        return False

    def expand(self):
        marker = self.marker
        if marker.dot or (marker.start == marker.hole.first and marker.stop == marker.hole.last):
            self.select_parent()
        else:
            tail_loc = marker.cursor < marker.tail
            tail = (marker.hole.first, marker.hole.last)[tail_loc]
            cursor = (marker.hole.first, marker.hole.last)[not tail_loc]
            self.marker = starmarker(marker.hole, cursor, tail)

    def at_leaf(self):
        if self.marker.dot:
            obj = self.marker.hole.a
            if obj is None or len(obj.holes) == 0:
                return True
        return False


#class Selection(object):
#    def __init__(self, buffer, finger, cursor, tail):
#        self.buffer = buffer
#        self.finger = finger
#        self.cursor = cursor
#        self.tail = tail
#
#    @property
#    def start(self):
#        return min(self.cursor, self.tail)
#
#    @property
#    def stop(self):
#        return max(self.cursor, self.tail)
#
#    @property
#    def top(self):
#        return self.buffer.document.context(self.finger)[-1]
#
#    @property
#    def ascendable(self):
#        return len(self.finger) > 0
#
#    def descendable(self, index):
#        top = self.top
#        return index < len(top) and isinstance(top[index], element)
#
#    @property
#    def yank(self):
#        return copyList(self.top[self.start:self.stop])
#
#    @property
#    @makelist
#    def frame_context(self):
#        current = self.buffer.visual
#        it = iter(self.finger)
#        while current is not None:
#            yield current
#            index = it.next()
#            next = None
#            for frame in current.find():
#                base, _ = frame.range
#                if base == index:
#                    next = frame
#            current = next
#
#    def splice(self, data):
#        length = len(data)
#        operation = splice(self.start, self.stop, data)
#        self.buffer.do(self.finger, operation)
#        return Selection(
#            self.buffer,
#            self.finger,
#            self.start + length,
#            self.start + length,
#        )
#        # SPLICE (text, elements, range)
#
#    @property
#    def ascend(self):
#        finger, cursor = pull(self.finger)
#        return Selection(self.buffer, finger, self.cursor, self.tail).grasp(cursor, cursor+1)
#
#    def descend(self, base):
#        finger = push(self.finger, base)
#        start, stop = 0, len(self.top[base])
#        return Selection(self.buffer, finger, self.cursor, self.tail).grasp(start,stop)
#
#    def build(self, outside=False, kw=None):
#        kw = {'which':'scratch'} if kw is None else kw
#        start = self.start
#        stop = self.stop
#        operation = build(start, stop, kw)
#        self.buffer.do(self.finger, operation)
#        if outside:
#            finger = self.finger
#            stop = start + 1
#        else:
#            finger = push(self.finger, start)
#            start -= start
#            stop -= start
#        return Selection(self.buffer, finger, self.cursor, self.tail).grasp(start, stop)
#        # BUILD (with selection and type)
#
#    def collapse(self):
#        finger, base = pull(self.finger)
#        start = self.start + base
#        stop = self.stop + base
#        operation = collapse(base)
#        self.buffer.do(finger, operation)
#        return Selection(self.buffer, finger, start, stop)
#        # COLLAPSE
#        
#    def modify(self, kw):
#        self.buffer.do(self.finger, modify(kw))
#        return self
#        # MODIFY
#
#    @property
#    def bounds(self):
#        top = self.top
#        cursor = self.cursor - 1
#
#        while cursor > 0:
#            if isinstance(top[cursor], element):
#                break
#            if isinstance(top[cursor-1], element):
#                break
#            cursor -= 1
#        start = cursor
#
#        cursor = self.cursor + 1
#        while cursor < len(top):
#            if isinstance(top[cursor], element):
#                break
#            if isinstance(top[cursor-1], element):
#                break
#            cursor += 1
#        stop = cursor
#
#        return start, stop
#
#    @property
#    def textbounds(self):
#        top = self.top
#        cursor = self.cursor
#        while cursor > 0:
#            if isinstance(top[cursor-1], element):
#                break
#            cursor -= 1
#        start = cursor
#
#        while cursor < len(top):
#            if isinstance(top[cursor], element):
#                break
#            cursor += 1
#        stop = cursor
#
#        return start, stop
#
#    def walk_backward(self):
#        top = self.top
#        cursor = self.cursor
#        if cursor == 0:
#            if self.ascendable:
#                finger, cursor = pull(self.finger)
#                return Selection(self.buffer, finger, cursor, cursor)
#            return self
#        elif isinstance(top[cursor-1], element):
#            finger = push(self.finger, cursor-1)
#            cursor = len(top[cursor-1])
#            return Selection(self.buffer, finger, cursor, cursor)
#        else:
#            cursor = self.bounds[0]
#            return Selection(self.buffer, self.finger, cursor, cursor)
#
#    def walk_forward(self):
#        top = self.top
#        cursor = self.cursor
#        if cursor >= len(top):
#            if self.ascendable:
#                finger, cursor = pull(self.finger)
#                return Selection(self.buffer, finger, cursor+1, cursor+1)
#            return self
#        elif isinstance(top[cursor], element):
#            finger = push(self.finger, cursor)
#            cursor = 0
#            return Selection(self.buffer, finger, cursor, cursor)
#        else:
#            cursor = self.bounds[1]
#            return Selection(self.buffer, self.finger, cursor, cursor)
#        # NAVIGATE (UP, DOWN, LEFT+[SH], RIGHT+[SH], LB, RB)
#
#    def grasp(self, start, stop):
#        if self.cursor < self.tail:
#            cursor, tail = start, stop
#        else:
#            tail, cursor = start, stop
#        return Selection(self.buffer, self.finger, cursor, tail)
