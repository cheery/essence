from argon import Argon, rgba, Texture, Framebuffer
import layout
from macron import macron
from schema import Struct, Meta, Constant, Proxy, Mutator, Selection, roll
from OpenGL.GL import *
from frame import Frame, Overlay

argon = Argon()
argon.pos = 0,0

circle64 = argon.cache.image('circle64.png')
box7 = argon.cache.patch9('box7.png')
font = argon.cache.font('AnonymousPro_17')

def sys_renderer(argon, node):
    background = node.style['background']
    color = node.style['color']
    if background:
        argon.render_rectangle(node.rect, background, color)
    if isinstance(node, layout.Label):
        font = node.style['font']
        argon.render_text(
            node.baseline_pos,
            node.source,
            font,
            color,
        )

default = layout.default.inherit(
    font = font,
    renderer = sys_renderer,
    background = None,
    color = rgba(255,255,255),
    spacing  = 7,
)
struct_style = default.inherit(
    background = box7,
    padding  = (14,14,14,14),
)
red_style = default.inherit(
    color = rgba(255,0,0)
)

yellow_style = default.inherit(
    color = rgba(128,128,0)
)

def refresh(intron):
    intron.rebuild()
    frame.dirty = True

#intron = locate_intron(frame.contents, mutor.struct, mutor.index)
#if intron is None:
#    return

def locate_intron(box, struct, index):
    if isinstance(box, layout.Intron) and box.args[0] == struct and box.args[1] == index:
        return box
    for item in box:
        res = locate_intron(item, struct, index)
        if res is not None:
            return res
    return None

class GenericMode(object):
    def __init__(self, intron, mutator):
        self.intron  = intron
        self.mutator = mutator
        self.overlay = Overlay(frame, self.render_overlay)

    def free(self):
        self.overlay.free()

    def render_overlay(self, argon):
        argon.clear(rgba(0,0,0,0))
        argon.render_rectangle(self.intron.rect, box7, color = rgba(0x00, 0x00, 0xFF, 0x80))
        mark = rgba(0x00, 0x00, 0xFF)
        if isinstance(self.mutator, Selection):
            start, stop = self.mutator.start, self.mutator.stop
            for box in self.intron.references():
                if box.in_range(start, stop):
                    rect = box.selection_marker(start, stop)
                    argon.render_rectangle(rect, color=mark)

    @classmethod
    def enter_click(cls, intron, pos):
        struct, index = intron.args
        mutator = Mutator(struct, index)
        if mutator.which in ('list', 'string', 'buffer'):
            index = intron.pick_offset(pos)
            mutator = Selection(mutator, index)
        set_mode( GenericMode(intron, mutator) )

    @classmethod
    def enter_descend(cls, intron, from_tail=False):
        struct, index = intron.args
        mutator = Mutator(struct, index)
        if mutator.which in ('list', 'string', 'buffer'):
            mutator = Selection(mutator, len(struct[index]) * from_tail)
        set_mode( GenericMode(intron, mutator) )

    def insert_text(self, text):
        mutator = self.mutator
        if isinstance(mutator, Selection):
            if mutator.which == 'list':
                # this is not nice way to do it.
                mutator.splice([language.Ref(u"")])
                struct = mutator.struct
                index0 = mutator.index
                index1 = mutator.start
                ref = struct[index0][index1]
                mutator = Selection(Mutator(ref, 0), 0)
                refresh(self.intron)
                self.intron = locate_intron(self.intron, ref, 0)
            if mutator.which != 'string':
                self.mutator = mutator
                refresh(self.intron)
                return False
            mutator.splice(text)
            mutator.start = mutator.stop
        else:
            mutator.replace(text)
            mutator = Selection(mutator, len(text))
        self.mutator = mutator
        refresh(self.intron)

    def keydown(self, key, modifiers, text):
        if text.isalnum() or text == '_':
            self.insert_text(text)
        print key

def slot_editor(intron, struct, index):
    intron.controller = GenericMode
    intron.style = default
    child = struct[index]
    if isinstance(child, (Struct, Constant)):
        intron.node = build_struct(child)
        # struct_editor(struct, index)
    elif isinstance(child, list):
        out = []
        for index, item in enumerate(child):
            node = build_struct(item)
            node.reference = (index, index+1)
            out.append(node)
        intron.node = layout.Column(out, default)
        # list_editor(struct, index)
    elif isinstance(child, unicode):
        intron.node = layout.Label(child, default)
        intron.node.reference = (0, len(child))
        # word_editor(struct, index)
    else:
        # hexadecimal_editor(struct, index)
        intron.node = layout.Label(child.encode('hex'), yellow_style)

def build_struct(struct):
    if isinstance(struct, Constant):
        return layout.Label(":%s" % struct.name, red_style)
    out = [layout.Label(':%s' % struct.meta.name, red_style)]
    for index, child in enumerate(struct):
        intron = layout.Intron(slot_editor, struct, index)
        out.append(intron)
        # generator.rebuild() rebuilds the thing.
    return layout.Row(out, struct_style)

README = open('README').read().splitlines()

Proxy.root("macron.spec", macron.spec)
root = build_struct(macron.spec)
frame = Frame((0, 0, 800, argon.resolution[1]), root)

def walk_head(struct, index):
    info, ctx = struct.proxy.unroll()
    current = struct
    while isinstance(current[index], Struct):
        current = current[index]
        ctx.append(index)
        index = 0
    # If ext happens, selection applied.
    if isinstance(current[index], (unicode, str, list)):
        ext = 0,0
    else:
        ext = None
    return ctx, index, ext


def get_mutor(root, (ctx, index, ext)):
    current = roll(root, ctx)
    mutor = Mutator(current, index)
    if ext:
        return Selection(mutor, *ext)
    else:
        return mutor

def get_str(mutor):
    if isinstance(mutor, Selection):
        info, ctx = mutor.mutator.struct.proxy.unroll()
        index = mutor.mutator.index
        return repr((ctx, index, (mutor.head, mutor.tail)))
    else:
        info, ctx = mutor.struct.unroll()
        return repr((ctx, mutor.index, None))

from schema import language 

frame.mode = None

def set_mode(mode):
    if frame.mode is not None:
        frame.mode.free()
    frame.mode = mode

ctx, index, ext = walk_head(macron.spec, 1)
intron = locate_intron(frame.contents, roll(macron.spec, ctx), index)
intron.controller.enter_descend(intron)

@argon.listen
def on_frame(time):
    width, height = argon.resolution
    hw = width  / 2
    hh = height / 2

    argon.clear(rgba(0x40, 0x40, 0x40))

    frame.render(argon)

    x, y = argon.pos
    argon.render_rectangle((x-32, y-32, 64, 64), circle64, color=rgba(0x1,0x0,0,0x80))

    if argon.average_latency > 0:
        argon.render_text(
            (0, height - font.height + font.baseline),
            "FPS %.2f" % (1.0 / argon.average_latency),
            font
        )

    argon.render_text(
        (200, height - font.height + font.baseline),
        get_str(frame.mode.mutator),
        font,
    )

@argon.listen
def on_keydown(key, modifiers, text):
    frame.mode.keydown(key, modifiers, text)

@argon.listen
def on_mousedown(button, pos):
    global mutor
    intron = None
    for node in frame.contents.pick(pos):
        if isinstance(node, layout.Intron) and node.controller:
            intron = node
    if intron is not None:
        intron.controller.enter_click(intron, pos)

@argon.listen
def on_mousemotion(pos, rel):
    argon.pos = pos

argon.run()
