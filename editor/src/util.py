import os, stat

def convertify(converter=list):
    def _decorator(fun):
        def _wrapper(*args, **kwargs):
            return converter(fun(*args, **kwargs))
        return _wrapper
    return _decorator

def get_mtime(name):
    return os.stat(name)[stat.ST_MTIME]

@convertify(converter=set)
def getfiles(path):
    for root, dirs, names in os.walk(path):
        for name in names:
            filename = os.path.join(root, name)
            if name.startswith('.'): continue
            if name.endswith('~'): continue
            yield root, name, get_mtime(filename)
