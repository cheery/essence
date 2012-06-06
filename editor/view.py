import graphics

def pprint(screen, struct):
    x = y = 16
    scope = []
    i = 0
    full_layout = []
    for node in struct:
        postcolor = None
        if node['type'] in '<s':
            text = node['data']
        if node['type'] == '<':
            scope.append(text)
            text = '<%s>' % text
            postcolor = 255, 255, 0
        if node['type'] == '>':
            text = '</%s>' % scope.pop()
            postcolor = 255, 255, 0
        layout = font.layoutmetrics(text)
        layout['x'] = x
        layout['y'] = y
        full_layout.append(layout)
        font.blit(screen, (x, y), text)
        if postcolor:
            rect = (
                x, layout['top']+y,
                layout['charactergaps'][-1],
                layout['bottom']-layout['top']
            )
            screen.fill(postcolor, rect, pygame.BLEND_RGB_MULT)
        x += layout['charactergaps'][-1] + 8
        i += 1
    return full_layout

def visualise_layout_piece(screen, layout):
    x = layout['x']
    y = layout['y']
    top = layout['top']
    bottom = layout['bottom']
    for i in layout['charactergaps']:
        screen.fill((255, 0, 0), (x+i, y+bottom, 1, 2))
        screen.fill((255, 0, 0), (x+i, y+top-2, 1, 2))

class view(object):
    def __init__(self, document):
        self.dirty = True
        self.document = document
        document.listeners.append(self)

    def on_splice(self, start, stop, data, res):
        print 'view registered splice, you need to handle it.'

    def refresh(self, rc):
        if not self.dirty:
            return
        self.dirty = False
        rect = graphics.rectangle(0,0,rc.width,rc.height)
        self.scene = graphics.scene(rect, [])
        x = 0
        y = 16
        lineheight = 16
        stripestack = []
        for node in self.document:
            if node.isbytes():
                obj = graphics.string(node.data, rc.font)
                obj.rect.move((x,y))
                self.scene.append(obj)
                x += 6 + obj.metrics['charactergaps'][-1]
            if node.isOPN():
                depth = len(stripestack) * 2 + y + 2
                stripestack.append((x, depth))
                lineheight = max(lineheight, depth+1)
                x += 2
            if node.isCLO():
                start, depth = stripestack.pop(-1)
                stop = x - 4
                rect = graphics.rectangle(start, depth, stop, depth+1)
                obj = graphics.fill(rect, (255,0,0))
                self.scene.append(obj)
                x += 2
