"""
Draws a rectangle in different ways.

In case you port this fine editor to other systems, changes
to this and main module should be enough.
"""
import pygame

class rectangle(object):
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def move(self, (x,y)):
        self.left += x
        self.right += x
        self.top += y
        self.bottom += y

    def inside(self, (x,y)):
        in_horizontal = self.left <= x <= self.right
        in_vertical = self.top <= y <= self.bottom
        return in_horizontal and in_vertical

    @property
    def xywh(self, (x,y)=(0,0)):
        return (self.left+x, self.top+y, self.width, self.height)        

    @property
    def width(self):
        return self.right-self.left

    @property
    def height(self):
        return self.bottom-self.top

    def pad(self, left, top=None, right=None, bottom=None):
        top = left if top is None else top
        right = left if right is None else right
        bottom = top if bottom is None else bottom
        return rectangle(self.left-left, self.top-top, self.right+right, self.bottom+bottom)

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
    return x0, x1, y0, y1

class patch9(object):
    def __init__(self, surface):
        self.surface = surface
        x0, x1, y0, y1 = borders(surface)
        w, h = surface.get_size()
        self.pieces = []
        xs = [1, x0, x1, w]
        ys = [1, y0, y1, h]
        for index in range(9):
            j, k = index % 3, index / 3
            x0,x1,y0,y1 = xs[j], xs[j+1], ys[k], ys[k+1]
            self.pieces.append(surface.subsurface((x0,y0,x1-x0,y1-y0)))
        self.padding = (xs[1]-xs[0], ys[1]-ys[0]), (xs[3]-xs[2], ys[3]-ys[2])
    
    def blit(self, screen, rect):
        x, y = rect.left, rect.top
        w2, h2 = rect.width, rect.height
        (w0,h0), (w1,h1) = self.padding
        xs = [x, x+w0, x+w2-w1, x+w2]
        ys = [y, y+h0, y+h2-h1, y+h2]
        for index, piece in enumerate(self.pieces):
            j, k = index % 3, index / 3
            x0,x1,y0,y1 = xs[j], xs[j+1], ys[k], ys[k+1]
            size = max(0, x1-x0), max(0, y1-y0)
            surface = pygame.transform.smoothscale(piece, size)
            screen.blit(surface, (x0,y0))

class stretch(object):
    def __init__(self, surface):
        self.surface = surface

    def blit(self, screen, rect):
        surface = pygame.transform.smoothscale(self.surface, (rect.width, rect.height))
        screen.blit(surface, (rect.left, rect.top))

class color(object):
    def __init__(self, r,g,b,a=255):
        self.rgba = r,g,b,a
    
    def blit(self, screen, rect):
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surface.fill(self.rgba)
        screen.blit(surface, (rect.xywh))

class invert(object):
    def __init__(self, graphic):
        self.graphic = graphic

    def blit(self, screen, rect):
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        self.graphic.blit(surface, rectangle(0,0,rect.width,rect.height))
        surface.blit(screen, (0,0), (rect.xywh), pygame.BLEND_SUB)
        screen.blit(surface, (rect.xywh))

#class box(object):
#    def __init__(self, rect, show=None):
#        self.rect = rect
#        self.show = show
#
#    def draw(self, screen):
#        if self.show != None:
#            self.show.blit(screen, self.rect)
#
#class string(object):
#    def __init__(self, text, font):
#        self.text = text
#        self.font = font
#        self.metrics = self.font.layoutmetrics(self.text)
#        top = self.metrics['top']
#        bottom = self.metrics['bottom']
#        charactergaps = self.metrics['charactergaps']
#        self.rect = rectangle(
#                charactergaps[0],  top,
#                charactergaps[-1], bottom)
#
#    def draw(self, screen):
#        top = self.metrics['top']
#        position = (self.rect.left, self.rect.top-top)
#        self.font.blit(screen, position, self.text)
#
#class group(object):
#    def __init__(self, rect, members):
#        self.rect = rect
#        self.members = members
#        self.surface = pygame.Surface((rect.width, rect.height))
#
#    def clear(self):
#        self.members = []
#
#    def append(self, member):
#        self.members.append(member)
#
#    def draw(self, screen):
#        self.surface.fill((0,0,0))
#        for member in self.members:
#            member.draw(self.surface)
#        screen.blit(self.surface, self.rect.xywh)
#
#    def __iter__(self):
#        return iter(self.members)
#
#    def pick(self, position):
#        for member in self:
#            hit = member.inside(position)
#            if hit:
#                yield member
#            if hit and isinstance(member, group):
#                for obj in member.pick(position):
#                    yield obj
