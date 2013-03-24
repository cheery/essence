from OpenGL.GL import *
from ctypes import  c_void_p
from array import array

class Buffer(object):
    def __init__(self, type=GL_ARRAY_BUFFER, usage=GL_STATIC_DRAW):
        self.buffer = glGenBuffers(1)
        self.type = type
        self.usage = usage

    def bind(self):
        glBindBuffer(self.type, self.buffer)

    def unbind(self):
        glBindBuffer(self.type, 0)

    def upload(self, data, usage=None):
        usage = self.usage if usage is None else usage
        self.bind()
        address, length = data.buffer_info()
        glBufferData(self.type, length * data.itemsize, c_void_p(address), usage)
        self.unbind()

    def uploadList(self, data, usage=None):
        self.upload(array('f', data), usage)

    def map(self, access=GL_READ_ONLY):
        return glMapBuffer(self.type, self.access)

    def unmap(self):
        glUnmapBuffer(self.type)
