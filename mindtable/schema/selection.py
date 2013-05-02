"""
  schema.selection
  ~~~~~~~~~~~~~~~~

  Selection is bit like mutator, but it's only valid within collections.
"""
import proxy

class Selection(object):
  length = property(lambda self: len(self.struct[self.index]))
  def _get_start(self):
    if self.head < self.tail:
      return self.head
    else:
      return self.tail
  def _set_start(self, value):
    if self.head < self.tail:
      self.head = value
    else:
      self.tail = value
  start = property(_get_start, _set_start)

  def _get_stop(self):
    if self.head < self.tail:
      return self.tail
    else:
      return self.head
  def _set_stop(self, value):
    if self.head < self.tail:
      self.tail = value
    else:
      self.head = value
  stop = property(_get_stop, _set_stop)

class DataSelection(Selection):
  def __init__(self, struct, index, head, tail=None):
    self.struct = struct
    self.index = index
    self.head = head
    self.tail = head if tail is None else tail

  def splice(self, data=None):
    data = self.selectiontype() if data is None else data
    immutable = self.struct[self.index]
    assert isinstance(data, self.selectiontype)
    assert isinstance(immutable, self.selectiontype)
    removed = immutable[self.start:self.stop]
    self.struct[self.index] = immutable[:self.start] + data + immutable[self.stop:]
    self.stop = self.start + len(data)
    return removed

class BufferSelection(DataSelection):
  selectiontype = str

class StringSelection(DataSelection):
  selectiontype = unicode

class ListSelection(Selection):
  def __init__(self, struct, index, head, tail=None):
    self.struct = struct
    self.index = index
    self.head = head
    self.tail = head if tail is None else tail

  def splice(self, data=None):
    data = [] if data is None else data
    assert isinstance(data, list)
    assert isinstance(self.struct[self.index], list)
    removed = self.struct[self.index][self.start:self.stop]
    self.struct[self.index][self.start:self.stop] = data
    proxy.reproxy_list(self.struct.proxy, self.index, self.struct[self.index])
    self.stop = self.start + len(data)
    return removed
