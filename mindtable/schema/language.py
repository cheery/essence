# this thing still needs some refining

from base import Constant, StructType

Ref = StructType(u"ref:name")

## appear only in Field.spec
List = StructType(u"list:spec")
String = Constant(u"string")
Buffer = Constant(u"buffer")

## Appears only in Struct.fields
Object = StructType(u"object:name:spec")

StructDecl = StructType(u"struct:name:objects")
GroupDecl  = StructType(u"group:name:members")
ConstDecl  = StructType(u"constant:name")

Language = StructType(u"language:name:types")

language = Language(u'language', [
  StructDecl(u"ref", [
    Object(u"name", [String])
  ]),
  StructDecl(u"list", [
    Object(u"spec", [List([Ref(u"ref")])])
  ]),
  ConstDecl(u"string"),
  ConstDecl(u"buffer"),
  StructDecl(u"object", [
    Object(u"name", [String]),
    Object(u"spec", [List([Ref(u"string"), Ref(u"buffer"), Ref(u"list"), Ref(u"ref")])]),
  ]),
  StructDecl(u"struct", [
    Object(u"name", [String]),
    Object(u"objects", [List([Ref(u"object")])])
  ]),
  StructDecl(u"group", [
    Object(u"name", [String]),
    Object(u"members", [List([Ref(u"ref")])])
  ]),
  StructDecl(u"constant", [
    Object(u"name", [String]),
  ]),
  StructDecl(u"language", [
    Object(u"name", [String]),
    Object(u"types", [List([Ref(u"constant"), Ref(u"group"), Ref(u"struct")])]),
  ]),
])

class Synthetizer(object):
  def __init__(self, language):
    self.table = {}
    for obj in language.types:
      if obj.type == StructDecl:
        uid = obj.name + u':' + u':'.join(_obj.name for _obj in obj.objects)
        self.table[obj.name] = StructType(uid)
      elif obj.type == ConstDecl:
        self.table[obj.name] = Constant(obj.name)

  def __getitem__(self, name):
    return self.table[name]
