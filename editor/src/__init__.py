import pygame, sys
import bitmapfont
import graphics
graphics = reload(graphics)
from graphics import rectangle, patch9, stretch, color, invert, picarea
import selection
selection = reload(selection)

import essence.document
from essence.document import string, block

doc = essence.document.new([
    string('var', 'a variable'),
    string('num', 'a number'),
])

font = bitmapfont.load('font/proggy_tiny')

dotsies = {
    ' ': 0b00000, 'a': 0b10000, 'b': 0b01000, 'c': 0b00100, 'd': 0b00010,
    'e': 0b00001, 'f': 0b11000, 'g': 0b01100, 'h': 0b00110, 'i': 0b00011,
    'j': 0b10100, 'k': 0b01010, 'l': 0b00101, 'm': 0b10010, 'n': 0b01001,
    'o': 0b10001, 'p': 0b11100, 'q': 0b11010, 'r': 0b10110, 's': 0b01110,
    't': 0b01101, 'u': 0b01011, 'v': 0b00111, 'w': 0b11001, 'x': 0b10101,
    'y': 0b10011, 'z': 0b11011,
}

def dots(screen, (x,y), text, color=(255,255,255,255), size=3):
    for character in text:
        pattern = dotsies.get(character, 31)
        for i in range(5):
            if pattern & (1 << (4-i)):
                screen.fill(color, (x,y+size*i,size,size))
        x += size

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

sel = selection.caret(head=0,tail=0)

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
                pair = alien_left, rectangle(x+2,y-8,x+5,y+3)
                output.append(pair)
                visual.entries.append(selection.selector(pair[1].pad(1), index))
                x += 6
            if obj.info == 'CLOSE':
                pair = alien_right, rectangle(x+2,y-8,x+5,y+3)
                output.append(pair)
                visual.entries.append(selection.selector(pair[1].pad(1), index))
                x += 6
        else:
            metrics = font.metadata[obj]
            if metrics['display']:
                pair = glyph(metrics), glyph_rect(metrics, x, y)
                output.append(pair)
            rect = rectangle(x, y-12, x+int(metrics['advance']), y+4)
            visual.entries.append(selection.selector(rect, index))
            x += int(metrics['advance'])

refresh()

#border = patch9(pygame.image.load('assets/border.png'))
#pupu = pygame.image.load('assets/pupu.jpg')
#quad = pygame.image.load('assets/quad.png')
#cyan = color(0,255,255)
#invert = invert(color(255,255,255))
#
#transcludent = color(100, 0, 0, 150)

pygame.key.set_repeat(500, 25)

dragging = False
def buttondown(button, pos):
    global sel, dragging
    if button==3:
        example[sel.start:sel.stop] = []
        sel.tail = sel.head = sel.start
        return refresh()
    start = visual.pick(pos)
    if start is not None:
        obj, edge = start
        sel.tail = sel.head = edge
        dragging = True

def buttonup(button, pos):
    global sel, dragging
    if dragging == False: return
    dragging = False
    stop = visual.pick(pos)
    if stop is not None:
        stop_obj, stop_edge = stop
        if stop_edge == sel.tail:
            sel.head = sel.tail
        elif stop_edge < sel.tail:
            sel.head = stop_obj
        elif stop_edge > sel.tail:
            sel.head = stop_obj+1

def motion(buttons, pos, rel):
    global sel, dragging
    if dragging == False: return
    stop = visual.pick(pos)
    if stop is not None:
        stop_obj, stop_edge = stop
        if stop_edge == sel.tail:
            sel.head = sel.tail
        elif stop_edge < sel.tail:
            sel.head = stop_obj
        elif stop_edge > sel.tail:
            sel.head = stop_obj+1

def keydown(key, character):
    global sel
    print key, repr(character)
    if key == 276:
        sel.tail = sel.head = sel.head - 1
    elif key == 275:
        sel.tail = sel.head = sel.head + 1
    elif key == 9:
        example[sel.start:sel.stop] = [node('OPEN'), node('CLOSE')]
        sel.tail = sel.head = sel.start+1
    elif key == 127:
        if sel.length == 0:
            sel.tail = sel.head + 1
        example[sel.start:sel.stop] = []
        sel.head = sel.tail = sel.start
    elif character == '\r':
        example[sel.start:sel.stop] = []
        sel.head = sel.tail = sel.start+1
    elif key == 8:
        if sel.length == 0:
            sel.tail = sel.head - 1
        example[sel.start:sel.stop] = []
        sel.head = sel.tail = sel.start
    elif character != '':
        example[sel.start:sel.stop] = [character]
        sel.head = sel.tail = sel.start+1
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

    dots(screen, (10, 140), "here be lots of dots", size=1)
    dots(screen, (10, 170), "here be lots of dots", size=2)
    dots(screen, (10, 200), "here be lots of dots", size=3)
    dots(screen, (10, 230), "here be lots of dots", size=4)

    visual.blit_range(screen, sel.start, sel.stop, visual_config)
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
