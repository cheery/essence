import pygame, time

def main():
    pygame.display.init()
    screen = pygame.display.set_mode((810, 1200), pygame.RESIZABLE)
    import src
    from src.util import getfiles
    files = getfiles('.')

    last_check = time.time()

    while 1:
        for event in pygame.event.get():
            src.on_event(event)
        src.fill(screen)
        pygame.display.flip()
        now = time.time()
        if last_check + 0.1 < now:
            last_check = now
            new_files = getfiles('.')
            if new_files - files:
                src = reload(src)
            files = new_files

if __name__=='__main__':main()

#from program import program, array, OPN, CLO
#from graphics import rectangle, patch9, stretch, color
#import sys
##from view import view
#
#class RC(object):
#    def __init__(self, **kw):
#        for key, value in kw.items():
#            setattr(self, key, value)
#
#document = program([
#  array('ultra'),
#  OPN, array('alpha'), array('beta'),
#  OPN, array('delta'), array('gamma'),
#  CLO,
#  CLO
#])

#frame = view(document)

#def main():
#    pygame.display.init()
#    screen = pygame.display.set_mode((800, 600))
#    rc = RC(
#        font = sdl_bitmapfont.load('font/proggy_tiny'),
#        width = 800,
#        height = 600,
#    )
#
#    quad = patch9(pygame.image.load('test_border.png'))
#    pupu = stretch(pygame.image.load('pupu1.jpg'))
#    red = color(255,0,0)
#
#    font = rc.font
#    red_font = font.colored((255,0,0))
#    green_font = font.colored((0,255,0))
#    while 1:
#        for event in pygame.event.get():
#            if event.type == pygame.QUIT:
#                sys.exit()
#            if event.type == pygame.KEYDOWN:
#                sys.exit()
#        screen.fill((0, 0, 0))
##        frame.refresh(rc)
##        frame.scene.draw(screen)
#
#        rside = rectangle(50,50,750,550)
#        bside = rectangle(300,200,740,540)
#        lside = rectangle(100,200,200,300)
#
#        red.blit(screen, lside)
#        quad.blit(screen, rside)
#        pupu.blit(screen, bside)
#
#        font.blit(screen, (150, 150), "hello lulz")
#        red_font.blit(screen, (150, 170), "hello lulz")
#        green_font.blit(screen, (150, 190), "hello lulz")
#
##        layout = font.layoutmetrics(test_sample)
##        left = layout['charactergaps'][0] + 150
##        right = layout['charactergaps'][-1] + 150
##        top = layout['top'] + 150
##        bottom = layout['bottom'] + 150
##        screen.fill(white, (left, top-5, right - left,5))
##        screen.fill(white, (left, bottom, right-left, 5))
##        screen.fill(white, (-10 + left, 150, right-left+20, 1))
##        screen.fill((255, 255, 0), (left, top, right-left, bottom-top), pygame.BLEND_RGB_MULT)
#
##        full_layout = pprint(screen, struct)
##        for layout in full_layout:
##            visualise_layout_piece(screen, layout)
#
##        screen.fill((255, 255, 255), (300, 300, 50, 10))
##        screen.blit(font.bitmap, (0, 0))
