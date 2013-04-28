from base import Struct, Meta, Constant
from proxy import RootProxy, Proxy
from mutator import Mutator, Selection

def roll(current, ctx):
    for index in ctx:
        current = current[index]
    return current
