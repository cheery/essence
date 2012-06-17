from essence.document import node, copy, deserialize
import sys

as_string = lambda obj: ''.join(obj.clusters)

class closure(object):
    def __init__(self, arguments, body, env):
        self.arguments = arguments
        self.body = body
        self.env = env

    def apply(self, arguments):
        env = dict(zip(self.arguments, arguments))
        env['__parent__'] = self.env
        res = None
        for obj in self.body:
            res = interpret(obj, env)
        return res

def interpret(obj, env):
    if not isinstance(obj, node):
        raise Exception("invalid structure")
    if obj.tag == 'int':
        return int(as_string(obj))
    if obj.tag == 'mul':
        acc = 1
        for term in obj.clusters:
            acc *= interpret(term, env)
        return acc
    if obj.tag == 'add':
        acc = 0
        for term in obj.clusters:
            acc += interpret(term, env)
        return acc
    if obj.tag == 'set':
        block = list(obj.clusters)
        value = interpret(block[-1], env)
        for key in block[:-1]:
            env[as_string(key)] = value
        return None
    if obj.tag == 'variable':
        key = as_string(obj)
        if not key in env:
            raise Exception("%r not in %r" % (key, env))
        return env[key]
    if obj.tag == 'define':
        body = list(obj.clusters)
        arguments = []
        if body[0].tag == 'arguments':
            for argument in list(body.pop(0).clusters):
                assert argument.tag == 'variable'
                arguments.append(as_string(argument))
        env[arguments.pop(0)] = closure(arguments, body, env)
        return None
    if obj.tag == 'call':
        block = list(obj.clusters)
        arguments = [interpret(obj, env) for obj in block]
        fn = arguments.pop(0)
        return fn.apply(arguments)
    raise Exception("unknown clause %r" % obj.tag)

program = deserialize(open(sys.argv[1]).read())
assert program.tag == 'root'

env = {}
print "program result:", [interpret(obj, env) for obj in program.clusters][-1]

