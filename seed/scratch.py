from schema import immutable, fileformat_flat
import os

mtime = os.path.getmtime("scratch.flat")
data = fileformat_flat.load_file("scratch.flat", immutable)
data.set_info({
    "filename":"scratch.flat",
    "mtime":mtime,
})

print data

print data[0].callee
print data[0].arguments

print data[0].arguments.proxy.unroll()
