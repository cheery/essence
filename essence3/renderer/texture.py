import pygame
from OpenGL.GL import *
from atlas import Allocator, OutOfArea

class Texture(object):
    def __init__(self, texture, width, height):
        self.texture = texture
        self.width = width
        self.height = height

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    @classmethod
    def load(cls, path):
        surface = pygame.image.load(path)
        width, height = surface.get_size()
        data = pygame.image.tostring(surface, "RGBA")
        return cls.from_rgba_string(width, height, data)

    @classmethod
    def from_rgba_string(cls, width, height, data):
        texture = cls(glGenTextures(1), width, height)
        texture.bind()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        texture.unbind()
        return texture

class Atlas(object):
    def __init__(self, texture, width, height):
        self.texture = texture
        self.allocator = Allocator()
        self.width = width
        self.height = height

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    @classmethod
    def empty(cls, width, height):
        atlas = cls(glGenTextures(1), width, height)
        atlas.bind()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        atlas.unbind()
        return atlas

    def add_rgba(self, (r, g, b, a)):
        pixel = ''.join(chr(c) for c in (r,g,b,a))
        return self.add_rgba_string(8,8,pixel*(8*8))

    def add_rgba_string(self, width, height, data):
        item = self.allocator.add(width, height)
        item.data = data
        item.atlas = self
        return item

    def load(self, path):
        surface = pygame.image.load(path)
        width, height = surface.get_size()
        data = pygame.image.tostring(surface, "RGBA")
        return self.add_rgba_string(width, height, data)

    def upload(self):
        self.allocator.allocate(self.width, self.height)
        self.bind()
        for item in self.allocator.items:
            glTexSubImage2D(GL_TEXTURE_2D, 0, item.x, item.y, item.width, item.height, GL_RGBA, GL_UNSIGNED_BYTE, item.data)
        self.unbind()
