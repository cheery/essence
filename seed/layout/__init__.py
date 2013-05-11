from box import Box
from column import Column
from row import Row
from align import Align
from flow import AlignByFlow
from config import Config
from label import Label
from intron import Intron
import flow

default = Config(None, dict(
    renderer   = None,
    min_width  = 0,
    min_height = 0,
    padding = (0,0,0,0),
    spacing = 0,
    align = AlignByFlow(0, 1),
    flow  = flow.simple,
    line_height = 1.2,
))

class Slate(Box):
    def __init__(self, width, height, style):
        Box.__init__(self, (0,0,width,height), style)
