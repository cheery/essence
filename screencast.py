from pyvpx import Encoder, Image, vpx

def le16(value):
    return chr(value & 0xFF) + chr((value >> 8) & 0xFF)

def le32(value):
    return le16(value & 0xFFFF) + le16((value >> 16) & 0xFFFF)

def le64(value):
    return le32(value & 0xFFFFFFFF) + le32((value >> 32) & 0xFFFFFFFF)

def ivf_file_header(width, height, (rate, scale), frame_count):
    return ''.join([
        'DKIF',
        le16(0), # version
        le16(32), # headersize
        le32(0x30385056), #fourcc?
        le16(width),
        le16(height),
        le32(rate),
        le32(scale),
        le32(frame_count),
        le32(0), #unused
    ])

def ivf_frame_header(size, pts):
    return le32(size) + le64(pts)

def save(path, (width, height), frames):
    count = 0
    fd = open(path, 'w')
    image = Image(width, height, vpx.VPX_IMG_FMT_I420)
    encoder = Encoder(width, height)
    width  = encoder.cfg.g_w
    height = encoder.cfg.g_h
    timebase = encoder.cfg.g_timebase.den, encoder.cfg.g_timebase.num
    fd.write(ivf_file_header(width, height, timebase, count))
    for t, frame in frames:
        image_src = Image(width, height, vpx.VPX_IMG_FMT_RGB24, buffer(frame))
        image_src.convertTo(image)
        image.flip()
        for kind, packet in encoder.encode(image, t):
            if kind == vpx.VPX_CODEC_CX_FRAME_PKT:
                fd.write(ivf_frame_header(len(packet), t))
                fd.write(packet)
                count += 1
    image.free()
    fd.seek(0)
    fd.write(ivf_file_header(width, height, timebase, count))
    fd.close()
    encoder.close()


from argon import graphics
from OpenGL.GL import *
from ctypes import CDLL

libgl = CDLL('libGL.so')

def getPixels(texture):
    texture.bind()
    data = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGB, GL_UNSIGNED_BYTE)
    texture.unbind()
    return data

class Frameset(object):
    def __init__(self, (width, height)):
        self.width  = width
        self.height = height
        self.frames = []
        self.counter = 0

    def capture(self, argon):
        texture = graphics.Texture.empty(self.width, self.height)
        texture.bind()
        glReadBuffer(GL_FRONT)
        texture.set_min_mag()
        glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 0, 0, texture.width, texture.height, 0)
        texture.unbind()
        self.frames.append((self.counter, texture))
        self.counter += 1

    def save(self, path):
        width, height = self.width, self.height
        count = 0
        fd = open(path, 'w')
        encoder = Encoder(width, height)
        image = Image(width, height, vpx.VPX_IMG_FMT_I420)
        timebase = encoder.cfg.g_timebase.den, encoder.cfg.g_timebase.num
        fd.write(ivf_file_header(width, height, timebase, count))
        for t, frame in self.frames:
            print "streaming frame %i..." % t,
            with Image(width, height, vpx.VPX_IMG_FMT_RGB24, getPixels(frame)) as src:
                src.convertTo(image)
            image.flip()
            for kind, packet in encoder.encode(image, t):
                if kind == vpx.VPX_CODEC_CX_FRAME_PKT:
                    fd.write(ivf_frame_header(len(packet), t))
                    fd.write(packet)
                    count += 1
            print "ok."
        image.free()
        fd.seek(0)
        fd.write(ivf_file_header(width, height, timebase, count))
        fd.close()
        encoder.close()

    def free(self):
        for t, frame in self.frames:
            frame.free()

#def get_frame():
#    global counter
#    w, h = argon.resolution
#    data = bytearray(w*h*3)
#    _data = (GLubyte*len(data)).from_buffer(data)
#    glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, _data)
##    texture.bind()
##    glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 0, 0, texture.width, texture.height, 0)
##    glGetTexImage(GL_TEXTURE_2D, 0, GL_RGB, GL_UNSIGNED_BYTE, _data)
##    texture.unbind()
##
##    pbo.bind()
##    glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, GLvoid)
##    data = pbo.map(GL_READ_ONLY)
##    print data
##    data = buffer(data, w*h*3)
##
##    pbo.unmap()
##    pbo.unbind()
##
#    counter += 1
#    return counter, data


#frame_count = 0
#with Encoder(320, 240) as encoder:
#
#    fd = open('screencast.webm', 'w')
#    fd.write(ivf_file_header(width, height, timebase, frame_count))
#
#    with Image(320, 240, vpx.VPX_IMG_FMT_I420) as img:
##        img.clear()
##        y,u,v = rgb_to_yuv(1.0, 0, 0)
##        print y, u, v
#        y,u,v = rgb_to_yuv(255, 0, 0)
##        print y, u, v
#        pixels = 320*240
#        k = (1, 2, 4, 8, 16, 32, 64, 128, 255)
#        for j in range(len(k)):
#            for i in range(pixels):
#                img.data[i] = chr(int(y))
#            for i in range(pixels/4):
#                img.data[pixels            + i] = chr(int(u))
#                img.data[pixels + pixels/4 + i] = chr(int(v))
#            # fetch and fill the image data buffer
#            for kind, packet in encoder.encode(img, frame_count*100):
#                if kind == vpx.VPX_CODEC_CX_FRAME_PKT:
#                    fd.write(ivf_frame_header(len(packet), frame_count*100))
#                    fd.write(packet)
#                    frame_count += 1
#    fd.seek(0)
#    fd.write(ivf_file_header(width, height, timebase, frame_count))
#    fd.close()
