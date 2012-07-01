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
require_api_version(major=2, minor=0)
from essence import string, image, xglue, yglue, group, expando, delimit, isstring
from essence.ui import composite, color, empty

operator = dict(
    mul = 20, add = 10, sub = 10, let = 1, set = 1, equal = 1,
)
operator_symbol = dict(
    mul = '*', add = '+', sub = '-', let = '.=', set = ":=", equal = '=',
)

orange = color(0xff, 0x80, 0x00)
gray = color(0x80, 0x80, 0x80)
blue = color(0, 0, 0xff)
dark = color(0x70, 0x70, 0x70)

def wrap((lparen, rparen), parent, this, data):
    if operator.get(parent, 0) >= operator.get(this):
        return [string(lparen)] + data + [string(rparen)]
    return data

class CoffeeSipper(object):
    priority = 1
    def __init__(self, editor):
        self.parens = (
            editor.font('(').mul(gray),
            editor.font(')').mul(gray),
        )

    def keyboard(self, editor, key, modifiers, ch):
        pass

    def layout(self, editor, obj, context):
        y = lambda: editor.layout_recurse(obj, context)
        parent = context[-1] if len(context) > 0 else None
        if isstring(obj):
            if parent.get('name') == 'int':
                return string(editor.font(obj).mul(blue))
            return None
        name = obj.get('name')
        if name == 'int' and len(obj) > 0:
            return group(delimit(y(), xglue, 8, 0))
        if name in operator and len(obj) == 2:
            label = editor.font(operator_symbol[name]).mul(orange)
            return group(
                delimit(
                    wrap(self.parens, parent.get('name'), name,
                        delimit(y(), string, label)
                    ),
                    xglue, 8, 0
                )
            )
        if name == 'variable' and len(obj) > 0:
            return group(delimit(y(), xglue, 8, 0))
        if name == 'program':
            language = obj.get('language') or '<unknown>'
            header = group([
                string(editor.font("program").mul(dark)),
                xglue(8,0),
                string(editor.font(language).mul(dark).mul(blue)),
            ])

            return group(delimit([header] + y(), yglue, 8, 0))
        if name == 'arguments':
            return group(delimit(wrap(self.parens, 'call', 'args', y()), xglue, 8, 0))
        if name == 'call' and len(obj) == 2:
            return group(delimit(y(), xglue, 8, 0))
        if name == 'function' and len(obj) == 2:
            bindings, body = y()
            return group([
                bindings,
                yglue(8, 0),
                body,
            ], background=editor.border, padding=(8,8,8,8))
        if name == 'prog' and len(obj) > 0:
            return group(delimit(y(), yglue, 8, 0), padding=(20,0,0,0))
        if name == 'bindings':
            return group(delimit(y(), xglue, 8, 0), background=dark)

        if name == 'if' and len(obj) == 2:
            cond, then = y()
            return group([
                group([
                    string(editor.font('if').mul(gray)),
                    xglue(8, 0),
                    cond
                ]),
                yglue(8, 0),
                group([
                    string(editor.font('then').mul(gray)),
                    xglue(8, 0),
                    then
                ])
            ])
        if name == 'if' and len(obj) == 3:
            cond, then, otherwise = y()
            return group([
                group([
                    string(editor.font('if').mul(gray)),
                    xglue(8, 0),
                    cond
                ]),
                yglue(8, 0),
                group([
                    string(editor.font('then').mul(gray)),
                    xglue(8, 0),
                    then
                ]),
                yglue(8, 0),
                group([
                    string(editor.font('otherwise').mul(gray)),
                    xglue(8, 0),
                    otherwise
                ])
            ])

plugins = [CoffeeSipper]
