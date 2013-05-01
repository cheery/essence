from argon import Argon, rgba
from frame import Frame, Overlay
from schema.base import Constant, Struct
from schema import proxy
from schema.mutator import Mutator
from schema.selection import Selection, BufferSelection, StringSelection, ListSelection
from schema.language import language
import layout

def roll(document, path):
    current = document
    for index in path:
        current = current[index]
    return current

def select_this(struct):
    if isinstance(struct.proxy, proxy.StructProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return Mutator(parent, struct.proxy.index)
    elif isinstance(struct.proxy, proxy.ListProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return ListSelection(parent, struct.proxy.list_index, struct.proxy.index+1, struct.proxy.index)

def wade_to_previous(sel):
    if isinstance(sel, ListSelection) and sel.head > 0:
        obj = sel.struct[sel.index][sel.head - 1]
        if isinstance(obj, Struct):
            return climb_tail(obj, len(obj) - 1)
        else:
            return sel.__class__(sel.struct, sel.index, sel.head - 1)
    else:
        return skip_to_previous(sel.struct, sel.index)

def wade_to_next(sel):
    if isinstance(sel, ListSelection) and sel.head < sel.length:
        obj = sel.struct[sel.index][sel.head]
        if isinstance(obj, Struct):
            return climb_head(obj, 0)
        else:
            return sel.__class__(sel.struct, sel.index, sel.head + 1)
    else:
        return skip_to_next(sel.struct, sel.index)

def skip_to_previous(struct, index):
    if index > 0:
        return climb_tail(struct, index - 1)
    elif isinstance(struct.proxy, proxy.StructProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return skip_to_previous(parent, struct.proxy.index)
    elif isinstance(struct.proxy, proxy.ListProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return ListSelection(parent, struct.proxy.list_index, struct.proxy.index)
    assert(struct.proxy is not None)

def skip_to_next(struct, index):
    if index + 1 < len(struct):
        return climb_head(struct, index + 1)
    elif isinstance(struct.proxy, proxy.StructProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return skip_to_next(parent, struct.proxy.index)
    elif isinstance(struct.proxy, proxy.ListProxy):
        parent = roll(document, struct.proxy.parent.unroll()[1])
        return ListSelection(parent, struct.proxy.list_index, struct.proxy.index + 1)
    assert(struct.proxy is not None)

def deep_climb_head(struct, index, head):
    obj = struct[index]
    if isinstance(obj, Struct):
        return deep_climb_head(obj, 0, 0)
    elif isinstance(obj, list) and head < len(obj) and isinstance(obj[head], Struct):
        return deep_climb_head(obj[head], 0, 0)
    elif isinstance(obj, list):
        sel = ListSelection(current, index, min(head, len(obj)))
    elif isinstance(obj, str):
        sel = BufferSelection(current, index, min(head, len(obj)))
    elif isinstance(obj, unicode):
        sel = StringSelection(current, index, min(head, len(obj)))
    else:
        sel = Mutator(current, index)
    return sel

def climb_head(struct, index):
    current = struct
    while isinstance(current[index], Struct):
        current = current[index]
        index = 0
    obj = current[index]
    if isinstance(obj, list):
        sel = ListSelection(current, index, 0)
    elif isinstance(obj, str):
        sel = BufferSelection(current, index, 0)
    elif isinstance(obj, unicode):
        sel = StringSelection(current, index, 0)
    else:
        sel = Mutator(current, index)
    return sel

def climb_tail(struct, index):
    current = struct
    while isinstance(current[index], Struct):
        current = current[index]
        index = len(current) - 1
    obj = current[index]
    if isinstance(obj, list):
        sel = ListSelection(current, index, len(obj))
    elif isinstance(obj, str):
        sel = BufferSelection(current, index, len(obj))
    elif isinstance(obj, unicode):
        sel = StringSelection(current, index, len(obj))
    else:
        sel = Mutator(current, index)
    return sel

def motion(sel, head, shift):
    sel.head = head
    if not shift:
        sel.tail = head

background_color = rgba(0x24, 0x24, 0x24)
green      = rgba(0x95, 0xe4, 0x54)
cyan       = rgba(0x8a, 0xc6, 0xf2)
red        = rgba(0xe5, 0x78, 0x6d)
lime       = rgba(0xca, 0xe6, 0x82)
gray       = rgba(0x99, 0x96, 0x8b)
back       = rgba(0x24, 0x24, 0x24)
whiteish   = rgba(0xf6, 0xf3, 0xe8)

mode = None
def set_mode(new_mode):
    global mode
    if mode:
        mode.free()
    mode = new_mode

class EditMode(object):
    def __init__(self, sel, click_response=False):
        self.sel = sel
        self.overlay = Overlay(main_frame, self.render_overlay)
        self.dragging = click_response

    def free(self):
        self.overlay.free()
    
    def render_overlay(self, argon):
        argon.clear(rgba(0,0,0,0))
        slot = find_slot(main_frame.contents, self.sel.struct, self.sel.index)
        if slot is not None:
            argon.render_rectangle(slot.rect, box7, color = rgba(32, 32, 32, 128))
        if slot is not None and isinstance(self.sel, Selection):
            head = self.sel.head
            start, stop = self.sel.start, self.sel.stop
            for box in slot.references():
                if box.in_range(start, stop):
                    rect = box.selection_marker(start, stop)
                    argon.render_rectangle(rect, color = rgba(0, 0, 255, 128))
                if box.in_range(head, head):
                    rect = box.selection_marker(head, head)
                    argon.render_rectangle(rect, color = rgba(255, 255, 255, 255))
        if slot is None:
            argon.render_rectangle((0,0,main_frame.width, main_frame.height), box7, color = rgba(255, 255, 0, 192))

    def on_keydown(self, key, modifiers, text):
        shift = 'shift' in modifiers
        ctrl = 'ctrl' in modifiers
        nxt = None
        if key == 'left' and self.sel.head > 0:
            motion(self.sel, self.sel.head - 1, shift)
        elif key == 'right' and self.sel.head < self.sel.length:
            motion(self.sel, self.sel.head + 1, shift)
        elif key == 'home':
            motion(self.sel, 0, shift)
        elif key == 'end':
            motion(self.sel, self.sel.length, shift)
        elif key == 'return' and shift:
            nxt = skip_to_previous(self.sel.struct, self.sel.index)  # it might need fixup. :P
        elif key == 'return':
            nxt = skip_to_next(self.sel.struct, self.sel.index)  # it might need fixup. :P
        elif key == 'up':
            nxt = wade_to_previous(self.sel)
        elif key == 'down':
            nxt = wade_to_next(self.sel)
        elif ctrl and key == 'a':
            if self.sel.start == 0 and self.sel.stop == self.sel.length:
                nxt = select_this(self.sel.struct)
            else:
                self.sel.start = 0
                self.sel.stop  = self.sel.length

        #fixme, maybe. :/
        if nxt is not None:
            self.sel = nxt
        self.overlay.dirty = True

    def on_mousedown(self, button, pos):
        return True # Execute default behavior

    def on_mousemotion(self, pos, vel):
        if self.dragging:
            slot = find_slot(main_frame.contents, self.sel.struct, self.sel.index)
            if slot is not None:
                self.sel.head = slot.pick_offset(pos)
                self.overlay.dirty = True

    def on_mouseup(self, button, pos):
        self.dragging = False

class StructureEditor(object):
    def __init__(self, struct, index):
        self.struct = struct
        self.index  = index

    def build(self, intron):
        obj = self.struct[self.index]
        if isinstance(obj, (Struct, Constant)):
            intron.node = visualize_struct(obj)
        elif isinstance(obj, list) and len(obj) == 0:
            intron.node = layout.Label("empty", gray_style)
        elif isinstance(obj, list):
            boxes = []
            for index, struct in enumerate(obj):
                box = visualize_struct(struct)
                box.reference = (index, index+1)
                boxes.append(box)
            intron.node = layout.Column(boxes, list_style)
        elif isinstance(obj, unicode) and len(obj) == 0:
            intron.node = layout.Label('""', gray_style)
        elif isinstance(obj, unicode):
            intron.node = layout.Label(obj, default)
            intron.node.reference = (0, len(obj))
        else:
            intron.node = layout.Label("undefined_style", gray_style)
        intron.style = default

    def click(self, intron, button, pos):
        obj = self.struct[self.index]
        if isinstance(obj, list):
            sel = ListSelection(self.struct, self.index, intron.pick_offset(pos))
        elif isinstance(obj, str):
            sel = BufferSelection(self.struct, self.index, intron.pick_offset(pos))
        elif isinstance(obj, unicode):
            sel = StringSelection(self.struct, self.index, intron.pick_offset(pos))
        else:
            sel = Mutator(self.struct, self.index)
        set_mode( EditMode(sel, True) )

#        mutator = Mutator(self.struct, self.index)
#        which = 
#        if mutator.which in ('list', 'string', 'buffer'):
#            Selection
#        print 'clicky!'
#        print self.struct

def visualize_struct(struct):
    if isinstance(struct, Constant):
        return layout.Label(struct.uid, type_style)
    boxes = [ ]
    label = layout.Label(struct.type.name, type_style)
    for index, obj in enumerate(struct):
        intron = layout.Intron(StructureEditor(struct, index))
        boxes.append(intron)
    return layout.Row([label, layout.Column(boxes, slot_style)], struct_style)

## Utility functions

def find_slot(box, struct, index):
    if isinstance(box, layout.Intron) and isinstance(box.controller, StructureEditor):
        if box.controller.struct == struct and box.controller.index == index:
            return box
    for _box in box:
        rt = find_slot(_box, struct, index)
        if rt is None:
            continue
        return rt

## Initializes the renderer and layouter.
argon = Argon()
box7 = argon.cache.patch9('box7.png')
box2 = argon.cache.patch9('box2.png')
bracket2 = argon.cache.patch9('bracket2.png')

def sys_renderer(argon, box):
    background       = box.style['background']
    if background:
        background_color = box.style['background_color']
        argon.render_rectangle(box.rect, background, background_color)
    if isinstance(box, layout.Label):
        font             = box.style['font']
        color            = box.style['color']
        argon.render_text(box.baseline_pos, box.source, font, color)

default = layout.default.inherit(
    renderer = sys_renderer,
    background = None,
    background_color = rgba(255, 255, 255),
    font = argon.cache.font('AnonymousPro_17'),
    color = whiteish,
    align = layout.Align(0, 0),
)

slot_style = default.inherit(align = layout.AlignByFlow(0, 1))

type_style = default.inherit(color = cyan)
gray_style = default.inherit(color = gray)

list_style   = default.inherit(background = bracket2, background_color = rgba(255, 255, 255, 0x40), spacing = 2, padding=(6, 6, 6, 6))
struct_style = default.inherit(background = box2, background_color = rgba(255, 255, 255, 0x80), spacing = 8, padding=(4,4,4,4))

# document
document = language
proxy.mkroot(None, document)

# main frame
main_frame = Frame((0, 0, argon.width, argon.height), visualize_struct(document))# layout.Label("hello there!", default))
main_frame.background_color = background_color

set_mode(EditMode( climb_head(document, 0) ))

@argon.listen
def on_frame(now):
    argon.clear(rgba(0x80, 0x90, 0xA0))
    main_frame.render(argon)

@argon.listen
def on_keydown(key, modifiers, text):
    if key == 'escape':
        argon.running = False
    if key == 'pageup':
        x, y = main_frame.scroll
        main_frame.scroll = x, min(y + 100, 0)
        main_frame.dirty = True
    if key == 'pagedown':
        x, y = main_frame.scroll
        main_frame.scroll = x, y - 100
        main_frame.dirty = True

    if mode is not None:
        mode.on_keydown(key, modifiers, text)

def pick_intron(frame, pos):
    intron = None
    for box in frame.contents.pick(pos):
        if isinstance(box, layout.Intron):
            intron = box
    return intron

@argon.listen
def on_mousedown(button, pos):
    if mode is None or mode.on_mousedown(button, pos):
        intron = pick_intron(main_frame, pos)
        if intron is not None:
            intron.controller.click(intron, button, pos)

@argon.listen
def on_mousemotion(pos, vel):
    if mode is not None:
        mode.on_mousemotion(pos, vel)

@argon.listen
def on_mouseup(button, pos):
    if mode is not None:
        mode.on_mouseup(button, pos)

argon.run()
