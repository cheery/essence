import pygame
from essence2 import vec2, rgba, rectangle

class Surface(object):
    def __init__(self, pys):
        self.pys = pys

    def subsurface(self, ((x,y), (w,h))):
        area = x,y,w,h
        return Surface(self.pys.subsurface(area))

    def at(self, (x,y)):
        pos = x,y
        return self.pys.get_at(pos)

    @staticmethod
    def load(path):
        return Surface(pygame.image.load(path))

    @staticmethod
    def empty(width, height):
        return Surface(pygame.Surface((width, height), pygame.SRCALPHA))

    @property
    def size(self):
        return vec2(*self.pys.get_size())

    def __call__(self, sampler, geometry=None):
        if geometry == None and hasattr(sampler, 'geometry'):
            geometry = sampler.geometry
        elif geometry == None:
            geometry = rectangle(vec2(0, 0), self.size)
        if hasattr(geometry, 'valid') and not geometry.valid():
            return
        if isinstance(sampler, rgba):
            (x,y), (w,h) = geometry
            self.pys.fill(tuple(sampler), (x,y,w,h))
        elif hasattr(sampler, 'blit_duck'):
            sampler.blit_duck(self.pys, geometry, 0)
        elif hasattr(sampler, 'comm_duck'):
            sampler.comm_duck(self, geometry)
        else:
            raise Exception("unknown draw command %r, %r", (sampler, geometry))
        return self

    def blit_duck(self, pys, ((x,y), (w,h)), op):
        if w <= 0 or h <= 0:
            return
        size = int(w), int(h)
        area = x,y,w,h
        surface = pygame.transform.scale(self.pys, size)
        pys.blit(surface, area, special_flags=op)
