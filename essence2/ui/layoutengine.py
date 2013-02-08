from essence2 import vec2, rgba, rectangle, clamp
from casuarius import (
    ConstraintVariable, Solver, ExplainedCassowaryError,
    required, strong, medium, weak,
    Strength, SymbolicWeight,
)
from os import urandom
from weakref import WeakValueDictionary

class Variable(ConstraintVariable):
    __slots__ = 'owner', 'which'
    def init(self, owner, which=None):
        self.owner = owner
        self.which = which

def variable(owner, which=None):
    var = Variable(urandom(4).encode('hex'))
    var.init(owner, which)
    return var

class Box(object):
    def __init__(self, left=None, top=None, right=None, bottom=None):
        self.left   = left   if left   else variable(self, 'left')
        self.top    = top    if top    else variable(self, 'top')
        self.right  = right  if right  else variable(self, 'right')
        self.bottom = bottom if bottom else variable(self, 'bottom')

    def __iter__(self):
        return iter((self.left, self.top, self.right, self.bottom))

    @property
    def value(self):
        left, top, right, bottom = self
        p0 = vec2(left.value, top.value)
        p1 = vec2(right.value, bottom.value)
        return rectangle(p0, p1-p0)

    def inset(self, (left, top, right, bottom)):
        return Box(
            self.left + left,
            self.top  + top,
            self.right  - right,
            self.bottom - bottom,
        )

class Fork(object):
    def __init__(self):
        self.low    = variable(self,    'low')
        self.middle = variable(self, 'middle')
        self.high   = variable(self,   'high')

class Layout(object):
    def __init__(self):
        self.solver = Solver()
        self.introns = WeakValueDictionary()

    def update(self, element):
        self.solver.autosolve = False
        for constraint in element.constraints[1]:
            self.solver.remove_constraint(constraint)
        for constraint in element.constraints[0]:
            self.solver.add_constraint(constraint)
        element.constraints = [], element.constraints[0]
        self.solver.autosolve = True

    def add_intron(self, source, intron):
        self.introns[source] = intron

    def pop_intron(self, source):
        return self.introns.pop(source)

    def get_intron(self, source, otherwise=None):
        return self.introns.get(source, otherwise)

class Config(object):
    def __init__(self, link=None, **properties):
        self.link = link
        self.properties = properties

    def __contains__(self, key):
        if key in self.properties:
            return True
        elif self.link is None:
            return False
        else:
            return key in self.link

    def __getitem__(self, key):
        if key in self.properties:
            return self.properties[key]
        elif self.link is None:
            raise KeyError(key)
        else:
            return self.link[key]

    def get(self, key, otherwise=None):
        if key in self.properties:
            return self.properties[key]
        elif self.link is None:
            return otherwise
        else:
            return self.link.get(key, otherwise)

class Frame(object):
    nofork = False
    def __init__(self, config):
        self.config = config
        self.box = Box()
        if not self.nofork:
            self.hfork = Fork()
            self.vfork = Fork()
        self.inset = self.box.inset(self.config.get('padding', (0,0,0,0)))
        self.constraints = [], ()
        self.maximize = None
        self.horizontal = None
        self.vertical = None

    def copy(self):
        return self.__class__(self.config)

    def constrain(self, *rules):
        self.constraints[0].extend(rules)

    def feed_maximizer(self, ignore=''):
        box = self.box
        maximize = self.config.get('maximize', '')
        minimize = self.config.get('minimize', '')
        hbox, horizontal, vbox, vertical = self.maximize
        if 'x' in maximize and 'x' not in ignore:
            self.constrain(
                (box.left  == hbox.left)  | medium,
                (box.right == hbox.right) | medium,
                horizontal == box.right - box.left,
            )
        if ('x' in maximize and 'x' not in ignore) or 'x' in minimize:
            hbox = self.box
            self.horizontal = horizontal = variable(self, 'horizontal') if self.horizontal is None else self.horizontal
        if 'y' in maximize and 'y' not in ignore:
            self.constrain(
                (box.top    == vbox.top)    | medium,
                (box.bottom == vbox.bottom) | medium,
                vertical == box.bottom - box.top,
            )
        if ('y' in maximize and 'y' not in ignore) or 'y' in minimize:
            vbox = self.box
            self.vertical = vertical = variable(self, 'vertical') if self.vertical is None else self.vertical
        return hbox, horizontal, vbox, vertical

    def reset(self, layout):
        layout.update(self)
        for element in self:
            element.reset(layout)

class AtomicFrame(Frame):
    @property
    def dfs(self):
        yield self

    def __iter__(self):
        return iter(())

class EnclosingFrame(Frame):
    def __init__(self, config, element):
        self.element = element
        Frame.__init__(self, config)

    def dfs(self):
        yield self
        for descendant in self.element.dfs:
            yield descendant

    def copy(self):
        return self.__class__(self.config, self.element.copy())

    def draw(self, screen):
        background = self.config.get('background')
        if background:
            screen(background, self.box.value)
        self.element.draw(screen)

    def __iter__(self):
        return iter((self.element,))
 
class ContainerFrame(Frame):
    def __init__(self, config, elements):
        self.elements = elements
        Frame.__init__(self, config)

    @property
    def dfs(self):
        yield self
        for child in self:
            for descendant in child.dfs:
                yield descendant

    def copy(self):
        return self.__class__(self.config, [element.copy() for element in self])

    def draw(self, screen):
        background = self.config.get('background')
        if background:
            screen(background, self.box.value)
        for element in self:
            element.draw(screen)

    def __getitem__(self, index):
        return self.elements[index]

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

class Intron(object):
    def __init__(self, layout, generator, source):
        self.layout = layout
        self.generator = generator
        self.source = source
        self.element = None
        self.maximize = None
        self.box = Box()
        self.proxy = Box()
        self.hfork = Fork()
        self.vfork = Fork()
        self.horizontal = variable(self, 'horizontal')
        self.vertical = variable(self, 'vertical')
        self.constraints = [], ()
        self.layout.add_intron(self.source, self)
        self.rebuild()

    def copy(self):
        return self.__class__(self, self.config, self.layout, self.generator)

    def constrain(self, *rules):
        self.constraints[0].extend(rules)

    def feed(self, layout):
        hbox, horizontal, vbox, vertical = self.maximize
        box = self.box
        proxy = self.box
        hfork = self.hfork
        vfork = self.vfork
        self.constrain(
            box.left == self.element.box.left,
            box.right == self.element.box.right,
            box.top == self.element.box.top,
            box.bottom == self.element.box.bottom,
            horizontal == self.horizontal,
            vertical == self.vertical,
            (hbox.left == proxy.left) | strong,
            (hbox.right == proxy.right) | strong,
            (vbox.top == proxy.top) | strong,
            (vbox.bottom == proxy.bottom) | strong,
            hfork.low == self.element.hfork.low,
            hfork.middle == self.element.hfork.middle,
            hfork.high == self.element.hfork.high,
            vfork.low == self.element.vfork.low,
            vfork.middle == self.element.vfork.middle,
            vfork.high == self.element.vfork.high,
        )
        layout.update(self)

    def reset(self, layout):
        layout.update(self)

    def refresh(self):
        self.rebuild()
        self.feed(self.layout)

    def rebuild(self):
        if self.element:
            self.element.reset(self.layout)
        self.element = self.generator(self.source)
        self.element.maximize = self.proxy, self.horizontal, self.proxy, self.vertical
        self.element.feed(self.layout)

    def discard(self):
        self.layout.pop_intron(self.source)

    def draw(self, screen):
        self.element.draw(screen)
