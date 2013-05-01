from OpenGL.GL import *
from ctypes import  c_void_p, sizeof, POINTER, cast
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

    def setSize(self, size):
        self.bind()
        glBufferData(self.type, size, c_void_p(0), self.usage)
        self.unbind()

    def map(self, access=GL_READ_ONLY):
        return glMapBuffer(self.type, access)

    def unmap(self):
        glUnmapBuffer(self.type)

class BufferStream(object):
    def __init__(self, vertex_fmt, which=GL_TRIANGLES):
        self.which = which
        self.maxCount = 4096
        self.vertex_fmt = vertex_fmt
        self.vertex_fmt_p = POINTER(self.vertex_fmt)
        self.buff = Buffer(usage=GL_STREAM_DRAW)
        self.buff.setSize(sizeof(vertex_fmt) * self.maxCount)
        self.data = None
        self.count = 0

    def commit(self):
        if self.count > 0:
            self.data = None
            self.buff.unmap()
            glDrawArrays(self.which, 0, self.count)
            self.count = 0

    def vertex(self, *data):
        if self.count == 0:
            address = self.buff.map(GL_WRITE_ONLY)
            assert address != 0
            self.data = cast(address, self.vertex_fmt_p)
        self.data[self.count] = data
        self.count += 1
        if self.count >= self.maxCount:
            self.end()

    def begin(self, program):
        self.buff.bind()
        stride = sizeof(self.vertex_fmt)
        for name, count, normalized, which in self.vertex_fmt.fmt:
            offset = getattr(self.vertex_fmt, name).offset
            program.setPointer(name, count, which, normalized, stride, offset)

    def end(self):
        if self.count > 0:
            self.commit()
        self.buff.unbind()
