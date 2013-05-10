from renderer import render_selection
from frame import Overlay
from schema import mutable

class Mode(object):
    def free(self):
        pass

    def on_keydown(self, key, modifiers, text):
        pass

    def on_mousedown(self, button, pos):
        return True

    def on_mousemotion(self, pos, vel):
        pass

    def on_mouseup(self, button, pos):
        pass

class SelectionMode(Mode):
    def __init__(self, frame, selection):
        self.frame     = frame
        self.selection = selection
        self.overlay   = Overlay(frame, self.render_overlay)

    def render_overlay(self, argon):
        argon.clear((0,0,0,0))
        render_selection(argon, self.frame, self.selection)

    def free(self):
        self.overlay.free()

    def insert_object(self, data):
        """
        Insert any object into the selection and adjust selection
        to cover the inserted object.
        """
        if isinstance(self.selection, mutable.Selection):
            if isinstance(self.selection.container, (mutable.Document, mutable.List)):
                self.selection.splice([data])
                return True
        else:
            mutable.get_document(self.selection).replace(self.selection, data)
            self.selection = data
            return True
