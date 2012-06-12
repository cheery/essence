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
import json

## structural nodes, these make up a document

# node directly consists from just nodes and characters.

class node(object):
    """
    A document node. May contain characters and other nodes.
    """
    def __init__(self, children, tag=None, uid=0):
        self.children = children
        self.tag = tag
        self.uid = uid

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def __setitem__(self, index, value):
        self.children[index] = value

    def context(self, finger):
        res = [self]
        for index in finger:
            self = self[index]
            res.append(self)
        return res

    def traverse(self, finger):
        for index in finger:
            self = self[index]
        return self

    def copy(self):
        children = [copy(child) for child in self]
        return node(children, self.tag, self.uid)

    def cluster(self):
        string = ''
        for child in self:
            if isinstance(child, node):
                if len(string) > 0:
                    yield string
                    string = ''
                yield child
            else:
                string += child

def copy(tree):
    """
    Make an unique copy of the entire tree.
    """
    if isinstance(tree, node):
        return tree.copy()
    return tree

## change records, as concatenated, they represent changes on a document

class splice(object):
    """
    Replace (finger)[start:stop] with blob.
    """
    def __init__(self, start, stop, blob):
        self.start = start
        self.stop = stop
        self.blob = blob

    def __call__(self, blob):
        drop = map(copy, blob[self.start:self.stop])
        blob[self.start:self.stop] = map(copy, self.blob)
        return splice(self.start, self.start + len(self.blob), drop)

class build(object):
    """
    Build (finger)[start:stop] into a <node tag, uid>
    """
    def __init__(self, start, stop, tag=None, uid=None):
        self.start = start
        self.stop = stop
        self.tag = tag
        self.uid = uid

    def __call__(self, blob):
        blob[self.start:self.stop] = [node(blob[self.start:self.stop], self.tag, self.uid)]
        return collapse(self.start)

class collapse(object):
    """
    Collapse (finger)[offset]
    """
    def __init__(self, offset):
        self.offset = offset

    def __call__(self, blob):
        collapse = blob[self.offset]
        blob[self.offset:self.offset+1] = collapse
        return build(self.offset, len(collapse), collapse.tag, collapse.uid)

class rename(object):
    """
    Rename context topmost (finger)
    """
    def __init__(self, tag=None, uid=None):
        self.tag = tag
        self.uid = uid

    def __call__(self, element):
        prev_tag = prev_uid = None
        if self.tag is not None:
            prev_tag = element.tag
            element.tag = self.tag
        if self.uid is not None:
            prev_uid = element.uid
            element.uid = self.uid
        return rename(prev_tag, prev_uid)

# application of change record:     undo = do(tree.traverse(finger))
can_walk_up = lambda tree, finger: len(finger) > 0
can_walk_left = lambda tree, finger, index: index > 0
can_walk_right = lambda tree, finger, index: index < len(tree.traverse(finger))

def can_walk_down(tree, finger, index):
    there = tree.traverse(finger)
    return 0 <= index < len(there) and isinstance(there[index], node)

def serialize(tree):
    """
    Convert essence document into json string dump.
    """
    def break_to_lists(obj):
        if isinstance(obj, node):
            return {
                "tag":obj.tag,
                "uid":obj.uid,
                "blob":[break_to_lists(child) for child in obj],
            }
        if isinstance(obj, list):
            return [break_to_lists(child) for child in obj]
        return obj
    return json.dumps(break_to_lists(tree))

def deserialize(data):
    """
    Convert json string dump into essence document.
    """
    def wrap_to_nodes(this):
        if isinstance(this, dict):
            return node([wrap_to_nodes(child) for child in this["blob"]], this["tag"], this["uid"])
        if isinstance(this, list):
            return [wrap_to_nodes(child) for child in this]
        return this
    return wrap_to_nodes(json.loads(data))
