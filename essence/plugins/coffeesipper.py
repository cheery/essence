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
from essence import string, image, xglue, yglue, group, expando, delimit
from essence.ui import composite, color, empty

class CoffeeSipper(object):
    priority = 1
    def __init__(self, editor):
        pass

plugins = [CoffeeSipper]
