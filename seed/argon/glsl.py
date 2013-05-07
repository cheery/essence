import re
record = re.compile(r"^(\w+):")

def parse(source):
    name    = None
    shared  = []
    lines   = shared
    for line in source.splitlines():
        match = record.match(line)
        if match:
            if name != None:
                yield name, '\n'.join(shared + lines)
            name = match.groups()[0]
            lines = []
        else:
            lines.append(line)
    if name != None:
        yield name, '\n'.join(shared + lines)
