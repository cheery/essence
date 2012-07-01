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
from pluginmanager import require_api_version
from fileformat import load, save, load_from_string, save_to_string
from document import element, copy, copyList, splice, build, collapse, modify
from util import makelist, pull, push, delimit, isstring, isscratch
from essence.layout import string, image, xglue, yglue, group, expando, engine

# def traverse(self, finger): # or this?
#        for index in finger:
#            self = self[index]
#        return self
## application of change record:     undo = do(tree.traverse(finger))
#can_walk_up = lambda tree, finger: len(finger) > 0
#can_walk_left = lambda tree, finger, index: index > 0
#can_walk_right = lambda tree, finger, index: index < len(tree.traverse(finger))
#
#def can_walk_down(tree, finger, index):
#    there = tree.traverse(finger)
#    return 0 <= index < len(there) and isinstance(there[index], node)
