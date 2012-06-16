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
"""
    To understand why layouter is like what it is, you'd need to understand
    what were the design constraints. Here I describe the design constraints
    that brought me to this design.

    * must be controllable by a plugin hook
    * must encode hierarchy in what it represents
    * must allow highlight of the selection that falls within some range.
    * must input dom and output frames
    * plugins must be able of defining more frames
    * there must be existing good frames like, string, image, group, glue
    * must allow background on frame (perhaps padding as well?)

    questions:
    * table anchors?
    * implement incremental now or later?
"""
from essence.document import node
from casuarius import Solver, ConstraintVariable, weak, medium, strong, required
from os import urandom

varying = lambda: ConstraintVariable(urandom(4).encode('hex'))
valueof = lambda obj: obj.value if hasattr(obj, 'value') else obj

class Frame(object):
#    def __init__(self, left, top, width, height, halign, valign, iscluster=False, background=None):
#        self.left = left
#        self.top = top
#        self.width = width
#        self.height = height
#        self.halign = halign
#        self.valign = valign
#        self.iscluster = iscluster
#        self.background = background

    right = property(lambda self: self.left + self.width)
    bottom = property(lambda self: self.top + self.height)

    @property
    def area(self):
        return map(valueof, (self.left, self.top, self.width, self.height))

    def render(self, surface):
        if self.background:
            surface(self.background, self.area)

    def highlight(self, start, stop):
        left, top, width, height = self.area
        offset0 = [left, left+width][start]
        offset1 = [left, left+width][stop]
        return (offset0, top - 1, offset1 - offset0 + 1, height + 2)

    cluster_length = 1

    def configure_layout(self, view):
        pass

    def traverse(self, finger, index=0):
        return None

class String(Frame):
    def __init__(self, string, font, iscluster=False, background=None):
        self.string = string
        self.label = font(self.string)

        self.left = varying()
        self.top = varying()
        self.width = self.label.width
        self.height = self.label.height
        self.halign = self.left
        self.valign = self.top + self.label.mathline
        self.iscluster = iscluster
        self.cluster_length = len(self.string)
        self.background = background

    def render(self, surface):
        if self.background:
            surface(self.background, self.area)
        surface(self.label, self.area)

    def highlight(self, start, stop):
        left, top, width, height = self.area
        offset0 = self.label.offsets[start]
        offset1 = self.label.offsets[stop]
        return (left + offset0, top - 1, offset1 - offset0 + 1, height + 2)

class Image(Frame):
    def __init__(self, background, width=None, height=None, iscluster=False):
        self.background = background
        self.left = varying()
        self.top = varying()
        self.width = background.width if width is None else width
        self.height = background.height if height is None else height
        self.halign = self.left
        self.valign = self.top + self.height / 2 
        self.iscluster = iscluster

class Glue(Frame):
    def __init__(self, size, stretch=None, background=None):
        self.size = size
        self.stretch = stretch

        self.left = varying()
        self.top = varying()
        self.height = varying()
        self.width = varying()
        self.halign = self.left + self.width / 2
        self.valign = self.top + self.height / 2
        self.iscluster = False
        self.background = background

class Padding(Frame):
    def __init__(self, child, left=0, top=0, right=0, bottom=0, background=None):
        self.child = child
        self.left = child.left - left
        self.top = child.top - top
        self.width = child.right + right - self.left
        self.height = child.bottom + bottom - self.top
        self.halign = child.halign
        self.valign = child.valign
        self.iscluster = child.iscluster
        self.background = background
    
    def configure_layout(self, view):
        self.child.configure_layout(view)

    def render(self, surface):
        if self.background:
            surface(self.background, self.area)
        self.child.render(surface)

    def traverse(self, finger, index=0):
        return self.child.traverse(finger, index)

class Group(Frame):
    min_width = 16
    min_height = 16
    def __init__(self, children, iscluster=False, background=None):
        self.children = children

        self.left = varying()
        self.top = varying()
        self.width = varying()
        self.height = varying()
        self.halign = self.left
        self.valign = self.top + self.height / 2
        self.iscluster = iscluster
        self.background = background

    def __iter__(self):
        return iter(self.children)

    def render(self, surface):
        if self.background:
            surface(self.background, self.area)
        for child in self:
            child.render(surface)

    def traverse(self, finger, index=0):
        if index >= len(finger):
            return self
        base = finger[index]
        for child in self:
            if child.iscluster:
                if base == 0:
                    return child.traverse(finger, index+1)
                base -= child.cluster_length
        return None

class Row(Group):
    def configure_layout(self, view):
        first = None
        last = None
        for child in self:
            child.configure_layout(view)
            view.require(self.left <= child.left)
            view.require(child.right <= self.right)
            view.require(self.top <= child.top)
            view.require(child.bottom <= self.bottom)
            view.prefer(self.valign == child.valign)
            if isinstance(child, Glue):
                view.guide(self.height == child.height)
                view.guide(child.size == child.width)
                view.require(child.size <= child.width)
                view.require(child.width <= child.size + child.stretch)
            if last is not None:
                view.require(last.right <= child.left)
            else:
                first = child
            last = child
        view.require(self.width >= self.min_width)
        view.require(self.height >= self.min_height)
        view.guide(self.width == self.min_width)
        view.guide(self.height == self.min_height)
        if first and last:
            view.guide(first.left - self.left == self.right - last.right)

class Column(Group):
    def configure_layout(self, view):
        first = None
        last = None
        for child in self:
            child.configure_layout(view)
            view.require(self.left <= child.left)
            view.require(child.right <= self.right)
            view.require(self.top <= child.top)
            view.require(child.bottom <= self.bottom)
            view.prefer(self.halign == child.halign)
            if isinstance(child, Glue):
                view.guide(self.width == child.width)
                view.guide(child.size == child.height)
                view.require(child.size <= child.height)
                view.require(child.height <= child.size + child.stretch)
            if last is not None:
                view.require(last.bottom <= child.top)
            else:
                first = child
            last = child
        view.require(self.width >= self.min_width)
        view.require(self.height >= self.min_height)
        view.guide(self.width == self.min_width)
        view.guide(self.height == self.min_height)
        if first and last:
            view.guide(first.top - self.top == self.bottom - last.bottom)

class View(object):
    def __init__(self, root):
        self.solver = Solver()
        self.root = root
        self.root.configure_layout(self)

    def require(self, rule):
        self.solver.add_constraint(rule)

    def prefer(self, rule):
        rule.strength = strong
        self.solver.add_constraint(rule)

    def guide(self, rule):
        rule.strength = weak
        self.solver.add_constraint(rule)

    def highlight(self, finger, start, stop):
        frame = self.traverse(finger)
        highlights = []
        for child in frame:
            offset = child.cluster_length
            if child.iscluster:
                if stop >= 0 and start <= offset:
                    highlights.append(child.highlight(max(start,0), min(stop,offset)))
                start -= offset
                stop -= offset
        if len(highlights) == 0:
            highlights.append(frame.area)
        return highlights

    def traverse(self, finger):
        return self.root.traverse(finger)

class DocumentView(View):
    def __init__(self, plugin_hook, document):
        self.plugin_hook = plugin_hook
        self.document = document
        View.__init__(self, root = self.build(document, ()))
        self.require(self.root.left == 32)
        self.require(self.root.top == 32)
        self.prefer(self.root.halign == 32)
        self.prefer(self.root.valign == 32)
        self.solver.autosolve = True

    def build(self, obj, context):
        def gen_children():
            frames = []
            subcontext = context + (obj.tag,)
            for child in obj.clusters:
                frames.append(self.build(child, subcontext))
            return frames
        return self.plugin_hook(obj, context, gen_children)

def ilast(seq):
    last = None
    for this in seq:
        yield last, this
        last = this
