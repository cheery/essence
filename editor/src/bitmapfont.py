import pygame, json
class Font(object):
    def __init__(self, bitmap, metadata):
        self.bitmap = bitmap
        self.metadata = metadata
        self.width, self.height = self.bitmap.get_size()

    def layoutmetrics(self, text):
        charactergaps = [0]
        accum = 0
        top = 0
        bottom = 0
        for character in text:
            metrics = self.metadata[character]
            if metrics['display']:
                height = metrics['height'] 
                vbearing = metrics['vbearing']
                top = min(top, - vbearing)
                bottom = max(bottom, height - vbearing)
            accum += metrics['advance']
            charactergaps.append(accum)
        return dict(
            charactergaps = charactergaps,
            top = top,
            bottom = bottom
        )

    def blit(self, screen, (x,y), text):
        for character in text:
            metrics = self.metadata[character]
            if metrics['display']:
                left = metrics['uv']['s'] * self.width
                top = metrics['uv']['t'] * self.height
                screen.blit(
                  self.bitmap,
                  (x + metrics['hbearing'], y - metrics['vbearing']),
                  (left, top, metrics['width'], metrics['height'])
                )
            x += metrics['advance']

    def colored(self, color):
        bitmap = self.bitmap.copy()
        bitmap.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        return Font(bitmap, self.metadata)

def load(directory):
    return Font(
        pygame.image.load(directory+'/bitmap.png'),
        json.load(file(directory+'/metadata.json')),
    )
