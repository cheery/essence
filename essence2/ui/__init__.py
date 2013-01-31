from casuarius import (
    ConstraintVariable, Solver, ExplainedCassowaryError,
    required, strong, medium, weak,
    Strength, SymbolicWeight,
)
from os import urandom
from essence2 import rgba, vec2, rectangle, clamp

microscopic = Strength('microscopic', SymbolicWeight((0.0, 0.0, 0.0, 1.0)))

class Variable(ConstraintVariable):
    __slots__ = 'owner', 'which'
    def init(self, owner, which=None):
        self.owner = owner
        self.which = which

class Expand(ConstraintVariable):
    __slots__ = 'owner', 'toplevel'
    def init(self, owner, toplevel):
        self.owner = owner
        self.toplevel = toplevel
    
def variable(owner, which=None):
    var = Variable(urandom(4).encode('hex'))
    var.init(owner, which)
    return var

def expander(parent, owner, toplevel=None):
    if parent is None:
        var = Expand(urandom(4).encode('hex'))
        var.init(owner, toplevel if toplevel != None else owner)
        return var
    else:
        return parent

class Box(object):
    def __init__(self):
        self.left   = variable(self, 'left')
        self.top    = variable(self, 'top')
        self.right  = variable(self, 'right')
        self.bottom = variable(self, 'bottom')

    def __iter__(self):
        return iter((self.left, self.top, self.right, self.bottom))

    @property
    def value(self):
        left, top, right, bottom = self
        p0 = vec2(left.value, top.value)
        p1 = vec2(right.value, bottom.value)
        return rectangle(p0, p1-p0)

class Layout(object):
    def __init__(self):
        self.solver = Solver()

    def update(self, element):
        self.solver.autosolve = False
        for constraint in element.constraints[1]:
            self.solver.remove_constraint(constraint)
        for constraint in element.constraints[0]:
            self.solver.add_constraint(constraint)
        element.constraints = [], element.constraints[0]
        self.solver.autosolve = True

#def cause_constraint_error():
#    solver = Solver()
#    green = variable('green wiener')
#    blue = variable('blue light')
#    a = green <= blue
#    b = blue + 1 == green
#    try:
#        solver.add_constraint(a)
#        solver.add_constraint(b)
#        solver.autosolve = True
#    except ExplainedCassowaryError, e:
#        return e, (a,b)

class Container(object):
    def __init__(self, config, elements):
        self.config = config
        self.elements = elements
        self.inner = Box()
        self.outer = Box()
        self.constraints = [], ()

    def __getitem__(self, index):
        return self.elements[index]

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def copy(self):
        return self.__class__(self.config, [element.copy() for element in self])

    def constrain(self, *rules):
        self.constraints[0].extend(rules)

    def draw(self, screen):
        background = self.config.get('background')
        inner_background = self.config.get('inner_background')
        if background:
            screen(background, self.outer.value)
        if inner_background:
            screen(inner_background, self.inner.value)
        for element in self:
            element.draw(screen)

class Label(object):
    def __init__(self, config, source):
        self.config = config
        self.source = source
        self.inner = Box()
        self.outer = Box()
        self.constraints = [], ()

    def constrain(self, *rules):
        self.constraints[0].extend(rules)

    def copy(self):
        return self.__class__(self.config, self.source)

    def feed(self, layout, h_expand=None, v_expand=None):
        inner = self.inner
        outer = self.outer
        font = self.config['font']
        postprocess = self.config.get('postprocess')

        self.surface = font(str(self.source))
        if postprocess:
            self.surface(postprocess)
        width, height = self.surface.geometry.size

        self.constrain(
            outer.left           == inner.left,
            outer.right          == inner.right,
            inner.left   + width == inner.right,
            outer.top    + 16    == outer.bottom,
            inner.top    + 12    == outer.bottom,
            inner.bottom + 5     == outer.bottom,
        )
        layout.update(self)

    def draw(self, screen):
        self.surface.geometry.base = vec2(
            self.inner.left.value,
            self.inner.bottom.value - self.surface.baseline,
        )
        screen(self.surface)

class Column(Container):
    def feed(self, layout, h_expand=None, v_expand=None):
        inner = self.inner
        outer = self.outer
        align_by = self.config.get('align_by', baseline)
        h_expand = expander(h_expand, self)
        v_expand = expander(v_expand, self)
        last = None
        for element in self:
            element.feed(layout, h_expand, v_expand)
            self.constrain(
                (outer.left  <= element.outer.left),
                (outer.left  == element.outer.left)  | medium | 2.0,
                (outer.right >= element.outer.right),
                (outer.right == element.outer.right) | medium | 2.0,
                (inner.left  <= element.inner.left),
                (inner.left  == element.inner.left)  | medium,
                (inner.right >= element.inner.right),
                (inner.right == element.inner.right) | medium,
            )
            if last != None:
                self.constrain(
                    align_by(last, element, 'column'),
                    last.outer.bottom == element.outer.top,
                )
            last = element
        first, last = self[0], self[-1]
        self.constrain(
            (outer.top    == first.outer.top),
            (outer.bottom == last.outer.bottom),
            (inner.top    == first.inner.top),
            (inner.bottom == last.inner.bottom),
        )
        layout.update(self)

class Row(Container):
    def feed(self, layout, h_expand=None, v_expand=None):
        inner = self.inner
        outer = self.outer
        align_by = self.config.get('align_by', baseline)
        h_expand = expander(h_expand, self)
        v_expand = expander(v_expand, self)
        last = None
        for element in self:
            element.feed(layout, h_expand, v_expand)
            self.constrain(
                (outer.top    <= element.outer.top),
                (outer.top    == element.outer.top)    | medium | 2.0,
                (outer.bottom >= element.outer.bottom),
                (outer.bottom == element.outer.bottom) | medium | 2.0,
                (inner.top    <= element.inner.top),
                (inner.top    == element.inner.top)    | medium,
                (inner.bottom >= element.inner.bottom),
                (inner.bottom == element.inner.bottom) | medium,
            )
            if last != None:
                self.constrain(
                    align_by(last, element, 'row'),
                    last.outer.right == element.outer.left,
                )
            last = element
        first, last = self[0], self[-1]
        self.constrain(
            (outer.left  == first.outer.left),
            (outer.right == last.outer.right),
            (inner.left  == first.inner.left),
            (inner.right == last.inner.right),
        )
        layout.update(self)

class Space(object):
    def __init__(self, config):
        self.config = config
        self.inner = Box()
        self.outer = self.inner
        self.constraints = [], ()

    def constrain(self, *rules):
        self.constraints[0].extend(rules)

    def copy(self):
        return self.__class__(self.config, self.element)

    def feed(self, layout, h_expand=None, v_expand=None):
        min_width, min_height = self.config.get('min_size', (0,0))
        expandflags = self.config.get('expand', None)
        outer = self.outer
        h_expand = expander(h_expand, self)
        v_expand = expander(v_expand, self)
        if expandflags in ('both', 'horizontal'):
            self.constrain(
                outer.left + min_width  <= outer.right,
                h_expand == outer.right - outer.left,
                (outer.left == h_expand.toplevel.outer.left)   | strong,
                (outer.right == h_expand.toplevel.outer.right) | strong,
            )
        else:
            self.constrain(outer.left + min_width  == outer.right)
        if expandflags in ('both', 'vertical'):
            self.constrain(
                outer.top  + min_height <= outer.bottom,
                v_expand == outer.bottom - outer.top,
                (outer.top    == v_expand.toplevel.outer.top)    | strong,
                (outer.bottom == v_expand.toplevel.outer.bottom) | strong,
            )
        else:
            self.constrain(outer.top  + min_height == outer.bottom)
        layout.update(self)

    def draw(self, screen):
        background = self.config.get('background')
        if background:
            screen(background, self.outer.value)

class Padding(object):
    def __init__(self, config, element):
        self.config = config
        self.element = element
        self.inner = element.inner
        self.outer = Box()
        self.constraints = [], ()

    def constrain(self, *rules):
        self.constraints[0].extend(rules)

    def copy(self):
        return self.__class__(self.config, self.element)

    def feed(self, layout, h_expand=None, v_expand=None):
        left, top, right, bottom = self.config.get('padding', (0,0,0,0))
        align_by = self.config.get('align_by', baseline)
        expandflags = self.config.get('expand', None)
        outer = self.outer
        element = self.element
        h_expand = expander(h_expand, self)
        v_expand = expander(v_expand, self)

        if expandflags in ('both', 'horizontal'):
            self.constrain(
                outer.left  + left <= element.outer.left,
                outer.right        >= element.outer.right + right,
                h_expand == outer.right - outer.left,
                (outer.left  == h_expand.toplevel.outer.left)  | strong,
                (outer.right == h_expand.toplevel.outer.right) | strong,
                align_by(self, element, 'horizontal'),
            )
            h_expand = expander(None, self, h_expand.toplevel)
        else:
            self.constrain(
                outer.left + left == element.outer.left,
                outer.right       == element.outer.right + right,
            )
        if expandflags in ('both', 'vertical'):
            self.constrain(
                outer.top   + top  <= element.outer.top,
                outer.bottom       >= element.outer.bottom + bottom,
                v_expand == outer.bottom - outer.top,
                (outer.top    == v_expand.toplevel.outer.top)    | strong,
                (outer.bottom == v_expand.toplevel.outer.bottom) | strong,
                align_by(self, element, 'vertical'),
            )
            v_expand = expander(None, self, v_expand.toplevel)
        else:
            self.constrain(
                outer.top  + top  == element.outer.top,
                outer.bottom      == element.outer.bottom + bottom,
            )
        element.feed(layout, h_expand, v_expand)
        layout.update(self)

    def draw(self, screen):
        background = self.config.get('background')
        if background:
            screen(background, self.outer.value)
        self.element.draw(screen)

class Root(object):
    def __init__(self, config, element):
        self.config = config
        self.element = element
        self.inner = Box()
        self.outer = self.inner
        self.constraints = [], ()

    def constrain(self, *rules):
        self.constraints[0].extend(rules)

    def copy(self):
        return self.__class__(self.config, self.element)

    def feed(self, layout, h_expand=None, v_expand=None):
        outer = self.outer
        element = self.element
        align_by = self.config.get('align_by', baseline)
        h_expand = expander(h_expand, self)
        v_expand = expander(v_expand, self)
        element.feed(layout, h_expand, v_expand)
        self.constrain(
            outer.left  <= element.outer.left,
            outer.right >= element.outer.right,
            outer.top    <= element.outer.top,
            outer.bottom >= element.outer.bottom,
            align_by(self, element, 'vertical'),
            align_by(self, element, 'horizontal'),
        )
        layout.update(self)
  
    def draw(self, screen):
        background = self.config.get('background')
        if background:
            screen(background, self.outer.value)
        self.element.draw(screen)
###class Spacer(object):
###    placement = None
###    def __init__(self, min_size, segment=None, target=None):
###        self.min_size = min_size
###        self.segment = segment
###        self.target = target
###
###    def dup(self):
###        res = self.__class__(
###            self.min_size,
###            self.segment,
###            self.target
###        )
###        return res
###
###    def layout0(self):
###        return self.min_size, 0
###
###    def layout1(self, space):
###        pass
###
###    def draw(self, screen):
###        pass
###
###    def __iter__(self):
###        return iter([])
###
###class Pad(object):
###    background = None
###    placement = None
###    def __init__(self, padding, content, segment=None, target=None):
###        self.padding = padding
###        self.content = content
###        self.segment = segment
###        self.target = target
###
###    def dup(self):
###        res = self.__class__(
###            self.padding,
###            self.content.dup(),
###            self.segment,
###            self.target
###        )
###        return res
###
###    def layout0(self):
###        self.min_size, extend = self.content.layout0()
###        l,t,r,b = self.padding
###        self.min_size += (l+r, t+b)
###        return self.min_size, 0
###
###    def layout1(self, space):
###        self.geometry = space
###        space = space.inset(self.padding)
###        self.content.layout1(space)
###
###    def draw(self, screen):
###        if self.background:
###            screen(self.background, self.geometry)
###        self.content.draw(screen)
###
###    def __iter__(self):
###        return iter([self.content])


def baseline(a, b, mode):
    if mode == 'column':
        return a.inner.left   == b.inner.left
    if mode == 'row':
        return a.inner.bottom == b.inner.bottom
    if mode == 'horizontal':
        return (a.outer.left == b.outer.left) | medium | 3.0
    if mode == 'vertical':
        return (a.outer.bottom == b.outer.bottom) | medium | 3.0

#def mathline(left, right, mode):
#    if mode == 0:
#        return [
#            left.outer.b.x == right.outer.a.x,
#            left.inner.a.y + left.inner.b.y == right.inner.a.y + right.inner.b.y,
#        ]
#    if mode == 1:
#        return [
#            left.outer.b.y == right.outer.a.y,
#            left.inner.a.x + left.inner.b.x == right.inner.a.x + right.inner.b.x,
#        ]
#
def center(a, b, mode):
    if mode == 'column':
        return a.outer.left + a.outer.right  == b.outer.left + b.outer.right
    if mode == 'row':
        return a.outer.top  + a.outer.bottom == b.outer.top  + b.outer.bottom
    if mode == 'horizontal':
        return (a.outer.left + a.outer.right == b.outer.left + b.outer.right) | medium | 3.0
    if mode == 'vertical':
        return (a.outer.top + a.outer.bottom == b.outer.top + b.outer.bottom) | medium | 3.0

#    if mode == 0:
#        return [
#            left.outer.b.x == right.outer.a.x,
#            left.outer.a.y + left.outer.b.y == right.outer.a.y + right.outer.b.y,
#        ]
#    if mode == 1:
#        return [
#            left.outer.b.y == right.outer.a.y,
#            left.outer.a.x + left.outer.b.x == right.outer.a.x + right.outer.b.x,
#        ]
#
##    if i == 0:
##        return [
##            parent.inner.b.y == element.inner.b.y,
##
##        ]
##    if i == 1:
##        return parent.inner.a.x == element.inner.a.x
        
#    
##
##class Label(Element):
##    def __init__(self, config, source):
##        Element.__init__(self)
##        self.config = config
##        self.source = source
##
##    def copy(self):
##        return self.__class__(self.config, self.source)
##
##    def feed(self, solver):
##        font = self.config['font']
##        self.surface = font(str(self.source))
##        size = self.surface.geometry.size
##
##        solver.add_constraint(self.x0 == self.x1)
##        solver.add_constraint(self.x2 == self.x3)
##        solver.add_constraint(self.x0 + size.x == self.x3)
##
##        solver.add_constraint(self.y0 + 16 == self.y3)
##        solver.add_constraint(self.y1 + 12 == self.y3)
##        solver.add_constraint(self.y2 + 5  == self.y3)
##
##        postprocess = self.config.get('postprocess')
##        if postprocess:
##            self.surface(postprocess)
##
##    def draw(self, screen):
##        surface = self.surface
##        surface.geometry.base = vec2(self.x1.value, self.y2.value - surface.baseline)
##        
##        background = self.config.get('background')
##        screen(surface)
##        if background:
##            screen(background, self.clearing)
##
##
##class Element(object):
##    next_num = 0
##
##    def __init__(self):
##        self.num = Element.next_num
##        Element.next_num += 1
##        self.x0 = ConstraintVariable('%i.x0' % self.num)
##        self.x1 = ConstraintVariable('%i.x1' % self.num)
##        self.x2 = ConstraintVariable('%i.x2' % self.num)
##        self.x3 = ConstraintVariable('%i.x3' % self.num)
##        self.y0 = ConstraintVariable('%i.y0' % self.num)
##        self.y1 = ConstraintVariable('%i.y1' % self.num)
##        self.y2 = ConstraintVariable('%i.y2' % self.num)
##        self.y3 = ConstraintVariable('%i.y3' % self.num)
##
##    @property
##    def clearing(self):
##        p0 = vec2(self.x0.value, self.y0.value)
##        p3 = vec2(self.x3.value, self.y3.value)
##        return rectangle(p0, p3-p0)
##
##    @property
##    def core(self):
##        p1 = vec2(self.x1.value, self.y1.value)
##        p2 = vec2(self.x2.value, self.y2.value)
##        return rectangle(p1, p2-p1)
##
##def left(parent, element):
##    return parent.x1 == element.x1
##
##def right(parent, element):
##    return parent.x2 == element.x2
##
##def center(parent, element):
##    return parent.x1 + parent.x2 == element.x1 + element.x2
##
##def baseline(parent, element):
##    return parent.y2 == element.y2
##
##class Row(Element):
##    def __init__(self, config, elements):
##        Element.__init__(self)
##        self.config = config
##        self.elements = elements
##
##    def copy(self):
##        return self.__class__(self.config, [element.copy() for element in self.elements])
##
##    def __getitem__(self, index):
##        return self.elements[index]
##
##    def __len__(self):
##        return len(self.elements)
##
##    def __iter__(self):
##        return iter(self.elements)
##
##    def feed(self, solver):
##        last = None
##        align_by = self.config.get('align_by', baseline)
##        expand = self.config.get('expand', vec2(0,0))
##
##        solver.add_constraint((self.x0 + expand.x == self.x3) | strong)
##        solver.add_constraint((self.y0 + expand.y == self.y3) | strong)
##        solver.add_constraint((self.x1 + expand.x == self.x2) | weak)
##        solver.add_constraint((self.y1 + expand.y == self.y2) | weak)
##
##        for element in self:
##            element.feed(solver)
##
##            solver.add_constraint(self.y0 <= element.y0)
##            solver.add_constraint(self.y1 <= element.y1)
##            solver.add_constraint(element.y2 <= self.y2)
##            solver.add_constraint(element.y3 <= self.y3)
##
##            if last != None:
##                solver.add_constraint(last.x3 <= element.x0)
##            last = element
##
##            solver.add_constraint(align_by(self, element) | strong)
##
##        if len(self) > 0:
##            solver.add_constraint(self.x0 <= self[0].x0)
##            solver.add_constraint(self.x1 <= self[0].x1)
##
##            solver.add_constraint(self[-1].x2 <= self.x2)
##            solver.add_constraint(self[-1].x3 <= self.x3)
##
#
##
##class Column(Element):
##    def __init__(self, config, elements):
##        Element.__init__(self)
##        self.config = config
##        self.elements = elements
##
##    def copy(self):
##        return self.__class__(self.config, [element.copy() for element in self.elements])
##
##    def __getitem__(self, index):
##        return self.elements[index]
##
##    def __len__(self):
##        return len(self.elements)
##
##    def __iter__(self):
##        return iter(self.elements)
##
##    def feed(self, solver):
##        last = None
##        align_by = self.config.get('align_by', left)
##        expand = self.config.get('expand', vec2(0,0))
##
##        solver.add_constraint((self.x0 + expand.x == self.x3) | strong)
##        solver.add_constraint((self.y0 + expand.y == self.y3) | strong)
##        solver.add_constraint((self.x1 + expand.x == self.x2) | weak)
##        solver.add_constraint((self.y1 + expand.y == self.y2) | weak)
##
##        for element in self:
##            element.feed(solver)
##
##            solver.add_constraint(self.x0 <= element.x0)
##            solver.add_constraint(self.x1 <= element.x1)
##            solver.add_constraint(element.x2 <= self.x2)
##            solver.add_constraint(element.x3 <= self.x3)
##
##            if last != None:
##                solver.add_constraint(last.y3 <= element.y0)
##            last = element
##
##            solver.add_constraint(align_by(self, element) | strong)
##
##        if len(self) > 0:
##            solver.add_constraint(self.y0 <= self[0].y0)
##            solver.add_constraint(self.y1 <= self[0].y1)
##
##            solver.add_constraint(self[-1].y2 <= self.y2)
##            solver.add_constraint(self[-1].y3 <= self.y3)
##
##    def draw(self, screen):
##        background = self.config.get('background')
##        if background:
##            screen(background, self.clearing)
##        for element in self:
##            element.draw(screen)
###
###class Column(object):
###    align = 0.0, 0.5
###    background = None
###    placement = 'y'
###    def __init__(self, children, segment=None, target=None):
###        self.children = children
###        self.segment = segment
###        self.target = target
###
###    def dup(self):
###        res = self.__class__(
###            [child.dup() for child in self.children],
###            self.segmelt,
###            self.target
###        )
###        res.align = self.align
###        res.background = self.background
###        return res
###
###    def layout0(self):
###        self.offsets = []
###        self.min_size = vec2(0, 0)
###        current = 0
###        for child in self.children:
###            self.offsets.append(current)
###            min_size, extend = child.layout0()
###            current += min_size.y
###            self.min_size.x = max(self.min_size.x, min_size.x)
###            self.min_size.y = current
###        self.offsets.append(current)
###        self.geometry = rectangle(vec2(0, 0), vec2(*self.min_size))
###        return self.min_size, 0
###
###    def layout1(self, space):
###        position = self.geometry.move_inside(space, *self.align)
###        for index, child in enumerate(self.children):
###            y0 = self.offsets[index]
###            y1 = self.offsets[index+1]
###            subspace = rectangle(
###                position.base + (0, y0),
###                vec2(position.size.x, y1-y0)
###            )
###            child.layout1(subspace)
###
###    def draw(self, screen):
###        if self.background:
###            screen(self.background, self.geometry)
###        for child in self.children:
###            child.draw(screen)
###
###    def __iter__(self):
###        return iter(self.children)
###
###class Row(object):
###    align = 0.0, 0.5
###    background = None
###    placement = 'x'
###    def __init__(self, children, segment=None, target=None):
###        self.children = children
###        self.segment = segment
###        self.target = target
###
###    def dup(self):
###        res = self.__class__(
###            [child.dup() for child in self.children],
###            self.segment,
###            self.target
###        )
###        res.align = self.align
###        res.background = self.background
###        return res
###
###    def layout0(self):
###        self.offsets = []
###        self.min_size = vec2(0, 0)
###        current = 0
###        for child in self.children:
###            self.offsets.append(current)
###            min_size, extend = child.layout0()
###            current += min_size.x
###            self.min_size.y = max(self.min_size.y, min_size.y)
###            self.min_size.x = current
###        self.offsets.append(current)
###        self.geometry = rectangle(vec2(0, 0), vec2(*self.min_size))
###        return self.min_size, 0
###
###    def layout1(self, space):
###        position = self.geometry.move_inside(space, *self.align)
###        for index, child in enumerate(self.children):
###            x0 = self.offsets[index]
###            x1 = self.offsets[index+1]
###            subspace = rectangle(
###                position.base + (x0, 0),
###                vec2(x1-x0, position.size.y)
###            )
###            child.layout1(subspace)
###
###    def draw(self, screen):
###        if self.background:
###            screen(self.background, self.geometry)
###        for child in self.children:
###            child.draw(screen)
###
###    def __iter__(self):
###        return iter(self.children)
###
####class List(object):
####    background = None
####    padding = 0, 0, 0, 0
####    spacing = 0
####    min_size = vec2(32, 0)
####    extend = 0
####    align = 0.5, 0.5
####    def __init__(self, children, target=None, slot=None):
####        self.children = children
####        self.target = target
####        self.slot = slot
####
####    def dup(self):
####        return self.__class__(
####            list(child.dup() for child in self.children),
####            self.target,
####            self.slot
####        )
####
####    def layout0(self, font):
####        self.offsets = []
####        min_size = vec2(0, 0)
####        self.layout_extend = 0
####        self._extend = 0
####        current = 0
####        for child in self.children:
####            stop = current
####            current += self.spacing if len(self.offsets) > 0 else 0
####            self.offsets.append((stop, current))
####            size, extend = child.layout0(font)
####            current += size.y
####            min_size.x = max(min_size.x, size.x)
####            min_size.y = current
####            self._extend |= extend
####        self.offsets.append((current, current))
####        self.outer = rectangle(vec2(0,0), min_size).offset(self.padding)
####        self._min_size0 = self.min_size.maximum(self.outer.size)
####        self._min_size1 = min_size
####        return self._min_size0, self._extend | self.extend
####
####    def layout1(self, space):
####        self.outer.size = space.size.mix(self._min_size0, self._extend | self.extend)
####        self.outer.move_inside(space, *self.align)
####        outinner = self.outer.inset(self.padding)
####        base, size = outinner
####        inner = rectangle(vec2(0, 0), outinner.size.mix(self._min_size1, self._extend))
####        base, size = inner.move_inside(outinner, *self.align)
####        for index, child in enumerate(self.children):
####            start = self.offsets[index  ][1]
####            stop  = self.offsets[index+1][0]
####            subspace = rectangle(
####                vec2(base.x, base.y + start),
####                vec2(size.x, stop - start)
####            )
####            child.layout1(subspace)
####
####    def draw(self, screen):
####        if self.background:
####            screen(self.background, self.outer)
####        for child in self.children:
####            child.draw(screen)
####
####    def locate_offset(self, index):
####        offset0 = self.offsets[0][0]
####        offset1 = None
####        for i, child in enumerate(self.children):
####            if child.slot != None:
####                if child.slot < index:
####                    offset0 = self.offsets[i+1][0]
####                if index <= child.slot and offset1 == None:
####                    offset1 = self.offsets[i][1]
####        if offset1 == None:
####            offset1 = self.offsets[i+1][1]
####        return offset0, offset1
####
####    def selection(self, start, stop):
####        inner = self.outer.inset(self.padding)
####        y0 = self.locate_offset(start)[1] - 1
####        y1 = self.locate_offset(stop)[0] + 1
####        base = inner.base + (-1, y0)
####        size = vec2(inner.size.x + 1, y1 - y0)
####        return rectangle(base, size)
####
####    def caret(self, index):
####        inner = self.outer.inset(self.padding)
####        y0 = self.locate_offset(index)[0] - 1
####        y1 = self.locate_offset(index)[1] + 1
####        base = inner.base + (-1, y0)
####        size = vec2(inner.size.x + 1, y1 - y0)
####        return rectangle(base, size)
####
####    def nearest_index(self, position):
####        inner = self.outer.inset(self.padding)
####        delta = position - inner.base
####        d0 = abs(delta.y - 0)
####        index = 0
####        for index, (offset0, offset1) in enumerate(self.offsets):
####            d1 = abs(delta.y - offset0)
####            if d0 < d1:
####                return index - 1
####            d0 = abs(delta.y - offset1)
####        return index
####
####    def nearest_caret(self, position):
####        nearest = self.nearest_index(position)
####        slot = 0
####        for index, child in enumerate(self.children):
####            if nearest <= index:
####                return slot
####            if child.slot != None:
####                slot = child.slot + 1
####        return slot + 1
####
###
###class Spacer(object):
###    placement = None
###    def __init__(self, min_size, segment=None, target=None):
###        self.min_size = min_size
###        self.segment = segment
###        self.target = target
###
###    def dup(self):
###        res = self.__class__(
###            self.min_size,
###            self.segment,
###            self.target
###        )
###        return res
###
###    def layout0(self):
###        return self.min_size, 0
###
###    def layout1(self, space):
###        pass
###
###    def draw(self, screen):
###        pass
###
###    def __iter__(self):
###        return iter([])
###
###class Pad(object):
###    background = None
###    placement = None
###    def __init__(self, padding, content, segment=None, target=None):
###        self.padding = padding
###        self.content = content
###        self.segment = segment
###        self.target = target
###
###    def dup(self):
###        res = self.__class__(
###            self.padding,
###            self.content.dup(),
###            self.segment,
###            self.target
###        )
###        return res
###
###    def layout0(self):
###        self.min_size, extend = self.content.layout0()
###        l,t,r,b = self.padding
###        self.min_size += (l+r, t+b)
###        return self.min_size, 0
###
###    def layout1(self, space):
###        self.geometry = space
###        space = space.inset(self.padding)
###        self.content.layout1(space)
###
###    def draw(self, screen):
###        if self.background:
###            screen(self.background, self.geometry)
###        self.content.draw(screen)
###
###    def __iter__(self):
###        return iter([self.content])
###
###class Label(object):
###    align = 0.0, 0.5
###    postprocess = None
###    placement = 'text'
###    def __init__(self, font, source='', segment=None, target=None):
###        self.font = font
###        self.source = source
###        self.segment = segment
###        self.target = target
###
###    def dup(self):
###        res = self.__class__(
###            self.font,
###            self.source,
###            self.segment,
###            self.target
###        )
###        res.align = self.align
###        res.postprocess = self.postprocess
###        return res
###
###    def layout0(self):
###        self.surface = self.font(str(self.source))
###        self.geometry = self.surface.geometry
###        if self.postprocess:
###            self.surface(self.postprocess)
###        return self.surface.geometry.size, 0
###
###    def layout1(self, space):
###        self.surface.geometry.move_inside(space, *self.align)
###
###    def draw(self, screen):
###        screen(self.surface)
###
###    def selection(self, start, stop):
###        return self.surface.selection(start, stop)
###
###    def nearest_caret(self, position):
###        return self.surface.nearest_caret(position)
###
###    def __iter__(self):
###        return iter([])
###
###def seg_selection_x(element, start, stop):
###    assert element.segment
###    field, index = element.segment
###    if start <= index <= stop:
###        start = clamp(index, index+1, start)
###        stop = clamp(index, index+1, stop)
###        x0 = (0, element.geometry.size.x)[start - index]
###        x1 = (0, element.geometry.size.x)[stop - index]
###        return rectangle(
###            element.geometry.base + (x0-1, -1),
###            vec2(x1-x0+2, element.geometry.size.y+2)
###        )
###
###def seg_selection_y(element, start, stop):
###    assert element.segment
###    field, index = element.segment
###    if start-1 <= index <= stop:
###        start = clamp(index, index+1, start)
###        stop = clamp(index, index+1, stop)
###        y0 = (0, element.geometry.size.y)[start - index]
###        y1 = (0, element.geometry.size.y)[stop - index]
###        return rectangle(
###            element.geometry.base + (-1, y0-1),
###            vec2(element.geometry.size.x+2, y1-y0+2)
###        )
###
###def seg_nearest_caret_x(element, position):
###    assert element.segment
###    field, index = element.segment
###    delta = position - element.geometry.base
###    d0 = abs(delta.x - 0)
###    d1 = abs(delta.x - element.geometry.size.x)
###    if d0 < d1:
###        return index, d0
###    else:
###        return index+1, d1
###
###def seg_nearest_caret_y(element, position):
###    assert element.segment
###    field, index = element.segment
###    delta = position - element.geometry.base
###    d0 = abs(delta.y - 0)
###    d1 = abs(delta.y - element.geometry.size.y)
###    if d0 < d1:
###        return index, d0
###    else:
###        return index+1, d1
###
###def segs_nearest_caret_x(elements, position):
###    index = 0
###    d0 = -1
###    for element in elements:
###        i, d1 = seg_nearest_caret_x(element, position)
###        if d0 == -1 or d1 < d0:
###            index = i
###            d0 = d1
###    return index, d0
###
###def segs_nearest_caret_y(elements, position):
###    index = 0
###    d0 = -1
###    for element in elements:
###        i, d1 = seg_nearest_caret_y(element, position)
###        if d0 == -1 or d1 < d0:
###            index = i
###            d0 = d1
###    return index, d0
###
###def find_target(element, field):
###    if element.target == field:
###        return element
###    for child in element:
###        match = find_target(child, field)
###        if match != None:
###            return match
###
###def find_segments(element, target):
###    for child in element:
###        if child.segment and child.segment[0] == target:
###            yield child
###        else:
###            for match in find_segments(child, target):
###                yield match
###
###def pick(element, position):
###    if element.target != None and element.geometry.inside(position):
###        yield element
###    for child in element:
###        for match in pick(child, position):
###            yield match
###
####class Label(object):
####    background = None
####    padding = 0, 0, 0, 0
####    extend = 0
####    min_size = vec2(8, 12)
####    align = 0.5, 0.5
####    blend = None
####    def __init__(self, target='', slot=None):
####        self.target = target
####        self.slot = slot
####
####    def dup(self):
####        return self.__class__(self.target, self.slot)
####
####    def layout0(self, font):
####        self.surface = font(str(self.target))
####        self.outer = self.surface.geometry.offset(self.padding)
####        self._min_size = self.min_size.maximum(self.outer.size)
####        self._extend = self.extend
####        if self.blend:
####            self.surface(self.blend)
####        return self._min_size, self._extend
####
####    def layout1(self, space):
####        self.outer.size = space.size.mix(self._min_size, self._extend | self.extend)
####        self.outer.move_inside(space, *self.align)
####        outinner = self.outer.inset(self.padding)
####        self.surface.geometry.move_inside(outinner, *self.align)
####
####    def draw(self, screen):
####        if self.background:
####            screen(self.background, self.outer)
####        screen(self.surface)
####
####    def selection(self, start, stop):
####        return self.surface.selection(start, stop)
####
####    def caret(self, index):
####        if len(self.target) == 0:
####            caret = rectangle(vec2(0, 0), vec2(1, 8))
####            caret.move_inside(self.outer.inset(self.padding), *self.align)
####            return caret
####        return self.surface.caret(index)
####
####    def nearest_caret(self, position):
