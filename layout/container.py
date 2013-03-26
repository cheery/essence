from box import Box

class Container(Box):
    def __init__(self, nodes, style):
        self.nodes = nodes
        self.offset0 = [0] * (len(nodes) + 1)
        self.offset1 = [0] * (len(nodes) + 1)
        self.flow0 = [0] * len(nodes)
        self.flow1 = [0] * len(nodes)
        self.base0 = 0 
        self.base1 = 0
        Box.__init__(self, (0,0,0,0), style)

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, key):
        return self.nodes[key]
