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

class element(object):
    """Makes up a document. Consists of child elements and characters"""
    def __init__(self, children, attributes):
        self.children = children
        self.attributes = attributes

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def __setitem__(self, index, value):
        self.children[index] = value

    @property
    def clusters(self):
        string = ''
        for child in self:
            if isinstance(child, element):
                if len(string) > 0:
                    yield string
                    string = ''
                yield child
            else:
                string += child
        if len(string) > 0:
            yield string
            string = ''

    @property
    def blocks(self):
        offset = 0
        for cluster in self.clusters:
            length = 1 if isinstance(cluster, element) else len(cluster)
            yield (offset, offset+length), cluster
            offset += length

    def copy(self):
        return element(copyList(self), self.attributes)

    def get(self, key, default=None):
        return self.attributes.get(key, default)

    @property
    def string(self):
        return ''.join(self)

    @property
    def array(self):
        for cluster in self.clusters:
            if isinstance(cluster, element):
                if cluster.get('which') == 'scratch':
                    continue
            yield cluster

    @makelist
    def context(self, finger):
        current = self
        yield current
        for index in finger:
            current = current[index]
            yield current

    def isinside(self, index, strict=False):
        return 0 <= index <= len(self)-strict

    def clamp(self, index, strict=False):
        return min(max(0, index), len(self)-strict)

def copy(tree):
    """Make an unique copy of the entire tree."""
    if isinstance(tree, element):
        return tree.copy()
    assert len(tree) == 1
    return tree

def copyList(list):
    """copy elements in a list or other sequence."""
    return [copy(child) for child in list]

## change records, as concatenated, they represent changes on a document
#
class splice(object):
    """Replace selection with a blob"""
    def __init__(self, start, stop, blob):
        self.start = start
        self.stop = stop
        self.blob = blob

    def __call__(self, this):
        deleted = copyList(this[self.start:self.stop])
        this[self.start:self.stop] = copyList(self.blob)
        return splice(self.start, self.start + len(self.blob), deleted)

class build(object):
    """Build an element around selection"""
    def __init__(self, start, stop, attributes):
        self.start = start
        self.stop = stop
        self.attributes = attributes

    def __call__(self, this):
        this[self.start:self.stop] = [element(this[self.start:self.stop], self.attributes)]
        return collapse(self.start)

class collapse(object):
    """Collapse element after offset"""
    def __init__(self, offset):
        self.offset = offset

    def __call__(self, this):
        deleted = this[self.offset]
        this[self.offset:self.offset+1] = deleted
        return build(self.offset, len(deleted), deleted.attributes)

class modify(object):
    """Modify element attributes"""
    def __init__(self, attributes):
        self.attributes = attributes

    def __call__(self, this):
        old_attributes = this.attributes
        this.attributes = self.attributes
        return modify(old_attributes)
