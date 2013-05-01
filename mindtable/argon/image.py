import pygame
import argon

class Image(object):
    def __init__(self, width, height, data):
        self.width  = width
        self.height = height
        self.data   = data

    @classmethod
    def load(cls, path):
        surface = pygame.image.load(path)
        width, height = surface.get_size()
        data = pygame.image.tostring(surface, "RGBA")
        return cls(width, height, data)

    def get_at(self, (x,y)):
        i = self.width*y + x
        r, g, b, a = self.data[i*4:i*4+4]
        return argon.rgba(ord(r), ord(g), ord(b), ord(a))
