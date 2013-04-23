import base
from base import Meta, Constant

Ref = Meta(u"ref", [
    u"name",
])

String = Constant(u"string")
Buffer = Constant(u"buffer")
List = Meta(u"list", [u"spec"])

Field = Meta(u"field", [u"name", u"spec"])

Struct = Meta(u"struct", [
    u"name",
    u"fields",
])

Group = Meta(u"group", [
    u"name",
    u"members",
])

Constant = Meta(u"constant", [
    u"name",
])

LanguageSpec = Meta(u"language", [
    u"name",
    u"semantics",
])

class Language(object):
    def __init__(self, spec):
        self.spec = spec
        for record in spec.semantics:
            if record.meta == Struct:
                obj = base.Meta(record.name, [field.name for field in record.fields])
                setattr(self, record.name.title(), obj)
            elif record.meta == Group:
                pass
            elif record.meta == Constant:
                obj = base.Constant(record.name)
                setattr(self, record.name.title(), obj)
            else:
                raise Exception("%r invalid in language_spec.semantics" % record)

# Language should also provide .verify(tree)
# As well as .mk_template(name, *fills)
# As well as .autospawn(name, index, goal)
