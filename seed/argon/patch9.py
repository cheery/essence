def borders(image):
    y0 = 0
    y1 = 0
    x0 = 0
    x1 = 0
    i = 0
    while i < image.height:
        r,g,b,a = image.get_at((0,i))
        if a > 0:
            y0 = i
            break
        i += 1
    while i < image.height:
        r,g,b,a = image.get_at((0,i))
        if a == 0:
            y1 = i
            break
        i += 1
    i = 0
    while i < image.width:
        r,g,b,a = image.get_at((i,0))
        if a > 0:
            x0 = i
            break
        i += 1
    while i < image.width:
        r,g,b,a = image.get_at((i,0))
        if a == 0:
            x1 = i
            break
        i += 1

    s1 = 1.0 / image.width
    t1 = 1.0 / image.height
    left   = x0-1
    top    = y0-1
    right  = image.width - x1
    bottom = image.height - y1
#    grid = [s1, x0*s1, x1*s1, 1.0], [t1, y0*t1, y1*t1, 1.0]

    grid = (
        ((0, 0, s1), (0, left, x0*s1), (1, -right,  x1*s1), (1, 0, 1.0)),
        ((0, 0, t1), (0, top,  y0*t1), (1, -bottom, y1*t1), (1, 0, 1.0)),
    )
    return (left,top,right,bottom), grid

class Patch9(object):
    def __init__(self, image):
        self.image = image
        self.width  = image.width - 1
        self.height = image.height - 1
        self.padding, self.grid = borders(image)

    def gridpoint(self, i, j, w):
        pc, x, y = self.grid[i][j]
        return w*pc + x, y
