version = 0, 0, 0

class string(object):
    dtype = 1
    parent = None
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data
        self.indices = len(data)+1

def reparent(children, parent):
    for child in children:
        child.parent = parent
    return children

class block(object):
    dtype = 0
    parent = None
    def __init__(self, tag, children):
        self.tag = tag
        self.children = reparent(children, self)
        self.indices = count_indices(children)

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def collapse(self):
        return [shard(0,self.tag)] + self.children + [shard(1,self.tag)]
        
class lshard(object):
    dtype = 2
    parent = None    
    indices = 0
    def __init__(self, tag):
        self.tag = tag
        
class rshard(object):
    dtype = 3
    parent = None    
    indices = 0
    def __init__(self, tag):
        self.tag = tag

class document(object):
    dtype = 15
    def __init__(self, tag, children):
        self.tag = tag
        self.children = reparent(children, self)
        self.indices = count_indices(children)

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

is_leaf = lambda(element): element.dtype == string.dtype

def count_indices(elements):
    indices = 0
    was_leaf = False
    for element in elements:
        leaf = is_leaf(element)
        if not (leaf or was_leaf):
            indices += 1
        indices += element.indices
        was_leaf = leaf
    if not was_leaf:
        indices += 1
    return indices
