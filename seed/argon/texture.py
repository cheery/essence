from OpenGL.GL import *

class Texture(object):
    def __init__(self, texture, width, height):
        self.texture = texture
        self.width   = width
        self.height  = height
        self.target  = GL_TEXTURE_2D

    @classmethod
    def empty(cls, width=0, height=0):
        texture = cls(glGenTextures(1), width, height)
        return texture

    def bind(self):
        glBindTexture(self.target, self.texture)

    def unbind(self):
        glBindTexture(self.target, 0)

    def free(self):
        glDeleteTextures(self.texture)

    def set_min_mag(self, min_filter=GL_NEAREST, mag_filter=GL_NEAREST):
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter)

    def upload(self, data, min_filter=GL_NEAREST, mag_filter=GL_NEAREST):
        self.bind()
        self.set_min_mag(min_filter, mag_filter)
        glTexImage2D(self.target, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        self.unbind()

    def resize(self, width, height, min_filter=GL_NEAREST, mag_filter=GL_NEAREST):
        self.width  = width
        self.height = height
        self.bind()
        glTexImage2D(self.target, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        self.set_min_mag(min_filter, mag_filter)
        self.unbind()
