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
from essence.layout import StringFrame, BlockFrame

precedence = {
    'mul': 20,
    'add': 10,
}

#def parent_precedence

class TestPlugin(object):
    priority = 1
    def __init__(self, editor):
        self.add_spacer = editor.font('+')
        self.mul_spacer = editor.font('*')
        self.lparen = editor.font('(')
        self.rparen = editor.font(')')

    def key(self, context, sel, name, modifiers, ch):
        #print (context, sel, name, modifiers, ch)
        return False

    def visualise(self, context, obj):
        pass

plugins = [TestPlugin]
