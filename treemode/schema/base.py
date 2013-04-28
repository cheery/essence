"""
    schema.base
    ~~~~~~~~~~~

    This particular structure puts accessibility
    before everything else. Yet it can be
    serialized/deserialized from a file.

    Formats are described in an another module.

    To understand this schema, go to the demonstration.
"""

class Struct(object):
    __slots__ = ('meta', 'data', 'proxy')
    unshadow = ('meta', 'data', 'proxy', 'copy')
    def __init__(self, meta, data):
        self.meta = meta
        self.data = data
        self.proxy = None

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __getattr__(self, name):
        if name in Struct.unshadow:
            raise AttributeError(name)
        else:
            index = self.meta.names.index(name)
            return self[index]

    def __setattr__(self, name, value):
        if name in Struct.unshadow:
            super(Struct, self).__setattr__(name, value)
        else:
            index = self.meta.names.index(name)
            self[index] = value

    def copy(self):
        duplicate = []
        for record in self:
            if isinstance(record, list):
                record = list(record)
            elif isinstance(record, Struct):
                record = record.copy()
            duplicate.append(record)
        return Struct(self.meta, duplicate)

    def __repr__(self):
        return "%s(%s)" % (self.meta.name, ', '.join(repr(item) for item in self))

class Meta(object):
    def __init__(self, name, names):
        self.name = name
        self.names = names

    def __call__(self, *args):
        assert len(self.names) == len(args)
        return Struct(self, list(args))

    def __repr__(self):
        return "Meta(%s, %r)" % (self.name, self.names)

    def __str__(self):
        return ':'.join([self.name] + self.names)

    def __cmp__(self, other):
        return cmp(str(self), str(other))

class Constant(object):
    def __init__(self, name):
        self.name = name
        self.proxy = None

    def __str__(self):
        return self.name

# Small demonstration.
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
        Fruit(u"kiwi"),
    ])

    assert meal.fruits[0].name == u"banana"

    new_meal = meal.copy()
    new_meal.fruits.append(Fruit(u'apple'))

    print meal
    print new_meal
    print meal.meta

    # If you modify a field interactively, you'd do this:
    # selection = mutator(meal, 0)
    # The mutator is introduced in an another module.
