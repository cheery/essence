import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_object import *
import time, os

import keyboard
from program import Program
from util import in_module
from imagecache import ImageCache
from renderer import Renderer

def event_dispatch(event, listeners):
    if 'on_keydown' in listeners     and event.type == KEYDOWN:
        name = keyboard.bindings.get(event.key, None)
        modifiers = frozenset(keyboard.parse_modifiers(event.mod))
        listeners["on_keydown"](name, modifiers, event.unicode)
    if 'on_keyup' in listeners       and event.type == KEYUP:
        name = keyboard.bindings.get(event.key, None)
        modifiers = frozenset(keyboard.parse_modifiers(event.mod))
        listeners["on_keyup"](name, modifiers)
    if 'on_mousedown' in listeners   and event.type == MOUSEBUTTONDOWN:
        listeners["on_mousedown"](event.button, event.pos)
    if 'on_mouseup' in listeners     and event.type == MOUSEBUTTONUP:
        listeners["on_mouseup"](event.button, event.pos)
    if 'on_mousemotion' in listeners and event.type == MOUSEMOTION:
        listeners["on_mousemotion"](event.pos, event.rel)

class Argon(object):
    def __init__(self, width, height):
        self.width  = width
        self.height = height

        self.load = ImageCache([in_module('assets'), os.getcwd(), '.'])
        self.default_font = self.load.font('AnonymousPro_17')

        self.running = False
        self.flags = HWSURFACE | OPENGL | DOUBLEBUF
        self.listeners = {}
        self.frame_latency = []

        pygame.display.set_mode((self.width, self.height), self.flags)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.render = Renderer(self, self.default_font)

    def listen(self, fn):
        self.listeners[fn.__name__] = fn
        return fn

    def run(self):
        self.running = True
        while self.running:
            now = time.time()
            self.listeners["on_frame"](now)
            pygame.display.flip()
            self.frame_latency.append(time.time() - now)
            while len(self.frame_latency) > 100:
                self.frame_latency.pop(0)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                event_dispatch(event, self.listeners)

    def clear(self, color):
        r, g, b, a = color
        glClearColor(r/255.0, g/255.0, b/255.0, a/255.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def unbind(self):
        pass

    def show_performance_log(self):
        latency = self.frame_latency
        font = self.default_font
        if len(latency) > 0:
            avg  = sum(latency) / len(latency)
            high = max(latency) 
            text = "avg=%.2fms high=%.2fms" % (avg * 1000, high * 1000)
            self.render.text((0, self.height - font.height + font.baseline), text)
