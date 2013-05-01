"""
  schema.proxy
  ~~~~~~~~~~~~

  Proxy represents the location of struct inside document.
"""
from base import Struct

class Proxy(object):
  def __repr__(self):
    info, path = self.unroll()
    classname = self.__class__.__name__
    return "%s:%r%s" % (classname, info, ''.join("[%i]" % index for index in path))

class RootProxy(Proxy):
  def __init__(self, info):
    self.info = info

  def unroll(self):
    return self.info, []

class StructProxy(Proxy):
  def __init__(self, parent, index):
    self.parent = parent
    self.index  = index

  def unroll(self):
    info, path = self.parent.unroll()
    path.append(self.index)
    return info, path

class ListProxy(Proxy):
  def __init__(self, parent, list_index, index):
    self.parent = parent
    self.list_index = list_index
    self.index = index

  def unroll(self):
    info, path = self.parent.unroll()
    path.append(self.list_index)
    path.append(self.index)
    return info, path

def mkroot(info, struct):
  """
  Construct new root proxy, possibly when initializing a document.
  """
  struct.proxy = RootProxy(info)
  for index, obj in enumerate(struct):
    reproxy(struct.proxy, index, obj)
  return struct.proxy

def reproxy_list(parent, list_index, objects, start=0):
  """
  Reconstructs proxies for objects within a list, maybe when object location changes.
  """
  for index, obj in enumerate(objects, start):
    if isinstance(obj, Struct):
        struct = obj
        struct.proxy = ListProxy(parent, list_index, index)
        for index, obj in enumerate(struct):
            reproxy(struct.proxy, index, obj)

def reproxy(parent, index, obj):
  """
  Reconstructs proxy, maybe when object location changes.
  """
  if isinstance(obj, Struct):
    struct = obj
    struct.proxy = StructProxy(parent, index)
    for index, obj in enumerate(struct):
      reproxy(struct.proxy, index, obj)
  elif isinstance(obj, list):
    reproxy_list(parent, index, obj)
