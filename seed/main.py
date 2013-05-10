#!/usr/bin/env python2
import sys, os
from argon import Argon, rgba
from frame import Frame, Overlay, LayoutController
from schema import mutable, fileformat_flat
import layout

filename = (sys.argv[1] if len(sys.argv) > 1 else 'scratch.flat')

if os.path.exists(filename):
    document = fileformat_flat.load_file(filename, mutable)
else:
    document = mutable.Document([])

argon = Argon(600, 800)

from mode import Mode, SelectionMode

class EditMode(SelectionMode):
    def on_keydown(self, key, modifiers, text):
        selection = self.selection
        overlay = self.overlay
        shift = 'shift' in modifiers
        ctrl  = 'ctrl' in modifiers
        if ctrl and key == 's':
            fileformat_flat.save_file(filename, mutable, document)
        if ctrl and key == 'a':
            self.selection = mutable.extend(selection)
            overlay.dirty = True
        if isinstance(selection, mutable.Selection):
            if key == 'left' and selection.head > 0:
                selection.head -= 1
            elif key == 'right' and selection.head < selection.last:
                selection.head += 1
            if key in ('left', 'right'):
                selection.tail = selection.tail if shift else selection.head
                overlay.dirty = True
            if isinstance(selection.container, mutable.String):
                if not ctrl and len(text) > 0 and text.isalnum() or text in ' ':
                    selection.splice(text)
                    selection.start = selection.stop
            if key in ('backspace', 'delete'):
                if selection.start == selection.stop:
                    selection.start -= (key == 'backspace')
                    selection.stop  += (key == 'delete')
                selection.splice(u'')
                selection.stop = selection.start
        else:
            parent = selection.parent
            index  = parent.index(selection)
            if key == 'left' and index > 0:
                self.selection = parent[index-1]
                overlay.dirty = True
            if key == 'right' and index+1 < len(parent):
                self.selection = parent[index+1]
                overlay.dirty = True

        if text == '/':
            target = mutable.String("")
            data = mutable.Struct(mutable.StructType(u'variable:name'), [target])
            if self.insert_object(data):
                self.selection = mutable.Selection(target, 0)

        if text == '(':
            target = mutable.Struct(mutable.StructType(u'null'), [])
            data = mutable.Struct(mutable.StructType(u'call:callee:arguments'), [target, mutable.List([])])
            if self.insert_object(data):
                self.selection = target

from layoutchain import LayoutRoot, LayoutChain

background_color = rgba(0x24, 0x24, 0x24)
green      = rgba(0x95, 0xe4, 0x54)
cyan       = rgba(0x8a, 0xc6, 0xf2)
red        = rgba(0xe5, 0x78, 0x6d)
lime       = rgba(0xca, 0xe6, 0x82)
gray       = rgba(0x99, 0x96, 0x8b)
back       = rgba(0x24, 0x24, 0x24)
whiteish   = rgba(0xf6, 0xf3, 0xe8)

box7 = argon.load.patch9('box7.png')
bracket2 = argon.load.patch9('bracket2.png')

import renderer
default = renderer.get_default_style(argon).inherit(
    color = whiteish,
)

row_default = default.inherit(spacing = 8)

sym_default  = default.inherit(color = cyan)
bad_default  = default.inherit(color = red)
obj_default = default.inherit(color = gray)
str_default = default.inherit(color = lime)
list_default = default.inherit(background = bracket2, background_color = gray, padding = (4, 4, 4, 4))

def mk_unknown(intron, obj):
    intron.style = default
    if isinstance(obj, mutable.Struct):
        intron.node = layout.Row([
            layout.Label(obj.type.name, sym_default),
            layout.Column(default_layouter.many(obj), default),
        ], row_default)
    elif isinstance(obj, mutable.String):
        data = layout.Label(obj.data, str_default)
        data.reference = 0, len(obj)
        intron.node = layout.Row([layout.Label('"', str_default), data, layout.Label('"', str_default)], default)
    elif isinstance(obj, mutable.List):
        intron.node = layout.Column(default_layouter.many(obj), list_default)
    else:
        intron.node = layout.Label("unknown %r" % obj, bad_default)

def mk_document(intron, document):
    intron.style = default
    if len(document) > 0:
        intron.node = layout.Column(default_layouter.many(document), default)
    else:
        intron.node = layout.Label("empty document", obj_default)

default_layouter = LayoutChain({
    mutable.Document: mk_document,
}, LayoutRoot(mk_unknown))

toolbar_height = argon.default_font.height*2
frame = Frame((0, 0, argon.width, argon.height-toolbar_height), document, default_layouter)
frame.mode = EditMode(frame, mutable.normalize(document, False))

frame.style.update(
    background_color = background_color,
    caret_color = rgba(255, 255, 255, 255),
    selection_background = box7,
    selection_color_inner = rgba(0,   0, 255, 128),
    selection_color_outer = rgba(32, 32, 255, 128),
    selection_color_bad   = rgba(255, 255, 0, 192),
)

def set_mode(new_mode):
    if frame.mode is not None:
        frame.mode.free()
    frame.mode = new_mode

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
                print obj, head
                set_mode( EditMode(frame, mutable.Selection(obj, head)) )
            else:
                print mutable.normalize(obj)
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
