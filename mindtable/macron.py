"""
    macron
    ~~~~~~

    Small language used by the editor.
"""
import os
from schema.base import Constant, StructType, Struct
from schema.flatfile import load_file
from schema.language import Synthetizer

def ugly_print(*args):
    print ','.join( map(repr, args) )

def in_module(path):
    return os.path.join(os.path.dirname(__file__), path)

language = load_file(in_module("scripts/macron.language"))
syn = Synthetizer(language)

class Scope(object):
    def __init__(self, parent):
        self.parent = parent
        self.local = {}

    def __getitem__(self, key):
        return self.local[key] if key in self.local else self.parent[key]

    def __setitem__(self, key, value):
        self.local[key] = value

def ist(obj, name):
    if isinstance(obj, Struct):
        return obj.type == syn[name]
    else:
        return obj == syn[name]

class Lambda(object):
    def __init__(self, lam, env):
        self.lam = lam
        self.env = env

    def __call__(self, *argv):
        env = Scope(self.env)
        for index, arg in enumerate(self.lam.arguments):
            if index < len(argv):
                env[arg.name] = argv[index]
            else:
                env[arg.name] = None
        for expr in self.lam.body:
            if ist(expr, 'return'):
                return interpret(expr.expr, env)
            interpret(expr, env)
        return None

def interpret(expr, env):
    if expr == syn['true']:
        return True
    if expr == syn['false']:
        return False
    if expr == syn['null']:
        return None
    if ist(expr, 'list'):
        out = []
        for subexpr in expr.body:
            out.append(interpret(subexpr, env))
        return out
    if ist(expr, 'dictionary'):
        out = {}
        for item in expr.items:
            out[interpret(item.key, env)] = interpret(item.value, env)
        return out
    if ist(expr, 'condition'):
        for rule in expr.body:
            if interpret(rule.when, env):
                return interpret(rule.then, env)
        return None
    if ist(expr, 'while'):
        inblock = Scope(env)
        while interpret(expr.condition, env):
            for subexpr in expr.body:
                interpret(subexpr, inblock)
        return None
    if ist(expr, 'foreach'):
        inblock = Scope(env)
        for value in interpret(expr.iterator, env):
            inblock[expr.name] = value
            for subexpr in expr.body:
                interpret(subexpr, inblock)
        return None
    if expr.type == syn['attribute']:
        return getattr(interpret(expr.expr, env), expr.name)
    if expr.type == syn['let']:
        env[expr.left.name] = value = interpret(expr.right, env)
        return value
    if expr.type == syn['string']:
        return expr.value
    if expr.type == syn['variable']:
        return env[expr.name]
    if expr.type == syn['call']:
        callee = interpret(expr.callee, env)
        return callee(*[interpret(arg, env) for arg in expr.arguments])
    if expr.type == syn['lambda']:
        return Lambda(expr, env)
    raise Exception("unknown expr %r" % expr)

def run(source, glob):
    ret = None
    module = Scope(glob)
    ret = None
    for expr in source.program:
        ret = interpret(expr, module)
    return ret, module

glob = {
    u"print": ugly_print,
}

if __name__=="__main__":
    test = load_file('macron_test.macron')

    ret, module = run(test, glob)
    print "return value:", ret
    print "module locals:", module.local

#def match_text(text):
#    def _impl(key, modifiers, _text):
#        return text == _text
#    return _impl
#
#macron_spec = LanguageSpec(u"macron", [
#    Constant(u"null"),
#    Struct(u"variable", [
#        Field(u"name", [String]),
#    ]),
#    Struct(u"call", [
#        Field(u"callee", [Ref(u"expr")]),
#        Field(u"arguments", [List([Ref(u"expr")])]),
#    ]),
#    Struct(u"lambda", [
#        Field(u"args", [List([Ref(u"variable")])]),
#        Field(u"body", [List([Ref(u"expr")])]),
#    ]),
#    Group(u"expr", [
#        Ref(u"call"),
#        Ref(u"variable"),
#        Ref(u"lambda"),
#        Ref(u"null"),
#    ]),
#    Struct(u"macron", [
#        Field(u"program", [List([Ref(u"expr")])]),
#    ])
#])
#
#macron = Language(macron_spec)
#macron.templates1 = {
#    u"variable": (lambda head: macron.Variable(head)     ),
#    u"call":     (lambda head: macron.Call    (head, []) ),
#    u"lambda":   (lambda head: macron.Lambda  (head, []) ),
#    u"macron":   (lambda head: macron.Macron  (head)     ),
#}
#macron.templates0 = {
#    u"variable": (lambda: macron.Variable(u"")           ),
#    u"call":     (lambda: macron.Call(macron.Null, [])   ),
#    u"lambda":   (lambda: macron.Lambda([], [])          ),
#    u"macron":   (lambda: macron.Macron([])              ),
#}
#macron.builders = [
#    (0, match_text('('), u"call"),
#    (0, match_text('{'), u"lambda"),
#]
#
#macron.hierarchy = [u"lambda", u"call", u"variable"]
#
#
#
#def _print(*a):
#    print ', '.join(map(repr, a))
#
#if __name__ == '__main__':
#    env = {
#        'print': _print,
#        'hello': "Hello World",
#    }
#    m_print = macron.Variable("print")
#    m_hello = macron.Variable("hello")
#    print macron.Lambda([], [])
#    print macron.Call(m_hello, [])
#
#    print interpret(
#        macron.Call(m_print, [m_hello]),
#        env
#    )
