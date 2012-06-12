from os import listdir
from os.path import splitext, join, dirname
from imp import find_module, load_module

def list_plugins(directory):
    names = set()
    for name in listdir(directory):
        if name.startswith('.'):
            continue
        names.add(splitext(name)[0])
    return names

def load_all_plugins(directories):
    plugins = []
    for directory in directories:
        for name in list_plugins(directory):
            fd, pathname, desc = find_module(name, [directory])
            plugin = load_module(name, fd, pathname, desc)
            plugins.append(plugin)
    return plugins

default_plugin_directory = join(dirname(__file__), 'plugins')
