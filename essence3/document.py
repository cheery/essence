from essence3.util import clamp

class ListField(object):
    def __init__(self, items, name=''):
        self.items = items
        self.name = name
        self.stamp = 0

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        self.items[key] = value
        self.stamp += 1

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def rename(self, name):
        self.name = name
        self.stamp += 1

    def resolve(self, field):
        if self == field:
            return []
        for subfield in self:
            response = subfield.resolve(field)
            if response != None:
                return [self] + response

    def index(self, field):
        return self.items.index(field)

    def contextof(self, field):
        if self == field:
            return ()
        for index, subfield in enumerate(self):
            if subfield == None:
                continue
            res = subfield.contextof(field)
            if res != None:
                return ((self, index),) + res

class TextField(object):
    def __init__(self, text, name=''):
        self.text = text
        self.name = name
        self.stamp = 0

    def __getitem__(self, key):
        return self.text[key]

    def __setitem__(self, key, value):
        key = key if isinstance(key, slice) else slice(key, key)
        prefix = self.text[:key.start]
        suffix = self.text[key.stop:]
        self.text = prefix + value + suffix
        self.stamp += 1

    def __iter__(self):
        return iter(self.text)

    def __len__(self):
        return len(self.text)

    def rename(self, name):
        self.name = name
        self.stamp += 1

    def resolve(self, field):
        if self == field:
            return []

    def __str__(self):
        return self.text

    def contextof(self, field):
        if self == field:
            return ()
        else:
            return None

class Selection(object):
    def __init__(self, field, head, tail):
        self.field = field
        self.head = head
        self.tail = tail

    def _get_start(self):
        if self.tail < self.head:
            return self.tail
        else:
            return self.head
    def _set_start(self, value):
        if self.tail < self.head:
            self.tail = value
        else:
            self.head = value
    start = property(_get_start, _set_start)

    def _get_stop(self):
        if self.tail < self.head:
            return self.head
        else:
            return self.tail
    def _set_stop(self, value):
        if self.tail < self.head:
            self.head = value
        else:
            self.tail = value
    stop = property(_get_stop, _set_stop)

    def replace(self, data):
        if isinstance(self.field, ListField):
            if self.head == self.tail and not self.field.name.endswith('*'):
                self.move(self.head+1, True)
        self.field[self.start:self.stop] = data
        self.head = self.tail = self.start + len(data)

    def move(self, position, drag):
        index = clamp(0, len(self.field), position)
        if drag:
            self.head = index
        else:
            self.head = self.tail = index
