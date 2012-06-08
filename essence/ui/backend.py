import pygame, sys, json
from time import time

def get(path, mode='img'):
    if mode == 'img':
        return surface(pygame.image.load(path))
    if mode == 'font':
        return font(
            surface(pygame.image.load(path + "/bitmap.png")),
            json.load(open(path + "/metadata.json")),
        )
    if mode == 'patch-9':
        return patch9(surface(pygame.image.load(path)))

class composite(object):
    pass

def borders(surface):
    width = surface.width
    height = surface.height
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

class patch9(composite):
    def __init__(self, surface):
        self.surface = surface
        self.subsurfaces = []
        h, v = borders(surface)
        for y in range(3):
            row = []
            for x in range(3):
                area = h[x], v[y], h[x+1]-h[x], v[y+1]-v[y]
                row.append(surface.subsurface(area))
            self.subsurfaces.append(row)
        self.padding = h[1]-h[0], v[1]-v[0], h[3]-h[2], v[3]-v[2]

    def __call__(self, target, area, op):
        left, top, right, bottom = self.padding
        h0, v0 = area[0], area[1]
        h3, v3 = area[2] + h0, area[3] + v0
        h = [h0, h0+left, h3-right, h3] 
        v = [v0, v0+top, v3-bottom, v3]
        for y, row in enumerate(self.subsurfaces):
            for x, surface in enumerate(row):
                sector = h[x], v[y], h[x+1]-h[x], v[y+1]-v[y]
                target(surface, sector, op)
        return target

class font(object):
    def __init__(self, surface, metadata):
        self.surface = surface
        self.metadata = metadata

    def calculate_mathline(self, baseline):
        metrics = self.metadata['+']
        return metrics["height"] / 2 - metrics["vbearing"] + baseline

    def __call__(self, text):
        font_width = self.surface.width
        font_height = self.surface.height
        offsets = [0]
        baseline = 0
        overline = 0
        x = 0
        for character in text:
            metrics = self.metadata.get(character)
            if metrics is None:
                continue
            if metrics["display"]:
                baseline = max(baseline, metrics["vbearing"])
                overline = max(overline, metrics["height"] - metrics["vbearing"])
            x += metrics['advance']
            offsets.append(x)
        surface = empty(offsets[-1], baseline + overline)
        x = 0
        for character in text:
            metrics = self.metadata.get(character)
            if metrics is None:
                continue
            if metrics["display"]:
                width = metrics["width"]
                height = metrics["height"]
                uv = metrics["uv"]
                glyph = self.surface.subsurface((
                    uv["s"] * font_width,
                    uv["t"] * font_height,
                    width,
                    height
                ))
                surface(glyph, (
                    x + metrics["hbearing"],
                    baseline - metrics["vbearing"],
                    width,
                    height
                ))
            x += metrics['advance']
        mathline = self.calculate_mathline(baseline)
        return label(surface.pys, offsets, baseline, mathline)

class surface(object):
    def __init__(self, pys):
        self.pys = pys

    def subsurface(self, area):
        return surface(self.pys.subsurface(area))

    def at(self, pos):
        return self.pys.get_at(pos)

    @property
    def data(self):
        return pygame.PixelArray(self.pys)

    @property
    def width(self):
        return self.pys.get_size()[0]

    @property
    def height(self):
        return self.pys.get_size()[1]

    def __call__(self, which, area=None, op=0):
        if isinstance(which, composite):
            return which(self, area, op)
        area = area if area else (0,0, self.width, self.height)
        which.paint_on(self.pys, area, op)
        return self

    def mul(self, which, area=None):
        return self(which, area, pygame.BLEND_MULT)

    def add(self, which, area=None):
        return self(which, area, pygame.BLEND_ADD)

    def sub(self, which, area=None):
        return self(which, area, pygame.BLEND_SUB)

    def paint_on(self, pys, area, special=0):
        pys.blit(pygame.transform.scale(self.pys, (int(area[2]), int(area[3]))), area)

class label(surface):
    def __init__(self, pys, offsets, baseline, mathline):
        surface.__init__(self, pys)
        self.offsets = offsets
        self.baseline = baseline
        self.mathline = mathline

class color(object):
    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
    
    def paint_on(self, pys, area, special=0):
        pys.fill((self.r,self.g,self.b,self.a), area, special)

def empty(width, height):
    if width == 0:
        width = 1
    if height == 0:
        height = 1
    return surface(pygame.Surface((width, height), pygame.SRCALPHA))

class window(object):
    dirty = False
    visible = None
    def __init__(self):
        self.width = 800
        self.height = 400
        self.handlers = {}
    
    def show(self):
        if window.visible in (None, self):
            window.dirty = True
            window.visible = self
        else:
            raise Exception("pygame cannot support multiple windows")

    def hide(self):
        window.visible = None
        window.dirty = True

    def paint(self, screen, dt):
        window.visible.send('paint', screen, dt)

    def on(self, name, handler=None):
        if handler is None:
            def decorator(handler):
                self.handlers[name] = handler
                return handler
            return decorator
        else:
            self.handlers[name] = handler

    def send(self, name, *args):
        if name in self.handlers:
            return self.handlers[name](*args)
        else:
            return False

def set_mode_by(this):
    return surface(pygame.display.set_mode((this.width, this.height), pygame.RESIZABLE))

def dispatch_event(event):
    if event.type == pygame.QUIT:
        if window.visible.send('quit') == False:
            sys.exit(0)
    if event.type == pygame.VIDEORESIZE:
        window.visible.width = event.w
        window.visible.height = event.h
        window.visible.send('resize', event.w, event.h)
        window.dirty = True
    if event.type == pygame.KEYDOWN:
        window.visible.send('keydown', event.key, event.mod)
        if event.unicode:
            window.visible.send('key', event.unicode)
    if event.type == pygame.KEYUP:
        window.visible.send('keyup', event.key, event.mod)
    if event.type == pygame.MOUSEMOTION:
        window.visible.send('mousemotion', event.pos, event.rel, event.buttons)
    if event.type == pygame.MOUSEBUTTONDOWN:
        window.visible.send('mousebuttondown', event.pos, event.button)
    if event.type == pygame.MOUSEBUTTONUP:
        window.visible.send('mousebuttonup', event.pos, event.button)

def eventloop():
    pygame.display.init()
    screen = None
    dt, now = 0, time()
    while 1:
        for event in pygame.event.get():
            dispatch_event(event)
        if screen:
            window.visible.paint(screen, dt)
            pygame.display.flip()
        if window.dirty:
            if window.visible:
                screen = set_mode_by(window.visible)
            elif screen != None:
                pygame.display.quit()
                pygame.display.init()
                screen = None
            window.dirty = False
        last, now = now, time()
        dt = now - last
