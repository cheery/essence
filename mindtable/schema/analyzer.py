# total rewrite needed

"""
    schema.autospawn
    ~~~~~~~~~~~~~~~~

    Whenever applied to a mutator, retrieves name of every template
    that can be instantiated, either directly, or indirectly.
"""
from language import Ref, List, Group, Struct, Constant, String, Buffer

def extract_names(table, name, out):
    """
    Groups are not true constructs, so they are
    traversed to retrieve list of names of constructs
    that can be truly instantiated.
    """
    record = table[name]
    if record.meta == Group:
        for ref in record.members:
            out = extract_names(table, ref.name, out)
    else:
        out.append(name)
    return out

def valid_templates(table, record, index):
    """
    Produces list of valid templates, and list of valid templates within a list.
    """
    sout = []
    mout = []
    for item in record.fields[index].spec:
        if item.meta == Ref:
            sout = extract_names(table, item.name, sout)
        elif item.meta == List:
            for ref in item.spec:
                mout = extract_names(table, ref.name, mout)
        else:
            sout.append(item)
    return sout, mout

def evaluate_template_chains(inversion, target):
    unvisited = [target]
    cost = {target:0}
    path = {}
    while len(unvisited) > 0:
        current = unvisited.pop(0)
        current_cost = cost[current]
        for name, many in inversion[current]:
            difficulty = 1 + many
            if not name in cost:
                unvisited.append(name)
                cost[name] = current_cost + difficulty
                path[name] = current, many
            elif cost[name] >= current_cost + difficulty:
                cost[name] = current_cost + difficulty
                path[name] = current, many
        unvisited.sort(key=lambda name: cost[name])
    for name, (_next, many) in path.items():
        yield name, (_next, many, cost[name])

def unroll_chain(chains, out, _next, target):
    _next, many, cost = chains[_next][target]
    if many:
        out.append(())
    if _next != target:
        out.append(_next)
        out = unroll_chain(chains, out, _next, target)
    return out

def template_path(chains, name, sout, mout):
    if name in sout:
        yield []
    if name in mout:
        yield [()]
    for key in sout:
        chain = chains[key]
        if name in chain:
            _next, many, cost = chain[name]
            yield unroll_chain(chains, [key], key, name)
    for key in mout:
        chain = chains[key]
        if name in chain:
            _next, many, cost = chain[name]
            yield unroll_chain(chains, [(), key], key, name)

class Spawner(object):
    def __init__(self, autospawn, mutator, sout, mout):
        self.autospawn = autospawn
        self.mutator = mutator
        self.sout = sout
        self.mout = mout

    def get(self, name, is_selection=None):
        is_selection = self.mutator.is_selection if is_selection is None else is_selection
        if is_selection:
            sout, mout = self.mout, ()
        else:
            sout, mout = self.sout, self.mout
        paths = list(template_path(self.autospawn.chains, name, sout, mout))
        if len(paths) > 0:
            return min(paths, key = lambda path: len(path))

class Autospawn(object):
    def __init__(self, language):
        self.language = language
        self.update_template_chains()

    def update_template_chains(self):
        language = self.language
        self.table = table = dict((record.name, record) for record in language.semantics)

        self.chains = chains = {}
        inversion = {}
        for record in language.semantics:
            if record.meta == Group:
                continue
            inversion[record.name] = []
            chains[record.name] = {}
        inversion[String] = []
        inversion[Buffer] = []
        for record in language.semantics:
            if record.meta == Struct:
                sout, mout = valid_templates(table, record, 0)
                for entry in sout:
                    inversion[entry].append((record.name, False))
                for entry in mout:
                    inversion[entry].append((record.name, True))

        for name in inversion:
            for key, route in evaluate_template_chains(inversion, name):
                chains[key][name] = route

    def get(self, mutator):
        name = mutator.struct.meta.name
        if name in self.table:
            record = self.table[name]
            sout, mout = valid_templates(self.table, record, mutator.index)
            return Spawner(self, mutator, sout, mout)