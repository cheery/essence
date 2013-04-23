from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import *
from ctypes import c_void_p
import glsl

shader_types = dict(
    GL_VERTEX_SHADER = GL_VERTEX_SHADER,
    GL_FRAGMENT_SHADER = GL_FRAGMENT_SHADER,
    GL_GEOMETRY_SHADER = GL_GEOMETRY_SHADER,
)

class Program(object):
    def __init__(self, shaders, program):
        self.shaders = shaders
        self.program = program

    @classmethod
    def from_string(cls, source):
        shaders = []
        for name, text in glsl.parse(source):
            shaders.append(compileShader(text, shader_types[name]))
        return cls(shaders, compileProgram(*shaders))

    @classmethod
    def load(cls, path):
        return cls.from_string(open(path).read())

    @staticmethod
    def enduse():
        glUseProgram(0)

    def use(self):
        glUseProgram(self.program)

    def loc(self, name):
        loc = glGetUniformLocation(self.program, name)
        return loc

    def attribLoc(self, name):
        loc = glGetAttribLocation(self.program, name)
        return loc

    def setPointer(self, name, size, type=GL_FLOAT, normalize=GL_FALSE, stride=0, offset=0):
        loc = self.attribLoc(name)
        if loc >= 0:
            glEnableVertexAttribArray(loc)
            glVertexAttribPointer(loc, size, type, normalize, stride, c_void_p(offset))

    def disablePointer(self, name):
        loc = self.attribLoc(name)
        if loc >= 0:
            glDisableVertexAttribArray(loc)

    def disablePointers(self, names):
        for name in names:
            self.disablePointer(name)

    def uniform1f(self, name, x):
        loc = self.loc(name)
        if loc >= 0:
            glUniform1f(loc, x)

    def uniform2f(self, name, (x, y)):
        loc = self.loc(name)
        if loc >= 0:
            glUniform2f(loc, x, y)

    def uniform3f(self, name, (x, y, z)):
        loc = self.loc(name)
        if loc >= 0:
            glUniform3f(loc, x, y, z)

    def uniform4f(self, name, (x, y, z, w)):
        loc = self.loc(name)
        if loc >= 0:
            glUniform4f(loc, x, y, z, w)
