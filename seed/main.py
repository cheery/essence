from argon import Argon, rgba
from frame import Frame, Overlay
from schema import mutable
import layout

document = mutable.Document([
    mutable.String(u"hello"),
    mutable.String(u"world"),
])

argon = Argon(600, 800)

def box_renderer(argon, box):
    x,y,w,h = box.rect
    if x+w < 0 or argon.width < x or y+h < 0 or argon.height < y:
        return
    background = box.style['background']
    if background:
        background_color = box.style['background_color']
        argon.render.rectangle(box.rect, background, background_color)
    if isinstance(box, layout.Label):
        font             = box.style['font']
        color            = box.style['color']
        argon.render.text(box.baseline_pos, box.source, font, color)

background_color = rgba(0x24, 0x24, 0x24)
green      = rgba(0x95, 0xe4, 0x54)
cyan       = rgba(0x8a, 0xc6, 0xf2)
red        = rgba(0xe5, 0x78, 0x6d)
lime       = rgba(0xca, 0xe6, 0x82)
gray       = rgba(0x99, 0x96, 0x8b)
back       = rgba(0x24, 0x24, 0x24)
whiteish   = rgba(0xf6, 0xf3, 0xe8)

box7 = argon.load.patch9('box7.png')

default = layout.default.inherit(
    renderer = box_renderer,
    background = None,
    background_color = rgba(255, 255, 255),
    font = argon.default_font,
    color = whiteish,
    align = layout.Align(0, 0),
)

def render_selection(argon, frame, selection):
    box = find_intron(frame.box, mutable.get_object(selection))
    if box is None:
        argon.render.rectangle((0,0,frame.width, frame.height), box7, color = rgba(255, 255, 0, 192))
    else:
        argon.render.rectangle(box.rect, box7, color = rgba(32, 32, 255, 128))
        if isinstance(selection, mutable.Selection):
            head = selection.head
            start, stop = selection.start, selection.stop
            for child in box.references():
                if child.in_range(start, stop):
                    rect = child.selection_marker(start, stop)
                    argon.render.rectangle(rect, color = rgba(0, 0, 255, 128))
                if child.in_range(head, head):
                    rect = child.selection_marker(head, head)
                    argon.render.rectangle(rect, color = rgba(255, 255, 255, 255))

class Mode(object):
    def on_keydown(self, key, modifiers, text):
        pass

    def on_mousedown(self, button, pos):
        return True

    def on_mousemotion(self, pos, vel):
        pass

    def on_mouseup(self, button, pos):
        pass

class EditMode(Mode):
    def __init__(self, frame, selection):
        self.frame = frame
        self.selection = selection
        self.overlay = Overlay(frame, self.render_overlay)

    def render_overlay(self, argon):
        argon.clear(rgba(0,0,0,0))
        render_selection(argon, self.frame, self.selection)

    def free(self):
        self.overlay.free()

from layoutchain import LayoutRoot, LayoutChain, LayoutController

def mk_unknown(intron, obj):
    intron.style = default
    if isinstance(obj, mutable.Struct):
        intron.node = layout.Row([
            layout.Label(obj.type.name, default),
            layout.Column(default_layouter.many(obj), default),
        ], default)
    elif isinstance(obj, mutable.String):
        intron.node = layout.Label(obj.data, default)
        intron.node.reference = 0, len(obj)
    else:
        intron.node = layout.Label("unknown %r" % obj)

def mk_document(intron, document):
    intron.style = default
    if len(document) > 0:
        intron.node = layout.Column(default_layouter.many(document), default)
    else:
        intron.node = layout.Label("empty document", default)

default_layouter = LayoutChain({
    mutable.Document: mk_document,
}, LayoutRoot(mk_unknown))

toolbar_height = argon.default_font.height*2
frame = Frame((0, 0, argon.width, argon.height-toolbar_height), document, default_layouter)
frame.background_color = background_color
frame.mode = EditMode(frame, mutable.normalize(document))

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

def find_intron(box, obj):
    if isinstance(box, layout.Intron) and isinstance(box.controller, LayoutController):
        if box.controller.obj == obj:
            return box
    for child in box:
        ret = find_intron(child, obj)
        if ret is None:
            continue
        return ret

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
def pick_intron(frame, pos):
    intron = None
    for box in frame.box.pick(pos):
        if isinstance(box, layout.Intron):
            intron = box
    return intron
#
@argon.listen
def on_mousedown(button, pos):
    if frame.mode is None or frame.mode.on_mousedown(button, pos):
        intron = pick_intron(frame, pos)
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
