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
import document

def makelist(fn):
    return lambda *a, **kw: list(fn(*a, **kw))

def pull(finger):
    return finger[:-1], finger[-1]

def push(finger, index):
    return finger + (index,)

@makelist
def delimit(seq, fn, *a, **kw):
    it = iter(seq)
    yield it.next()
    for obj in it:
        yield fn(*a, **kw)
        yield obj

def isstring(cluster):
    return not isinstance(cluster, document.element)

def isscratch(cluster):
    return cluster.kw.get('which') == 'scratch'
