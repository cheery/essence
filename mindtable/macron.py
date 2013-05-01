"""
    macron
    ~~~~~~

    Small language used by the editor.
"""
from schema.language import Ref, String, Buffer, List, Field, Struct, Constant, Group, LanguageSpec, Language

def match_text(text):
    def _impl(key, modifiers, _text):
        return text == _text
    return _impl

macron_spec = LanguageSpec(u"macron", [
    Constant(u"null"),
    Struct(u"variable", [
        Field(u"name", [String]),
    ]),
    Struct(u"call", [
        Field(u"callee", [Ref(u"expr")]),
        Field(u"arguments", [List([Ref(u"expr")])]),
    ]),
    Struct(u"lambda", [
        Field(u"args", [List([Ref(u"variable")])]),
        Field(u"body", [List([Ref(u"expr")])]),
    ]),
    Group(u"expr", [
        Ref(u"call"),
        Ref(u"variable"),
        Ref(u"lambda"),
        Ref(u"null"),
    ]),
    Struct(u"macron", [
        Field(u"program", [List([Ref(u"expr")])]),
    ])
])

macron = Language(macron_spec)
macron.templates1 = {
    u"variable": (lambda head: macron.Variable(head)     ),
    u"call":     (lambda head: macron.Call    (head, []) ),
    u"lambda":   (lambda head: macron.Lambda  (head, []) ),
    u"macron":   (lambda head: macron.Macron  (head)     ),
}
macron.templates0 = {
    u"variable": (lambda: macron.Variable(u"")           ),
    u"call":     (lambda: macron.Call(macron.Null, [])   ),
    u"lambda":   (lambda: macron.Lambda([], [])          ),
    u"macron":   (lambda: macron.Macron([])              ),
}
macron.builders = [
    (0, match_text('('), u"call"),
    (0, match_text('{'), u"lambda"),
]

macron.hierarchy = [u"lambda", u"call", u"variable"]

class Scope(object):
    def __init__(self, parent):
        self.parent = parent
        self.local = {}

    def __getitem__(self, key):
        return self.local[key] if key in self.local else self.parent[key]

    def __setitem__(self, key, value):
        self.local[key] = value

class MacronLambda(object):
    def __init__(self, lamb, env):
        self.lamb = lamb
        self.env  = env

    def __call__(self, *argv):
        env = Scope(self.env)
        for arg, value in zip(self.lamb.arguments, argv):
            env[arg.name] = value
        res = None
        for expr in self.lamb.body:
            res = interpret(expr, env)
        return res

def interpret(expr, env):
    if expr.meta == macron.Variable:
        return env[expr.name]
    if expr.meta == macron.Call:
        callee = interpret(expr.callee, env)
        return callee(*[interpret(arg, env) for arg in expr.arguments])
    if expr.meta == macron.Lambda:
        return MacronLambda(expr, env)
    raise Exception("unknown expr %r" % expr)

def _print(*a):
    print ', '.join(map(repr, a))

if __name__ == '__main__':
    env = {
        'print': _print,
        'hello': "Hello World",
    }
    m_print = macron.Variable("print")
    m_hello = macron.Variable("hello")
    print macron.Lambda([], [])
    print macron.Call(m_hello, [])

    print interpret(
        macron.Call(m_print, [m_hello]),
        env
    )
