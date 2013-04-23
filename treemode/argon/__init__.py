import pygame, os, time
from pygame.locals import *
from OpenGL.GL import *
import keyboard
from program import Program
from ctypes import Structure, c_ubyte, c_float, sizeof
from bufferstream import BufferStream
from cache import Cache
from texturecache import TextureCache
from image import Image
from patch9 import Patch9

def in_module(path):
    return os.path.join(os.path.dirname(__file__), path)

class rgba(object):
    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __iter__(self):
        return iter((self.r, self.g, self.b, self.a))

def mix(a, b, t):
    v = 1 - t
    return tuple(int(i*v + j*t) for i,j in zip(a, b))

class Vertex(Structure):
    _fields_ = [
        ('position', c_float*2),
        ('texcoord', c_float*2),
        ('color',    c_ubyte*4),
    ]
    fmt = [
        ('position', 2, GL_FALSE, GL_FLOAT),
        ('texcoord', 2, GL_FALSE, GL_FLOAT),
        ('color',    4, GL_TRUE,  GL_UNSIGNED_BYTE),
    ]

def quad(stream, (left, top, width, height), (s0,t0,s1,t1), (tl,tr,bl,br)):
    stream.vertex((left,       top),        (s0, t0), tl)
    stream.vertex((left,       top+height), (s0, t1), bl)
    stream.vertex((left+width, top),        (s1, t0), tr)
    stream.vertex((left+width, top),        (s1, t0), tr)
    stream.vertex((left,       top+height), (s0, t1), bl)
    stream.vertex((left+width, top+height), (s1, t1), br)

class Argon(object):
    def __init__(self, resolution=(1200, 1000)):
        self.flags = HWSURFACE | OPENGL | DOUBLEBUF
        self.resolution = resolution
        pygame.display.set_mode(self.resolution, self.flags)
        self.initgl()
        self.listeners = {}
        self.average_latency = 0
        self.cache = Cache([in_module('assets'), os.getcwd(), '.'])
        self.texture_cache = TextureCache()
        self.image_empty = Image(1, 1, "\xff\xff\xff\xff")

    def initgl(self):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.program =program= Program.load(in_module('glsl/flat.glsl'))
        program.use()
        program.uniform2f('resolution', self.resolution)
        self.stream = BufferStream(Vertex, GL_TRIANGLES)

    def listen(self, fn):
        self.listeners[fn.__name__] = fn
        return fn

    def run(self):
        self.running = True
        latencies = []
        while self.running:
            frame_begin = now = time.time()
            self.listeners["on_frame"](now)
            pygame.display.flip()
            now = time.time()
            latencies.append(now - frame_begin)
            if len(latencies) >= 100:
                latencies.pop(0)
            self.average_latency = sum(latencies) / len(latencies)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                if 'on_keydown' in self.listeners and event.type == KEYDOWN:
                    name = keyboard.bindings.get(event.key, None)
                    modifiers = frozenset(keyboard.parse_modifiers(event.mod))
                    self.listeners["on_keydown"](name, modifiers, event.unicode)
                if 'on_keyup' in self.listeners and event.type == KEYUP:
                    name = keyboard.bindings.get(event.key, None)
                    modifiers = frozenset(keyboard.parse_modifiers(event.mod))
                    self.listeners["on_keyup"](name, modifiers)
                if 'on_mousedown' in self.listeners and event.type == MOUSEBUTTONDOWN:
                    self.listeners["on_mousedown"](event.button, event.pos)
                if 'on_mouseup' in self.listeners and event.type == MOUSEBUTTONUP:
                    self.listeners["on_mouseup"](event.button, event.pos)
                if 'on_mousemotion' in self.listeners and event.type == MOUSEMOTION:
                    self.listeners["on_mousemotion"](event.pos, event.rel)

    def clear(self, color=rgba(255,255,255)):
        r,g,b,a = color
        glClearColor(r/255.0, g/255.0, b/255.0, a/255.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def render_rectangle(self, rect, image=None, color=rgba(255,255,255,255), gradient=None):
        image = self.image_empty if image is None else image
        if isinstance(image, Patch9):
            patch9 = image
            image = image.image
        else:
            patch9 = None
        if isinstance(color, rgba):
            color = tuple(color)
        if gradient is None:
            gradient = color, color, color, color
        texture = self.texture_cache.get(image)
        texture.bind()
        stream = self.stream
        stream.begin(self.program)
        if patch9 is None:
            quad(stream, rect, (0,0,1,1), gradient)
        else:
            quad(stream, *patch9.cell(rect, gradient, 0, 0))
            quad(stream, *patch9.cell(rect, gradient, 1, 0))
            quad(stream, *patch9.cell(rect, gradient, 2, 0))
            quad(stream, *patch9.cell(rect, gradient, 0, 1))
            quad(stream, *patch9.cell(rect, gradient, 1, 1))
            quad(stream, *patch9.cell(rect, gradient, 2, 1))
            quad(stream, *patch9.cell(rect, gradient, 0, 2))
            quad(stream, *patch9.cell(rect, gradient, 1, 2))
            quad(stream, *patch9.cell(rect, gradient, 2, 2))
        stream.end()
        texture.unbind()

    def render_text(self, (x,y), text, font, color=rgba(255,255,255,255), gradient=None):
        if isinstance(color, rgba):
            color = tuple(color)
        if gradient is None:
            gradient = color, color, color, color
        pass
        texture = self.texture_cache.get(font.image)
        texture.bind()
        stream = self.stream
        stream.begin(self.program)
        offset = 0
        sK = 1.0 / font.image.width
        tK = 1.0 / font.image.height
        for character in text:
            metrics = font.metadata.get(character)
            if metrics is None:
                continue
            if metrics['display']:
                width = metrics["width"]
                height = metrics["height"]
                hbearing = metrics["hbearing"]
                vbearing = -metrics["vbearing"]
                s0 = metrics["uv"]["s"]
                t0 = metrics["uv"]["t"]
                s1 = s0 + width*sK
                t1 = t0 + height*tK
                left = x + offset + hbearing
                top  = y + vbearing
                quad(stream, (left, top, width, height), (s0,t0,s1,t1), gradient)
            offset += metrics["advance"]
        stream.end()
        texture.unbind()
