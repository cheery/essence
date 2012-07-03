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

#TODO: table layout
#TODO: breaker, breakable, (penalty, pre, post) into glue

import itertools
from casuarius import Solver, ConstraintVariable, weak, medium, strong, required
valueof = lambda obj: obj.value if hasattr(obj, 'value') else obj

class declaration(object):
    hole = None
    def render(self, surface):
        pass
    
    def glue(self, engine, parent, prev, next):
        pass

    def configure(self, engine):
        pass

    def highlight(self, start, stop):
        pass

    def find(self):
        return iter([])

    def variables(self, *a):
        template = repr(self) + ".%s"
        for name in a:
            setattr(self, name, ConstraintVariable(template % name))

class frame(declaration):
    right = property(lambda self: self.left + self.width)
    bottom = property(lambda self: self.top + self.height)

    @property
    def area(self):
        return map(valueof, (self.left, self.top, self.width, self.height))

    def glue(self, engine, parent, prev, next):
        engine.require(parent.left + parent.padding[0] <= self.left)
        engine.require(parent.top + parent.padding[1] <= self.top)
        engine.require(self.right + parent.padding[2] <= parent.right)
        engine.require(self.bottom + parent.padding[3] <= parent.bottom)

    def highlight(self, start1, stop1):
        start0, stop0 = self.hole.start, self.hole.stop
        if stop0 >= start1 and stop1 >= start0:
            start, stop = max(start0, start1) - start0, min(stop0, stop1) - start0
            left, top, width, height = self.area
            offset0 = [left, left+width][start]
            offset1 = [left, left+width][stop]
            return (offset0, top - 1, offset1 - offset0 + 1, height + 2)

class string(frame):
    def __init__(self, label, xalign=None, yalign=None):
        self.label = label
        self.variables('left', 'top')
        self.width = label.width
        self.height = label.height
        self.xalign = self.left if xalign is None else xalign(self)
        self.yalign = self.top + label.mathline if yalign is None else yalign(self)
    
    def render(self, surface):
        surface(self.label, self.area)

    def highlight(self, start1, stop1):
        start0, stop0 = self.hole.start, self.hole.stop
        if stop0 >= start1 and stop1 >= start0:
            start, stop = max(start0, start1) - start0, min(stop0, stop1) - start0
            left, top, width, height = self.area
            offset0 = self.label.offsets[start] + left
            offset1 = self.label.offsets[stop] + left
            return (offset0, top - 1, offset1 - offset0 + 1, height + 2)

class image(frame):
    def __init__(self, image, width=None, height=None, xalign=None, yalign=None):
        self.image = image
        self.variables('left', 'top')
        self.width = image.width if width is None else width
        self.height = image.height if height is None else height
        self.xalign = self.left if xalign is None else xalign(self)
        self.yalign = self.top + self.height/2 if yalign is None else yalign(self)

    def render(self, surface):
        if self.image:
            surface(self.image, self.area)

class xglue(declaration):
    def __init__(self, gap, stretch):
        self.gap = gap
        self.stretch = stretch

    def glue(self, engine, parent, prev, next):
        if prev is not None and next is not None:
            engine.prefer(prev.right + self.gap == next.left)
            if self.stretch is not None:
                engine.require(prev.right + self.gap + self.stretch >= next.left)
            engine.require(prev.right + self.gap <= next.left)
            engine.prefer(prev.yalign == next.yalign)

class yglue(declaration):
    def __init__(self, gap, stretch):
        self.gap = gap
        self.stretch = stretch

    def glue(self, engine, parent, prev, next):
        if prev is not None and next is not None:
            engine.prefer(prev.bottom + self.gap == next.top)
            if self.stretch is not None:
                engine.require(prev.bottom + self.gap + self.stretch >= next.top)
            engine.require(prev.bottom + self.gap <= next.top)
            engine.prefer(prev.xalign == next.xalign)

def neighboured(obj):
    it = iter(obj)
    item0 = None
    item1 = it.next()
    for item2 in it:
        yield item0, item1, item2
        item0 = item1
        item1 = item2
    yield item0, item1, None

class group(frame):
    def __init__(self, elements, background=None, padding=(0,0,0,0), xalign=None, yalign=None):
        self.elements = elements
        self.background = background
        self.padding = padding
        self.variables('left', 'top', 'width', 'height')
        self.xalign = self.left if xalign is None else xalign(self)
        self.yalign = self.top + self.height / 2 if yalign is None else yalign(self)

    def __iter__(self):
        return iter(self.elements)

    def __getitem__(self, index):
        return self.elements[index]

    def configure(self, engine):
        for item0, item1, item2 in neighboured(self):
            item1.configure(engine)
            item1.glue(engine, self, item0, item2)

    def glue(self, engine, parent, prev, next):
        frame.glue(self, engine, parent, prev, next)
        engine.guide(self.width == 1)
        engine.guide(self.height == 1)

    def render(self, surface):
        if self.background:
            surface(self.background, self.area)
        for decl in self:
            decl.render(surface)

    def find(self):
        for obj in self:
            yield obj
            for desc in obj.find():
                yield desc

class expando(frame):
    def __init__(self, element, width, height, expanded=True, background=None, xalign=None, yalign=None):
        self.element = element
        self.expanded = expanded
        self.background = background
        self.variables('left', 'top')
        self.width = width
        self.height = height
        self.xalign = self.left if xalign is None else xalign(self)
        self.yalign = self.top + self.height/2 if yalign is None else yalign(self)
    
    def configure(self, engine):
        self.element.configure(engine)

    def glue(self, engine, parent, prev, next):
        frame.glue(self, engine, parent, prev, next)
        engine.guide(self.xalign == self.element.xalign)
        engine.guide(self.yalign == self.element.yalign)

    def render(self, surface):
        if self.background:
            surface(self.background, self.area)
        if self.expanded:
            self.element.render(surface)

    def find(self):
        yield self.element
        for decl in self.element.find():
            yield decl

class engine(object):
    def __init__(self):
        self.solver = Solver()
        self.solver.autosolve = True

    def require(self, rule):
        self.solver.add_constraint(rule)

    def prefer(self, rule):
        rule.strength = strong
        self.solver.add_constraint(rule)

    def guide(self, rule):
        rule.strength = weak
        self.solver.add_constraint(rule)

__all__ = [
    declaration, frame, string, image, xglue, yglue, neighboured, group, expando, engine
]
