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
from essence import require_api_version
require_api_version(major=0, minor=0)
from essence import string, image, xglue, yglue, group, expando, delimit
from essence.ui import composite, color, empty

precedence = {
    'mul': 20,
    'add': 10,
}

red = color(0xFF, 0x00, 0x00)
blue = color(0x00, 0x00, 0xFF)
gray = color(0x80, 0x80, 0x80)


#def parent_precedence(sel, ):

class TestPlugin(object):
    priority = 1
    def __init__(self, editor):
        self.font = editor.font
#        self.add_spacer = editor.font('+')
#        self.mul_spacer = editor.font('*')
#        self.lparen = editor.font('(')
#        self.rparen = editor.font(')')

    def keyboard_hook(self, mode, key, modifiers, ch): #context, sel, name, modifiers, ch):
#        if 'shift' in modifiers and key == 'a':
        if ch == '+':
            mode.build('add')
        if ch == '*':
#        elif 'shift' in modifiers and key == 'm':
            mode.build('mul')
        elif ch.isdigit() and mode.context[-1].tag != 'int':
            mode.build('int')
            return False
        else:
            return False
        return True
        #print (context, sel, name, modifiers, ch)

    def algebraic_wrap(self, context, tag, ch, gen_children):
        children = []
        for last, frame in ilast(gen_children()):
            if last is not None:
                marker = String(ch, self.font)
                marker.label.mul(red)
                children.extend([
                    Glue(8, 0),
                    marker,
                    Glue(8, 0),
                ])
            children.append(frame)

        if len(children) < 2:
            marker = String(ch, self.font)
            marker.label.mul(red)
            children.append(marker)

        top = None if len(context) == 0 else context[-1]
        if precedence.get(top, 0) > precedence.get(tag, 0) or len(children) == 2:
            left = String('(', self.font)
            right = String(')', self.font)
            left.label.mul(gray)
            right.label.mul(gray)
            return [left] + children + [right]
        else:
            return children

    def layout_hook(self, obj, context, gen_children):
        if isinstance(obj, node):
            if obj.tag == 'int':
                return Padding(Row(gen_children(), iscluster=True), left=8, right=8)
            if obj.tag == 'mul':
                return Row(self.algebraic_wrap(context, obj.tag, '*', gen_children), iscluster=True)
            if obj.tag == 'add':
                return Row(self.algebraic_wrap(context, obj.tag, '+', gen_children), iscluster=True)
        else:
            if 'int' in context:
                frame = String(obj, self.font, iscluster=True)
                frame.label.mul(blue)
                return frame

plugins = [TestPlugin]
