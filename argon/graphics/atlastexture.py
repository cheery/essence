from atlas import Allocator, OutOfArea
from texture import Texture
from OpenGL.GL import *

class AtlasTexture(Texture):
    def __init__(self, texture, width, height):
        Texture.__init__(self, texture, width, height)
        self.allocator = Allocator()

    @classmethod
    def empty(cls, width, height):
        atlas = cls(glGenTextures(1), width, height)
        atlas.clear()
        return atlas

    def add(self, image):
        item = self.allocator.add(image.width, image.height)
        item.image = image
        return item

    def clear(self):
        self.bind()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        self.unbind()

    def reset(self):
        self.allocator.reset()

    def upload(self):
        self.allocator.allocate(self.width, self.height)
        self.bind()
        for item in self.allocator.items:
            image = item.image
            glTexSubImage2D(GL_TEXTURE_2D, 0, item.x, item.y, item.width, item.height, GL_RGBA, GL_UNSIGNED_BYTE, image.data)
        self.unbind()
