from argon import Argon, rgba
import layout

argon = Argon()
argon.pos = 0,0

circle64 = argon.cache.image('circle64.png')
box7 = argon.cache.patch9('box7.png')
font = argon.cache.font('AnonymousPro_17')

README = open('README').read().splitlines()

@argon.listen
def on_frame(time):
    width, height = argon.resolution
    hw = width  / 2
    hh = height / 2

    argon.clear(rgba(0x40, 0x40, 0x40))
    argon.render_rectangle((hw * 0.5, hh * 0.5, hw, hh))
    argon.render_rectangle((hw * 0.5, hh * 0.5, hw, hh), box7, color=rgba(0x80, 0, 0, 0xFF))

    x, y = hw * 0.6, hh * 0.6
    for line in README:
        argon.render_text((x, y), line, font, color=rgba(0,0,0))
        y += font.height


    x, y = argon.pos
    argon.render_rectangle((x-32, y-32, 64, 64), circle64, color=rgba(0x1,0x0,0,0x80))


@argon.listen
def on_mousemotion(pos, rel):
    argon.pos = pos

argon.run()
