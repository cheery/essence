from schema.base import Constant, StructType, Struct
from schema import proxy


Variable = StructType(u"variable:name")
print Variable.name
print Variable.labels

Call = StructType(u"call:callee:arguments")
print Call

Yes = Constant(u"yes")
No  = Constant(u"no")

print Yes, No

document = Call(Variable(u"hello"), [
  Variable(u"world")
])
print document

proxy.mkroot('document', document)

print document.arguments[0].proxy