"""
  schema.mutator
  ~~~~~~~~~~~~~~
"""
from base import Constant, Struct
import proxy

class Mutator(object):
  """
  Mutator is bit like a finger into a structure.
  You can change a part in the structure through the Mutator,
  so that you don't need to be aware about the whole document.
  """
  def __init__(self, struct, index):
    self.struct = struct
    self.index  = index

  def replace(self, obj=None):
    removed = self.struct[self.index]
    if obj is not None:
      self.struct[self.index] = obj
      proxy.reproxy(self.struct.proxy, self.index, obj)
    return removed

  @property
  def which(self):
    obj = self.struct[self.index]
    if isinstance(obj, Struct):
      return 'struct'
    if isinstance(obj, Constant):
      return 'constant'
    if isinstance(obj, list):
      return 'list'
    if isinstance(obj, unicode):
      return 'string'
    if isinstance(obj, str):
      return 'buffer'
    raise Exception("Invalid Mutator (corrupted document?)")

class ListMutator(object):
  """
  Analogous to Mutator, ListMutator operates within a list.
  """
  def __init__(self, struct, list_index, index):
    self.struct     = struct
    self.list_index = list_index
    self.index      = index

  def replace(self, obj=None):
    removed = self.struct[self.list_index][self.index]
    if obj is not None:
      self.struct[self.list_index][self.index] = obj
      proxy.reproxy_list(self.struct.proxy, self.list_index, [obj], self.index)
    return removed

  @property
  def which(self):
    obj = self.struct[self.index]
    if isinstance(obj, Struct):
      return 'struct'
    if isinstance(obj, Constant):
      return 'constant'
    raise Exception("Invalid Mutator (corrupted document?)")