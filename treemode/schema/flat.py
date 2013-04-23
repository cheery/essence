from base import Struct, Meta, Constant

def read_byte(fd):
    return ord(fd.read(1))

def write_byte(fd, value):
    fd.write(chr(value & 255))

def read_le16(fd):
    out = 0
    for offset, ch in zip(range(0, 16, 8), fd.read(2)):
        out |= ord(ch) << offset
    return out

def write_le16(fd, value):
    shf = (value >> i for i in range(0, 16, 8))
    fd.write(''.join(chr(x & 255) for x in shf))

def read_le32(fd):
    out = 0
    for offset, ch in zip(range(0, 32, 8), fd.read(4)):
        out |= ord(ch) << offset
    return out

def write_le32(fd, value):
    shf = (value >> i for i in range(0, 32, 8))
    fd.write(''.join(chr(x & 255) for x in shf))

def read_raw(fd, length):
    return fd.read(length)

def write_raw(fd, value):
    fd.write(value)

def read_record(fd):
    code = read_le16(fd)
    length = read_le16(fd)
    if code == 0x0: # constant/meta decl
        cols = read_raw(fd, length).decode('utf-8').split(':')
        if len(cols) == 1:
            return 'decl', Constant(cols[0])
        else:
            return 'decl', Meta(cols[0], list(cols[1:]))
    elif code == 0x1: # buffer
        return 'data', read_raw(fd, length)
    elif code == 0x2: # string
        return 'data', read_raw(fd, length).decode('utf-8')
    elif code == 0x3: # list
        return 'list', length
    else:
        return 'block', code - 0x4

def write_decl(fd, decl):
    decl = unicode(decl).encode('utf-8')
    write_le16(fd, 0x0)
    write_le16(fd, len(decl))
    write_raw(fd, decl)

def write_data(fd, data):
    if isinstance(data, unicode):
        data = data.encode('utf-8')
        write_le16(fd, 0x2)
    else:
        write_le16(fd, 0x1)
    write_le16(fd, len(data))
    write_raw(fd, data)

def push_decl(fd, decls, decl):
    if not decl in decls:
        write_decl(fd, decl)
        decls[decl] = decls[None]
        decls[None] += 1
    return decls[decl] + 0x4

def read_block(fd, decls, decl):
    if isinstance(decl, Constant):
        return decl
    struct = Struct(decl, [])
    for name in decl.names:
        which, data = read_record(fd)
        while which == 'decl':
            decls.append(data)
            which, data = read_record(fd)
        if which == 'block':
            item = read_block(fd, decls, decls[data])
        elif which == 'list':
            item = read_list(fd, decls, length=data)
        elif which == 'data':
            item = data
        else:
            raise Exception("bad record")
        struct.data.append(item)
    return struct

def write_block(fd, decls, block):
    if isinstance(block, Constant):
        uid = push_decl(fd, decls, block)
        write_le16(fd, uid)
        write_le16(fd, 0)
    else:
        uid = push_decl(fd, decls, block.meta)
        count = len(block.meta.names)
        write_le16(fd, uid)
        write_le16(fd, count)
        for i in range(count):
            item = block[i]
            if isinstance(item, Struct):
                write_block(fd, decls, item)
            elif isinstance(item, list):
                write_list(fd, decls, item)
            else:
                write_data(fd, item)

def read_list(fd, decls, length):
    out = []
    for index in range(length):
        which, data = read_record(fd)
        while which == 'decl':
            decls.append(data)
            which, data = read_record(fd)
        if which == 'block':
            item = read_block(fd, decls, decls[data])
            out.append(item)
        else:
            raise Exception("bad record")
    return out

def write_list(fd, decls, data):
    write_le16(fd, 0x3)
    write_le16(fd, len(data))
    for item in data:
        write_block(fd, decls, item)

version  = "0.0"
mimetype = "struct/flat"
padding  = '.'*(32 - len(version) - len(mimetype))
header   = mimetype + padding + version

def load(fd):
    if fd.read(32) != header:
        raise Exception("Invalid format")
    decls = []
    which, data = read_record(fd)
    while which == 'decl':
        decls.append(data)
        which, data = read_record(fd)
    if which != 'block':
        raise Exception("bad file begin")
    root = read_block(fd, decls, decls[data])
    fd.close()
    return root

def save(fd, root):
    fd.write(header)
    write_block(fd, {None:0}, root)
    fd.close()

load_file = lambda path:       load(open(path, 'r'))
save_file = lambda path, root: save(open(path, 'w'), root)

if __name__ == "__main__":
    Fruit = Meta(u'fruit', [
        u"name"
    ])

    Meal = Meta(u'meal', [
        u"fruits"
    ])

    meal = Meal([
        Fruit(u"banana"),
        Fruit(u"peach"),
        Fruit(u"orange"),
        Meal([
            Fruit(u"lemon"),
            Fruit(u"grape"),
        ]),
        Fruit(u"kiwi"),
    ])

    save_file("fruits", meal)

    meal = load_file("fruits")

    print meal
    print "%r" % unicode(meal.meta)
    print "%r" % unicode(meal.fruits[0].meta)
