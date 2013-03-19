class Item(object):
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.area = width*height

    def __repr__(self):
        return '<Item %s %s %s %s>' % (self.x, self.y, self.width, self.height)

class Area(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.size = width*height

    def __repr__(self):
        return '<Area %s %s %s %s>' % (self.x, self.y, self.width, self.height)

    def score(self, item):
        width = item.width+2
        height = item.height+2
        area = width*height

        a = self.width - width
        b = self.height - height
        return min(a, b) * (self.size-area)

    def split(self, item):
        width = item.width + 2
        height = item.height + 2

        if width == self.width and height == self.height:
            return []
        elif width == self.width:
            return [Area(self.x, self.y+height, self.width, self.height-height)]
        elif height == self.height:
            return [Area(self.x+width, self.y, self.width-width, self.height)]
        else:
            w = self.width - width
            h = self.height - height
            if w > h:
                a = Area(self.x+width, self.y, self.width-width, self.height)
                b = Area(self.x, self.y+height, width, self.height-height)
            else:
                a = Area(self.x, self.y+height, self.width, self.height-height)
                b = Area(self.x+width, self.y, self.width-width, height)
            return a, b

class OutOfArea(Exception): pass

class Allocator(object):
    def __init__(self):
        self.items = []

    def reset(self):
        self.items = []

    def add(self, width, height):
        item = Item(
            width = width,
            height = height,
        )
        self.items.append(item)
        return item

    def findMatch(self, item, free):
        width = item.width+2
        height = item.height+2
        candidates = [area for area in free if area.width >= width and area.height >= height]
        if not candidates:
            raise OutOfArea('out of area')
        best = sorted(candidates, key=lambda area: area.score(item))
        return best[0]

    def allocate(self, width, height):
        try:
            items = sorted(self.items, key=lambda item: item.area)
            free = [Area(0, 0, width, height)]
            while items:
                item = items.pop(-1)
                area = self.findMatch(item, free)
                free.remove(area)
                item.x = area.x+1
                item.y = area.y+1
                free.extend(area.split(item))
            return True
        except OutOfArea:
            return False
