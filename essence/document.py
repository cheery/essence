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
"""
    essence.document
    ~~~~~~~~~~~~~~~~

    Document model for essence.
"""
from util import makelist

def editlength(obj):
    if obj == None:
        return 1
    return 1 if iselement(obj) else len(obj)

def merge(a, b):
    if len(a) > 0 and len(b) > 0 and not (iselement(a[-1]) or iselement(b[0])):
        return a + [a.pop(-1) + b.pop(0)] + b
    return a + b

class star(object):
    def __init__(self, a):
        self.a = a

    @staticmethod
    def empty():
        return star([])

    def copy(self):
        return self.__class__(copyList(self.a))

    @property
    def first(self):
        return 0

    @property
    def last(self):
        return sum(editlength(obj) for obj in self.a)

    @makelist
    def slice(self, start, stop):
        if start==stop:
            return
        for obj in self.a:
            length = editlength(obj)
            if start <= 0 and length <= stop:
                yield obj
            elif 0 < start < length or length > stop > 0:
                yield obj[max(start,0):min(stop,length)]
            start -= length
            stop -= length

    def splice(self, start, stop, data):
        head = self.slice(0, start)
        drop = self.slice(start, stop)
        tail = self.slice(stop, self.last)
        self.a = merge(merge(head, data), tail)
        return drop

    @property
    def partials(self):
        base = 0
        for obj in self.a:
            length = editlength(obj)
            yield holepartial(self, base, base+length, obj)
            base += length

class dot(object):
    def __init__(self, a):
        self.a = a

    @staticmethod
    def empty():
        return dot(None)

    def copy(self):
        return self.__class__(copy(self.a))

    def replace(self, data):
        assert len(data) == 1
        assert editlength(data[0]) == 1
        drop = [self.a]
        self.a = data[0]
        return drop

class element(object):
    def __init__(self, name, holes):
        self.name = name
        self.holes = holes

    def copy(self):
        return self.__class__(self.name, [hole.copy() for hole in self.holes])

    def __len__(self):
        return len(self.holes)

    def __iter__(self):
        for hole in self.holes:
            yield hole.a

    def as_string(self, index):
        return ''.join(self.holes[index].a)

    def __getitem__(self, index):
        return self.holes[index].a

def iselement(obj):
    return isinstance(obj, element)

def empty_template(name, *holes):
    return element(name, [hole.empty() for hole in holes])

def filled_template(name, *holes):
    return element(name, [hole for hole in holes])

class replace(object):
    def __init__(self, data):
        self.data = data

    def apply(self, hole):
        drop = copy(hole.replace(self.data))
        return replace(drop)

class holepartial(object):
    def __init__(self, hole, start, stop, a):
        self.hole = hole
        self.start = start
        self.stop = stop
        self.a = a

class dotmarker(object):
    dot = True
    def __init__(self, hole, visited):
        self.hole = hole
        self.visited = visited

    def replace(self, data):
        return self.hole.replace(data)

    def test(self, hole):
        return self.hole == hole

    @property
    def at_top(self):
        return self.visited == False

    @property
    def at_bottom(self):
        return self.visited == True

    @property
    def yank(self):
        return copyList([self.hole.a])

class starmarker(object):
    dot = False
    def __init__(self, hole, cursor, tail):
        self.hole = hole
        self.cursor = cursor
        self.tail = tail
        self.start = min(cursor, tail)
        self.stop = max(cursor, tail)

    def replace(self, data):
        return self.hole.splice(self.start, self.stop, data)

    def test(self, hole):
        return self.hole == hole.hole if isinstance(hole, holepartial) else False

    def test2(self, hole):
        return self.hole == hole

    @property
    def at_top(self):
        return self.hole.first == self.cursor

    @property
    def at_bottom(self):
        return self.hole.last == self.cursor

    @property
    def yank(self):
        return copyList(self.hole.slice(self.start, self.stop))

#from util import makelist
#
#class element(object):
#    """Makes up a document. Consists of child elements and characters"""
#    def __init__(self, children, attributes):
#        self.children = children
#        self.attributes = attributes
#
#    def __len__(self):
#        return len(self.children)
#
#    def __iter__(self):
#        return iter(self.children)
#
#    def __getitem__(self, index):
#        return self.children[index]
#
#    def __setitem__(self, index, value):
#        self.children[index] = value
#
#    @property
#    def clusters(self):
#        string = ''
#        for child in self:
#            if isinstance(child, element):
#                if len(string) > 0:
#                    yield string
#                    string = ''
#                yield child
#            else:
#                string += child
#        if len(string) > 0:
#            yield string
#            string = ''
#
#    @property
#    def blocks(self):
#        offset = 0
#        for cluster in self.clusters:
#            length = 1 if isinstance(cluster, element) else len(cluster)
#            yield (offset, offset+length), cluster
#            offset += length
#
#    def copy(self):
#        return element(copyList(self), self.attributes)
#
#    def get(self, key, default=None):
#        return self.attributes.get(key, default)
#
#    @property
#    def string(self):
#        return ''.join(self)
#
#    @property
#    def array(self):
#        for cluster in self.clusters:
#            if isinstance(cluster, element):
#                if cluster.get('which') == 'scratch':
#                    continue
#            yield cluster
#
#    @makelist
#    def context(self, finger):
#        current = self
#        yield current
#        for index in finger:
#            current = current[index]
#            yield current
#
#    def isinside(self, index, strict=False):
#        return 0 <= index <= len(self)-strict
#
#    def clamp(self, index, strict=False):
#        return min(max(0, index), len(self)-strict)
#
def copy(tree):
    """Make an unique copy of the entire tree."""
    if isinstance(tree, element):
        return tree.copy()
    return tree

def copyList(list):
    """copy elements in a list or other sequence."""
    return [copy(child) for child in list]
#
### change records, as concatenated, they represent changes on a document
##
#class splice(object):
#    """Replace selection with a blob"""
#    def __init__(self, start, stop, blob):
#        self.start = start
#        self.stop = stop
#        self.blob = blob
#
#    def __call__(self, this):
#        deleted = copyList(this[self.start:self.stop])
#        this[self.start:self.stop] = copyList(self.blob)
#        return splice(self.start, self.start + len(self.blob), deleted)
#
#class build(object):
#    """Build an element around selection"""
#    def __init__(self, start, stop, attributes):
#        self.start = start
#        self.stop = stop
#        self.attributes = attributes
#
#    def __call__(self, this):
#        this[self.start:self.stop] = [element(this[self.start:self.stop], self.attributes)]
#        return collapse(self.start)
#
#class collapse(object):
#    """Collapse element after offset"""
#    def __init__(self, offset):
#        self.offset = offset
#
#    def __call__(self, this):
#        deleted = this[self.offset]
#        this[self.offset:self.offset+1] = deleted
#        return build(self.offset, len(deleted), deleted.attributes)
#
#class modify(object):
#    """Modify element attributes"""
#    def __init__(self, attributes):
#        self.attributes = attributes
#
#    def __call__(self, this):
#        old_attributes = this.attributes
#        this.attributes = self.attributes
#        return modify(old_attributes)
