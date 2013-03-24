from argon import rgba
from box import Box
blackish   = rgba(0x00, 0x00, 0x00, 0x40)
whiteish   = rgba(0xf6, 0xf3, 0xe8)
blueish    = rgba(0x00, 0xf3, 0xe8, 0x80)

def clamp(low, high, value):
    return min(high, max(low, value))

class Segment(object):
    def __init__(self, width, text):
        self.width = width
        self.text = text

def line_break(width, words, space_width):
    table = [(0.0, 0)]
    for stop in range(1, len(words)+1):
        start = stop - 1
        c = words[start].width
        best = (width-c)**2.0 + table[start][0], start
        start -= 1
        while start >= 0 and c <= width:
            c += words[start].width + space_width
            p = (width-c)**2.0 + table[start][0]
            if p <= best[0] and c <= width:
                best = p, start
            start -= 1
        table.append(best)
    lines = []
    j = len(words)
    while j > 0:
        _, i = table[j]
        lines.append(words[i:j])
        j = i
    lines.reverse()
    return lines

def line_offsets(lines):
    yield 0
    current = 0
    for line in lines:
        current += sum(len(word.text) for word in line) + max(0, len(line)-1) + 1
        yield current

class Paragraph(Box):
    def __init__(self, font, text, tags, head=0, tail=0):
        self.font = font
        self.text = text
        self.tags = tags
        self.head = head + 11
        self.tail = tail + 40
        Box.__init__(self)
        self.width  = 300
        self.line_height = font.height * 1.2
        self.dragging = False

    def update(self):
        font = self.font
        space_width = font.measure(' ')[-1]
        self.lines = line_break(self.width, [
            Segment(font.measure(word)[-1], word)
            for word in self.text.split(' ')
        ], space_width)
        self.height = self.line_height * len(self.lines)
        self.bases = list(line_offsets(self.lines))
        self.offsets = font.measure(self.text)

    def getline(self, offset):
        for j, base in enumerate(reversed(self.bases), 1):
            if base <= offset:
                return len(self.bases) -j
        return len(self.bases) - j

    def getlox(self, offset):
        line = self.getline(offset)
        base = self.bases[line]
        return line, self.offsets[offset] - self.offsets[base]

    @property
    def start(self):
        return min(self.head, self.tail)

    @property
    def stop(self):
        return max(self.head, self.tail)

    def textgeometry(self, argon):
        x, y = self.left, self.top + self.font.baseline
        for line in self.lines:
            text = ' '.join(word.text for word in line)
            yield (x, y), text, whiteish, self.font
            y += self.line_height

    def selgeometry(self, argon, start, stop):
        x0, y = self.left, self.top
        x1 = x0 + self.width
        l0, o0 = self.getlox(start)
        l1, o1 = self.getlox(stop)
        x2, x3 = x0+o0, x0+o1
        if l0 == l1:
            rect = x2, y + self.line_height * l0, x3-x2, self.line_height
            return [(rect, blueish, argon.plain)]
        elif l0+1 == l1:
            rect0 = x2, y + self.line_height * l0, x1-x2, self.line_height
            rect1 = x0, y + self.line_height * l1, x3-x0, self.line_height
            return [
                (rect0, blueish, argon.plain),
                (rect1, blueish, argon.plain)
            ]
        else:
            rect0 = x2, y + self.line_height * l0, x1-x2, self.line_height
            rect1 = x0, y + self.line_height * l1, x3-x0, self.line_height
            rect2 = x0, y + self.line_height * (l0+1), x1-x0, self.line_height*(l1-l0-1)
            return [
                (rect0, blueish, argon.plain),
                (rect1, blueish, argon.plain),
                (rect2, blueish, argon.plain)
            ]

    def render(self, argon):
        self.update()
        font = self.font
        x, y = self.left, self.top + font.baseline
        l, o = self.getlox(self.head)
        argon.render([
            (self.rect, blackish, argon.plain),
            ((x+o-1, self.top+self.line_height*l, 2, self.line_height), blueish, argon.plain),
        ] + list(self.textgeometry(argon))
          + list(self.selgeometry(argon, self.start, self.stop))
        )

    def pick_offset(self, (x, y)):
        line = clamp(0, len(self.lines)-1, int((y - self.top) / self.line_height))
        base = self.bases[line]
        x = (x - self.left)
        best = base, abs(x)
        for i in range(base, self.bases[line+1]):
            if len(self.offsets) <= i:
                continue
            o = abs(self.offsets[i] - self.offsets[base] - x)
            if o <= best[1]:
                best = i, o
        return best[0]

    def mousedown(self, buttons, pos):
        self.head = self.tail = self.pick_offset(pos)
        self.dragging = True

    def mouseup(self, buttons, pos):
        self.head = self.pick_offset(pos)
        self.dragging = False

    def mousemotion(self, pos, vel):
        if self.dragging:
            self.head = self.pick_offset(pos)

    def replace(self, text, start, stop):
        self.text = self.text[:start] + text + self.text[stop:]

    def keydown(self, name, mod, text):
        if name in ('backspace', 'delete') and self.start < self.stop:
            self.replace(text, self.start, self.stop)
            self.head = self.tail = self.start
        elif name == 'backspace':
            last = clamp(0, len(self.text), self.head-1)
            self.replace('', last, self.head)
            self.head = self.tail = last
        elif name == 'delete':
            nxt = clamp(0, len(self.text), self.head+1)
            self.replace('', self.head, nxt)
            self.head = self.tail = self.head
        elif len(text) > 0:
            self.replace(text, self.start, self.stop)
            self.head = self.tail = self.start + len(text)
