from texture import Texture

class TextureCache(object):
    def __init__(self):
        self.cache = {}

    def get(self, image):
        if image in self.cache:
            return self.cache[image]
        else:
            self.cache[image] =texture= Texture.empty(image.width, image.height)
            texture.upload(image.data)
            return texture
