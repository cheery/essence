import core, re

title_regex = re.compile(r'([^\x00]+)\x00+([0-9]+)\.([0-9]+)\.([0-9]+)')

str_version = lambda (version): '.'.join(str(i) for i in version)

def read_w_string(fd, Class, tag, b):
    err, sz = must_read(fd, 1<<b)
    if err:
        return err, None
    err, data = must_read(fd, decode_unum(sz))
    if err:
        return err, None
    return None, Class(tag, data.decode('utf-8'))

def read_w_children(fd, Class, tag, b):
    err, sz = must_read(fd, 1<<b)
    if err:
        return err, None
    children = []
    for i in range(decode_unum(sz)):
        err, element = read_element(fd)
        if err:
            return err, None
        children.append(element)
    return None, Class(tag, children)

def read_w_none(fd, Class, tag, b):
    assert b == 0
    return None, Class(tag)

def read_element(fd):
    err, head = must_read(fd, 1)
    if err:
        return err, None
    a, b, dtype = decode_224(head)
    err, sz = must_read(fd, 1<<a)
    if err:
        return err, None
    err, tag = must_read(fd, decode_unum(sz))
    if err:
        return err, None
    decoder, Class = dectable[dtype]
    return decoder(fd, Class, tag.decode('utf-8'), b)

def must_read(fd, count):
    res = fd.read(count)
    if len(res) == count:
        return None, res
    return 'file broken', None

def write_w_children(fd, element):
    count, b = encode_unum(len(element))
    write_element(fd, element, b)
    fd.write(count)
    for child in element:
        enctable[child.dtype](fd, child)

def write_w_string(fd, element):
    data = element.data.encode('utf-8')
    sz, b = encode_unum(len(data))
    write_element(fd, element, b)
    fd.write(sz)
    fd.write(data)
    
def write_element(fd, element, b=0):
    tag = element.tag.encode('utf-8')
    sz, a = encode_unum(len(tag))
    fd.write(encode_224(a, b, element.dtype))
    fd.write(sz)
    fd.write(tag)

def encode_224(a, b, t):
    return chr((t & 15) | ((b << 4) & 3) | ((a << 6) & 3))

def decode_224(ch):
    p = ord(ch)
    return p >> 6 & 3, p >> 4 & 3, p & 15

def decode_unum(s):
    value = 0
    for i, ch in enumerate(s):
        value |= ord(ch) << i*8
    return value

def encode_unum(value):
    s = ''
    s += chr(value & 255)
    if value >> 8 == 0:
        return s, 0
    s += chr(value >> 8 & 255)
    if value >> 16 == 0:
        return s, 1
    s += chr(value >> 16 & 255)
    s += chr(value >> 24 & 255)
    if value >> 32 == 0:
        return s, 2
    s += chr(value >> 32 & 255)
    s += chr(value >> 40 & 255)
    s += chr(value >> 48 & 255)
    s += chr(value >> 56)
    return s, 3

def load_from_stream(fd):
    match = title_regex.match(fd.read(32))
    if match == None:
        return 'cannot recognise file', None
    filetype, major, minor, patch = match.groups()
    version = int(major), int(minor), int(patch)
    semver = str_version(version)
    if core.version[0] > version[0]:
        return 'old major (%s)' % semver, None
    if core.version[0] < version[0]:
        return 'new major (%s)' % semver, None
    if core.version[1] < version[1]:
        return 'new minor (%s)' % semver, None
    if filetype != 'stream document':
        return 'incompatible filetype', None
    err, document = read_element(fd)
    if err:
        return err, document
    if document.dtype != core.document.dtype:
        return 'schema violation', None
    return err, document

def load(path):
    try:
        fd = open(path)
    except IOError, e:
        return str(e), None
    res = load_from_stream(fd)
    fd.close()
    return res

def save(document, path):
    assert isinstance(document, core.document)
    semver = str_version(core.version)
    filetype = 'stream document'
    assert len(semver) + len(filetype) + 1 < 32
    padding = 32 - len(semver) - len(filetype)
    title = filetype + '\x00' * padding + semver
    fd = open(path, 'w')
    fd.write(title)
    write_w_children(fd, document)
    fd.close()

enctable = {
    core.string.dtype: write_w_string,
    core.block.dtype: write_w_children,
    core.lshard.dtype: write_element,
    core.rshard.dtype: write_element,
    core.document.dtype: write_w_children,
}

dectable = {
    core.string.dtype: (read_w_string, core.string),
    core.block.dtype: (read_w_children, core.block),
    core.lshard.dtype: (read_w_none, core.lshard),
    core.rshard.dtype: (read_w_none, core.rshard),
    core.document.dtype: (read_w_children, core.document),
}
