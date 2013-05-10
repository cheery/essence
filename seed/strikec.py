"""
    strikec
    ~~~~~~~

    strike compiler
"""
import os
from llvm import *
from llvm.core import *
from llvm.ee import *

from schema import immutable, fileformat_flat
from schema.immutable import istype

int_t = Type.int()
main_t = Type.function(int_t, [])

filename = "strike_test.flat"

mtime = os.path.getmtime(filename)
source = fileformat_flat.load_file(filename, immutable)
source.set_info({
    "filename":filename,
    "mtime":mtime,
})

runtime_module = Module.from_assembly(file("strikert.s", 'r'))

main_module = Module.new("main")
main_module.link_in(runtime_module)


main_fn = main_module.add_function(main_t, "main")

main_fn_entry = main_fn.append_basic_block("entry")

build = Builder.new(main_fn_entry)

class CompilationError(Exception):
    def __init__(self, proxy, message):
        self.proxy = proxy
        self.message = message

    def __str__(self):
        info, path = self.proxy.unroll()
        path_str = ''.join("[%i]" % index for index in path)
        return "%r%s: %s" % (info, path_str, self.message)

def compile_expr(build, expr, env):
    if istype(expr, u"number:value"):
        return Constant.int(int_t, int(expr.value))
    if istype(expr, u"call:callee:arguments"):
        assert istype(expr.callee, u"variable:name")
        callee_fn = main_module.get_function_named(expr.callee.name)
        if len(callee_fn) != len(expr.arguments):
            raise CompilationError(expr.arguments.proxy, "incorrect argument count")
        argv = [compile_expr(build, argument, env) for argument in expr.arguments]
        return build.call(callee_fn, argv)
    if istype(expr, u"variable:name"):
        if expr.name in env:
            return env[expr.name]
        else:
            raise CompilationError(expr.proxy, "out of scope")
    if istype(expr, u"assign:slot:value"):
        assert istype(expr.slot, u"variable:name")
        value = compile_expr(build, expr.value, env)
        env[expr.slot.name] = value
        return value
    if istype(expr, u"return:value"):
        value = compile_expr(build, expr.value, env)
        build.ret(value)
        return value
    raise CompilationError(expr.proxy, "unknown statement")

scope = {
    "print_i32": main_module.get_function_named("print_i32"),
    "mul_i32": main_module.get_function_named("mul_i32"),
}

for stmt in source:
    compile_expr(build, stmt, scope)

build.ret(Constant.int(int_t, 0))

main_module.verify()

print "program was compiled, evaluating program"

ex = ExecutionEngine.new(main_module)

retval = ex.run_function(main_fn, [])

print "program output:", retval.as_int()
