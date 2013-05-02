## I just threw these in here..
from schema.base import Constant, Struct
from schema.mutator import Mutator
from schema import proxy
from schema.selection import Selection, BufferSelection, StringSelection, ListSelection

def roll(document, path):
    current = document
    for index in path:
        if index >= len(current):
            raise Exception("something fukked up")
        current = current[index]
    return current

def select_this(document, struct):
    if isinstance(struct.proxy, proxy.StructProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return Mutator(parent, struct.proxy.index)
    elif isinstance(struct.proxy, proxy.ListProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return ListSelection(parent, struct.proxy.list_index, struct.proxy.index+1, struct.proxy.index)

def wade_to_previous(document, sel):
    if isinstance(sel, ListSelection) and sel.head > 0:
        obj = sel.struct[sel.index][sel.head - 1]
        if isinstance(obj, Struct):
            return climb_tail(obj, len(obj) - 1)
        else:
            return sel.__class__(sel.struct, sel.index, sel.head - 1)
    else:
        return skip_to_previous(document, sel.struct, sel.index)

def wade_to_next(document, sel):
    if isinstance(sel, ListSelection) and sel.head < sel.length:
        obj = sel.struct[sel.index][sel.head]
        if isinstance(obj, Struct):
            return climb_head(obj, 0)
        else:
            return sel.__class__(sel.struct, sel.index, sel.head + 1)
    else:
        return skip_to_next(document, sel.struct, sel.index)

def skip_to_previous(document, struct, index):
    if index > 0:
        return climb_tail(struct, index - 1)
    elif isinstance(struct.proxy, proxy.StructProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return skip_to_previous(document, parent, struct.proxy.index)
    elif isinstance(struct.proxy, proxy.ListProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return ListSelection(parent, struct.proxy.list_index, struct.proxy.index)
    assert(struct.proxy is not None)

def skip_to_next(document, struct, index):
    if index + 1 < len(struct):
        return climb_head(struct, index + 1)
    elif isinstance(struct.proxy, proxy.StructProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return skip_to_next(document, parent, struct.proxy.index)
    elif isinstance(struct.proxy, proxy.ListProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return ListSelection(parent, struct.proxy.list_index, struct.proxy.index + 1)
    assert(struct.proxy is not None)

def deep_climb_head(struct, index, head):
    obj = struct[index]
    if isinstance(obj, Struct):
        return deep_climb_head(obj, 0, 0)
    elif isinstance(obj, list) and head < len(obj) and isinstance(obj[head], Struct):
        return deep_climb_head(obj[head], 0, 0)
    elif isinstance(obj, list):
        sel = ListSelection(struct, index, min(head, len(obj)))
    elif isinstance(obj, str):
        sel = BufferSelection(struct, index, min(head, len(obj)))
    elif isinstance(obj, unicode):
        sel = StringSelection(struct, index, min(head, len(obj)))
    else:
        sel = Mutator(struct, index)
    return sel

def climb_head(struct, index):
    current = struct
    while isinstance(current[index], Struct):
        current = current[index]
        index = 0
    obj = current[index]
    if isinstance(obj, list):
        sel = ListSelection(current, index, 0)
    elif isinstance(obj, str):
        sel = BufferSelection(current, index, 0)
    elif isinstance(obj, unicode):
        sel = StringSelection(current, index, 0)
    else:
        sel = Mutator(current, index)
    return sel

def climb_tail(struct, index):
    current = struct
    while isinstance(current[index], Struct):
        current = current[index]
        index = len(current) - 1
    obj = current[index]
    if isinstance(obj, list):
        sel = ListSelection(current, index, len(obj))
    elif isinstance(obj, str):
        sel = BufferSelection(current, index, len(obj))
    elif isinstance(obj, unicode):
        sel = StringSelection(current, index, len(obj))
    else:
        sel = Mutator(current, index)
    return sel

def motion(sel, head, shift):
    sel.head = head
    if not shift:
        sel.tail = head

