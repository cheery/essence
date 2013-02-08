from essence2 import vec2, rgba, rectangle, clamp
from essence2.ui.layoutengine import variable, Box, Layout, Config, AtomicFrame, EnclosingFrame, ContainerFrame, Intron
from essence2.ui.layoutengine import required, strong, medium, weak

class Space(AtomicFrame):
    def feed(self, layout):
        self.feed_maximizer()
        box = self.inset
        hfork = self.hfork
        vfork = self.vfork
        width = self.config['width']
        height = self.config['height']
        self.constrain(
            box.left + width  <= box.right,
            box.top  + height <= box.bottom,
            (box.left + width  == box.right)  | weak,
            (box.top  + height == box.bottom) | weak,
            vfork.low == box.top,
            vfork.middle*2 == box.top + box.bottom,
            vfork.high == box.bottom,
            hfork.low == box.left,
            hfork.middle*2 == box.left + box.right,
            hfork.high == box.right,
        )
        layout.update(self)

    def draw(self, screen):
        background = self.config.get('background')
        if background:
            screen(background, self.box.value)
 
class Label(AtomicFrame):
    def __init__(self, config, source):
        self.source = source
        AtomicFrame.__init__(self, config)

    def copy(self):
        return self.__class__(self.config, self.source)

    def feed(self, layout):
        box = self.inset
        hfork = self.hfork
        vfork = self.vfork
        font = self.config['font']
        postprocess = self.config.get('postprocess')
        self.surface = font(str(self.source))
        if postprocess:
            self.surface(postprocess)
        width, height = self.surface.geometry.size
        self.constrain(
            box.left + width  == box.right,
            box.top  + height == box.bottom,
            hfork.low == box.left,
            hfork.middle*2 == box.left + box.right,
            hfork.high == box.right,
            vfork.low == box.top,
            vfork.middle == box.top + self.surface.mathline,
            vfork.high == box.top + self.surface.baseline,
        )
        layout.update(self)

    def draw(self, screen):
        self.surface.geometry.base = self.inset.value.base
        screen(self.surface)

    def selection(self, start, stop, base=0):
        if start <= base + len(self.source) and base <= stop:
            start = clamp(0, len(self.source), start - base)
            stop  = clamp(0, len(self.source), stop  - base)
            (x0, y0), (w0, h0) = self.surface.selection(start, stop)
            (x1, y1), (w1, h1) = self.box.value
            return rectangle(vec2(x0, y1), vec2(w0, h1))
    

class Row(ContainerFrame):
    def feed(self, layout):
        maximize = self.feed_maximizer(ignore='x')
        spacing = self.config.get('spacing', 0)
        box = self.inset
        hfork = self.hfork
        vfork = self.vfork
        valign = self.config['valign']
        last = None
        for element in self:
            element.maximize = maximize
            element.feed(layout)
            self.constrain(
                box.top <= element.box.top,
                element.box.bottom <= box.bottom,
                valign(self, element, 'y'),

                vfork.low <= element.vfork.low,
                vfork.high >= element.vfork.high,
                (vfork.middle == element.vfork.middle) | weak,
            )
            if last is not None:
                self.constrain(
                    last.box.right + spacing == element.box.left,
                )
            last = element
        if len(self) % 2 == 1:
            midfork = self[len(self)/2].hfork.middle
        else:
            midfork = (self[len(self)/2-1].box.right + self[len(self)/2].box.left) / 2
        self.constrain(
            (vfork.low == vfork.high) | weak,
            (hfork.low == hfork.high) | weak,
            hfork.low == self[0].hfork.low,
            (hfork.middle == midfork),
            hfork.high == self[-1].hfork.high,
            (box.left == box.right)  | weak,
            (box.top == box.bottom) | weak,
            box.left <= self[0].box.left,
            self[-1].box.right <= box.right,
        )
        layout.update(self)

class Column(ContainerFrame):
    def feed(self, layout):
        maximize = self.feed_maximizer(ignore='y')
        spacing = self.config.get('spacing', 0)
        box = self.inset
        hfork = self.hfork
        vfork = self.vfork
        halign = self.config['halign']
        last = None
        for element in self:
            element.maximize = maximize
            element.feed(layout)
            self.constrain(
                box.left <= element.box.left,
                element.box.right <= box.right,
                halign(self, element, 'x'),
                hfork.low <= element.hfork.low,
                hfork.high >= element.hfork.high,
                (hfork.middle == element.hfork.middle) | weak,
            )
            if last is not None:
                self.constrain(
                    last.box.bottom + spacing == element.box.top,
                )
            last = element
        if len(self) % 2 == 1:
            midfork = self[len(self)/2].vfork.middle
        else:
            midfork = (self[len(self)/2-1].box.bottom + self[len(self)/2].box.top) / 2
        self.constrain(
            (hfork.low == hfork.high) | weak,
            (vfork.low == vfork.high) | weak,
            vfork.low == self[0].vfork.low,
            (vfork.middle == midfork),
            vfork.high == self[-1].vfork.high,
            (box.left == box.right)  | weak,
            (box.top == box.bottom) | weak,
            box.top <= self[0].box.top,
            self[-1].box.bottom <= box.bottom,
        )
        layout.update(self)

class Border(EnclosingFrame):
    nofork = True
    def feed(self, layout):
        maximize = self.feed_maximizer()
        box = self.inset
        halign = self.config['halign']
        valign = self.config['valign']
        self.element.maximize = maximize
        self.element.feed(layout)
        self.constrain(
            box.left <= self.element.box.left,
            self.element.box.right <= box.right,
            box.top <= self.element.box.top,
            self.element.box.bottom <= box.bottom,
            (box.left == box.right )  | weak,
            (box.top == box.bottom ) | weak,
            halign(self, self.element, 'x'),
            valign(self, self.element, 'y'),
        )
        layout.update(self)

    @property
    def hfork(self):
        return self.element.hfork

    @property
    def vfork(self):
        return self.element.vfork

class Root(EnclosingFrame):
    nofork = True
    def __init__(self, config, element):
        EnclosingFrame.__init__(self, config, element)
        self.scroll = vec2(0,0)
        self.viewport = vec2(100, 100)
        self.layout = None

    def feed(self, layout):
        box = self.inset
        self.maximize = box, variable(self, 'horizontal'), box, variable(self, 'vertical')
        self.element.maximize = self.maximize
        self.element.feed(layout)
        self.layout = layout
        self.refresh()

    def refresh(self):
        box = self.box
        inset = self.inset
        self.constrain(
            inset.left == self.element.box.left,
            inset.top  == self.element.box.top,
            (self.element.box.right <= inset.right),
            (self.element.box.bottom <= inset.bottom),

            box.left == self.scroll.x, # scrolling variables
            box.top  == self.scroll.y,
            box.right - box.left >= self.viewport.x,
            box.bottom - box.top >= self.viewport.y,
        )
        self.layout.update(self)

    def move(self, scroll):
        (w,h) = self.box.value.size
        self.scroll = vec2(
            clamp(self.viewport.x - w, 0, scroll.x),
            clamp(self.viewport.y - h, 0, scroll.y),
        )
