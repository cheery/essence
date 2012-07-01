# This file is part of Essential Editor Research Project (EERP)
#
# EERP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EERP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EERP.  If not, see <http://www.gnu.org/licenses/>.
from essence import load, makelist
import sys

evaluators = {}
def defname(name, evaluator):
    evaluators[name] = evaluator

def ev_add(exp, env):
    left, right = list_of_values(exp, env)
    return left + right
defname('add', ev_add)

def ev_sub(exp, env):
    left, right = list_of_values(exp, env)
    return left - right
defname('sub', ev_sub)

def ev_mul(exp, env):
    left, right = list_of_values(exp, env)
    return left * right
defname('mul', ev_mul)

def ev_equal(exp, env):
    left, right = list_of_values(exp, env)
    return left == right
defname('equal', ev_equal)    

def ev_call(exp, env):
    callee, arguments = exp.array
    assert arguments.get('name') == 'arguments'
    arguments = list_of_values(arguments, env)
    procedure = evaluate(callee, env)
    return appl(procedure, arguments)
defname('call', ev_call)

def ev_string(exp, env):
    return exp.string
defname('string', ev_string)

def ev_getitem(exp, env):
    left, right = list_of_values(exp, env)
    return left[right]
defname('getitem', ev_getitem)

def ev_variable(exp, env):
    return env[exp.string]
defname('variable', ev_variable)

def ev_let(exp, env):
    left, right = exp.array
    assert left.get('name') == 'variable'
    env[left.string] = evaluate(right, env)
defname('let', ev_let)

def ev_set(exp, env):
    left, right = exp.array
    assert left.get('name') == 'variable'
    env.deepset(left.string, evaluate(right, env))
defname('set', ev_set)

def ev_function(exp, env):
    bindings, body = exp.array
    assert bindings.get('name') == 'bindings'
    return compound(bindings, body, env)
defname('function', ev_function)

def ev_prog(exp, env):
    values = list_of_values(exp, env)
    return values[-1] if len(values) > 0 else None
defname('prog', ev_prog)

def ev_if(exp, env):
    exp = list(exp.array)
    if len(exp) == 3:
        cond, then, otherwise = exp
    if len(exp) == 2:
        cond, then = exp
        otherwise = None
    if evaluate(cond, env) not in (False, None):
        return evaluate(then, env)
    elif otherwise != None:
        return evaluate(otherwise, env)
defname('if', ev_if)

def ev_list(exp, env):
    return list_of_values(exp, env)
defname('list', ev_list)

def ev_int(exp, env):
    return int(exp.string)
defname('int', ev_int)

def ev_env(exp, env):
    return env
defname('env', ev_env)

def evaluate(exp, env):
    name = exp.get('name')
    if name in evaluators:
        return appl(evaluators[name], [exp, env])
    raise Exception("Unknown expression type -- EVAL %s" % name)

def appl(procedure, arguments):
    if isinstance(procedure, compound):
        return procedure.appl(arguments)
    if callable(procedure):
        return procedure(*arguments)
    raise Exception("Unknown procedure type -- APPLY %s" % procedure)

@makelist
def list_of_values(exps, env):
    for exp in exps.array:
        yield evaluate(exp, env)

class scope(object):
    def __init__(self, parent):
        self.parent = parent
        self.bound = {}

    def __setitem__(self, key, value):
        self.bound[key] = value

    def deepset(self, key, value):
        if key in self.bound:
            self[key] = value
        else:
            self.parent.deepset(key, value)

    def __getitem__(self, key):
        if key in self.bound:
            return self.bound[key]
        return self.parent[key]

    def get(self, key):
        if key in self.bound:
            return self.bound[key]
        return self.parent.get(key)

    def update(self, *a, **kw):
        self.bound.update(*a, **kw)

def bind(env, binding, arguments):
    name = binding.get('name')
    if name == 'variable':
        env[binding.string] = arguments.pop(0)
    else:
        raise Exception("Unknown binding type -- BIND %s" % name)

class compound(object):
    def __init__(self, bindings, body, env):
        self.bindings = bindings
        self.body = body
        self.env = env

    def appl(self, arguments):
        env = scope(self.env)
        for binding in self.bindings.array:
            bind(env, binding, arguments)
        return list_of_values(self.body, env)[-1]

glob = scope(None)
glob.update([
    ('list-of-values', list_of_values),
    ('apply', appl),
    ('evaluate', evaluate),
    ('defname', defname),
    ('load', load),
])


program = load(sys.argv[1])
assert program.get('name') == 'program'
# assert program.get('language') == 'coffeesipper'
#.. for now

env = scope(glob)
res = None
for expr in program.array:
    res = evaluate(expr, env)
print res
