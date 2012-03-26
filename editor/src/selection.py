class selector(object):
    def __init__(self, rect, index):
        self.rect = rect
        self.index = index

    def edge(self, (x,y)):
        return self.index + (x - self.rect.left > self.rect.right - x)

class visual(object):
    def __init__(self, entries):
        self.entries = entries

    def pick(self, pos):
        for entry in self.entries:
            if entry.rect.inside(pos):
                return entry.index, entry.edge(pos)

    def blit_edge(self, screen, index, config):
        left = config['left']
        right = config['right']
        for entry in self.entries:
            if entry.index == index - 1:
                right.blit(screen, entry.rect)
            if entry.index == index:
                left.blit(screen, entry.rect)

    def blit_range(self, screen, start, stop, config):
        if start == stop:
            return self.blit_edge(screen, start, config)
        left = config['left']
        right = config['right']
        for entry in self.entries:
            if entry.index == start:
                left.blit(screen, entry.rect)
            if entry.index == stop - 1:
                right.blit(screen, entry.rect)
