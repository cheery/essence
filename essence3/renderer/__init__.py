from program import ShadingProgram
from texture import Texture, Atlas
from patch9 import Patch9
from color import Color
from font import Font

from OpenGL.GL import *
from ctypes import  c_void_p
from array import array

class Buffer(object):
    def __init__(self, type=GL_ARRAY_BUFFER):
        self.buffer = glGenBuffers(1)
        self.type = type

    def bind(self):
        glBindBuffer(self.type, self.buffer)

    def unbind(self):
        glBindBuffer(self.type, 0)

    def upload(self, data, usage=GL_STATIC_DRAW):
        self.bind()
        address, length = data.buffer_info()
        glBufferData(self.type, length * data.itemsize, c_void_p(address), usage)
        self.unbind()

    def uploadList(self, data, usage=GL_STATIC_DRAW):
        self.upload(array('f', data), usage)
