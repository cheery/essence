import json
from surface import Surface
import os
from essence2 import vec2, rgba, rectangle, clamp

class Font(object):
    def __init__(self, surface, metadata):
        self.surface = surface
        self.metadata = metadata

    def calculate_mathline(self, baseline):
        metrics = self.metadata['+']
        return metrics["height"] / 2 - metrics["vbearing"] + baseline

    @staticmethod
    def load(path):
        return Font(
            Surface.load(os.path.join(path, 'bitmap.png')),
            json.load(open(os.path.join(path, 'metadata.json')))
        )

    def __call__(self, text):
        font_width, font_height = self.surface.size
        offsets = [0]
        baseline = 0
        overline = 0
        x = 0
        for character in text:
            metrics = self.metadata.get(character)
            if metrics is None:
                continue
            if metrics["display"]:
                baseline = max(baseline, metrics["vbearing"])
                overline = max(overline, metrics["height"] - metrics["vbearing"])
            x += metrics['advance']
            offsets.append(x)
        surface = Surface.empty(offsets[-1], baseline + overline)
        x = 0
        for character in text:
            metrics = self.metadata.get(character)
            if metrics is None:
                continue
            if metrics["display"]:
                width = metrics["width"]
                height = metrics["height"]
                uv = metrics["uv"]
                glyph = self.surface.subsurface((
                    (uv["s"] * font_width,
                    uv["t"] * font_height),
                    (width,
                    height)
                ))
                surface(glyph, (
                    (x + metrics["hbearing"],
                    baseline - metrics["vbearing"]),
                    (width,
                    height)
                ))
            x += metrics['advance']
        mathline = self.calculate_mathline(baseline)
        return Label(surface.pys, offsets, baseline, mathline)

class Label(Surface):
    def __init__(self, pys, offsets, baseline, mathline):
        Surface.__init__(self, pys)
        self.offsets = offsets
        self.baseline = baseline
        self.mathline = mathline
        self.geometry = rectangle(vec2(0, 0), self.size)

    def carets(self):
        base = self.geometry.base
        size = self.geometry.size
        for offset in self.offsets:
            yield rectangle(base + vec2(offset-1, -1), vec2(1, size.y+1))

    def caret(self, index):
        index = clamp(0, len(self.offsets) - 1, index)
        base = self.geometry.base
        size = self.geometry.size
        return rectangle(base + vec2(self.offsets[index]-1, -1), vec2(1, size.y+1))

    def selection(self, head, tail):
        head = clamp(0, len(self.offsets) - 1, head)
        tail = clamp(0, len(self.offsets) - 1, tail)
        start = min(head, tail)
        stop = max(head, tail)
        base = self.geometry.base
        size = self.geometry.size
        x0 = self.offsets[start]
        x1 = self.offsets[stop]
        return rectangle(base + vec2(x0-1, -1), vec2(x1 - x0 + 1, size.y+1))

    def nearest_caret(self, pos):
        delta = pos - self.geometry.base
        d0 = abs(delta.x - 0)
        for index, offset in enumerate(self.offsets):
            d1 = abs(delta.x - offset)
            if d0 < d1:
                return index - 1
            d0 = d1
        return index
