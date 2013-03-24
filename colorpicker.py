from argon import hsva, rgba
from box import Box
white = rgba(255,255,255)
black = rgba(0,0,0)

class Colorpicker(Box):
    def __init__(self, argon):
        self.hue = 0.0
        self.saturation = 0.0
        self.value = 1.0
        self.gradient = argon.image('hue-saturation-360x256.png')
        Box.__init__(self, 0, 0,  480+20, 256+20)
        self.which = -1

    @property
    def rgba(self):
        return hsva(self.hue, self.saturation, self.value).rgba

    def update(self):
        self.major   = Box(self.left+10+0,   self.top+10, 360, 256)
        self.minor   = Box(self.left+10+360, self.top+10, 30,  256)
        self.preview = Box(self.left+10+390, self.top+10, 90,  256)

    def render(self, argon):
        self.update()
        v1 = hsva(self.hue, self.saturation, 1.0).rgba
        x0, y0 = self.major.interpolate((self.hue/360.0, self.saturation))
        x1, y1 = self.minor.interpolate((0, 1-self.value))
        argon.render([
            (self.rect, black, argon.plain),
            (self.major.rect, white.mix(black, self.value), self.gradient),
            (self.minor.rect, (v1, v1, black, black), argon.plain),
            (self.preview.rect, self.rgba, argon.plain),
            ((x0, y0, 1, 1), black, argon.plain),
            ((x1, y1, 30, 1), black, argon.plain),
        ])

    def setcolor(self, pos, which):
        if which == 0:
            i, j = self.major.point_interval(pos)
            self.hue        = i * 360.0
            self.saturation = j
        elif which == 1:
            i, j = self.minor.point_interval(pos)
            self.value = 1 - j

    def mousedown(self, button, pos):
        if button == 1:
            if self.major.point_inside(pos):
                self.setcolor(pos, 0)
                self.which = 0
            if self.minor.point_inside(pos):
                self.setcolor(pos, 1)
                self.which = 1

    def mouseup(self, button, pos):
        self.which = -1

    def mousemotion(self, pos, vel):
        self.setcolor(pos, self.which)
