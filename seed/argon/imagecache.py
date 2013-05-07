import os, json
from image import Image
from patch9 import Patch9
from font import Font

def which(paths, path):
    for directory in paths:
        p = os.path.join(directory, path)
        if not os.path.exists(p):
            continue
        return p
    raise Exception("%r not found" % path)

class ImageCache(object):
    def __init__(self, paths):
        self.paths = paths
        self.cache = {}

    def image(self, path):
        if path in self.cache:
            return self.cache[path]
        self.cache[path] =image= Image.load(which(self.paths, path))
        return image

    def patch9(self, path):
        return Patch9(self.image(path))

    def font(self, path):
        return Font(
            self.image(os.path.join(path, 'bitmap.png')),
            json.load(open(which(self.paths, os.path.join(path, 'metadata.json'))))
        )
