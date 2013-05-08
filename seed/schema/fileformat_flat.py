class StreamReader(object):
    def __init__(self, fd, debug=False):
        self.fd = fd
        self.debug = debug

    def b(self):
        out = ord(self.fd.read(1))
        if self.debug:
            print 'b', out
        return out

    def le16(self):
        out = 0
        for offset, ch in zip(range(0, 16, 8), self.fd.read(2)):
            out |= ord(ch) << offset
        if self.debug:
            print 'le16', out
        return out

    def le32(self):
        out = 0
        for offset, ch in zip(range(0, 32, 8), self.fd.read(4)):
            out |= ord(ch) << offset
        if self.debug:
            print 'le32', out
        return out

    def raw(self, length):
        out = self.fd.read(length)
        if self.debug:
            print 'raw', repr(out)
        return out

class StreamWriter(object):
    def __init__(self, fd):
        self.fd = fd

    def b(self, value):
        self.fd.write(chr(value & 255))

    def le16(self, value):
        shf = (value >> i for i in range(0, 16, 8))
        self.fd.write(''.join(chr(x & 255) for x in shf))

    def le32(self, value):
        shf = (value >> i for i in range(0, 32, 8))
        self.fd.write(''.join(chr(x & 255) for x in shf))

    def raw(self, value):
        self.fd.write(value)

def read_block(read, module, types, allow_decl=True):
    code = read.le16()
    length = read.le16()
    if code == 0x0: # StructType declaration
        assert allow_decl
        uid = read.raw(length).decode('utf-8')
        types.append( module.StructType(uid) )
        return read_block(read, module, types, False)
    elif code == 0x1: # Buffer (let it crash)
        return module.Buffer(read.raw(length))
    elif code == 0x2: # String
        return module.String(read.raw(length).decode('utf-8'))
    elif code == 0x3: # List
        out = []
        for i in range(length):
            out.append( read_block(read, module, types) )
        return module.List(out)
    else:
        typecode = code - 0x4
        struct_type = types[typecode]
        out = []
        for i in range( len(struct_type.labels) ):
            out.append( read_block(read, module, types) )
        return module.Struct(struct_type, out)

def save_struct_type(write, typecodes, struct_type):
    if struct_type in typecodes:
        return typecodes[struct_type]
    else:
        raw_uid = struct_type.uid.encode('utf-8')
        write.le16(0x0)
        write.le16(len(raw_uid))
        write.raw( raw_uid )
        typecodes[struct_type] = typecode = typecodes[None] + 0x4
        typecodes[None] += 1
        return typecode

def write_block(write, module, typecodes, block):
    if module.isstruct(block):
        typecode = save_struct_type(write, typecodes, block.type)
        write.le16(typecode)
        write.le16(1337)
        for subblock in block:
            write_block(write, module, typecodes, subblock)
    elif module.islist(block):
        write.le16(0x3)
        write.le16(len(block))
        for subblock in block:
            write_block(write, module, typecodes, subblock)
    elif module.isstring(block):
        data = module.getdata(block).encode('utf-8')
        write.le16(0x2)
        write.le16(len(data))
        write.raw(data)
    elif module.isbuffer(block):
        data = module.getdata(block)
        write.le16(0x1)
        write.le16(len(data))
        write.raw(data)
    else:
        raise Exception("I don't know what this is")

version  = "0.1"
mimetype = "struct/flat"
padding  = '.'*(32 - len(version) - len(mimetype))
header   = mimetype + padding + version

def load(fd, module):
    read = StreamReader(fd)
    if read.raw(32) != header:
        raise Exception("Invalid format")
    length = read.le32()
    types = []
    out = []
    for i in range(length):
        out.append( read_block(read, module, types) )
    fd.close()
    return module.Document(out)

def save(fd, module, document):
    typecodes = {None:0}
    write = StreamWriter(fd)
    write.raw(header)
    write.le32(len(document))
    for block in document:
        write_block(write, module, typecodes, block)
    fd.close()

load_file = lambda path, module:       load(open(path, 'r'), module)
save_file = lambda path, module, root: save(open(path, 'w'), module, root)
