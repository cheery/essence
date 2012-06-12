class TestPlugin(object):
    priority = 1
    def __init__(self, editor):
        pass

    def key(self, context, sel, name, modifiers, ch):
        print (context, sel, name, modifiers, ch)
        return False

    def visualise(self, context, obj, y):
        print (context, obj, y)

plugins = [TestPlugin]
