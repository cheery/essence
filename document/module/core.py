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
