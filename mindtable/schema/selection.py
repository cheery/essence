"""
  schema.selection
  ~~~~~~~~~~~~~~~~

  Selection is bit like mutator, but it's only valid within collections.
"""
import proxy

class Selection(object):
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
  def __init__(self, struct, data_index, head, tail=None):
    self.struct = struct
    self.data_index = data_index
    self.head = head
    self.tail = head if tail is None else tail

  def splice(self, start, stop, data):
    immutable = self.struct[self.data_index]
    assert isinstance(immutable, data)
    assert isinstance(immutable, self.selectiontype)
    removed = immutable[start:stop]
    self.struct[self.data_index] = immutable[:start] + data + immutable[stop:]
    self.stop = self.start + len(data)
    return removed

class BufferSelection(DataSelection):
  selectiontype = str

class StringSelection(DataSelection):
  selectiontype = unicode

class ListSelection(Selection):
  def __init__(self, struct, list_index, head, tail=None):
    self.struct = struct
    self.list_index = list_index
    self.head = head
    self.tail = head if tail is None else tail

  def splice(self, start, stop, data):
    assert isinstance(data, list)
    assert isinstance(self.struct[self.list_index], list)
    removed = self.struct[self.list_index][start:stop]
    self.struct[self.list_index][start:stop] = data
    proxy.reproxy_list(self.struct.proxy, self.list_index, data, self.start)
    self.stop = self.start + len(data)
    return removed