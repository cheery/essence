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
    def __init__(self, children, tag=None, uid=None):
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
        return obj
    return json.dumps(break_to_lists(tree))

def deserialize(data):
    """
    Convert json string dump into essence document.
    """
    def wrap_to_nodes(this):
        if isinstance(this, dict):
            return node([wrap_to_nodes(child) for child in this["blob"]], this["tag"], this["uid"])
        return this
    return wrap_to_nodes(json.loads(data))
