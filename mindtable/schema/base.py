"""
  schema.base
  ~~~~~~~~~~~
"""

class ParsedString(object):
  def __cmp__(self, other):
    if isinstance(other, ParsedString):
        return cmp(self.uid, other.uid)
    else:
        return -1

  def __hash__(self):
    return hash(self.uid)

  def __repr__(self):
    return self.uid

class Constant(ParsedString):
  __slots__ = ('uid',)
  def __init__(self, uid):
    self.uid = uid

  def copy(self):
    return self

class StructType(ParsedString):
  __slots__ = ('uid', 'name', 'labels')
  def __init__(self, uid):
    self.name, fid = uid.split(':', 1)
    self.labels = fid.split(':')
    self.uid = uid

  def __call__(self, *args):
    assert len(self.labels) == len(args)
    return Struct(self, list(args))

class Struct(object):
  """
  Struct consists of ordered and labeled objects.
  It can hold a proxy, which represents it's location in a document.
  Some object labels are shadowed, and preserved for implementation use.
  """
  __slots__ = ('type', 'data', 'proxy')
  unshadow = 'type', 'data', 'proxy', 'copy'
  def __init__(self, type, data, proxy=None):
    self.type = type
    self.data = data
    self.proxy = proxy

  def __getitem__(self, index):
    return self.data[index]

  def __setitem__(self, index, value):
    self.data[index] = value

  def __iter__(self):
    return iter(self.data)

  def __len__(self):
    return len(self.data)

  def __repr__(self):
    return "%s(%s)" % (self.type.name, ', '.join(repr(obj) for obj in self))

  def copy(self):
    copies = []
    for obj in self:
      if isinstance(obj, list):
        copies.append(list(obj))
      elif isinstance(obj, (str, unicode)):
        copies.append(obj)
      else:
        copies.append(obj.copy())
    return Struct(self.type, copies)

  def __getattr__(self, name):
    if name in Struct.unshadow:
      raise AttributeError(name)
    else:
      return self[self.type.labels.index(name)]

  def __setattr__(self, name, value):
    if name in Struct.unshadow:
      super(Struct, self).__setattr__(name, value)
    else:
      self[self.type.labels.index(name)] = value
