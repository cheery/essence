from argon import rgba
from schema import mutable
import layout

def renderer(argon, box):
    x,y,w,h = box.rect
    if x+w < 0 or argon.width < x or y+h < 0 or argon.height < y:
        return
    background = box.style['background']
    if background:
        background_color = box.style['background_color']
        argon.render.rectangle(box.rect, background, background_color)
    if isinstance(box, layout.Label):
        font             = box.style['font']
        color            = box.style['color']
        argon.render.text(box.baseline_pos, box.source, font, color)

def render_selection(argon, frame, selection):
    background = frame.style['selection_background']
    box = frame.find_intron(mutable.get_object(selection))
    if box is None:
        argon.render.rectangle((0,0,frame.width, frame.height), background, color=frame.style['selection_color_bad'])
    else:
        argon.render.rectangle(box.rect, background, color=frame.style['selection_color_outer'])
        if isinstance(selection, mutable.Selection):
            head = selection.head
            start, stop = selection.start, selection.stop
            for child in box.references():
                if child.in_range(start, stop):
                    rect = child.selection_marker(start, stop)
                    argon.render.rectangle(rect, color=frame.style['selection_color_inner'])
                if child.in_range(head, head):
                    rect = child.selection_marker(head, head)
                    argon.render.rectangle(rect, color=frame.style['caret_color'])

def get_default_style(argon):
    return layout.default.inherit(
        renderer = renderer,
        background = None,
        background_color = rgba(255, 255, 255),
        font = argon.default_font,
        color = rgba(255, 255, 255),
        align = layout.Align(0, 0),
    )
