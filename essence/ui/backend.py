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
        pygame
        pass

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

    @property
    def width(self):
        return self.pys.get_size()[0]

    @property
    def height(self):
        return self.pys.get_size()[1]

    def __call__(self, which, area=None):
        area = area if area else (0,0, self.width, self.height)
        which.paint_on(self.pys, area)

    def paint_on(self, pys, area):
        pys.blit(pygame.transform.scale(self.pys, area[2:4]), area)

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
    
    def paint_on(self, pys, area):
        pys.fill((self.r,self.g,self.b,self.a), area)

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
