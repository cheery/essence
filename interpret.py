from essence import load
import sys

class closure(object):
    def __init__(self, arguments, body, env):
        self.arguments = arguments
        self.body = body
        self.env = env

    def apply(self, arguments):
        env = dict(zip(self.arguments, arguments))
        env['__parent__'] = self.env
        res = None
        for expr in self.body.array:
            res = interpret(expr, env)
        return res

def interpret(expr, env):
    name = expr.get('name')
    if name == 'int':
        return int(expr.string) # on early versions it's a string.
    if name == 'mul':
        left, right = expr.array
        return left * right
    if name == 'add':
        left, right = expr.array
        return left + right
    if name == 'set':
        left, right = expr.array
        env[left] = interpret(right, env)
    if name == 'variable':
        variable = expr.string
        if not variable in env:
            raise Exception("%r not in %r" % (variable, env))
        return env[variable]
    if name == 'define':
        name, arglist, body = expr.array
        arguments = []
        for argument in arglist.array:
            assert argument.get('name') == 'variable'
            arguments.append(argument.string)
        env[name] = closure(arguments, body, env)
    if name == 'call':
        caller, arguments = expr.array
        caller = interpret(caller, env)
        arguments = [interpret(arg, env) for arg in arguments]
        return caller.apply(arguments)
    raise Exception("unknown clause %r", expr)

program = load(sys.argv[1])
assert program.get('tag') == 's-expr'

env = {}
res = None
for item in program.array:
    res = interpret(item, env)
return res
