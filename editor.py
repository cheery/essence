from essence.ui import color, window, get, eventloop
from essence.document import node, copy, splice, build, collapse, serialize, deserialize
from essence.layout import StringFrame, BlockFrame, ImageFrame, generate_frames

black = color(0x00, 0x00, 0x00)
yellow = color(0x20, 0x20, 0x10)
dark_gray = color(0x10, 0x10, 0x10)

class Editor(object):
    def __init__(self):
        self.window = window()
        self.window.on('paint', self.frame)
        self.window.on('key', self.key_in)
        self.window.on('keydown', self.keydown)
        self.window.show()
        
        self.font = get('font/proggy_tiny', 'font')

        self.document = node(['t', 'y', 'p', 'e', ' ', node(['h', 'e', 'r', 'e'], 'var')], 'root', 0)

        #TODO: mode and finger

        self.cursor = len(self.document)

    def frame(self, screen, dt):
        screen(black)

        root = generate_frames(self.document, self.font, yellow)
        root.decorator = dark_gray
        root(screen)

        #TODO: selection = root.traverse(finger).highlight(range)

    def key_in(self, ch):
        if ch.isalnum() or ch in '_.':
            do = splice(self.cursor, self.cursor, [ch])
            self.cursor += len(ch)
            undo = do(self.document)
        pass #TODO: key_in(ch), pass to mode..

    def keydown(self, key, mod):
        pass #TODO: keydown(key, mod, unicode), map to keybind, pass to mode..

if __name__ == "__main__":
    editor = Editor()
    eventloop()
