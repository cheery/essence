"""
    strike
    ~~~~~~

    strike editing environment
"""
import unknown
from schema import mutable, fileformat_flat
from mode import SelectionMode
from layoutchain import LayoutChain
from layout import Slate, Label, Row, Column, Align, AlignByFlow

def mkstruct(uid, *args):
    return mutable.Struct(mutable.StructType(uid), list(args))

def prev_selection(obj):
    if isinstance(obj, mutable.Document):
        return mutable.Selection(obj, 0)
    index = obj.parent.index(obj)
    if mutable.isstruct(obj.parent):
        if index > 0:
            nxt = obj.parent[index-1]
            if mutable.islist(nxt):
                return mutable.Selection(nxt, len(nxt))
            else:
                return nxt
        else:
            return prev_selection(obj.parent)
    else:
        return mutable.Selection(obj.parent, index)

def next_selection(obj):
    if isinstance(obj, mutable.Document):
        return mutable.Selection(obj, len(obj))
    index = obj.parent.index(obj)
    if mutable.isstruct(obj.parent):
        if index + 1 < len(obj.parent):
            nxt = obj.parent[index+1]
            if mutable.islist(nxt):
                return mutable.Selection(nxt, 0)
            else:
                return nxt
        else:
            return next_selection(obj.parent)
    else:
        return mutable.Selection(obj.parent, index+1)

def enter_tail(obj):
    if mutable.isstruct(obj) and len(obj) > 0:
        return enter_tail(obj[len(obj)-1])
    if mutable.isstruct(obj):
        return obj
    else:
        return mutable.Selection(obj, len(obj))

def walk_prev_selection(obj):
    if isinstance(obj, mutable.Selection):
        if mutable.iscont(obj.container) and obj.head > 0:
            return enter_tail(obj.container[obj.head-1])
        else:
            obj = obj.container
    if isinstance(obj, mutable.Document):
        return mutable.Selection(obj, 0)
    index = obj.parent.index(obj)
    if mutable.isstruct(obj.parent):
        if index > 0:
            nxt = obj.parent[index-1]
            return enter_tail(nxt)
        else:
            return walk_prev_selection(obj.parent)
    else:
        return mutable.Selection(obj.parent, index)

def enter_head(obj):
    if mutable.isstruct(obj) and len(obj) > 0:
        return enter_head(obj[0])
    if mutable.isstruct(obj):
        return obj
    else:
        return mutable.Selection(obj, 0)

def walk_next_selection(obj):
    if isinstance(obj, mutable.Selection):
        if mutable.iscont(obj.container) and obj.head < obj.last:
            return enter_head(obj.container[obj.head])
        else:
            obj = obj.container
    if isinstance(obj, mutable.Document):
        return mutable.Selection(obj, len(obj))
    index = obj.parent.index(obj)
    if mutable.isstruct(obj.parent):
        if index + 1 < len(obj.parent):
            nxt = obj.parent[index+1]
            return enter_head(nxt)
        else:
            return walk_next_selection(obj.parent)
    else:
        return mutable.Selection(obj.parent, index+1)

def find_parent(obj, which):
    if isinstance(obj, mutable.Document):
        return None
    if mutable.istype(obj.parent, which):
        return obj.parent
    else:
        return find_parent(obj.parent, which)

def find_parent_deep(obj, which):
    if isinstance(obj, mutable.Document):
        return None
    if mutable.istype(obj.parent, which):
        while mutable.isinside(obj.parent, which):
            obj = obj.parent
        return obj.parent
    else:
        return find_parent(obj.parent, which)

expressions = (
    u"number:value",
    u"variable:name",
    u"call:callee:arguments",
    u"assign:slot:value",
    u"return:value",
)

class EditMode(SelectionMode):
    def insert_text(self, text):
        selection = self.selection
        if isinstance(selection, mutable.Selection) and mutable.isstring(selection.container):
            selection.splice(text)
            selection.start = selection.stop
            return True

    def insert_inline(self, target, block, which):
        parent = find_parent(mutable.get_object(self.selection), which)
        if parent is None:
            if self.insert_object(block):
                self.selection = target
        else:
            document = mutable.get_document(parent)
            document.replace(parent, block)
            document.replace(target, parent)
            self.selection = next_selection(parent)

    def insert_inline_deep(self, target, block, which):
        parent = find_parent_deep(mutable.get_object(self.selection), which)
        if parent is None:
            if self.insert_object(block):
                self.selection = target
        else:
            document = mutable.get_document(parent)
            document.replace(parent, block)
            document.replace(target, parent)
            self.selection = next_selection(parent)

    def on_keydown(self, key, modifiers, text):
        selection = self.selection
        overlay = self.overlay
        shift = 'shift' in modifiers
        ctrl  = 'ctrl' in modifiers
        alt   = 'alt' in modifiers
        if ctrl and key == 's':
            document = mutable.get_document(mutable.get_object(selection))
            fileformat_flat.save_file(document.filename, mutable, document)
            return
        if ctrl and key == 'a':
            self.selection = mutable.extend(selection)
            overlay.dirty = True
            return
        if ctrl and key == 'left':
            self.selection = walk_prev_selection(selection)
            overlay.dirty = True
            return
        if ctrl and key == 'right':
            self.selection = walk_next_selection(selection)
            overlay.dirty = True
            return
        if isinstance(selection, mutable.Selection):
            if key == 'left':
                if selection.head > 0:
                    selection.head -= 1
                else:
                    self.selection = prev_selection(mutable.get_object(selection))
                    overlay.dirty = True
                    return
            elif key == 'right':
                if selection.head < selection.last:
                    selection.head += 1
                else:
                    self.selection = next_selection(mutable.get_object(selection))
                    overlay.dirty = True
                    return
            elif key == 'home':
                selection.head = 0
            elif key == 'end':
                selection.head = selection.last
            if key in ('left', 'right', 'home', 'end'):
                selection.tail = selection.tail if shift else selection.head
                overlay.dirty = True
#            if isinstance(selection.container, mutable.String):
#                if not ctrl and len(text) > 0 and text.isalnum() or text in ' ':
#                    selection.splice(text)
#                    selection.start = selection.stop
            if key == 'backspace' or key == 'delete':
                if selection.start == selection.stop:
                    selection.start -= (key == 'backspace')
                    selection.stop  += (key == 'delete')
                selection.splice(u'')
                selection.stop = selection.start
                return
        else:
            parent = selection.parent
            index  = parent.index(selection)
            if key == 'left':
                self.selection = prev_selection(selection)
                overlay.dirty = True
            if key == 'right':
                self.selection = next_selection(selection)
                overlay.dirty = True

        if text == '=':
            target = mkstruct(u"null")
            block = mkstruct(u"assign:slot:value", target, mkstruct(u"null"))
            return self.insert_inline(target, block, expressions)
        if alt and key == 'r':
            target = mkstruct(u"null")
            block = mkstruct(u"return:value", target)
            return self.insert_inline_deep(target, block, expressions)
        if text == '(':
            target = mkstruct(u"null")
            block = mkstruct(u"call:callee:arguments", target, mutable.List([]))
            return self.insert_inline(target, block, expressions)
        if key == 'space':
            self.selection = next_selection(mutable.get_object(selection))
            overlay.dirty = True
        elif len(text) > 0 and not self.insert_text(text):
            if text.isalpha():
                target = mutable.String(u"")
                if self.insert_object(mkstruct(u'variable:name', target)):
                    self.selection = mutable.Selection(target, 0)
                    self.insert_text(text)
            elif text.isdigit():
                target = mutable.String(u"")
                if self.insert_object(mkstruct(u'number:value', target)):
                    self.selection = mutable.Selection(target, 0)
                    self.insert_text(text)

def init(argon, default, theme):
    default_layouter = unknown.init(argon, default, theme)
    bracket2 = argon.load.patch9('bracket2.png')

    object_style = default.inherit(
        color = theme.object_color,
        background_color = theme.object_color,
    )

    keyword_style = default.inherit(
        color = theme.keyword_color,
    )

    number_style = default.inherit(
        color = theme.number_color,
    )

    spacerow = default.inherit(spacing=4)

    def mk_document(intron, document):
        intron.style = default
        if len(document) > 0:
            intron.node = Column(statement.many(document), default)
        else:
            intron.node = Label("empty program", object_style)

    def mk_number_string(intron, string):
        intron.style = default
        if len(string) > 0:
            intron.node = Label(string.data, number_style)
        else:
            intron.node = Label("$", number_style)
        intron.node.reference = 0, len(string)
    number = LayoutChain({mutable.String: mk_number_string}, default_layouter)

    def mk_number_value(intron, var):
        intron.style = default
        intron.node  = number(var[0])

    def mk_variable_string(intron, string):
        intron.style = default
        if len(string) > 0:
            intron.node = Label(string.data, default)
        else:
            intron.node = Label("$", object_style)
        intron.node.reference = 0, len(string)
    variable = LayoutChain({mutable.String: mk_variable_string}, default_layouter)

    def mk_variable_name(intron, var):
        intron.style = default
        intron.node  = variable(var[0])

    expression_style = default.inherit(
        align = AlignByFlow(0, 0),
    )

    argv_list_style = default.inherit(
        background = bracket2,
        background_color = theme.symbol_color,
        padding    = (4,4,4,4)
    )
    def mk_argv_list(intron, argv):
        intron.style = default
        if len(argv) > 0:
            intron.node = Column(expression.many(argv), argv_list_style)
        else:
            x = default['font'].height + 4
            intron.node = Slate(12, x, argv_list_style)
    argv_list = LayoutChain({mutable.List: mk_argv_list}, default_layouter)

    def mk_call_callee_arguments(intron, call):
        callee, arguments = call
        intron.style = default
        intron.node  = Row([
            expression(callee),
            argv_list(arguments),
        ], expression_style)

    def mk_assign_slot_value(intron, assign):
        slot, value = assign
        intron.style = default
        intron.node  = Row([expression(slot), Label('=', object_style), expression(value)], spacerow)

    def mk_return_value(intron, ret):
        value, = ret
        intron.style = default
        intron.node  = Row([Label("return", keyword_style), expression(value)], spacerow)

    expression = LayoutChain({
        u"number:value": mk_number_value,
        u"variable:name": mk_variable_name,
        u"call:callee:arguments": mk_call_callee_arguments,
        u"assign:slot:value": mk_assign_slot_value,
    }, default_layouter)

    statement = LayoutChain({
        mutable.Document: mk_document,
        u"number:value": mk_number_value,
        u"variable:name": mk_variable_name,
        u"call:callee:arguments": mk_call_callee_arguments,
        u"assign:slot:value": mk_assign_slot_value,
        u"return:value": mk_return_value,
    }, default_layouter)

    return statement
