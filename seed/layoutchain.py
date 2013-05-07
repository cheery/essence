"""
    layoutchain
    ~~~~~~~~~~~

    This tool makes it easy to write layouts, by letting you to chain
    them together with no effort.
"""
from schema import mutable
import layout

class LayoutRoot(object):
    def __init__(self, mk_unknown):
        self.mk_unknown = mk_unknown

    def __call__(self, obj):
        return layout.Intron(LayoutController(self.mk_unknown, obj))

class LayoutChain(object):
    def __init__(self, chain, parent):
        self.chain = chain
        self.parent = parent

    def __call__(self, obj):
        key = obj.type.uid if isinstance(obj, mutable.Struct) else type(obj)
        if key in self.chain:
            fn = self.chain[key]
            return layout.Intron(LayoutController(fn, obj))
        else:
            return self.parent(obj)

    def many(self, objs, start=0):
        introns = []
        for index, obj in enumerate(objs, start):
            intron = self(obj)
            intron.reference = (index, index+1)
            introns.append(intron)
        return introns

class LayoutController(object):
    def __init__(self, fn, obj):
        self.fn  = fn
        self.obj = obj
        assert not isinstance(self.fn, layout.Intron)

    def build(self, intron):
        self.fn(intron, self.obj)
