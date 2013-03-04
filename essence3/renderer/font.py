import json, os

class Font(object):
    def __init__(self, metadata, item):
        self.metadata = metadata
        self.item = item

    @classmethod
    def load(cls, atlas, path):
        return cls(
            json.load(open(os.path.join(path, 'metadata.json'))),
            atlas.load(os.path.join(path, 'bitmap.png'))
        )

    def measure(self, text, scale=1.0):
        offsets = [0]
        offset  = 0
        for character in text:
            metrics = self.metadata.get(character)
            if metrics is None:
                continue
            offset += metrics["advance"] * scale
            offsets.append(offset)
        return offsets

    def __call__(self, emit, text, (x,y), scale=1.0, color=None):
        color = color or self.item.atlas.white
        offset = 0
        s0 = float(self.item.x) / self.item.atlas.width
        t0 = float(self.item.y) / self.item.atlas.height
        s1 = float(self.item.width) / self.item.atlas.width
        t1 = float(self.item.height) / self.item.atlas.height
        px_s = s1 / self.item.width
        px_t = t1 / self.item.height
        for character in text:
            metrics = self.metadata.get(character)
            if metrics is None:
                continue
            elif metrics["display"]:
                width = metrics["width"]
                height = metrics["height"]
                hbearing = metrics["hbearing"]
                vbearing = -metrics["vbearing"]
                s = s0 + metrics["uv"]["s"] * s1
                t = t0 + metrics["uv"]["t"] * t1
                left   = x + scale * (offset + hbearing)
                right  = x + scale * (offset + hbearing + width)
                top    = y + scale * (vbearing)
                bottom = y + scale * (vbearing + height)
                emit(left,  top,    s,              t,               color.s, color.t)
                emit(right, top,    s + px_s*width, t,               color.s, color.t)
                emit(right, bottom, s + px_s*width, t + px_t*height, color.s, color.t)
                emit(left,  bottom, s,              t + px_t*height, color.s, color.t)
            offset += metrics["advance"]
