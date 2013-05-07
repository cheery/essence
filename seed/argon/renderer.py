from util import mix, in_module, rgba
from OpenGL.GL import *
from vertexformat import VertexFormat
from vertexstream import VertexStream
from texturecache import TextureCache
from patch9 import Patch9
from image import Image
from program import Program

image_empty = Image(1, 1, "\xff\xff\xff\xff")
white = rgba(255, 255, 255, 255)

fmt = VertexFormat([
    ('position', 2, GL_FALSE, GL_FLOAT),
    ('texcoord', 2, GL_FALSE, GL_FLOAT),
    ('color',    4, GL_TRUE,  GL_UNSIGNED_BYTE),
])

def quad_gradient(stream, (left, top, width, height), (s0,t0,s1,t1), (tl,tr,bl,br)):
    stream.vertex((left,       top),        (s0, t0), tuple(tl))
    stream.vertex((left,       top+height), (s0, t1), tuple(bl))
    stream.vertex((left+width, top),        (s1, t0), tuple(tr))
    stream.vertex((left+width, top),        (s1, t0), tuple(tr))
    stream.vertex((left,       top+height), (s0, t1), tuple(bl))
    stream.vertex((left+width, top+height), (s1, t1), tuple(br))

def quad_flat(stream, (left, top, width, height), (s0,t0,s1,t1), color):
    color = tuple(color)
    stream.vertex((left,       top),        (s0, t0), color)
    stream.vertex((left,       top+height), (s0, t1), color)
    stream.vertex((left+width, top),        (s1, t0), color)
    stream.vertex((left+width, top),        (s1, t0), color)
    stream.vertex((left,       top+height), (s0, t1), color)
    stream.vertex((left+width, top+height), (s1, t1), color)

def characters_flat(stream, font, (x,y), text, color):
    offset = 0
    sK = 1.0 / font.image.width
    tK = 1.0 / font.image.height
    for character in text:
        metrics = font.metadata.get(character)
        if metrics is None:
            continue
        if metrics['display']:
            width = metrics["width"]
            height = metrics["height"]
            hbearing = metrics["hbearing"]
            vbearing = -metrics["vbearing"]
            s0 = metrics["uv"]["s"]
            t0 = metrics["uv"]["t"]
            s1 = s0 + width*sK
            t1 = t0 + height*tK
            left = x + offset + hbearing
            top  = y + vbearing
            quad_flat(stream, (left, top, width, height), (s0,t0,s1,t1), color)
        offset += metrics["advance"]

def patch9_cell_flat(stream, patch9, x, y, (left, top, width, height), color):
    x0,s0 = patch9.gridpoint(0, x+0, width)
    x1,s1 = patch9.gridpoint(0, x+1, width)
    y0,t0 = patch9.gridpoint(1, y+0, height)
    y1,t1 = patch9.gridpoint(1, y+1, height)
    quad_flat(stream, (left+x0, top+y0, x1-x0, y1-y0), (s0, t0, s1, t1), color)

def patch9_cell_gradient(stream, patch9, x, y, (left, top, width, height), (c0,c1,c2,c3)):
    x0,s0 = patch9.gridpoint(0, x+0, width)
    x1,s1 = patch9.gridpoint(0, x+1, width)
    y0,t0 = patch9.gridpoint(1, y+0, height)
    y1,t1 = patch9.gridpoint(1, y+1, height)
    k0 = mix(c0, c1, float(x0)/width)
    k1 = mix(c0, c1, float(x1)/width)
    k2 = mix(c2, c3, float(x0)/width)
    k3 = mix(c2, c3, float(x1)/width)
    c0 = mix(k0, k2, float(y0)/height)
    c1 = mix(k1, k3, float(y0)/height)
    c2 = mix(k0, k2, float(y1)/height)
    c3 = mix(k1, k3, float(y1)/height)
    quad_gradient(stream, (left+x0, top+y0, x1-x0, y1-y0), (s0, t0, s1, t1), (c0,c1,c2,c3))

class Renderer(object):
    def __init__(self, output, default_font, program=None):
        self.output = output
        self.default_font = default_font
        self.stream = VertexStream(fmt)
        self.textures = TextureCache()
        if program is None:
            self.program = Program.load(in_module('shaders/flat.glsl'))
        else:
            self.program = program

    def bind(self):
        self.output.bind()
        self.program.use()
        self.program.uniform2f('resolution', (self.output.width, self.output.height))
        glViewport(0, 0, self.output.width, self.output.height)
        self.stream.vbo.bind()
        fmt.use(self.program)

    def unbind(self):
        fmt.enduse(self.program)
        self.stream.vbo.unbind()
        self.program.enduse()
        self.output.unbind()

    def rectangle(self, rect, image=image_empty, color=white, gradient=None):
        if isinstance(image, Patch9) and gradient is None:
            patch9 = image
            image  = image.image
            texture = self.textures.get(image)
            texture.bind()
            patch9_cell_flat(self.stream, patch9, 0, 0, rect, color)
            patch9_cell_flat(self.stream, patch9, 1, 0, rect, color)
            patch9_cell_flat(self.stream, patch9, 2, 0, rect, color)
            patch9_cell_flat(self.stream, patch9, 0, 1, rect, color)
            patch9_cell_flat(self.stream, patch9, 1, 1, rect, color)
            patch9_cell_flat(self.stream, patch9, 2, 1, rect, color)
            patch9_cell_flat(self.stream, patch9, 0, 2, rect, color)
            patch9_cell_flat(self.stream, patch9, 1, 2, rect, color)
            patch9_cell_flat(self.stream, patch9, 2, 2, rect, color)
            self.stream.flush()
            texture.unbind()
        elif isinstance(image, Patch9):
            patch9 = image
            image  = image.image
            texture = self.textures.get(image)
            texture.bind()
            patch9_cell_gradient(self.stream, 0, 0, rect, gradient)
            patch9_cell_gradient(self.stream, 1, 0, rect, gradient)
            patch9_cell_gradient(self.stream, 2, 0, rect, gradient)
            patch9_cell_gradient(self.stream, 0, 1, rect, gradient)
            patch9_cell_gradient(self.stream, 1, 1, rect, gradient)
            patch9_cell_gradient(self.stream, 2, 1, rect, gradient)
            patch9_cell_gradient(self.stream, 0, 2, rect, gradient)
            patch9_cell_gradient(self.stream, 1, 2, rect, gradient)
            patch9_cell_gradient(self.stream, 2, 2, rect, gradient)
            self.stream.flush()
            texture.unbind()
        else:
            if gradient is None:
                gradient = color, color, color, color
            texture = self.textures.get(image)
            texture.bind()
            quad_gradient(self.stream, rect, (0,1,1,0), gradient)
            self.stream.flush()
            texture.unbind()

    def text(self, pos, text, font=None, color=white):
        font = self.default_font if font is None else font
        texture = self.textures.get(font.image)
        texture.bind()
        characters_flat(self.stream, font, pos, text, color)
        self.stream.flush()
        texture.unbind()
