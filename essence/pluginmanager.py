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

def load_all_plugins(directories, *a, **kw):
    plugins = []
    for directory in directories:
        for name in list_plugins(directory):
            fd, pathname, desc = find_module(name, [directory])
            try:
                plugin = load_module(name, fd, pathname, desc)
                if not hasattr(plugin, 'plugins'):
                    continue
                for plugin in plugin.plugins:
                    plugins.append(plugin(*a, **kw))
            except APIVersionMismatch, e:
                print "%s: %r" % (pathname, e)
    plugins.sort(key=lambda obj: obj.priority)
    return plugins

default_plugin_directory = join(dirname(__file__), 'plugins')

major = _major = 2
minor = _minor = 0
patch = 0

class APIVersionMismatch(Exception):
    pass

def require_api_version(major, minor):
    if _major != major or _minor < minor:
        raise APIVersionMismatch()
