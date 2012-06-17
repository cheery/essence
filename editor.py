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
from essence.layout import String, Image, Glue, Padding, Row, Column, View, DocumentView, ilast
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
transparent_white = color(0xFF, 0xFF, 0xFF, 0x80)

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
    pygame.K_m: 'm',
    pygame.K_DELETE: 'delete',
    pygame.K_BACKSPACE: 'backspace',
    pygame.K_INSERT: 'insert',
}
modbindings = [
    (pygame.KMOD_SHIFT, 'shift'),
    (pygame.KMOD_CTRL, 'ctrl')
]

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

    def keyboard_hook(self, mode, key, modifiers, ch):
        for plugin in self.plugins:
            if plugin.keyboard_hook(mode, key, modifiers, ch):
                return True
        return False

    def layout_hook(self, obj, context, gen_children):
        for plugin in self.plugins:
            frame = plugin.layout_hook(obj, context, gen_children)
            if frame is not None:
                return frame
        # return some default instead
        if isinstance(obj, node) and obj.tag == 'root':
            children = []
            for last, frame in ilast(gen_children()):
                if last is not None:
                    children.append(Glue(8, 30))
                children.append(frame)
            return Column(children, iscluster=True)

        if isinstance(obj, node):
            children = []
            for last, frame in ilast(gen_children()):
                if last is not None:
                    children.append(Glue(8, 30))
                children.append(frame)
            frame = Row(children, iscluster=True)
            return Padding(frame, left=8, right=8, top=2, bottom=2, background=self.border)
        else:
            return String(obj, self.font, iscluster=True)

    def new_console(self):
        self.console = Buffer(
            node([], 'console', 0),
            history = ([],[]),
        )
        self.console.sel = Selection(self.console)
        return self.console

    def frame(self, screen, dt):
        screen(black)
        screen(almost_white)

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
            if buf.view is None:
                buf.view = view = DocumentView(self.layout_hook, buf.document)
            root = buf.view.root
            root.render(canvas)
            canvases[buf] = canvas

        sel = self.sel
        highlight = sel.buf.view.highlight(sel.finger, sel.start, sel.stop)
        for area in highlight:
            canvases[sel.buf](transparent_white, area) #.mul(almost_white, area).add(about_blue, area)

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

    def keydown(self, key, mod, ch):
        key = keybindings.get(key)
        modifiers = set()
        for mask, ident in modbindings:
            if mod & mask != 0:
                modifiers.add(ident)

        if self.keyboard_hook(self.sel, key, modifiers, ch): # TODO: replace with mode.
            return

        context = [obj.tag for obj in self.sel.context]
        sel = self.sel
        name = key

        if len(ch) > 0 and (ch.isalnum() or ch in '_.'):
            self.sel.splice([ch])
        elif key == 'left':
            self.sel.cursor -= self.sel.isinside(self.sel.cursor - 1)
            if not 'shift' in modifiers:
                self.sel.tail = self.sel.cursor
        elif key == 'right':
            self.sel.cursor += self.sel.isinside(self.sel.cursor + 1)
            if not 'shift' in modifiers:
                self.sel.tail = self.sel.cursor

        if name == 'enter' and ('console' in context):
            self.sel = self.buf.sel
            self.interpret(self.console.document)
        if name == 'up':
            while sel.isinside(sel.cursor - 1):
                sel.cursor -= 1
                if sel.can_descend(sel.cursor) or sel.can_descend(sel.cursor-1):
                    break
            if not 'shift' in modifiers:
                self.sel.tail = self.sel.cursor
        if name == 'down':
            while sel.isinside(sel.cursor + 1):
                sel.cursor += 1
                if sel.can_descend(sel.cursor) or sel.can_descend(sel.cursor-1):
                    break
            if not 'shift' in modifiers:
                sel.tail = sel.cursor
        if name == 'enter' and sel.can_descend(sel.cursor):
            sel.finger = sel.finger + (sel.cursor,)
            sel.cursor = sel.tail = len(sel.top) if 'shift' in modifiers else 0
        elif name == 'enter' and sel.can_descend(sel.cursor - 1):
            sel.finger = sel.finger + (sel.cursor - 1,)
            sel.cursor = sel.tail = len(sel.top) if 'shift' in modifiers else 0
        if name == 'space' and sel.can_ascend():
            sel.cursor = sel.tail = sel.finger[-1] + (1 - bool('shift' in modifiers))
            sel.finger = sel.finger[:-1]
        if name == 'tab':
            sel.build('unk')
        if name == 's' and 'ctrl' in modifiers:
            sel.buf.save()
        if name == 'q' and 'ctrl' in modifiers and not sel.buf.modified:
            exit(0)
        if name == 'q' and 'ctrl' in modifiers and 'shift' in modifiers:
            exit(0)
        if name == 'u' and 'ctrl' in modifiers:
            sel.buf.undo()
        if name == 'r' and 'ctrl' in modifiers:
            sel.buf.redo()
        if name in ('delete', 'backspace'):
            offset = ('backspace', 'delete').index(name)*2 - 1
            if sel.cursor == sel.tail and sel.isinside(sel.cursor + offset):
                sel.cursor += offset
            sel.buf.do(sel.finger, splice(sel.start, sel.stop, []))
            sel.tail = sel.cursor = sel.start
        if name == 'a' and 'ctrl' in modifiers:
            sel.start = 0
            sel.stop = len(sel.top)
        if name == 'y' and 'ctrl' in modifiers:
            blob = sel.yank()
            if len(blob) > 0:
                scrap.put(pygame.SCRAP_TEXT, serialize(blob))
        if name == 'insert' and 'ctrl' in modifiers:
            data = scrap.get(pygame.SCRAP_TEXT)
            if data:
                blob = deserialize(data)
                sel.buf.do(sel.finger, splice(sel.start, sel.stop, blob))
                sel.cursor = sel.tail = sel.start + len(blob)
        if name == 'delete' and 'ctrl' in modifiers:
            blob = sel.yank()
            if len(blob) > 0:
                scrap.put(pygame.SCRAP_TEXT, serialize(blob))
            sel.buf.do(sel.finger, splice(sel.start, sel.stop, []))
            sel.stop = sel.start
        if name == 'n' and 'ctrl' in modifiers and len(context) > 0:
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
