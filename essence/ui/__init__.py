from backend import get, color, empty, window, eventloop
from util import vec2

class view(object):
    def __init__(self, document):
        self.document = document

    def paint(self, screen, dt):
        screen.fill((0xff,0x00,0x00))

