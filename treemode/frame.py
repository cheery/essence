from argon import rgba, Texture, Framebuffer

class Frame(object):
    def __init__(self, (left, top, width, height), contents):
        self.left   = left
        self.top    = top
        self.width  = width
        self.height = height
        self.contents = contents
        self.texture = Texture.empty()
        self.texture.resize(self.width, self.height)
        self.framebuffer = Framebuffer()
        self.framebuffer.configure(self.texture)
        self.dirty = True
        self.scroll = (0,0)
        self.overlays = set()

    @property
    def rect(self):
        return self.left, self.top, self.width, self.height

    def update(self, argon):
        texture = self.texture
        if texture.width != self.width or texture.height != self.height:
            texture.resize(self.width, self.height)
        self.framebuffer.bind()
        argon.use_program((self.width, self.height))
        argon.clear(rgba(0x30,0x30,0x30))
        self.contents.measure(None)
        self.contents.arrange(None, self.scroll)
        self.contents.render(argon)
        argon.use_program(argon.resolution)
        self.framebuffer.unbind()

    def render(self, argon):
        if self.dirty:
            self.update(argon)
            self.dirty = False
            for overlay in self.overlays:
                overlay.dirty = True
        argon.render_rectangle(self.rect, self.texture)
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
        self.framebuffer = Framebuffer()
        self.framebuffer.configure(self.texture)
        self.dirty = True

    def update(self, argon):
        texture = self.texture
        if texture.width != self.frame.width or texture.height != self.frame.height:
            texture.resize(self.frame.width, self.frame.height)
        self.framebuffer.bind()
        argon.use_program((self.frame.width, self.frame.height))
        self.renderer(argon)
        argon.use_program(argon.resolution)
        self.framebuffer.unbind()

    def render(self, argon):
        if self.dirty:
            self.update(argon)
            self.dirty = False
        argon.render_rectangle(self.frame.rect, self.texture)

    def free(self):
        self.texture.free()
        self.framebuffer.free()
        self.frame.overlays.remove(self)
