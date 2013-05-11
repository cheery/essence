"""
    unknown
    ~~~~~~~

    We tend to hit something that's unknown to us
    once in a while. This file describes what to do.
"""
from mode import SelectionMode
from layoutchain import LayoutRoot, LayoutChain
from schema import mutable
import layout

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

def init(argon, default, theme):
    box7 = argon.load.patch9('box7.png')
    bracket2 = argon.load.patch9('bracket2.png')

    row_default = default.inherit(spacing = 8)
    sym_default  = default.inherit(color = theme.keyword_color)
    bad_default  = default.inherit(color = theme.malform_color)
    obj_default = default.inherit(color = theme.object_color)
    str_default = default.inherit(color = theme.string_color)
    list_default = default.inherit(
        background = bracket2,
        background_color = theme.object_color,
        padding = (4, 4, 4, 4)
    )

    def mk_unknown(intron, obj):
        intron.style = default
        if isinstance(obj, mutable.Struct) and len(obj) == 0:
            intron.node = layout.Label(obj.type.name, sym_default)
        elif isinstance(obj, mutable.Struct):
            intron.node = layout.Row([
                layout.Label(obj.type.name, sym_default),
                layout.Column(layouter.many(obj), default),
            ], row_default)
        elif isinstance(obj, mutable.String):
            data = layout.Label(obj.data, str_default)
            data.reference = 0, len(obj)
            intron.node = layout.Row([layout.Label('"', str_default), data, layout.Label('"', str_default)], default)
        elif isinstance(obj, mutable.List):
            intron.node = layout.Column(layouter.many(obj), list_default)
        else:
            intron.node = layout.Label("unknown %r" % obj, bad_default)

    def mk_document(intron, document):
        intron.style = default
        if len(document) > 0:
            intron.node = layout.Column(layouter.many(document), default)
        else:
            intron.node = layout.Label("empty document", obj_default)

    layouter = LayoutChain({
        mutable.Document: mk_document,
    }, LayoutRoot(mk_unknown))
    return layouter
