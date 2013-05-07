class Font(object):
    def __init__(self, image, metadata):
        self.image = image
        self.metadata = metadata
        self.height   = metadata.pop('height')
        self.baseline = int(metadata.pop('baseline'))

    def measure(self, text):
        offsets = [0]
        offset  = 0
        for character in text:
            metrics = self.metadata.get(character)
            if metrics is None:
                continue
            offset += metrics["advance"]
            offsets.append(offset)
        return offsets
