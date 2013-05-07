from OpenGL.GL import *
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_object import *
from ctypes import byref

class Framebuffer(object):
    def __init__(self, color_attachment0):
        self.framebuffer = glGenFramebuffers(1)
        self.color_attachment0 = color_attachment0
        self.configure()
        
    @property
    def width(self):
        return self.color_attachment0.width
        
    @property
    def height(self):
        return self.color_attachment0.height

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def configure(self):
        color_attachment0 = self.color_attachment0
        self.bind()
        glFramebufferTexture2D(
            GL_FRAMEBUFFER,
            GL_COLOR_ATTACHMENT0,
            color_attachment0.target,
            color_attachment0.texture,
            0
        )
        argc = 1
        argv = (GLenum*argc)(GL_COLOR_ATTACHMENT0)
        glDrawBuffers(argc, argv)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Broken framebuffer")
        self.unbind()

    def free(self):
        framebuffer = GLuint(self.framebuffer)
        glDeleteFramebuffers(1, byref(framebuffer))
