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

def cut_selection(elements, start, stop, index0, index1):
    ldata = rdata = None
    if start == stop and (not None in (index0, index1)):
        ldata, drop, rdata = elements[start].partition(index0, index1)
        return [drop], ldata, rdata
    if index0 != None:
        ldata, elements[start] = elements[start].partition(index0)
    if index1 != None:
        elements[stop], rdata = elements[stop].partition(index1)
        stop += 1
    return elements[start:stop], ldata, rdata, stop

def splice_span((start, index0), (stop, index1), segment):
    return core.count_span(segment) - (index0 != None) - (index1 != None)

def respan(element, delta):
    if element.dtype != core.document.dtype:
        element.span += delta
    element.span += delta

def splice(document, (start, index0), (stop, index1), segment):
    common, start, stop = find_common(document, start, stop)
    output, start, stop = contiguous(common, start, stop)
    dropping, ldata, rdata, stop = cut_selection(output, start, stop, index0, index1)
    lmerge = ldata is not None
    rmerge = rdata is not None
    if len(segment) == 0 and lmerge or rmerge:
        return None
    if lmerge and not segment[0] & ldata:
        return None
    if rmerge and not segment[-1] & rdata:
        return None
    data = core.dup(segment)
    if lmerge:
        data[0] = ldata + data[0]
    if rmerge:
        data[-1] = data[-1] + rdata
    output[start:stop] = data
    common.children = core.reparent(output, common)
    inserted = splice_span((start, index0), (stop, index1), segment)
    deleted = splice_span((start, index0), (stop, index1), dropping)
    respan(common, inserted - deleted)
    return dropping
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