import pygame
from essence2 import vec2, rgba, rectangle

class Blend(object):
    def __init__(self, op, sampler):
        self.op = op
        self.sampler = sampler

    def blit_duck(self, pys, geometry, op):
        if isinstance(self.sampler, rgba):
            (x,y), (w,h) = geometry
            pys.fill(tuple(self.sampler), (x,y,w,h), op | self.op)
        else:
            self.sampler.blit_duck(pys, geom, op | self.op)
