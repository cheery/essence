#!/usr/bin/env python2
import sys, os
from argon import Argon, rgba
from frame import Frame, Overlay, LayoutController
from schema import mutable, fileformat_flat
import layout
import renderer

green      = rgba(0x95, 0xe4, 0x54)
cyan       = rgba(0x8a, 0xc6, 0xf2)
red        = rgba(0xe5, 0x78, 0x6d)
lime       = rgba(0xca, 0xe6, 0x82)
gray       = rgba(0x99, 0x96, 0x8b)
whiteish   = rgba(0xf6, 0xf3, 0xe8)

class default_theme(object):
    background   = rgba(0x24, 0x24, 0x24)
    symbol_color  = whiteish
    keyword_color = cyan
    string_color = lime
    number_color = red
    object_color = gray
    malform_color = red

theme = default_theme

filename = (sys.argv[1] if len(sys.argv) > 1 else 'scratch.flat')
if os.path.exists(filename):
    document = fileformat_flat.load_file(filename, mutable)
else:
    document = mutable.Document([])
document.filename = filename

argon = Argon(600, 800)

#from mode import Mode, SelectionMode

default = renderer.get_default_style(argon).inherit(
    color = whiteish,
)

language = __import__('strike')
EditMode = language.EditMode
layouter = language.init(argon, default, theme)

toolbar_height = argon.default_font.height*2
frame = Frame((0, 0, argon.width, argon.height-toolbar_height), document, layouter)
frame.mode = EditMode(frame, mutable.normalize(document, False))

def set_mode(new_mode):
    if frame.mode is not None:
        frame.mode.free()
    frame.mode = new_mode

box7 = argon.load.patch9('box7.png')
frame.style.update(
    background_color = theme.background,
    caret_color = rgba(255, 255, 255, 255),
    selection_background = box7,
    selection_color_inner = rgba(0,   0, 255, 128),
    selection_color_outer = rgba(32, 32, 255, 128),
    selection_color_bad   = rgba(255, 255, 0, 192),
)

@argon.listen
def on_frame(now):
    argon.render.bind()
    argon.clear(rgba(0x30, 0x30, 0x30))
    frame.render(argon)
    #argon.render.rectangle((0,0, 200, 200), box7)
    argon.show_performance_log()
    argon.render.unbind()

@argon.listen
def on_keydown(key, modifiers, text):
    if key == 'escape':
        argon.running = False
#    if key == 'pageup':
#        x, y = main_frame.scroll
#        main_frame.scroll = x, min(y + 100, 0)
#        main_frame.dirty = True
#    if key == 'pagedown':
#        x, y = main_frame.scroll
#        main_frame.scroll = x, y - 100
#        main_frame.dirty = True
#
    if frame.mode is not None:
        frame.mode.on_keydown(key, modifiers, text)
#
@argon.listen
def on_mousedown(button, pos):
    if frame.mode is None or frame.mode.on_mousedown(button, pos):
        intron = frame.pick_intron(pos)
        if intron is None:
            set_mode( None )
            return
        if isinstance(intron.controller, LayoutController):
            obj = intron.controller.obj
            if isinstance(obj, (mutable.List, mutable.String, mutable.Document)):
                head = intron.pick_offset(pos)
                set_mode( EditMode(frame, mutable.Selection(obj, head)) )
            else:
                set_mode( EditMode(frame, mutable.normalize(obj)) )
        # replace EditMode with grabber later.

@argon.listen
def on_mousemotion(pos, vel):
    if frame.mode is not None:
        frame.mode.on_mousemotion(pos, vel)

@argon.listen
def on_mouseup(button, pos):
    if frame.mode is not None:
        frame.mode.on_mouseup(button, pos)

argon.run()
