import pygame, sys
import bitmapfont
import graphics
graphics = reload(graphics)
from graphics import rectangle, patch9, stretch, color, invert

selectables = []

for i in range(200):
    x = i % 20
    y = i / 20
    rect = rectangle(10+x*30, 10+y*30, 10+x*30+25, 10+y*30+25)
    selectables.append(rect)

def pick_index(pos):
    x,y=pos
    for index, rect in enumerate(selectables):
        if rect.inside(pos):
            return index, index + (x - rect.left > rect.right - x)

def selection_rect(index):
    if 0 < index < len(selectables):
        return selectables[index]

caret_left = invert(patch9(pygame.image.load('assets/caret.left.png')))
caret_top = invert(patch9(pygame.image.load('assets/caret.top.png')))
caret_right = invert(patch9(pygame.image.load('assets/caret.right.png')))
caret_bottom = invert(patch9(pygame.image.load('assets/caret.bottom.png')))

font = bitmapfont.load('font/proggy_tiny')

border = patch9(pygame.image.load('assets/border.png'))
pupu = pygame.image.load('assets/pupu.jpg')
quad = pygame.image.load('assets/quad.png')
cyan = color(0,255,255)
invert = invert(color(255,255,255))

transcludent = color(100, 0, 0, 150)

r1 = rectangle(10, 10, 100, 100)
r2 = rectangle(10, 100, 100, 200)
r3 = rectangle(10, 200, 100, 300)
r4 = rectangle(0, 0, 300, 500)
r5 = rectangle(50, 0, 100, 100)
r6 = rectangle(70, 50, 120, 400)

b0 = rectangle(100,800,200,900)
b1 = rectangle(192,825,300,900)

selection0 = rectangle(600,600,660,660)
selection1 = rectangle(600,600,660,660)

start = stop = None
sel = 0,0

def buttondown(button, pos):
    global start, selection0, selection1, sel
    if button==3:
        selectables[sel[0]:sel[1]] = []
        selection0 = selection1 = None
        sel = 0,0
        return
    start = pick_index(pos)
    if start is not None:
        obj, edge = start
        selection0 = selection_rect(edge-1)
        selection1 = selection_rect(edge)

def buttonup(button, pos):
    global start, stop, selection0, selection1, sel
    stop = pick_index(pos)
    if start is None or stop is None: return
    start_obj, start_edge = start
    stop_obj, stop_edge = stop
    if start<stop:
        selection1 = selection_rect(start_edge)
        selection0 = selection_rect(stop_obj)
    if start>stop:
        selection0 = selection_rect(start_edge-1)
        selection1 = selection_rect(stop_obj)
    sel = min(start_edge, stop_obj), max(start_edge,stop_obj+1)
    if start==stop:
        selection0 = selection_rect(start_edge-1)
        selection1 = selection_rect(start_edge)
        sel = start_edge, start_edge
    start = stop = None

def motion(buttons, pos, rel):
    global start, stop, selection0, selection1, sel
    stop = pick_index(pos)
    if start is None or stop is None: return
    start_obj, start_edge = start
    stop_obj, stop_edge = stop
    if start<stop:
        selection1 = selection_rect(start_edge)
        selection0 = selection_rect(stop_obj)
    if start>stop:
        selection0 = selection_rect(start_edge-1)
        selection1 = selection_rect(stop_obj)
    sel = min(start_edge, stop_obj), max(start_edge,stop_obj+1)
    if start==stop:
        selection0 = selection_rect(start_edge-1)
        selection1 = selection_rect(start_edge)
        sel = start_edge, start_edge

def on_event(event):
    if event.type == pygame.QUIT:            sys.exit()
    if event.type == pygame.MOUSEBUTTONDOWN: buttondown(event.button, event.pos)
    if event.type == pygame.MOUSEBUTTONUP:   buttonup(event.button, event.pos)
    if event.type == pygame.MOUSEMOTION:     motion(event.buttons, event.pos, event.rel)

def fill(screen):
    screen.fill((20,22,10))
    width, height = screen.get_size()
#    font.blit(screen, (width/2,40), "font blitting test")

#    stretch(pupu).blit(screen, r1)
#    stretch(quad).blit(screen, r2)
#    cyan.blit(screen, r3)
#    border.blit(screen, r4)
#    transcludent.blit(screen, r5)
#    invert.blit(screen, r6)

    graphic = border
    #graphic = stretch(pupu)
    for i, sn in enumerate(selectables):
        graphic.blit(screen, sn)

    if selection1: caret_left.blit(screen, selection1.pad(2))
    if selection0: caret_right.blit(screen, selection0.pad(2))

#    caret_right.blit(screen, b0)
#    caret_left.blit(screen, b1)

    
    font.blit(screen, (10,720), "selection: x=%i y=%i" % sel)
    font.blit(screen, (10,740), "REMINDER FOR SELF: Avoid image stretching, it makes things slow.")
