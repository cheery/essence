import pygame
from pygame.locals import *
from OpenGL.GL import *
import keyboard
import os
import graphics
import time
import json

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

    @property
    def vec4(self):
        return vec4(self.r,self.g,self.b,self.a) / 255.0
    
    def mix(self, other, s):
        t = 1 - s
        return rgba(
            self.r*s + other.r*t,
            self.g*s + other.g*t,
            self.b*s + other.b*t,
            self.a*s + other.a*t,
        )

    def to_string(self):
        return "".join(chr(int(v)) for v in self)

class hsva(object):
    def __init__(self, h, s, v, a=1.0):
        self.h = h
        self.s = s
        self.v = v
        self.a = a

    @property
    def rgba(self):
        k = int(self.h / 60) % 6
        i = (self.h % 60) / 60.0
        v = self.v
        c = v * (1 - self.s)
        d = (v-c)*i
        if k < 1:
            r,g,b = v,   c+d, c
        elif k < 2:
            r,g,b = v-d, v,   c
        elif k < 3:
            r,g,b = c,   v,   c+d
        elif k < 4:
            r,g,b = c,   v-d, v
        elif k < 5:
            r,g,b = c+d, c,   v
        elif k < 6:
            r,g,b = v,   c,   v-d
        return rgba(r*255,g*255,b*255,self.a*255)

class vec4(object):
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __iter__(self):
        return iter((self.x, self.y, self.z, self.w))

    def __div__(self, scalar):
        return vec4(self.x/scalar, self.y/scalar, self.z/scalar, self.w/scalar)

class Argon(object):
    def __init__(self, resolution=(1200,1000)):
        self.flags = HWSURFACE | OPENGL | DOUBLEBUF
        self.resolution = resolution
        self.done = False
        pygame.display.set_mode(self.resolution, self.flags)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.ui = graphics.Program.load(in_module('ui.glsl'))
        self.buf = graphics.Buffer(usage=GL_STREAM_DRAW)
        self.atlas = graphics.AtlasTexture.empty(4096, 4096)
        self.paths = [in_module('assets'), os.getcwd(), '.']
        self.cache = {}
        self.plain = graphics.Image(4,4, '\xff'*64)
        self.avg_latency = 0

    def image(self, path):
        if path in self.cache:
            return self.cache[path]
        for directory in self.paths:
            p = os.path.join(directory, path)
            if not os.path.exists(p):
                continue
            self.cache[path] =image= graphics.Image.load(p)
            return image
        raise Exception("%r not found" % path)

    def patch9(self, path):
        return graphics.Patch9(self.image(path))

    def font(self, path):
        return graphics.Font(
            self.image(os.path.join(path, 'bitmap.png')),
            json.load(open(os.path.join(path, 'metadata.json')))
        )

    def run(self, on_frame, on_keydown=None, on_keyup=None, on_mousedown=None, on_mouseup=None, on_mousemotion=None):
        latencies = []
        while not self.done:
            frame_begin = now = time.time()
            on_frame()
            pygame.display.flip()
            now = time.time()
            latencies.append(now - frame_begin)
            if len(latencies) >= 100:
                latencies.pop(0)
            self.avg_latency = sum(latencies) / len(latencies)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.done = True
                if on_keydown and event.type == KEYDOWN:
                    name = keyboard.bindings.get(event.key, None)
                    modifiers = frozenset(keyboard.parse_modifiers(event.mod))
                    on_keydown(name, modifiers, event.unicode)
                if on_keyup and event.type == KEYDOWN:
                    name = keyboard.bindings.get(event.key, None)
                    modifiers = frozenset(keyboard.parse_modifiers(event.mod))
                    on_keyup(name, modifiers)
                if on_mousedown and event.type == MOUSEBUTTONDOWN:
                    on_mousedown(event.button, event.pos)
                if on_mouseup and event.type == MOUSEBUTTONUP:
                    on_mouseup(event.button, event.pos)
                if on_mousemotion and event.type == MOUSEMOTION:
                    on_mousemotion(event.pos, event.rel)

    def clear(self, color=rgba(255,255,255)):
        glClearColor(*color.vec4)
        glClear(GL_COLOR_BUFFER_BIT)

    def render_with_texture(self, (left, top, width, height), texture):
        right  = left + width
        bottom = top  + height
        self.buf.uploadList([
            left,  top,    0.0, 0.0, 1.0, 1.0, 1.0, 1.0,
            left,  bottom, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0,
            right, top,    1.0, 0.0, 1.0, 1.0, 1.0, 1.0,
            right, top,    1.0, 0.0, 1.0, 1.0, 1.0, 1.0,
            left,  bottom, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0,
            right, bottom, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        ])
        prg = self.ui
        prg.use()
        prg.uniform2f('resolution', self.resolution)
        self.buf.bind()
        texture.bind()
        prg.setPointer("position", 2, GL_FLOAT, stride=8*4, offset=0*4)
        prg.setPointer("texcoord", 2, GL_FLOAT, stride=8*4, offset=2*4)
        prg.setPointer("color",    4, GL_FLOAT, stride=8*4, offset=4*4)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        prg.disablePointers(("position", "texcoord", "color"))
        self.buf.unbind()
        texture.unbind()
        prg.enduse()

    def render(self, quads):
        sampler = atlas_sampler(self.atlas, quads)
        out = triangulate_quads(quads, sampler)
        self.buf.uploadList(out)
        count = len(out)/8
        prg = self.ui
        prg.use()
        prg.uniform2f('resolution', self.resolution)
        self.buf.bind()
        self.atlas.bind()
        prg.setPointer("position", 2, GL_FLOAT, stride=8*4, offset=0*4)
        prg.setPointer("texcoord", 2, GL_FLOAT, stride=8*4, offset=2*4)
        prg.setPointer("color",    4, GL_FLOAT, stride=8*4, offset=4*4)
        glDrawArrays(GL_TRIANGLES, 0, count)
        prg.disablePointers(("position", "texcoord", "color"))
        self.buf.unbind()
        self.atlas.unbind()
        prg.enduse()

def triangulate_quads(quads, (items,s1,t1)):
    out = []
    for args in quads:
        obj = args[-1]
        color = args[-2]
        if isinstance(color, rgba):
            color = color, color, color, color
        if isinstance(obj, graphics.Font):
            source = items[obj.image],s1,t1
            triangulate_font(out, obj, source, args[0], args[1], color)
        elif isinstance(obj, graphics.Patch9):
            source = items[obj.image],s1,t1
            for k in range(9):
                x, y = k % 3, k / 3
                r, c, st = obj.cell(args[0], color, x, y)
                triangulate_quad(out, source, r, c, st)
        else:
            source = items[obj],s1,t1
            triangulate_quad(out, source, args[0], color, (0,0,1,1))
    return out

def sample((item, s1, t1), s, t):
    return (item.x + item.width*s)*s1, (item.y + item.height*t)*t1

def triangulate_quad(out, source, (left, top, width, height), (c0,c1,c2,c3), (s0, t0, s1, t1)):
    s0, t0 = sample(source, s0, t0)
    s1, t1 = sample(source, s1, t1)
    out.extend((left,       top,        s0, t0, c0.r/255.0, c0.g/255.0, c0.b/255.0, c0.a/255.0))
    out.extend((left,       top+height, s0, t1, c2.r/255.0, c2.g/255.0, c2.b/255.0, c2.a/255.0))
    out.extend((left+width, top,        s1, t0, c1.r/255.0, c1.g/255.0, c1.b/255.0, c1.a/255.0))
    out.extend((left+width, top,        s1, t0, c1.r/255.0, c1.g/255.0, c1.b/255.0, c1.a/255.0))
    out.extend((left,       top+height, s0, t1, c2.r/255.0, c2.g/255.0, c2.b/255.0, c2.a/255.0))
    out.extend((left+width, top+height, s1, t1, c3.r/255.0, c3.g/255.0, c3.b/255.0, c3.a/255.0))

def triangulate_font(out, font, source, (x,y), text, color):
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
            triangulate_quad(out, source, (left, top, width, height), color, (s0,t0,s1,t1))
        offset += metrics["advance"]
    return out

def atlas_sampler(atlas, quads):
    atlas.reset()
    items = {}
    for args in quads:
        obj = args[-1]
        if isinstance(obj, (graphics.Patch9, graphics.Font)):
            image = obj.image
        else:
            image = obj
        if not image in items:
            items[image] = atlas.add(image)
    atlas.upload()
    s1 = 1.0 / atlas.width
    t1 = 1.0 / atlas.height
    return items, s1, t1
