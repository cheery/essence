# this thing still needs some refining

from base import Constant, StructType

Ref = StructType(u"ref:name")

## appear only in Field.spec
List = StructType(u"list:spec")
String = Constant(u"string")
Buffer = Constant(u"buffer")

## Appears only in Struct.fields
Object = StructType(u"object:name:spec")

Struct = StructType(u"struct:name:objects")
Group  = StructType(u"group:name:members")

Const = StructType(u"constant:name")

Language = StructType(u"language:name:types")

class Constructors(object):
  def __init__(self, language):
    self.language = language
    for obj in language.types:
      if obj.type == Struct:
        uid = obj.name + u':' + u':'.join(_obj.name for _obj in obj.objects)
        setattr(self, obj.name.title(), StructType(uid))
      elif obj.type == Const:
        setattr(self, obj.name.title(), Constant(obj.name))

language = Language('language', [
  Struct(u"ref", [
    Object(u"name", [String])
  ]),
  Struct(u"list", [
    Object(u"spec", [List([Ref(u"ref")])])
  ]),
  Const(u"string"),
  Const(u"buffer"),
  Struct(u"object", [
    Object(u"name", [String]),
    Object(u"spec", [String, Buffer, List([Ref(u"ref")])]),
  ]),
  Struct(u"group", [
    Object(u"name", [String]),
    Object(u"members", [List([Ref(u"ref")])])
  ]),
  Struct(u"constant", [
    Object(u"name", [String]),
  ]),
  Struct(u"language", [
    Object(u"name", [String]),
    Object(u"types", [List([Ref(u"constant"), Ref(u"group"), Ref(u"struct")])]),
  ]),
])