import sys, os
from argon import Argon, rgba
from frame import Frame, Overlay, LayoutController
from schema import mutable, fileformat_flat
import layout

filename = (sys.argv[1] if len(sys.argv) > 1 else 'scratch.flat')

if os.path.exists(filename):
    document = fileformat_flat.load_file(filename, mutable)
else:
    document = mutable.Document([
    #    mutable.String(u"hello"),
    #    mutable.String(u"world"),
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

def render_selection(argon, frame, selection):
    box = frame.find_intron(mutable.get_object(selection))
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
    def free(self):
        pass

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

    def insert_object(self, data):
        if isinstance(self.selection, mutable.Selection):
            if isinstance(self.selection.container, (mutable.Document, mutable.List)):
                self.selection.splice([data])
                return True
        else:
            mutable.get_document(self.selection).replace(self.selection, data)
            self.selection = data
            return True

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

default = layout.default.inherit(
    renderer = box_renderer,
    background = None,
    background_color = rgba(255, 255, 255),
    font = argon.default_font,
    color = whiteish,
    align = layout.Align(0, 0),
)

row_default = default.inherit(spacing = 8)

sym_default  = default.inherit(color = cyan)
bad_default  = default.inherit(color = red)
obj_default = default.inherit(color = gray)
list_default = default.inherit(background = bracket2, background_color = gray, padding = (4, 4, 4, 4))

def mk_unknown(intron, obj):
    intron.style = default
    if isinstance(obj, mutable.Struct):
        intron.node = layout.Row([
            layout.Label(obj.type.name, sym_default),
            layout.Column(default_layouter.many(obj), default),
        ], row_default)
    elif isinstance(obj, mutable.String):
        intron.node = layout.Label(obj.data, default)
        intron.node.reference = 0, len(obj)
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
frame.background_color = background_color
frame.mode = EditMode(frame, mutable.normalize(document, False))

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
