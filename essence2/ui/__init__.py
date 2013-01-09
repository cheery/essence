import pygame
import sys
from essence2 import vec2
import keyboard
from surface import Surface
from font import Font
from patch9 import Patch9
from blend import Blend

def blend_add(sampler):
    return Blend(pygame.BLEND_RGBA_ADD, sampler)

def blend_sub(sampler):
    return Blend(pygame.BLEND_RGBA_SUB, sampler)

def blend_mult(sampler):
    return Blend(pygame.BLEND_RGBA_MULT, sampler)

def stub(name, arguments):
    pass

screen = None

def dispatch(emit, event):
    global screen
    if event.type == pygame.QUIT:
        if not emit('quit', []):
            sys.exit(0)
    if event.type == pygame.VIDEORESIZE:
        size = [event.w, event.h]
        emit('resize', size)
        screen = Surface(pygame.display.set_mode(size, pygame.RESIZABLE))
        emit('frame', [screen])
        pygame.display.flip()
    if event.type == pygame.KEYDOWN:
        key = keyboard.bindings[event.key]
        modifiers = frozenset(keyboard.parse_modifiers(event.mod))
        emit('keydown', [key, modifiers, event.unicode])
    if event.type == pygame.KEYUP:
        key = keyboard.bindings[event.key]
        modifiers = frozenset(keyboard.parse_modifiers(event.mod))
        emit('keyup', [key, modifiers])
    if event.type == pygame.MOUSEMOTION:
        emit('motion', [vec2(*event.pos), vec2(*event.rel), event.buttons])
    if event.type == pygame.MOUSEBUTTONDOWN:
        emit('buttondown', [vec2(*event.pos), event.button])
    if event.type == pygame.MOUSEBUTTONUP:
        emit('buttonup', [vec2(*event.pos), event.button])

def eventloop(emit=stub, width=640, height=480):
    global screen
    pygame.display.init()
    screen = Surface(pygame.display.set_mode((width, height), pygame.RESIZABLE))
    while 1:
        for event in pygame.event.get():
            dispatch(emit, event)
        emit('frame', [screen])
        pygame.display.flip()
