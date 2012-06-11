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
from essence.document import node
from casuarius import Solver, ConstraintVariable, weak
from os import urandom

varying = lambda: ConstraintVariable(urandom(4).encode('hex'))

class Frame(object):
    @property
    def right(self):
        return self.left + self.width
    @property
    def bottom(self):
        return self.top + self.height

    def metric(self, attr):
        var = getattr(self, attr)
        if isinstance(var, ConstraintVariable):
            return var.value
        else:
            return var

    @property
    def area(self):
        return (
            self.metric('left'),
            self.metric('top'),
            self.metric('width'),
            self.metric('height')
        )

class StringFrame(Frame):
    def __init__(self, string, font):
        self.string = string

        self.label = font(self.string)

        self.width = self.label.width
        self.height = self.label.height
        self.left = varying()
        self.top = varying()

        self.valign = self.top + self.label.mathline
        self.halign = self.left

    def highlight_outer(self, start, stop):
        left, top, width, height = self.area
        offset0 = self.label.offsets[0 if start is None else start]
        offset1 = self.label.offsets[-1 if stop is None else stop]
        return (left + offset0, top - 1, offset1 - offset0 + 1, height + 2)

    def __call__(self, screen):
        screen(self.label, self.area)

    def highlight_length(self):
        return len(self.string)

class BlockFrame(Frame):
    def __init__(self, children, decorator=None):
        self.children = children
        self.decorator = decorator

        self.width = varying()
        self.height = varying()
        self.left = varying()
        self.top = varying()

        self.valign = varying()
        self.halign = varying()

    def highlight_outer(self, start, stop):
        left, top, width, height = self.area
        offset0 = [left, left+width][start]
        offset1 = [left, left+width][stop]
        return (offset0, top - 1, offset1 - offset0 + 1, height + 2)

    def highlight_length(self):
        return 1

    def highlight(self, start, stop):
        highlights = []
        for child in self.children:
            offset = child.highlight_length()
            if stop >= 0 and start <= offset:
                highlights.append(child.highlight_outer(max(start,0), min(stop,offset)))
            start -= offset
            stop -= offset
        if len(highlights) == 0:
            x, y, width, height = self.area
            highlights.append((x + width / 2, y-1, 1, height+2))
        return highlights
        
    def traverse(self, finger, index=0):
        if index >= len(finger):
            return self
        base = finger[index]
        for child in self.children:
            if base == 0:
                return child.traverse(finger, index+1)
            base -= child.highlight_length()
        return None
    
    def __call__(self, screen):
        if self.decorator:
            screen.add(self.decorator, self.area)
        for child in self.children:
            child(screen)

class ImageFrame(Frame):
    def __init__(self, image, width=None, height=None):
        self.image = image

        self.width = image.width if width is None else width
        self.height = image.height if height is None else height
        self.left = varying()
        self.top = varying()

        self.valign = (self.top + self.bottom) / 2
        self.halign = self.left

    def __call__(self, screen):
        screen(self.image, self.area)

class Root(BlockFrame):
    def __init__(self, children):
        BlockFrame.__init__(self, children)
        self.solver = Solver()

    def satisfy(self, rule, strength=None):
        if strength is not None:
            rule.strength = strength
        self.solver.add_constraint(rule)

def row_layout(this, children, satisfy):
    last = None
    for child in children:
        satisfy(this.left <= child.left - 10)
        satisfy(child.right <= this.right - 10)
        satisfy(this.top <= child.top - 10)
        satisfy(child.bottom <= this.bottom - 10)
        satisfy(this.valign == child.valign)
        if last is not None:
            satisfy(last.right <= child.left - 8)
            #satisfy(last.bottom <= child.top - 8)
        last = child
    satisfy(this.halign == this.left)
    satisfy(this.width >= 20)
    satisfy(this.height >= 20)
    satisfy(this.valign >= this.top + 20)
    satisfy(this.valign <= this.bottom - 20)

    satisfy(this.width == 0, weak)
    satisfy(this.height == 0, weak)
    #satisfy(this.valign == (this.top + this.bottom) / 2)

def layout_blob(blob, font, unk_color, satisfy):
    string = ''
    for item in blob:
        if isinstance(item, node):
            if len(string) > 0:
                yield StringFrame(string, font)
                string = ''
            children = []
            this = BlockFrame(children, unk_color)
            children.extend(layout_blob(item, font, unk_color, satisfy))
            yield this
            row_layout(this, children, satisfy)
        else:
            string += item
    if len(string) > 0:
        yield StringFrame(string, font)


def generate_frames(tree, font, unk_color):
    frames = []
    root = Root(frames)
    frames.extend(layout_blob(tree, font, unk_color, root.satisfy))
    row_layout(root, frames, root.satisfy)
    root.satisfy(root.left == 10)
    root.satisfy(root.top == 10)
    root.solver.autosolve = True
    return root
