from argon import rgba, graphics, hsva
import layout
from document import ListField, TextField
from weakref import WeakKeyDictionary

def clamp(low, high, value):
    return min(high, max(low, value))

def pad((left, top, width, height), (l,t,r,b)):
    return (left-l, top-t, width+l+r, height+t+b)

def selection(intron, color, pattern, start, stop):
    out = []
    for subintron in intron.subintrons():
        if subintron.index is None:
            continue
        if subintron.in_range(start, stop):
            rect = subintron.selection_rect(start, stop)
            out.append((rect, color, pattern))
    for label in intron.labels():
        if label.source is not intron.source:
            continue
        if label.in_range(start, stop):
            rect = label.selection_rect(start, stop)
            out.append((rect, color, pattern))
    return out

class TextInputMode(object):
    def __init__(self, root, intron, head, tail):
        self.root = root
        self.intron = intron
        self.head = head
        self.tail = tail

    start = property(lambda self: min(self.head, self.tail))
    stop = property(lambda self: max(self.head, self.tail))

    def draw(self, argon):
        out = []
        rect = pad(self.intron.rect, (7,7,7,7))
        white = rgba(255,255,255)
        out.extend([
            (rect, white, argon.patch9('marker.png'))
        ])
        out.extend(selection(self.intron, rgba(0x80,255,255,0x80), argon.plain, self.start, self.stop))
        out.extend(selection(self.intron, white, argon.plain, self.head, self.head))

        font = self.root.font
        width, height = argon.resolution
        out.extend([
            ((0,0,width,font.height*1.2), rgba(0,0,0), argon.plain),
            ((0,font.baseline), "-- text input --", rgba(0x80, 0x80, 0x80), font),
        ])
        argon.render(out)

    def on_keydown(self, name, mod, text):
        if name == 'escape':
            self.root.reset()
        if name == 'a' and 'ctrl' in mod:
            try_select_all(self.root, self.intron)
        elif len(text) > 0 and 32 <= ord(text) < 127:
            self.intron.source[self.start:self.stop] = text
            self.head = self.tail = self.start + len(text)
            self.intron.rebuild()
        if name == 'left':
            if self.head > 0:
                self.head -= 1
            else:
                try_leave_head(self.root, self.intron)
            if 'shift' not in mod:
                self.tail = self.head
        if name == 'right':
            if self.head < len(self.intron.source):
                self.head += 1
            else:
                try_leave_tail(self.root, self.intron)
            if 'shift' not in mod:
                self.tail = self.head

    def on_keyup(self, name, mod):
        pass

    def on_mousedown(self, button, pos):
        self.root.pick(pos)

    def on_mouseup(self, button, pos):
        pass

    def on_mousemotion(self, pos, vel):
        pass

    @classmethod
    def enter_click(cls, root, intron, pos):
        head = tail = intron.pick_offset(pos)
        root.control = cls(root, intron, head, tail)
        return True

    @classmethod
    def enter_head(cls, root, intron):
        root.control = cls(root, intron, 0, 0)
        return True

    @classmethod
    def enter_tail(cls, root, intron):
        l = len(intron.source)
        root.control = cls(root, intron, l, l)
        return True

class StructInputMode(object):
    def __init__(self, root, intron, which=0):
        self.root   = root
        self.intron = intron
        self.which  = which

    def draw(self, argon):
        out = []
        rect = pad(self.intron.rect, (7,7,7,7))
        white = rgba(255,255,255)
        out.extend([
            (rect, white, argon.patch9('marker.png'))
        ])
        for intron in self.intron.subintrons():
            if intron.index == self.which:
                rect = pad(intron.rect, (7,7,7,7))
                out.append((rect, rgba(255,255,0), argon.patch9('marker.png')))

        font = self.root.font
        width, height = argon.resolution
        out.extend([
            ((0,0,width,font.height*1.2), rgba(0,0,0), argon.plain),
            ((0,font.baseline), "-- struct input --", rgba(0x80, 0x80, 0x80), font),
        ])
        argon.render(out)

    def on_keydown(self, name, mod, text):
        if name == 'escape':
            self.root.reset()
        if name == 'a' and 'ctrl' in mod:
            try_select_all(self.root, self.intron)
        if name == 'left':
            if self.which > 0:
                self.which -= 1
                self.try_enter_tail(self.which)
            else:
                try_leave_head(self.root, self.intron)
        if name == 'right':
            if self.which < len(self.intron.source)-1:
                self.which += 1
                self.try_enter_head(self.which)
            else:
                try_leave_tail(self.root, self.intron)
        if name == 'up':
            if self.which > 0:
                self.which -= 1
        if name == 'down':
            if self.which < len(self.intron.source)-1:
                self.which += 1

    def on_keyup(self, name, mod):
        pass

    def on_mousedown(self, button, pos):
        self.root.pick(pos)

    def on_mouseup(self, button, pos):
        pass

    def on_mousemotion(self, pos, vel):
        pass   

    @classmethod
    def enter_click(cls, root, intron, pos):
        which = None
        for subintron in intron.subintrons():
            if subintron.inside(pos):
                which = subintron.index
        if which is not None:
            root.control = cls(root, intron, which)
            return True

    @classmethod
    def enter_head(cls, root, intron):
        if len(intron.source) > 0:
            root.control = ctl = cls(root, intron, 0)
            ctl.try_enter_head(0)
            return True

    @classmethod
    def enter_tail(cls, root, intron):
        length = len(intron.source) 
        if length > 0:
            root.control = ctl = cls(root, intron, length)
            ctl.try_enter_tail(length-1)
            return True

    @classmethod
    def enter_child_head(cls, root, intron, index):
        if index > 0:
            root.control = ctl = cls(root, intron, index-1)
            ctl.try_enter_tail(index-1)
            return True
        else:
            return try_leave_head(root, intron)

    @classmethod
    def enter_child_tail(cls, root, intron, index):
        if index < len(intron.source)-1:
            root.control = ctl = cls(root, intron, index+1)
            ctl.try_enter_head(index+1)
            return True
        else:
            return try_leave_tail(root, intron)

    @classmethod
    def enter_select(cls, root, intron, index):
        root.control = cls(root, intron, index)
        return True

    def try_enter_head(self, index):
        for subintron in self.intron.subintrons():
            if subintron.index == index and subintron.control:
                if subintron.control.enter_head(self.root, subintron):
                    return True

    def try_enter_tail(self, index):
        for subintron in self.intron.subintrons():
            if subintron.index == index and subintron.control:
                if subintron.control.enter_tail(self.root, subintron):
                    return True

class ListInputMode(object):
    def __init__(self, root, intron, head, tail):
        self.root = root
        self.intron = intron
        self.head = head
        self.tail = tail

    start = property(lambda self: min(self.head, self.tail))
    stop = property(lambda self: max(self.head, self.tail))

    def draw(self, argon):
        out = []
        rect = pad(self.intron.rect, (7,7,7,7))
        white = rgba(255,255,255)
        out.extend([
            (rect, white, argon.patch9('marker.png'))
        ])
        out.extend(selection(self.intron, rgba(0x80,255,255,0x80), argon.plain, self.start, self.stop))
        out.extend(selection(self.intron, white, argon.plain, self.head, self.head))

        font = self.root.font
        width, height = argon.resolution
        out.extend([
            ((0,0,width,font.height*1.2), rgba(0,0,0), argon.plain),
            ((0,font.baseline), "-- list input --", rgba(0x80, 0x80, 0x80), font),
        ])
        argon.render(out)

    def on_keydown(self, name, mod, text):
        if name == 'escape':
            self.root.reset()
        if name == 'a' and 'ctrl' in mod:
            try_select_all(self.root, self.intron)
        if name == 'left':
            if self.head > 0:
                self.head -= 1
                self.try_enter_tail(self.head)
            else:
                try_leave_head(self.root, self.intron)
            if 'shift' not in mod:
                self.tail = self.head
        if name == 'right':
            if self.head < len(self.intron.source):
                self.try_enter_head(self.head)
                self.head += 1
            else:
                try_leave_tail(self.root, self.intron)
            if 'shift' not in mod:
                self.tail = self.head
        if name == 'up':
            if self.head > 0:
                self.head -= 1
            if 'shift' not in mod:
                self.tail = self.head
        if name == 'down':
            if self.head < len(self.intron.source):
                self.head += 1
            if 'shift' not in mod:
                self.tail = self.head

    def on_keyup(self, name, mod):
        pass

    def on_mousedown(self, button, pos):
        self.root.pick(pos)

    def on_mouseup(self, button, pos):
        pass

    def on_mousemotion(self, pos, vel):
        pass

    @classmethod
    def enter_click(cls, root, intron, pos):
        head = tail = intron.pick_offset(pos)
        root.control = cls(root, intron, head, tail)
        return True

    @classmethod
    def enter_head(cls, root, intron):
        root.control = cls(root, intron, 0, 0)
        return True

    @classmethod
    def enter_tail(cls, root, intron):
        l = len(intron.source)
        root.control = cls(root, intron, l, l)
        return True

    @classmethod
    def enter_child_head(cls, root, intron, index):
        root.control = cls(root, intron, index, index)
        return True

    @classmethod
    def enter_child_tail(cls, root, intron, index):
        root.control = cls(root, intron, index+1, index+1)
        return True

    @classmethod
    def enter_select(cls, root, intron, index):
        root.control = cls(root, intron, index, index+1)
        return True

    def try_enter_head(self, index):
        for subintron in self.intron.subintrons():
            if subintron.index == index and subintron.control:
                if subintron.control.enter_head(self.root, subintron):
                    return True

    def try_enter_tail(self, index):
        for subintron in self.intron.subintrons():
            if subintron.index == index and subintron.control:
                if subintron.control.enter_tail(self.root, subintron):
                    return True

def try_leave_head(root, intron):
    parent = root.find_parent(intron)
    if parent is not None:
        return parent.control.enter_child_head(root, parent, intron.index)

def try_leave_tail(root, intron):
    parent = root.find_parent(intron)
    if parent is not None:
        return parent.control.enter_child_tail(root, parent, intron.index)

def try_select_all(root, intron):
    parent = root.find_parent(intron)
    if parent is not None:
        return parent.control.enter_select(root, parent, intron.index)

class Visualizer(object):
    def __init__(self, argon, font):
        self.argon = argon
        self.default = layout.default.inherit(
            font = font,
            background = None,
            color = rgba(0xf6, 0xf3, 0xe8),
            spacing = 10,
        )
        self.namecolor = self.default.inherit(
            color = rgba(0xe5, 0x78, 0x6d),
        )
        self.unknown_list = self.default.inherit(
            background = (argon.patch9('border.png'), rgba(0x24, 0x24, 0x24)),
            padding    = (5,5,5,5),
            spacing = 0,
        )

    def many(self, nodes, start=0):
        out = []
        for index, node in enumerate(nodes, start):
            out.append( layout.Intron(node, self, index=index) )
        return out

    def __call__(self, intron, node):
        intron.style = self.default
        if node is None:
            intron.control = None
            return layout.Label('None', self.default)
        if len(node) == 0:
            intron.control = ListInputMode
            return layout.Row([
                layout.Label(':%s' % node.name, self.namecolor),
            ], self.unknown_list)
        if isinstance(node, ListField) and node.name.endswith('*'):
            intron.control = ListInputMode
            return layout.Row([
                layout.Column(self.many(node), self.default),
                layout.Label(':%s' % node.name, self.namecolor),
            ], self.unknown_list)
        if isinstance(node, ListField):
            intron.control = StructInputMode
            return layout.Row([
                layout.Row(self.many(node), self.default),
                layout.Label(':%s' % node.name, self.namecolor),
            ], self.unknown_list)
        if isinstance(node, TextField):
            intron.control = TextInputMode
            return layout.Row([
                layout.Label(node, self.default),
                layout.Label(':%s' % node.name, self.namecolor),
            ], self.unknown_list)

def build(argon, font, root):
    return layout.Intron(root, Visualizer(argon, font))
