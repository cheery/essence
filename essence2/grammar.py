class Symbolic(object):
    _tmp_cost = None
    _tmp_path = None
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
        self.distances = {}

    def __getitem__(self, index):
        return self.fields[index]

    def text(self):
        return '%s = %s' % (self.name, ' '.join(self.fields))

class Group(object):
    def __init__(self, name, group):
        self.name = name
        self.group = group
        self.distances = {}

    def text(self):
        return '%s = %s' % (self.name, ' | '.join(self.group))

class Data(object):
    def __init__(self, name, which):
        self.name = name
        self.which = which

    def text(self):
        return '%s = {%s}' % (self.name, self.which)

class Language(object):
    def __init__(self, rules, root):
        self.rules = rules
        self.language = dict((rule.name, rule) for rule in rules)
        self.root = root
        build_all_semantic_routes(self)

    def text(self):
        return '\n'.join(rule.text() for rule in self.rules)
    
    def iter_instances_of(self, cls):
        for rule in self.rules:
            if isinstance(rule, cls):
                yield rule

    def __getitem__(self, name):
        return self.language[name]

    def unroll_group(self, node):
        if isinstance(node, Group):
            for name in node.group:
                for name in self.unroll_group(self[name]):
                    yield name
        else:
            yield node.name

    def slot_accepts(self, field, index):
        to = self[field[index].rstrip('*')]
        if isinstance(to, Group):
            return list(self.unroll_group(to))
        else:
            return [to.name]

    def get_distances(self, name):
        bare = name.rstrip('*')
        node = self[bare]
        if isinstance(node, (Symbolic, Group)):
            return node.distances
        elif name.endswith('*'):
            return {bare: (1, bare)}
        else:
            return {}
            

def inverted_edges(language):
    edges = {}
    for t in language.iter_instances_of(Symbolic):
        for to in language.slot_accepts(t, 0):
            edges[to] = edges.get(to, ()) + (t,)
    return edges

def build_semantic_routes(language, edges, target):
    unvisited = []
    current = target
    current_distance = 0
    done = False
    while not done:
        for node in edges.get(current, ()):
            if node._tmp_cost == None:
                unvisited.append(node)
            if node._tmp_cost == None or node._tmp_cost > current_distance:
                node._tmp_cost = current_distance + 1
                node._tmp_path = current
        unvisited.sort(key=lambda node: node._tmp_cost)
        if len(unvisited) > 0:
            node = unvisited.pop(0)
            current_distance = node._tmp_cost
        else:
            done = True

    for node in language.iter_instances_of(Symbolic):
        if node._tmp_cost != None:
            node.distances[target] = node._tmp_cost, node._tmp_path
        node._tmp_cost = None
        node._tmp_path = None

def build_all_semantic_routes(language):
    edges = inverted_edges(language)
    for node in language.iter_instances_of((Symbolic, Data)):
        build_semantic_routes(language, edges, node.name)

    for node in language.iter_instances_of(Group):
        for name in language.unroll_group(node):
            node.distances[name] = (1, name)
            subnode = language[name]
            if isinstance(subnode, Symbolic):
                for target, (cost, _) in subnode.distances.items():
                    if target in node.distances:
                        continue
                    node.distances[target] = (cost+1, name)
        print "COST", node.name, node.distances

    for node in language.iter_instances_of(Symbolic):
        print "COST", node.name, node.distances
