from OpenGL.GL import *

class Texture(object):
    def __init__(self, texture, width, height):
        self.texture = texture
        self.width   = width
        self.height  = height

    @classmethod
    def empty(cls, width, height):
        texture = cls(glGenTextures(1), width, height)
        return texture

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def free(self):
        glDeleteTextures(self.texture)

    def set_min_mag(self, min_filter=GL_NEAREST, mag_filter=GL_NEAREST):
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter)
