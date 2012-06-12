# This file is part of Essential Editor Research Project (EERP)
#
# EERP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EERP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EERP.  If not, see <http://www.gnu.org/licenses/>.
from essence.ui import color, window, get, eventloop, empty
from essence.document import node, copy, splice, build, collapse, rename, serialize, deserialize, can_walk_up, can_walk_down, can_walk_left, can_walk_right
from essence.layout import StringFrame, BlockFrame, ImageFrame, generate_frames
from essence.buffer import Buffer
from essence.selection import Selection
from essence.pluginmanager import default_plugin_directory, load_all_plugins
from random import randint
from sys import argv, exit
from pygame import scrap
import os

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
    pygame.K_a: 'a',
    pygame.K_s: 's',
    pygame.K_q: 'q',
    pygame.K_u: 'u',
    pygame.K_r: 'r',
    pygame.K_y: 'y',
    pygame.K_n: 'n',
    pygame.K_DELETE: 'delete',
    pygame.K_BACKSPACE: 'backspace',
    pygame.K_INSERT: 'insert',
}

SHIFT = pygame.KMOD_SHIFT
CTRL = pygame.KMOD_CTRL
#KMOD_NONE, KMOD_LSHIFT, KMOD_RSHIFT, KMOD_SHIFT, KMOD_CAPS,
#KMOD_LCTRL, KMOD_RCTRL, KMOD_CTRL, KMOD_LALT, KMOD_RALT,
#KMOD_ALT, KMOD_LMETA, KMOD_RMETA, KMOD_META, KMOD_NUM, KMOD_MODE

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

        document = node([], 'root', 0)
        if len(argv) > 1 and os.path.exists(argv[1]):
            document = deserialize(open(argv[1]).read())

        self.buf = Buffer(
            document = document,
            history = ([],[]),
            filename = argv[1] if len(argv) > 1 else None,
        )
        self.sel = self.buf.sel = Selection(self.buf)
        self.new_console()

        self.plugins = []
        for module in load_all_plugins([default_plugin_directory]):
            if not hasattr(module, 'plugins'):
                continue
            for plugin in module.plugins:
                self.plugins.append(plugin(self))
        self.plugins.sort(key=lambda obj: obj.priority)

    def key(self, context, sel, name, modifiers, ch):
        for plugin in self.plugins:
            if plugin.key(context, sel, name, modifiers, ch):
                return True
        return False

    def visualise(self, context, obj, y):
        for plugin in self.plugins:
            frame = plugin.visualise(context, obj, y)
            if frame is not None:
                return frame
        # return some default instead

    def new_console(self):
        self.console = Buffer(
            node([], 'console', 0),
            history = ([],[]),
        )
        self.console.sel = Selection(self.console)
        return self.console

    def frame(self, screen, dt):
        screen(black)

        construct_frame = lambda document: generate_frames(document, self.font, self.border)

        if self.sel == self.console.sel:
            width, height = screen.width, screen.height
            frames = {
#                self.buf: (0, 0, width, height - 64),
#                self.console: (0, height - 64, width, 64),
                self.console: (0, 0, width, height),
            }
        else:
            frames = {
                self.buf: (0, 0, screen.width, screen.height),
            }
        canvases = {}
        for buf, area in frames.items():
            canvas = empty(area[2], area[3])
            root = buf(screen, construct_frame)
            root.decorator = dark_gray # tiny hack, removed later.
            root(canvas)
            canvases[buf] = canvas

        sel = self.sel
        highlight = sel.buf.root_frame.traverse(sel.finger).highlight(sel.start, sel.stop)
        for area in highlight:
            canvases[sel.buf](about_blue, area) #.mul(almost_white, area).add(about_blue, area)

        for buf in frames:
            screen(canvases[buf], frames[buf])
        
        ContextVisual(self.sel, self.font)(screen)

        caption, iconname = pygame.display.get_caption()
        if self.buf.caption != caption:
            pygame.display.set_caption(self.buf.caption, 'upi')

    def interpret(self, command):
        if len(command) != 3: # a cheap hack.
            return
        new_tag = ''.join(command[2])
        sel = self.sel
        sel.buf.do(sel.finger, rename(new_tag))

    def key_in(self, ch):
        sel = self.sel
        if ch.isalnum() or ch in '_.':
            sel.buf.do(sel.finger, splice(sel.start, sel.stop, [ch]))
            sel.tail = sel.cursor = sel.start + len(ch)
        pass #TODO: key_in(ch), pass to mode..

    def keydown(self, key, mod, ch):
        sel = self.sel
        name = keybindings.get(key)
        context = [item.tag for item in sel.context]
        modifiers = []
        if mod & SHIFT:
            modifiers.append('shift')
        if mod & CTRL:
            modifiers.append('ctrl')
        if self.key(context, sel, name, modifiers, ch):
            return

        if name == 'enter' and ('console' in context):
            self.sel = self.buf.sel
            self.interpret(self.console.document)

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
            sel.finger = sel.finger + (sel.cursor,)
            sel.cursor = sel.tail = len(sel.top) if mod & SHIFT else 0
        elif name == 'enter' and sel.can_descend(sel.cursor - 1):
            sel.finger = sel.finger + (sel.cursor - 1,)
            sel.cursor = sel.tail = len(sel.top) if mod & SHIFT else 0
        if name == 'space' and sel.can_ascend():
            sel.cursor = sel.tail = sel.finger[-1] + (1 - bool(mod & SHIFT))
            sel.finger = sel.finger[:-1]
        if name == 'tab':
            base = sel.start
            sel.buf.do(sel.finger, build(sel.start, sel.stop, 'unk', randint(1, 10**10)))
            sel.finger = sel.finger + (base,)
            sel.cursor -= base
            sel.tail -= base
        if name == 's' and mod & CTRL:
            sel.buf.save()
        if name == 'q' and mod & CTRL and not sel.buf.modified:
            exit(0)
        if name == 'q' and mod & CTRL and mod & SHIFT:
            exit(0)
        if name == 'u' and mod & CTRL:
            sel.buf.undo()
        if name == 'r' and mod & CTRL:
            sel.buf.redo()
        if name in ('delete', 'backspace'):
            offset = ('backspace', 'delete').index(name)*2 - 1
            if sel.cursor == sel.tail and sel.isinside(sel.cursor + offset):
                sel.cursor += offset
            sel.buf.do(sel.finger, splice(sel.start, sel.stop, []))
            sel.tail = sel.cursor = sel.start
        if name == 'a' and mod & CTRL:
            sel.start = 0
            sel.stop = len(sel.top)
        if name == 'y' and mod & CTRL:
            blob = sel.yank()
            if len(blob) > 0:
                scrap.put(pygame.SCRAP_TEXT, serialize(blob))
        if name == 'insert' and mod & CTRL:
            data = scrap.get(pygame.SCRAP_TEXT)
            if data:
                blob = deserialize(data)
                sel.buf.do(sel.finger, splice(sel.start, sel.stop, blob))
                sel.cursor = sel.tail = sel.start + len(blob)
        if name == 'delete' and mod & CTRL:
            blob = sel.yank()
            if len(blob) > 0:
                scrap.put(pygame.SCRAP_TEXT, serialize(blob))
            sel.buf.do(sel.finger, splice(sel.start, sel.stop, []))
            sel.stop = sel.start
        if name == 'n' and mod & CTRL and len(context) > 0:
            console = self.new_console()
            self.sel = console.sel
            rename_symbol = node(['r','e','n','a','m','e'], 'action', randint(1, 10**10))
            selection_symbol = node(['t','o','p'], 'symbol', randint(1, 10**10))
            slot = node([], 'str', randint(1, 10**10))
            console.do(console.sel.finger, splice(0, 0, [rename_symbol, selection_symbol, slot]))
            console.sel.finger = (2,)
            console.sel.current = console.sel.tail = 0
        pass #TODO: keydown(key, mod, unicode), map to keybind, pass to mode..

if __name__ == "__main__":
    editor = Editor()
    eventloop(use_scrap=True)
