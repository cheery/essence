from surface import Surface

def borders(surface):
    width, height = surface.size
    y0 = 0
    y1 = 0
    x0 = 0
    x1 = 0
    i = 0
    while i < height:
        r,g,b,a = surface.at((0,i))
        if a > 0:
            y0 = i
            break
        i += 1
    while i < height:
        r,g,b,a = surface.at((0,i))
        if a == 0:
            y1 = i
            break
        i += 1
    i = 0
    while i < width:
        r,g,b,a = surface.at((i,0))
        if a > 0:
            x0 = i
            break
        i += 1
    while i < width:
        r,g,b,a = surface.at((i,0))
        if a == 0:
            x1 = i
            break
        i += 1
    return [1, x0, x1, width], [1, y0, y1, height]

class Patch9(object):
    def __init__(self, surface):
        self.surface = surface
        self.subsurfaces = []
        h, v = borders(surface)
        for y in range(3):
            row = []
            for x in range(3):
                area = (h[x], v[y]), (h[x+1]-h[x], v[y+1]-v[y])
                row.append(surface.subsurface(area))
            self.subsurfaces.append(row)
        self.padding = h[1]-h[0], v[1]-v[0], h[3]-h[2], v[3]-v[2]

    @staticmethod
    def load(path):
        return Patch9(Surface.load(path))

    def comm_duck(self, target, ((x,y), (w,h))):
        area = x,y,w,h
        left, top, right, bottom = self.padding
        h0, v0 = area[0], area[1]
        h3, v3 = area[2] + h0, area[3] + v0
        h = [h0, h0+left, h3-right, h3] 
        v = [v0, v0+top, v3-bottom, v3]
        for y, row in enumerate(self.subsurfaces):
            for x, surface in enumerate(row):
                sector = (h[x], v[y]), (h[x+1]-h[x], v[y+1]-v[y])
                target(surface, sector)
