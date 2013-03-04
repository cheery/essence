from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import *
from ctypes import c_void_p
import re

shader_record = re.compile(r"^(\w+):")

shader_types = dict(
    GL_VERTEX_SHADER = GL_VERTEX_SHADER,
    GL_FRAGMENT_SHADER = GL_FRAGMENT_SHADER,
    GL_GEOMETRY_SHADER = GL_GEOMETRY_SHADER,
)

def parse_shader_program(program):
    common = []
    name = None
    lines = []
    for line in program.splitlines():
        match = shader_record.match(line)
        if match:
            if name == None:
                common = lines
            else:
                yield name, '\n'.join(common + lines)
            name = match.groups()[0]
            lines = []
        else:
            lines.append(line)
    if name:
        yield name, '\n'.join(common + lines)

class TextureBinder(object):
    def __init__(self, program):
        self.program = program
        self.active = {}
        self.inactive = set(i for i in range(glGetInteger(GL_MAX_TEXTURE_UNITS)))

    def bind(self, name, texture):
        loc = self.program.loc(name)
        if loc >= 0:
            unit = self.inactive.pop()
            glActiveTexture(GL_TEXTURE0 + unit)
            texture.bind()
            glUniform1i(loc, unit)
            self.active[name] = (unit, texture)

    def unbind(self, name):
        unit, texture = self.active.pop(name, (None, None))
        if unit != None:
            glActiveTexture(unit)
            texture.unbind()
            self.inactive.add(unit)

    def unbind_all(self):
        for name, (unit, texture) in self.active.iteritems():
            glActiveTexture(GL_TEXTURE0 + unit)
            texture.unbind()
            self.inactive.add(unit)
        self.active = {}

class ShadingProgram(object):
    def __init__(self, shaders, program):
        self.shaders = shaders
        self.program = program
        self.binder = TextureBinder(self)

    @classmethod
    def from_string(cls, program):
        shaders = []
        for name, text in parse_shader_program(program):
            shaders.append(compileShader(text, shader_types[name]))

        return cls(shaders, compileProgram(*shaders))

    @classmethod
    def load(cls, path):
        return cls.from_string(open(path).read())

    def use(self):
        glUseProgram(self.program)

    def loc(self, name):
        loc = glGetUniformLocation(self.program, name)
        return loc

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

    def bind(self, name, texture):
        self.binder.bind(name, texture)

    def unbind(self, name):
        self.binder.unbind(name)

    def unbind_all(self):
        self.binder.unbind_all()
