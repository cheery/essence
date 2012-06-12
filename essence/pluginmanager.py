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

def load_all_plugins(directories):
    plugins = []
    for directory in directories:
        for name in list_plugins(directory):
            fd, pathname, desc = find_module(name, [directory])
            plugin = load_module(name, fd, pathname, desc)
            plugins.append(plugin)
    return plugins

default_plugin_directory = join(dirname(__file__), 'plugins')
