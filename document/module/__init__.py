from storage import load, save
from core import string, block, lshard, rshard, document
from transform import splice, retag, wrap, unwrap

def new(content=None):
    return document('', [] if content is None else content)

def pretty_print(document):
    def do_print(element, depth):
        indent = ' '*depth
        if element.dtype == string.dtype:
            print indent + 'string %r %r ' % (element.data,element.tag)
        elif element.dtype == block.dtype:
            print indent + 'block %r' % (element.tag)
            for child in element.children:
                do_print(child, depth+2)
        elif element.dtype == lshard.dtype:
            print indent + 'lshard %r' % (element.tag)
        elif element.dtype == rshard.dtype:
            print indent + 'rshard %r' % (element.tag)
        else:
            print indent + repr(element)
    print 'document'
    for child in document.children:
        do_print(child, 2)
