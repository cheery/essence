from storage import load, save
from core import string, block, lshard, rshard, document
from transform import flat, segment, splice, retag, wrap, collapse

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

def search_finger(elements, finger):
    current = 0
    was_leaf = False
    for index, element in enumerate(elements):
        if not (element.leaf or was_leaf):
            if current == finger:
                return 'edge', index, None
            current += 1
        if current <= finger < current + element.fingers:
            if element.leaf:
                return 'leaf', index, finger - current
            else:
                return 'block', index, finger - current
        current += element.fingers
        was_leaf = element.leaf
    if not was_leaf and current == finger:
        return 'edge', index+1, None
    return None

#    current = document
#    current_base = 0
#    type0, index0, offset0 = None, None, None
#    while not type0 in ('leaf', 'edge'):
#        type0, index0, offset0 = search_finger(current.children, start - base)
#        if type0 == 'block':
#            base = start - offset0
#            block = current.children[index0]
#            if stop - base < block.fingers:
#                current = block
#                current_base = base
#            else:
#                current.children[index0:index0+1] = block.collapse()
#    while not type1 in ('leaf', 'edge'):
#        type1, index1, offset1 = search_finger(current.children, start - base)
#        if type1 == 'block':
#            current.children[index1:index1+1] = current.children[index1].collapse()
#    if type0 == type1 == 'leaf' and index0 == index1:
#        simple_splice
#    cutaway0 = index0
#    cutaway1 = index1 + (type1 == 'leaf')
#    cutaway = children[cutaway0:cutaway1]
#    partition0 = cutaway.pop(0) if type0 == 'leaf' else None
#    partition1 = cutaway.pop(-1) if type1 == 'leaf' else None
#    if typeof(data) == typeof(partition0) == typeof(partition1):
#        special_splice
#    else:
#        cut_partitions_and_normal_splice

# [INTERNAL DETAIL] This is what selection looks like.
# i:n

# (None, [], 0)
# ('string', [0], 0)


# find the block, where start and stop starts diverging (count the depth as well)
# go back a bit if the block was a leaf.

# collapse the remaining blocks from where start/stop are diverging.
# recalculate start/stop (sum(path) + len(path))

# reparent and insert the collapse result of blocks.

# remove items appropriately, recover start/stop leaf blocks if there are those.

# if start/stop and data matches
#   insert and reparent a produced merge
#   if start==stop, return a string data
# otherwise (or if data=None)
#   retrieve splitted versions and put data between them.
#   insert and reparent the thing back in.

# - data removed should be reparented.
# - data inserted should be re-copied.
# - if block split results in empty block, then the block should be removed.



# there is a straightforward way to recalculate fingers after a splice,
# because the splicing alters the space regularly.

# - everything outside diverging point stays same.
# - everything inside diverging path gets flattened
# - everything between gets removed
# - insert grows the containers in regular style

# - edge is a valid index only if it's neighbours aren't string blocks.



# there's two additional commands with splice: repair and retag
