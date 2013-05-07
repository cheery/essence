from OpenGL.GL import *
from ctypes import Structure, sizeof, c_float, c_ubyte

gltype_to_ctype = {
    GL_FLOAT: c_float,
    GL_UNSIGNED_BYTE: c_ubyte,
}

def mk_ctype(attributes):
    fields = []
    for name, count, normalized, gltype in attributes:
        fields.append((name, gltype_to_ctype[gltype]*count))
    return type('vertexformat', (Structure,), {"_fields_":fields})

class VertexFormat(object):
    def __init__(self, attributes):
        self.attributes = attributes
        self.ctype = mk_ctype(attributes)

    def use(self, program):
        stride = sizeof(self.ctype)
        for name, count, normalized, gltype in self.attributes:
            offset = getattr(self.ctype, name).offset
            program.setPointer(name, count, gltype, normalized, stride, offset)

    def enduse(self, program):
        for name, count, normalized, gltype in self.attributes:
            program.disablePointer(name)
