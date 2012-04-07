version = 0, 0, 0

class string(object):
    dtype = 1
    parent = None
    span = 0
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data

    def copy(self):
        return string(self.tag, self.data)

    def partition(self, *indices):
        out = []
        last = 0
        for index in indices:
            out.append(string(self.tag, self.data[last:index]))
            last = index
        return out + [string(self.tag, self.data[last:])]

    def __add__(self, other):
        if not isinstance(other, string):
            raise Exception("cannot join")
        tag = tagmerge(self.tag, other.tag)
        return string(tag, self.data + other.data)

    def __radd__(self, other):
        if not isinstance(other, string):
            raise Exception("cannot join")
        tag = tagmerge(self.tag, other.tag)
        return string(tag, other.data + self.data)

    def __and__(self, other):
        return isinstance(other, string)

    def __rand__(self, other):
        return isinstance(other, string)
    
    def __repr__(self):
        return 'string(%r,%r)' % (self.tag, self.data)

class block(object):
    dtype = 0
    parent = None
    def __init__(self, tag, children):
        self.tag = tag
        self.children = reparent(children, self)
        self.span = count_span(children)

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def index(self, element):
        return self.children.index(element)

    def copy(self):
        return block(self.tag, dup(self))

    def __repr__(self):
        return 'block(%r,%r)' % (self.tag, self.children)

class lshard(object):
    dtype = 2
    parent = None    
    span = 0
    def __init__(self, tag):
        self.tag = tag

    def copy(self):
        return lshard(self.tag)
        
class rshard(object):
    dtype = 3
    parent = None    
    span = 0
    def __init__(self, tag):
        self.tag = tag

    def copy(self):
        return rshard(self.tag)

class document(object):
    dtype = 15
    def __init__(self, tag, children):
        self.tag = tag
        self.children = reparent(children, self)
        self.span = count_span(children)

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def index(self, element):
        return self.children.index(element)

    def copy(self):
        return document(self.tag, dup(self))

def count_span(elements):
    span = sum(element.span for element in elements)
    span += len(elements) + 1
    return span

def dup(elements):
    return [element.copy() for element in elements]

def reparent(children, parent):
    for child in children:
        child.parent = parent
    return children

def tagmerge(tag0, tag1):
    if tag0 == tag1 or u'' in (tag0,tag1):
        return tag0 or tag1
    return u''
