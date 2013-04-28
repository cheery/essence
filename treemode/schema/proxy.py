"""
    schema.proxy
    ~~~~~~~~~~~~

    Proxies do not reference structures
    directly, but they can represent a
    location in the structure.
"""
from base import Struct, Constant

class RootProxy(object):
    def __init__(self, info):
        self.info = info

    def unroll(self):
        return self.info, []

class Proxy(object):
    def __init__(self, parent, index):
        self.parent = parent
        self.index  = index

    def unroll(self):
        info, ctx = self.parent.unroll()
        ctx.append(self.index)
        return info, ctx

    @classmethod
    def root(cls, info, struct):
        struct.proxy = proxy = RootProxy(info)
        for index, child in enumerate(struct):
            cls.reproxy(proxy, index, child)
        return proxy

    @classmethod
    def reproxy(cls, parent, index, record):
        current = cls(parent, index)
        if isinstance(record, (Struct, Constant)):
            record.proxy = current
        if isinstance(record, (Struct, list)):
            for index, child in enumerate(record):
                cls.reproxy(current, index, child)
        return current
