import pygame
from texture import Texture

def borders(surface):
    width, height = surface.get_size()
    y0 = 0
    y1 = 0
    x0 = 0
    x1 = 0
    i = 0
    while i < height:
        r,g,b,a = surface.get_at((0,i))
        if a > 0:
            y0 = i
            break
        i += 1
    while i < height:
        r,g,b,a = surface.get_at((0,i))
        if a == 0:
            y1 = i
            break
        i += 1
    i = 0
    while i < width:
        r,g,b,a = surface.get_at((i,0))
        if a > 0:
            x0 = i
            break
        i += 1
    while i < width:
        r,g,b,a = surface.get_at((i,0))
        if a == 0:
            x1 = i
            break
        i += 1
    return [1, x0, x1, width], [1, y0, y1, height]

class Patch9(object):
    def __init__(self, texture, (xc, yc)):
        self.texture = texture
        self.coords = xc, yc
        self.width = texture.width - 1
        self.height = texture.height - 1
        self.padding = xc[1]-xc[0], yc[1]-yc[0], xc[3]-xc[2], yc[3]-yc[2]

    @classmethod
    def load(cls, atlas, path):
        surface = pygame.image.load(path)
        width, height = surface.get_size()
        data = pygame.image.tostring(surface, "RGBA", 0)
        texture = atlas.add_rgba_string(width, height, data)
        coords = borders(surface)
        return cls(texture, coords)

    def __call__(self, emit, (left, top, width, height), color=None):
        texture = self.texture
        color = color or texture.atlas.white
#        c_x = float(color.x+2) / color.atlas.width
#        c_y = float(color.y+2) / color.atlas.height
        s0 = float(texture.x) / texture.atlas.width
        t0 = float(texture.y) / texture.atlas.height
        s1 = float(texture.width) / texture.atlas.width
        t1 = float(texture.height) / texture.atlas.height
        sn = s1 / texture.width
        tn = t1 / texture.height
        x_cs, y_cs = self.coords
        xs = (left, left+self.padding[0], left+width-self.padding[2], left+width)
        ys = (top,  top +self.padding[1], top+height-self.padding[3], top+height)
        for i in range(9):
            x = i % 3
            y = i / 3
            emit(xs[x+0], ys[y+0], x_cs[x+0]*sn + s0, y_cs[y+0]*tn + t0, color.s, color.t)
            emit(xs[x+1], ys[y+0], x_cs[x+1]*sn + s0, y_cs[y+0]*tn + t0, color.s, color.t)
            emit(xs[x+1], ys[y+1], x_cs[x+1]*sn + s0, y_cs[y+1]*tn + t0, color.s, color.t)
            emit(xs[x+0], ys[y+1], x_cs[x+0]*sn + s0, y_cs[y+1]*tn + t0, color.s, color.t)
