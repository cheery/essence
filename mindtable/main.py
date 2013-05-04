from argon import Argon, rgba
from frame import Frame, Overlay
from schema.base import Constant, Struct
from schema import proxy, analyzer
from schema.mutator import Mutator
from schema.selection import Selection, BufferSelection, StringSelection, ListSelection
from schema.language import language, Synthetizer
from schema.flatfile import load_file, save_file
from navigation import *
import macron
import layout
import os, sys

def in_module(path):
    return os.path.join(os.path.dirname(__file__), path)

background_color = rgba(0x24, 0x24, 0x24)
green      = rgba(0x95, 0xe4, 0x54)
cyan       = rgba(0x8a, 0xc6, 0xf2)
red        = rgba(0xe5, 0x78, 0x6d)
lime       = rgba(0xca, 0xe6, 0x82)
gray       = rgba(0x99, 0x96, 0x8b)
back       = rgba(0x24, 0x24, 0x24)
whiteish   = rgba(0xf6, 0xf3, 0xe8)

class DefaultTheme(object):
    pass


mode = None
def set_mode(new_mode):
    global mode
    if mode:
        mode.free()
    mode = new_mode

null = Constant(u"null")

cost_addweights = {
    'variable': -1,
    'number': 0,
}

def list_templates(arg, marg, top):
#    print 'LIST TEMPLATES'
    for name in arg:
        addweight = cost_addweights.get(name, 0)
        if name == top:
#            print name, False, 0
            yield name, False, 0 + addweight
        elif isinstance(name, unicode) and top in chains[name]:
            nxt, in_list, cost = chains[name][top]
#            print name, False, cost + 1
            yield name, False, cost + 1 + addweight
    for name in marg:
        addweight = cost_addweights.get(name, 0)
        if name == top:
#            print name, True,  1
            yield name, True,  1 + addweight
        elif isinstance(name, unicode) and top in chains[name]:
            nxt, in_list, cost = chains[name][top]
#            print name, True, cost + 2
            yield name, True, cost + 2 + addweight

def mkstruct(ndef, syn, name, argv):
    for i in range(len(argv), len(ndef[name])):
        ok, mok = ndef[name][i]
        if len(ok) == 1 and ok[0] == analyzer.String:
            argv.append(u"")
        elif len(ok) == 1 and ok[0] == analyzer.Buffer:
            argv.append("")
        elif len(ok) > 0:
            argv.append(null)
        else:
            argv.append([])
    if len(argv) == 0:
        return syn[name]
    else:
        return syn[name](*argv)
    

def instantiate(this, top):
    if this == top and top == analyzer.String:
        return u""
    if this == top and top == analyzer.Buffer:
        return ""
    argv = []
    if this != top:
        nxt, in_list, _ = chains[this][top]
        if in_list:
            argv.append([instantiate(nxt, top)])
        else:
            argv.append(instantiate(nxt, top))
    return mkstruct(ndef, syn, this, argv)
#
#    for i in range(len(argv), len(ndef[this])):
#        ok, mok = ndef[this][i]
#        if len(ok) == 1 and ok[0] == analyzer.String:
#            argv.append(u"")
#        elif len(ok) == 1 and ok[0] == analyzer.Buffer:
#            argv.append("")
#        elif len(ok) > 0:
#            argv.append(null)
#        else:
#            argv.append([])
#    if len(argv) == 0:
#        return syn[this]
#    else:
#        return syn[this](*argv)

def autoinstantiate(arg, marg, top):
    ts = list(list_templates(arg, marg, top))
    if len(ts) > 0:
        nxt, in_list, cost = min(ts, key=lambda x: x[2])
        inst = instantiate(nxt, top)
        if in_list:
            return [inst]
        return inst

copybuf = None

def fullcopy(obj):
    if isinstance(obj, Struct):
        obj = obj.copy()
    elif isinstance(obj, list):
        obj = [o.copy() for o in obj]
    return obj

class EditMode(object):
    def __init__(self, sel, click_response=False):
        self.sel = sel
        self.overlay = Overlay(main_frame, self.render_overlay)
        self.dragging = click_response

    def set_dirtyfile(self, dirty=True):
        if dirty:
            argon.set_caption("macron[%s] %s*" % (current_language.name, filename))
        else:
            argon.set_caption("macron[%s] %s" % (current_language.name, filename))

    def free(self):
        self.overlay.free()
    
    def render_overlay(self, argon):
        argon.clear(rgba(0,0,0,0))
        slot = find_slot(main_frame.contents, self.sel.struct, self.sel.index)
        if slot is not None:
            argon.render_rectangle(slot.rect, box7, color = rgba(32, 32, 255, 128))
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

    def gen_struct(self, top):
        arg, marg = ndef[self.sel.struct.type.name][self.sel.index]
        if isinstance(self.sel, ListSelection):
            inst = autoinstantiate((), marg, top)
            if inst is not None:
                self.sel.splice(inst)
                self.sel = deep_climb_head(self.sel.struct, self.sel.index, self.sel.start)
            else:
                return
                print "cannot instantiate", top, "here"
        elif isinstance(self.sel, Mutator):
            inst = autoinstantiate(arg, marg, top)
            if inst is not None:
                self.sel.replace(inst)
                self.sel = deep_climb_head(self.sel.struct, self.sel.index, 0)
            else:
                return
                print "cannot instantiate", top, "here"
        assert self.sel is not None
        return True

    def put_struct(self, top):
        slot = find_slot(main_frame.contents, self.sel.struct, self.sel.index)
        if self.gen_struct(top):
            if isinstance(self.sel, Selection):
                self.sel.start = self.sel.stop
            if slot is not None:
                slot.rebuild()
            main_frame.dirty = True
            self.set_dirtyfile()

    def copy_selection(self):
        global copybuf
        if isinstance(self.sel, Selection):
            dup = self.sel.struct[self.sel.index][self.sel.start:self.sel.stop]
            if len(dup) == 1:
                dup = dup[0]
            copybuf = fullcopy(dup)
        else:
            dup = self.sel.struct[self.sel.index]
            copybuf = fullcopy(dup)
            print 'copy success'

    def paste_selection(self):
        slot = find_slot(main_frame.contents, self.sel.struct, self.sel.index)
        if isinstance(self.sel, ListSelection) and isinstance(copybuf, list):
            self.sel.splice(fullcopy(copybuf))
        elif isinstance(self.sel, ListSelection) and isinstance(copybuf, (Struct, Constant)):
            self.sel.splice([fullcopy(copybuf)])
        elif isinstance(self.sel, StringSelection) and isinstance(copybuf, unicode):
            self.sel.splice(copybuf)
        elif isinstance(self.sel, BufferSelection) and isinstance(copybuf, str):
            self.sel.splice(copybuf)
        elif isinstance(self.sel, Mutator) and isinstance(copybuf, (Struct, Constant, unicode, str)):
            self.sel.replace(fullcopy(copybuf))
        else:
            print 'paste unsuccessful'
            return
        if slot is not None:
            slot.rebuild()
        main_frame.dirty = True
        self.set_dirtyfile()

    def on_keydown(self, key, modifiers, text):
        shift = 'shift' in modifiers
        ctrl = 'ctrl' in modifiers
        alt = 'alt' in modifiers
        nxt = None

        if key == 'left' and isinstance(self.sel, Selection):
            bkg = self.sel.head > 0
            motion(self.sel, self.sel.head - bkg, shift)
        elif key == 'right' and isinstance(self.sel, Selection):
            fwd = self.sel.head < self.sel.length
            motion(self.sel, self.sel.head + fwd, shift)
        elif key == 'home' and isinstance(self.sel, Selection):
            motion(self.sel, 0, shift)
        elif key == 'end' and isinstance(self.sel, Selection):
            motion(self.sel, self.sel.length, shift)
        elif key == 'return' and shift:
            nxt = skip_to_previous(document, self.sel.struct, self.sel.index)  # it might need fixup. :P
        elif key == 'return':
            nxt = skip_to_next(document, self.sel.struct, self.sel.index)  # it might need fixup. :P
        elif key == 'up':
            nxt = wade_to_previous(document, self.sel)
        elif key == 'down' or (key == 'space' and not ctrl):
            nxt = wade_to_next(document, self.sel)
        elif ctrl and key == 'y':
            self.copy_selection()
        elif ctrl and key == 'p':
            self.paste_selection()
        elif ctrl and key == 's':
            save_file(filename, document)
            self.set_dirtyfile(False)
        elif ctrl and key == 'a':
            if self.sel.start == 0 and self.sel.stop == self.sel.length:
                nxt = select_this(document, self.sel.struct)
            else:
                self.sel.start = 0
                self.sel.stop  = self.sel.length
        elif key == 'delete':
            if isinstance(self.sel, Selection):
                if self.sel.start == self.sel.stop and self.sel.stop < self.sel.length:
                    self.sel.stop += 1
                self.sel.splice()
                self.set_dirtyfile()
            slot = find_slot(main_frame.contents, self.sel.struct, self.sel.index)
            if slot is not None:
                slot.rebuild()
            main_frame.dirty = True
        elif key == 'backspace':
            if isinstance(self.sel, Selection):
                if self.sel.start == self.sel.stop and self.sel.start > 0:
                    self.sel.start -= 1
                self.sel.splice()
                self.set_dirtyfile()
            slot = find_slot(main_frame.contents, self.sel.struct, self.sel.index)
            if slot is not None:
                slot.rebuild()
            main_frame.dirty = True
        elif key == 'space':
            slot = find_slot(main_frame.contents, self.sel.struct, self.sel.index)
            self.gen_struct(analyzer.String)
            if isinstance(self.sel, StringSelection):
                self.sel.splice(u' ')
                self.sel.start = self.sel.stop
            if slot is not None:
                slot.rebuild()
            main_frame.dirty = True
            self.set_dirtyfile()
        elif alt and text == 'w':
            self.put_struct(u"while")
        elif alt and text == 'e':
            self.put_struct(u"foreach")
        elif alt and text == 't':
            self.put_struct(u"true")
        elif alt and text == 'f':
            self.put_struct(u"false")
        elif len(text) > 0 and (text.isalnum() or text in u"_"):
            slot = find_slot(main_frame.contents, self.sel.struct, self.sel.index)
            self.gen_struct(("number" if text.isdigit() else analyzer.String))
                #self.gen_struct(analyzer.String)
            if isinstance(self.sel, StringSelection):
                self.sel.splice(text)
                self.sel.start = self.sel.stop
            if slot is not None:
                slot.rebuild()
            main_frame.dirty = True
            self.set_dirtyfile()
        elif text == '!':
            self.put_struct(u"buffer")
        elif text == '"':
            self.put_struct(u"string")
        elif text == '#':
            self.put_struct(u"constant")
        elif text == '(':
            self.put_struct(u"struct") or self.put_struct(u"call")
        elif text == '[':
            self.put_struct(u"list")
        elif text == '{':
            self.put_struct(u"group") or self.put_struct(u"lambda")
        elif text == '=':
            self.put_struct(u"let")
        elif text == '.':
            self.put_struct(u"attribute")
        elif text == '<':
            self.put_struct(u"return")
        elif text == '@':
            self.put_struct(u"dictionary")
        elif text == '[':
            self.put_struct(u"list")
        elif text == '?':
            self.put_struct(u"condition_rule")

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
    def __init__(self, struct, index, builder=lambda intron: False):
        self.struct = struct
        self.index  = index
        self.builder = builder

    def build(self, intron):
        if self.builder(intron):
            return
        obj = self.struct[self.index]
        if isinstance(obj, (Struct, Constant)):
            intron.node = default_visualizer(obj)
        elif isinstance(obj, list) and len(obj) == 0:
            intron.node = layout.Label("[]", gray_style)
        elif isinstance(obj, list):
            boxes = []
            for index, struct in enumerate(obj):
                box = default_visualizer(struct)
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

def default_visualizer(struct):
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
argon = Argon((600, 1100))
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
known_languages = {
    u"language": lambda: language
}

script_directory = in_module('scripts')
for filename in os.listdir(script_directory):
    if not os.path.isdir(filename) and filename.endswith('.language'):
        name, ext = os.path.splitext(filename)
        path = os.path.join(script_directory, filename)
        known_languages[name] = lambda: load_file(path)

filename = sys.argv[1]

langtype = os.path.splitext(filename)[1][1:]
current_language = known_languages[langtype]()

syn = Synthetizer(current_language)
ndef = analyzer.normalize(current_language)
inv = analyzer.partial_inversion(ndef)

chains = analyzer.build_all_chains(ndef, inv)

for name, argv in ndef.items():
    print 'TDEF:', name, ', '.join(map(repr, argv))

for name, sources in inv.items():
    print "INV:", name, sources

if os.path.exists(filename):
    document = load_file(filename)
else:
    document = mkstruct(ndef, syn, current_language.name, [])
proxy.mkroot(None, document)

def iss(obj, name):
    if isinstance(obj, Constant):
        return obj.uid == name
    elif isinstance(obj, Struct):
        return obj.type.name == name

glob = {
    u"theme": DefaultTheme,
    u"lengthof": len,
    u"isstruct": lambda obj: isinstance(obj, Struct),
    u"isconst": lambda obj: isinstance(obj, Constant),
    u"islist": lambda obj: isinstance(obj, list),
    u"isstring": lambda obj: isinstance(obj, unicode),
    u"isbuffer": lambda obj: isinstance(obj, str),
    u"iss": iss,
    u"rgba": rgba,
    u"argon": argon,
    u"layout": layout,
    u"StructureEditor": StructureEditor,
}
glob.update(macron.glob)

visualizer = default_visualizer
visualizer_mtime = None
def load_visualizer(name, at_reload=False):
    global visualizer, visualizer_mtime
    try:
        path = os.path.join(script_directory, name + '.macron')
        mtime = os.path.getmtime(path)
        if visualizer_mtime == mtime:
            return False
        visualizer_mtime = mtime
        program = load_file(path)
        ret, module = macron.run(program, glob)
        def visualizer_bind(struct):
            try:
                obj = module['visualizer'](struct)
                if isinstance(obj, layout.Box):
                    return obj
                else:
                    return default_visualizer(struct)
            except Exception, exception:
                print "visualizer bad:", exception
                return default_visualizer(struct)
        visualizer = visualizer_bind
        return True
    except Exception, exception:
        print exception
    return False

    
load_visualizer(langtype)
#after loading visualizer, update the main_frame

# main frame
main_frame = Frame((0, 0, argon.width, argon.height), visualizer(document))# layout.Label("hello there!", default))
main_frame.background_color = background_color

set_mode(EditMode( climb_head(document, 0) ))

argon.set_caption("macron[%s] %s" % (current_language.name, filename))


argon.previous_sys_check = 0.0

@argon.listen
def on_frame(now):
    ## reload visualizer if it changed.
    if argon.previous_sys_check + 2.0 < now:
        if load_visualizer(langtype, at_reload=True):
            print 'trying to reload visualizer'
            main_frame.contents = visualizer(document)
            main_frame.dirty = True
        argon.previous_sys_check = now

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
