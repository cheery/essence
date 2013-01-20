class Symbolic(object):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def text(self):
        return '%s = %s' % (self.name, ' '.join(self.fields))

class Group(object):
    def __init__(self, name, group):
        self.name = name
        self.group = group

    def text(self):
        return '%s = %s' % (self.name, ' | '.join(self.group))

class Data(object):
    def __init__(self, name, which):
        self.name = name
        self.which = which

    def text(self):
        return '%s = {%s}' % (self.name, self.which)

class Language(object):
    def __init__(self, rules, root):
        self.rules = rules
        self.language = dict((rule.name, rule) for rule in rules)
        self.root = root

    def text(self):
        return '\n'.join(rule.text() for rule in self.rules)
