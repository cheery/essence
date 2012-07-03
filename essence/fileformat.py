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
"""
    essence.fileformat
    ~~~~~~~~~~~~~~~~~~

    File format for essence.
"""
import document, StringIO

def test():
    import zlib
    root = document.element('root', [
        document.star([
            'huh',
        ])
    ])
    pre = len(root)
    s = save_to_string(root)
    print "string length=%i, compressed=%i" % (len(s), len(zlib.compress(s)))
    root = load_from_string(s)
    assert len(root) == pre
    assert root.name == 'root'
    assert root.holes[0].a == ['huh']

def load(filename):
    with open(filename, 'r') as fd:
        fd = ByteStream(fd)
        root = fd.read_element()
    return root
    
def save(filename, element):
    with open(filename, 'w') as fd:
        fd = ByteStream(fd)
        fd.write_element(element)

def load_from_string(string):
    fd = ByteStream(StringIO.StringIO(string))
    return fd.read_element()

def save_to_string(element):
    string = StringIO.StringIO()
    fd = ByteStream(string)
    fd.write_element(element)
    return string.getvalue()

class ByteStream(object):
    def __init__(self, fd):
        self.fd = fd

    def read_bytes(self, count):
        return [ord(ch) for ch in self.fd.read(count)]

    def write_bytes(self, *data):
        self.fd.write(''.join(chr(ch) for ch in data))

    def read(self, count):
        return self.fd.read(count)

    def write(self, data):
        self.fd.write(data)

    def write_uint32(self, num):
        self.write_bytes(
            num >>  0 & 255,
            num >>  8 & 255,
            num >> 16 & 255,
            num >> 24 & 255,
        )

    def read_uint32(self):
        b0, b1, b2, b3 = self.read_bytes(4)
        return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)

    def read_string(self):
        length = self.read_uint32()
        string = self.read(length)
        return string.decode('utf-8')

    def write_string(self, string):
        string = string.encode('utf-8')
        self.write_uint32(len(string))
        self.write(string)

    def read_attributes(self):
        res = {}
        length = self.read_uint32()
        for i in range(length):
            key = self.read_string()
            value = self.read_string()
            res[key] = value
        return res

    def write_attributes(self, attrs):
        self.write_uint32(len(attrs))
        for key, value in attrs.items():
            self.write_string(key)
            self.write_string(value)

    def read_item(self):
        type = self.read_uint32()
        if type == 0:
            return self.read_string()
        if type == 1:
            return self.read_element()
        if type == 2:
            return None

    def write_item(self, obj):
        if obj is None:
            self.write_uint32(2)
        elif isinstance(obj, document.element):
            self.write_uint32(1)
            self.write_element(obj)
        else:
            self.write_uint32(0)
            self.write_string(obj)

    def read_hole(self):
        type = self.read_uint32()
        if type == 0:
            return document.dot(self.read_item())
        if type == 1:
            length = self.read_uint32()
            blob = []
            for i in range(length):
                blob.append(self.read_item())
            return document.star(blob)

    def write_hole(self, hole):
        if isinstance(hole, document.dot):
            self.write_uint32(0)
            self.write_item(hole.a)
        else:
            self.write_uint32(1)
            self.write_uint32(len(hole.a))
            for obj in hole.a:
                self.write_item(obj)

    def write_element(self, element):
        self.write_string(element.name)
        self.write_uint32(len(element.holes))
        for hole in element.holes:
            self.write_hole(hole)
        
        #self.write_attributes(element.attributes)
        #self.write_clusters(list(element.clusters))

    def read_element(self):
        name = self.read_string()
        length = self.read_uint32()
        holes = []
        for i in range(length):
            holes.append(self.read_hole())
        return document.element(name, holes)

        #attributes = self.read_attributes()
        #children = self.read_elements()
        #return document.element(children, attributes)

if __name__ == '__main__':
    test()
