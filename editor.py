from essence.ui import color, window, get, eventloop, empty
from essence.document import node, copy, splice, build, collapse, serialize, deserialize, can_walk_up, can_walk_down, can_walk_left, can_walk_right
from essence.layout import StringFrame, BlockFrame, ImageFrame, generate_frames
from random import randint

black = color(0x00, 0x00, 0x00)
yellow = color(0x20, 0x20, 0x10)
dark_gray = color(0x10, 0x10, 0x10)
white = color(0xFF, 0xFF, 0xFF)

almost_white = color(0xA0, 0xA0, 0xA0, 0xFF)
about_blue = color(0x10, 0x10, 0xFF, 0x80)

import pygame
keybindings = {
    pygame.K_DOWN: 'down',
    pygame.K_UP: 'up',
    pygame.K_LEFT: 'left',
    pygame.K_RIGHT: 'right',
    pygame.K_RETURN: 'enter',
    pygame.K_SPACE: 'space',
    pygame.K_TAB: 'tab',
    pygame.K_ESCAPE: 'escape',
}

SHIFT = pygame.KMOD_SHIFT
#KMOD_NONE, KMOD_LSHIFT, KMOD_RSHIFT, KMOD_SHIFT, KMOD_CAPS,
#KMOD_LCTRL, KMOD_RCTRL, KMOD_CTRL, KMOD_LALT, KMOD_RALT,
#KMOD_ALT, KMOD_LMETA, KMOD_RMETA, KMOD_META, KMOD_NUM, KMOD_MODE

class Selection(object):
    def __init__(self, document):
        self.document = document
        self.finger = []
        self.cursor = 0
        self.tail = 0

    start = property(lambda self: min(self.cursor, self.tail))
    stop = property(lambda self: max(self.cursor, self.tail))
    top = property(lambda self: self.document.traverse(self.finger))
    context = property(lambda self: self.document.context(self.finger))

    def isinside(self, index):
        return 0 <= index <= len(self.top)

    def can_descend(self, index):
        return can_walk_down(self.document, self.finger, index)

    def can_ascend(self):
        return len(self.finger) > 0

class ContextVisual(object):
    def __init__(self, sel, font):
        self.cols = []
        self.height = 32
        self.width = 0
        for item in sel.context:
            if self.width != 0:
                self.width += 10
            tagl = font(item.tag)
            uidl = font(repr(item.uid))
            width = max(tagl.width, uidl.width)
            self.cols.append((tagl, uidl, width))
            self.width += width
    
    def __call__(self, screen):
        x = screen.width - self.width - 10
        y = screen.height - 32
        for tagl, uidl, width in self.cols:
            p = (width - tagl.width) / 2
            area = x + p, y + 10 - tagl.baseline, tagl.width, tagl.height
            screen(tagl, area)
            p = (width - uidl.width) / 2
            area = x + p, y + 26 - uidl.baseline, uidl.width, uidl.height
            screen(uidl, area)
            x += width + 10

class Editor(object):
    def __init__(self):
        self.window = window()
        self.window.on('paint', self.frame)
        self.window.on('key', self.key_in)
        self.window.on('keydown', self.keydown)
        self.window.show()
        
        self.font = get('font/proggy_tiny', 'font')
        self.border = get('assets/border.png', 'patch-9')

        self.document = node(['t', 'y', 'p', 'e', node(['h', 'e', 'r', 'e'], 'var')], 'root', 0)

        self.sel = Selection(self.document)

    def frame(self, screen, dt):
        screen(black)

        root = generate_frames(self.document, self.font, self.border) #dark_gray)
        root.decorator = dark_gray
        root(screen)

        highlight = root.traverse(self.sel.finger).highlight(self.sel.start, self.sel.stop)
        for area in highlight:
            screen.mul(almost_white, area).add(about_blue, area)
        
        ContextVisual(self.sel, self.font)(screen)

    def key_in(self, ch):
        sel = self.sel
        if ch.isalnum() or ch in '_.':
            do = splice(sel.start, sel.stop, [ch])
            sel.cursor += len(ch)
            sel.tail = sel.cursor
            undo = do(sel.top)
        pass #TODO: key_in(ch), pass to mode..

    def keydown(self, key, mod):
        sel = self.sel
        name = keybindings.get(key)
        if name == 'up':
            while sel.isinside(sel.cursor - 1):
                sel.cursor -= 1
                if sel.can_descend(sel.cursor) or sel.can_descend(sel.cursor-1):
                    break
            if not mod & SHIFT:
                sel.tail = sel.cursor
        if name == 'down':
            while sel.isinside(sel.cursor + 1):
                sel.cursor += 1
                if sel.can_descend(sel.cursor) or sel.can_descend(sel.cursor-1):
                    break
            if not mod & SHIFT:
                sel.tail = sel.cursor
        if name == 'left':
            sel.cursor -= sel.isinside(sel.cursor - 1)
            if not mod & SHIFT:
                sel.tail = sel.cursor
        if name == 'right':
            sel.cursor += sel.isinside(sel.cursor + 1)
            if not mod & SHIFT:
                sel.tail = sel.cursor
        if name == 'enter' and sel.can_descend(sel.cursor):
            sel.finger.append(sel.cursor)
            sel.cursor = sel.tail = len(sel.top) if mod & SHIFT else 0
        elif name == 'enter' and sel.can_descend(sel.cursor - 1):
            sel.finger.append(sel.cursor - 1)
            sel.cursor = sel.tail = len(sel.top) if mod & SHIFT else 0
        if name == 'space' and sel.can_ascend():
            sel.cursor = sel.tail = sel.finger.pop(-1) + (1 - bool(mod & SHIFT))
        if name == 'tab':
            base = sel.start
            undo0 = splice(base, sel.stop, [node([], 'unk', randint(1, 10**10))])(sel.top)
            sel.finger.append(base)
            undo1 = splice(0, 0, undo0.blob)(sel.top)
            sel.cursor -= base
            sel.tail -= base

        pass #TODO: keydown(key, mod, unicode), map to keybind, pass to mode..

if __name__ == "__main__":
    editor = Editor()
    eventloop()
