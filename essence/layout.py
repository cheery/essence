from essence.document import node
from casuarius import Solver, ConstraintVariable
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

    def highlight(self, start, stop):
        left, top, width, height = self.area
        offset0 = self.label.offsets[0 if start is None else start]
        offset1 = self.label.offsets[-1 if stop is None else stop]
        return (left + offset0, top, offset1 - offset0 + 1, height)

    def __call__(self, screen):
        screen(self.label, self.area)

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
    
    def __call__(self, screen):
        if self.decorator:
            screen(self.decorator, self.area)
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

    def satisfy(self, rule):
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