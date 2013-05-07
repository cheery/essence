from argon import rgba, Texture, Framebuffer

class Frame(object):
    def __init__(self, (left, top, width, height), document, layouter):
        self.left = left
        self.top  = top
        self.width  = width
        self.height = height
        self.document = document
        self.box = layouter(document)
        self.texture = Texture.empty()
        self.texture.resize(self.width, self.height)
        self.framebuffer = Framebuffer(self.texture)
        self.dirty = True
        self.scroll = (0, 0)
        self.overlays = set()
        self.background_color = rgba(0x30, 0x30, 0x30)

    @property
    def rect(self):
        return self.left, self.top, self.width, self.height

    def update(self, argon):
        texture = self.texture
        if texture.width != self.width or texture.height != self.height:
            texture.resize(self.width, self.height)
        argon.render.output = self.framebuffer
        argon.render.bind()
        argon.clear(self.background_color)
        self.box.measure(None)
        self.box.arrange(None, self.scroll)
        self.box.render(argon)
        argon.render.output = argon
        argon.render.bind()

    def render(self, argon):
#        self.box.measure(None)
#        self.box.arrange(None, self.scroll)
#        self.box.render(argon)
        if self.dirty:
            self.update(argon)
            self.dirty = False
            for overlay in self.overlays:
                overlay.dirty = True
        argon.render.rectangle(self.rect, self.texture)
        for overlay in self.overlays:
            overlay.render(argon)

    def free(self):
        self.texture.free()
        self.framebuffer.free()

class Overlay(object):
    def __init__(self, frame, renderer):
        self.frame = frame
        self.frame.overlays.add(self)
        self.renderer = renderer
        self.texture = Texture.empty()
        self.texture.resize(frame.width, frame.height)
        self.framebuffer = Framebuffer(self.texture)
        self.dirty = True

    def update(self, argon):
        texture = self.texture
        if texture.width != self.frame.width or texture.height != self.frame.height:
            texture.resize(self.frame.width, self.frame.height)
        argon.render.output = self.framebuffer
        argon.render.bind()
        self.renderer(argon)
        argon.render.output = argon
        argon.render.bind()

    def render(self, argon):
        if self.dirty:
            self.update(argon)
            self.dirty = False
        argon.render.rectangle(self.frame.rect, self.texture)

    def free(self):
        self.texture.free()
        self.framebuffer.free()
        self.frame.overlays.remove(self)
