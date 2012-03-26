import pygame, sys
import bitmapfont
import graphics
graphics = reload(graphics)
from graphics import rectangle, patch9, stretch, color, invert, picarea
import selection
selection = reload(selection)

visual_config = dict(
    left = (patch9(pygame.image.load('assets/caret.left.png'))),
    top = (patch9(pygame.image.load('assets/caret.top.png'))),
    right = (patch9(pygame.image.load('assets/caret.right.png'))),
    bottom = (patch9(pygame.image.load('assets/caret.bottom.png'))),
)

alien_left = stretch(pygame.image.load('assets/alien.left.png'))
alien_right = stretch(pygame.image.load('assets/alien.right.png'))

font = bitmapfont.load('font/proggy_tiny')
def glyph(metrics):
    #metrics = font.metadata[character]
    left = metrics['uv']['s'] * font.width
    top = metrics['uv']['t'] * font.height
    return picarea(font.bitmap, (left, top, metrics['width'], metrics['height']))

def glyph_rect(metrics, x, y):
    return rectangle(
        int(x + metrics['hbearing']),
        int(y - metrics['vbearing']),
        int(x + metrics['width']),
        int(y + metrics['height'])
    )

class node(object):
    def __init__(self, info):
        self.info = info

sel = None
start = stop = None

example = [
    node('OPEN'),
    'C','r','u','d','e',' ','e','x','a','m','p','l','e',' ','i','s',' ','b','e','t','t','e','r',' ','t','h','a','n',' ','n','o','t','h','i','n','g',
    node('CLOSE'),
]

output = []
visual = selection.visual([])

def refresh():
    x = 10
    y = 30
    output[:] = []
    visual.entries[:] = []
    for index, obj in enumerate(example):
        if isinstance(obj, node):
            if obj.info == 'OPEN':
                pair = alien_left, rectangle(x+2,y-13,x+10,y+7)
                output.append(pair)
                visual.entries.append(selection.selector(pair[1].pad(1), index))
                x += 12
            if obj.info == 'CLOSE':
                pair = alien_right, rectangle(x+2,y-13,x+10,y+7)
                output.append(pair)
                visual.entries.append(selection.selector(pair[1].pad(1), index))
                x += 12
        else:
            metrics = font.metadata[obj]
            if metrics['display']:
                pair = glyph(metrics), glyph_rect(metrics, x, y)
                output.append(pair)
            rect = rectangle(x, y-12, x+int(metrics['advance']), y+4)
            visual.entries.append(selection.selector(rect, index))
            x += int(metrics['advance'])

refresh()

#selectables = []
#
#
#width = 16
#height = 39
#stepx = width + 5
#stepy = height + 5
#for i in range(200):
#    x = i % 20
#    y = i / 20
#    rect = rectangle(10+x*stepx, 10+y*stepy, 10+x*stepx+width, 10+y*stepy+height)
#    selectables.append(selector(rect, i))
#
#v = visual(selectables)
#
#def pick_index(pos):
#    return v.pick(pos)
#
#
#
#border = patch9(pygame.image.load('assets/border.png'))
#pupu = pygame.image.load('assets/pupu.jpg')
#quad = pygame.image.load('assets/quad.png')
#cyan = color(0,255,255)
#invert = invert(color(255,255,255))
#
#transcludent = color(100, 0, 0, 150)
#
#r1 = rectangle(10, 10, 100, 100)
#r2 = rectangle(10, 100, 100, 200)
#r3 = rectangle(10, 200, 100, 300)
#r4 = rectangle(0, 0, 300, 500)
#r5 = rectangle(50, 0, 100, 100)
#r6 = rectangle(70, 50, 120, 400)
#
#b0 = rectangle(100,800,200,900)
#b1 = rectangle(192,825,300,900)
#
#start = stop = None
#sel = None
#
def buttondown(button, pos):
    global start, stop, sel
#    global start, selection0, selection1, sel
    if button==3 and sel:
        example[sel[0]:sel[1]] = []
        sel = None
        refresh()
        return
    start = visual.pick(pos)
    if start is not None:
        obj, edge = start
        sel = edge, edge

def buttonup(button, pos):
    global start, stop, sel
    if start is None: return
    stop = visual.pick(pos)
    if stop is None:
        start = None
        return
    start_obj, start_edge = start
    stop_obj, stop_edge = stop
    sel = min(start_edge, stop_obj), max(start_edge,stop_obj+1)
    if start==stop: sel = start_edge, start_edge
    start = stop = None
#    global start, stop, sel
#    if start is None or stop is None: return
#    start_obj, start_edge = start
#    stop_obj, stop_edge = stop
##    if start<stop:
##        selection1 = selection_rect(start_edge)
##        selection0 = selection_rect(stop_obj)
##    if start>stop:
##        selection0 = selection_rect(start_edge-1)
##        selection1 = selection_rect(stop_obj)
#    sel = min(start_edge, stop_obj), max(start_edge,stop_obj+1)
#    if start==stop:
##        selection0 = selection_rect(start_edge-1)
##        selection1 = selection_rect(start_edge)
#        sel = start_edge, start_edge
#    start = stop = None
#
def motion(buttons, pos, rel):
    global start, stop, sel
    if start is None: return
    stop = visual.pick(pos)
    if stop is None: return
    start_obj, start_edge = start
    stop_obj, stop_edge = stop
    sel = min(start_edge, stop_obj), max(start_edge,stop_obj+1)
    if start==stop: sel = start_edge, start_edge

def keydown(key, character):
    global sel
    print key, repr(character)
    if key == 276:
        sel = sel[0]-1, sel[0]-1
    if key == 275:
        sel = sel[0]+1, sel[0]+1
    if key == 9:
        example[sel[0]:sel[1]] = [node('OPEN'), node('CLOSE')]
        sel = sel[0]+1, sel[0]+1
    elif character == '\r':
        example[sel[0]:sel[1]] = []
        sel = sel[0]+1, sel[0]+1
    elif key == 8:
        if sel[0] == sel[1]:
            sel = sel[0]-1, sel[0]
        example[sel[0]:sel[1]] = []
        sel = sel[0], sel[0]
    elif character != '' and sel:
        example[sel[0]:sel[1]] = [character]
        sel = sel[0]+1, sel[0]+1
    return refresh()

def keyup(key):
    pass

def on_event(event):
    if event.type == pygame.QUIT:            sys.exit()
    if event.type == pygame.MOUSEBUTTONDOWN: buttondown(event.button, event.pos)
    if event.type == pygame.MOUSEBUTTONUP:   buttonup(event.button, event.pos)
    if event.type == pygame.MOUSEMOTION:     motion(event.buttons, event.pos, event.rel)
    if event.type == pygame.KEYDOWN:         keydown(event.key, event.unicode)
    if event.type == pygame.KEYUP:           keyup(event.key)

def fill(screen):
    screen.fill((20,22,10))
    for graphic, rect in output:
        graphic.blit(screen, rect)

    if sel:
        start, stop = sel
        visual.blit_range(screen, start, stop, visual_config)
#    width, height = screen.get_size()
##    font.blit(screen, (width/2,40), "font blitting test")
#
##    stretch(pupu).blit(screen, r1)
##    stretch(quad).blit(screen, r2)
##    cyan.blit(screen, r3)
##    border.blit(screen, r4)
##    transcludent.blit(screen, r5)
##    invert.blit(screen, r6)
#
#    graphic = border
#    #graphic = stretch(pupu)
#    for i, sn in enumerate(selectables):
#        graphic = alien_left if i & 1 else alien_right
#        graphic.blit(screen, sn.rect)
#
#    if sel:
#        start, stop = sel
#        v.blit_range(screen, start, stop, visual_config)
#        font.blit(screen, (10,720), "selection: x=%i y=%i" % sel)
#
##    if selection1 is not None: caret_left.blit(screen, selection1.pad(2))
##    if selection0 is not None: caret_right.blit(screen, selection0.pad(2))
#
##    caret_right.blit(screen, b0)
##    caret_left.blit(screen, b1)
#
#    
#    font.blit(screen, (10,740), "REMINDER FOR SELF: Avoid image stretching, it makes things slow.")
