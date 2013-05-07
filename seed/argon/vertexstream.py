from OpenGL.GL import *
from ctypes import sizeof, POINTER, cast

from buffer import Buffer

class VertexStream(object):
    """
    VertexFormat must be set for this class to render correctly.
    And before vertexformat is set, you have to bind the vbo.
    """
    def __init__(self, fmt, which=GL_TRIANGLES, maxCount=4096):
        self.fmt      = fmt
        self.fmt_ctype_p = POINTER(self.fmt.ctype)
        self.which    = which
        self.maxCount = 4096
        self.vbo = Buffer(usage=GL_STREAM_DRAW)
        self.vbo.setSize(sizeof(fmt.ctype) * self.maxCount)
        self.data = None
        self.count = 0

    def vertex(self, *data):
        if self.count == 0:
            address = self.vbo.map(GL_WRITE_ONLY)
            assert address != 0
            self.data = cast(address, self.fmt_ctype_p)
        self.data[self.count] = data
        self.count += 1
        if self.count >= self.maxCount:
            self.flush()

    def flush(self):
        if self.count > 0:
            self.data = None
            self.vbo.unmap()
            glDrawArrays(self.which, 0, self.count)
            self.count = 0
