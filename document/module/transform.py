import core

def find_common(element, start, stop):
    base = 0
    for child in element:
        if start == base:
            break
        if stop == base:
            break
        if child.span > 0:
            start_inside = base < start < base + child.span + 1
            stop_inside = base < stop < base + child.span + 1
            if start_inside and stop_inside:
                return find_common(child, start - base - 1, stop - base - 1)
            elif start_inside or stop_inside:
                break
        base += child.span + 1
    return element, start, stop

def collapse(element, target):
    base = 0
    for index, child in enumerate(element):
        if base == target:
            break
        if child.span > 0 and base < target < base + child.span:
            collapsed, offset = collapse(child, target - base - 1)
            return [core.lshard(element.tag)] + collapsed + [core.rshard(element.tag)], offset + index
        base += child.span + 1
    return [core.lshard(element.tag)] + element.children + [core.rshard(element.tag)], index

def contiguous(elements, start, stop):
    output = []
    last = 0
    base = 0
    index0 = None
    index1 = None
    for index, child in enumerate(elements):
        if child.span > 0:
            if base < start < base + child.span:
                output.extend(elements[last:index])
                children, offset = collapse(child, start - base - 1)
                index0 = offset + len(output)
                output.extend(children)
                last = index + 1
            if base < stop < base + child.span:
                output.extend(elements[last:index])
                children, offset = collapse(child, stop - base - 1)
                index1 = offset + len(output)
                output.extend(children)
                last = index + 1
        if base == start:
            index0 = len(output) + (index - last)
        if base == stop:
            index1 = len(output) + (index - last)
        base += child.span + 1
    if base == start:
        index0 = len(output) + (index+1 - last)
    if base == stop:
        index1 = len(output) + (index+1 - last)
    output.extend(elements[last:])
    return output, index0, index1

def find(document, start, stop):
    common, start, stop = find_common(document, start, stop)
    base = 0
    for child in common:
        if base == start and base + child.span + 1 == stop:
            return child
        base += child.span + 1

def splice(document, (start, pos0), (stop, pos1), segment):
    common, start, stop = find_common(document, start, stop)
    output, start, stop = contiguous(common, start, stop)

    lmerge, data, rmerge = segment
    # cut selection into objects with given coordinates (do not change anything yet)
    # check that remaining possible merger pieces match with data, if merging.
    # if merging, merge.
    # duplicate and insert new selection, give old selection back.

def retag(document, start, stop, tag):
    element = find(document, start, stop)
    if element is not None:
        element.tag = tag
        return True

def wrap(document, start, stop):
    if stop - start < 2:
        return False
    common, start, stop = find_common(document, start, stop)
    output, start, stop = contiguous(common, start, stop)
    if start is None or stop is None:
        return False
    if output[start].dtype != core.lshard.dtype:
        return False
    if output[stop-1].dtype != core.rshard.dtype:
        return False
    tag = core.tagmerge(output[start].tag, output[stop-1].tag)
    element = core.block(tag, output[start+1:stop-1])
    output[start:stop] = [element]
    common.children = core.reparent(output, common)
    return True

def unwrap(document, start, stop):
    element = find(document, start, stop)
    if element is not None:
        parent = element.parent
        index = parent.index(element)
        dropping = [core.lshard(element.tag)] + element.children + [core.rshard(element.tag)]
        parent.children[index:index+1] = core.reparent(dropping, parent)
        return True
