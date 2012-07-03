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
require_api_version(major=3, minor=0)
from essence import string, image, xglue, yglue, group, expando, delimit, isstring, push
from essence.ui import composite, color, empty
from essence import empty_template, dot, star

operator = dict(
    mul = 20, add = 10, sub = 10, let = 1, set = 1, equal = 1,
)
operator_symbol = dict(
    mul = '*', add = '+', sub = '-', let = '=', set = ":=", equal = '==',
)

orange = color(0xff, 0x80, 0x00)
gray = color(0x80, 0x80, 0x80)
blue = color(0, 0, 0xff)
dark = color(0x70, 0x70, 0x70)

purple = color(0xFF, 0x80, 0xFF)


class CoffeeSipper(object):
    priority = 1
    def __init__(self, editor):
        self.parens = (
            editor.font('(').mul(gray),
            editor.font(')').mul(gray),
        )
    def wrap(self, parent, this, data):
        lparen, rparen = self.parens
        if operator.get(parent, 0) >= operator.get(this):
            return [string(lparen)] + data + [string(rparen)]
        return data

    def keyboard(self, editor, key, modifiers, ch):
        selection = editor.selection
        if selection.parent.name in ('int', 'variable', 'string'):
            return
        structure = None

        shift = 'shift' in modifiers
        if ch == '*':
            structure = empty_template('mul', dot, dot)
        if ch == '+':
            structure = empty_template('add', dot, dot)
        if ch == '-':
            structure = empty_template('sub', dot, dot)
        if ch == '=':
            structure = empty_template('equal', dot, dot)
        if ch == 'L':
            structure = empty_template('let', dot, dot)
        if ch == 'S':
            structure = empty_template('set', dot, dot)
        if ch == 'C':
            structure = empty_template('call', dot, star)
        if ch == '"':
            structure = empty_template('string', star)
        if ch == 'F':
            structure = empty_template('function', star, star)
        if ch == 'I':
            structure = empty_template('if', dot, star, star)
        if ch == '[':
            structure = empty_template('list', star)
        if ch == 'Z':
            structure = empty_template('env')

        if structure:
            selection.replace([structure], branch_in=True)
            return True

        if ch.isdigit() and len(ch) == 1:
            selection.replace([empty_template('int', star)], branch_in=True)
            selection.replace([ch])
            return True
        if ch.isalnum() and len(ch) == 1:
            selection.replace([empty_template('variable', star)], branch_in=True)
            selection.replace([ch])
            return True

    def layout(self, editor, obj, context):
        parent = context[-1] if len(context) > 0 else None
        context = push(context, obj)
        ys = lambda i, plac="*": editor.layout_star(obj.holes[i], context, plac)
        y = lambda i: editor.layout_dot(obj.holes[i], context)

        if isstring(obj):
            if parent.name == 'int':
                return string(editor.font(obj).mul(blue))
            if parent.name == 'string':
                return string(editor.font(obj).mul(purple))
            return None

        if obj.name in ('variable', 'int', 'string'):
            return group(ys(0))

#        if name == 'int' and len(obj) > 0:
#            return group(delimit(y(), xglue, 8, 0))
        if obj.name in operator:
            label = editor.font(operator_symbol[obj.name]).mul(orange)
            return group(delimit(
                self.wrap(parent.name, obj.name,
                    [ y(0), string(label), y(1) ]
                ),
                xglue, 8, 0
            ))
#                )
#            )

#        if name == 'program':
#            language = obj.get('language') or '<unknown>'
#            header = group([
#                string(editor.font("program").mul(dark)),
#                xglue(8,0),
#                string(editor.font(language).mul(dark).mul(blue)),
#            ])

        if obj.name == 'call':
            return group([ y(0), xglue(8,0), 
                group(
                    delimit(self.wrap('call', 'call', ys(1)), xglue, 8, 0)
                )
            ])

        if obj.name == 'function':
            return group([
                group(delimit(ys(0, 'argument*'), xglue, 8, 0)),
                yglue(3, 0),
                group(delimit(ys(1, 'exp*'), yglue, 3, 0)),
            ])

        if obj.name == 'if':
            return group([
                group([
                    string(editor.font('if').mul(gray)),
                    xglue(8, 0),
                    y(0),
                ]),
                yglue(3, 0),
                group([
                    string(editor.font('else').mul(gray)),
                    xglue(8, 0),
                    group(delimit(ys(1, 'exp*'), yglue, 3, 0)),
                ]),
                yglue(3, 0),
                group([
                    string(editor.font('otherwise').mul(gray)),
                    xglue(8, 0),
                    group(delimit(ys(2, 'exp*'), yglue, 3, 0)),
                ]),
            ])
#            cond, then = y()
#            return group([
#                group([
#                    string(editor.font('if').mul(gray)),
#                    xglue(8, 0),
#                    cond
#                ]),
#                yglue(8, 0),
#                group([
#                    string(editor.font('then').mul(gray)),
#                    xglue(8, 0),
#                    then
#                ])
#            ])
plugins = [CoffeeSipper]
