import ctypes

lib = ctypes.CDLL('libfreetype.so.6')

###############
## constants ##
###############

LOAD_RENDER = 0x4

#############
## helpers ##
#############

POINTER     = ctypes.POINTER
byref       = ctypes.byref

###########
## types ##
###########

PVoid       = ctypes.c_void_p
Char        = ctypes.c_char
#PChar       = POINTER(Char)
PChar       = ctypes.c_char_p
Int         = ctypes.c_int
UInt        = ctypes.c_uint
PUInt       = POINTER(UInt)
Int32       = ctypes.c_int32
Long        = ctypes.c_long
ULong       = ctypes.c_ulong
Short       = ctypes.c_short
UShort      = ctypes.c_ushort

####################
## semantic types ##
####################

Error       = Int
F26Dot6     = Long
Pos         = Long
Fixed       = Long
GlyphFormat = Int
Library     = PVoid
PLibrary    = POINTER(PVoid)
Finalizer   = ctypes.CFUNCTYPE(None, PVoid)
Structure   = ctypes.Structure

################
## structures ##
################

class Generic(Structure):
    _fields_ = [
        ('data', PVoid),
        ('finalizer', Finalizer),
    ]

class Vector(Structure):
    _fields_ = [
        ('x', Pos),
        ('y', Pos),
    ]

class BBox(Structure):
    _fields_ = [
        ('xMin', Pos),
        ('yMin', Pos),
        ('xMax', Pos),
        ('yMax', Pos),
    ]

class Bitmap(Structure):
    _fields_ = [
        ('rows', Int),
        ('width', Int),
        ('pitch', Int),
        ('buffer', POINTER(Char)),
        ('num_grays', Short),
        ('pixel_mode', Char),
        ('palette_mode', Char),
        ('palette', PVoid),
    ]

class Glyph_Metrics(Structure):
    _fields_ = [
        ('width', Pos),
        ('height', Pos),
        ('horiBearingX', Pos),
        ('horiBearingY', Pos),
        ('horiAdvance', Pos),
        ('vertBearingX', Pos),
        ('vertBearingY', Pos),
        ('vertAdvance', Pos),
    ]

class GlyphSlot(Structure):
    _fields_ = [
        ('library', PVoid),
        ('face', PVoid),
        ('next', PVoid),
        ('reserved', UInt),
        ('generic', Generic),
        ('metrics', Glyph_Metrics),
        ('linearHoriAdvance', Fixed),
        ('linearVertAdvance', Fixed),
        ('advance', Vector),
        ('format', GlyphFormat),
        ('bitmap', Bitmap),
        ('bitmap_left', Int),
        ('bitmap_top', Int),
    ]
PGlyphSlot = POINTER(GlyphSlot)

class FaceRecord(Structure):
    _fields_ = [
        ('num_faces', Long),
        ('face_index', Long),
        ('face_flags', Long),
        ('style_flags', Long),
        ('num_glyphs', Long),
        ('family_name', PChar),
        ('style_name', PChar),
        ('num_fixed_sizes', Int),
        ('available_sizes', PVoid), # FT_Bitmap_Size* wtf?
        ('num_charmaps', Int),
        ('charmaps', PVoid), # FT_CharMap*
        ('generic', Generic),
        ('bbox', BBox),
        ('units_per_EM', UShort),
        ('ascender', Short),
        ('descender', Short),
        ('height', Short),
        ('max_advance_width', Short),
        ('max_advance_height', Short),
        ('underline_position', Short),
        ('underline_thickness', Short),
        ('glyph', PGlyphSlot),
#        ('size', Size),
    ]

    def init(self, size):
        self.setPixelSizes(0, size)

    def setPixelSizes(self, a, b): 
        if pixelSizes(byref(self), a, b) != 0:
            raise FreeTypeError('could not set face pixel sizes')

    def __iter__(self):
        i = UInt()
        codepoint = firstChar(byref(self), byref(i)) 
        while i.value != 0:
            loadChar(byref(self), codepoint, LOAD_RENDER) 
            glyph = self.glyph.contents
            metrics = glyph.metrics
                    
            width   = glyph.bitmap.width
            height  = glyph.bitmap.rows

            if width*height > 0:
                bitmap = glyph.bitmap.buffer[:width*height]
            else:
                bitmap = ''

            glyph_data = dict(
                char        = unichr(codepoint),
                codepoint   = codepoint,
                metric      = dict(
                    width   = metrics.width/64.0,
                    height  = metrics.height/64.0,
                    bearing = dict(
                        h   = dict(
                            x       = metrics.horiBearingX/64.0,
                            y       = metrics.horiBearingY/64.0,
                            advance = metrics.horiAdvance/64.0,
                        ),
                        v = dict(
                            x       = metrics.vertBearingX/64.0,
                            y       = metrics.vertBearingY/64.0,
                            advance = metrics.vertAdvance/64.0,
                        ),
                    )
                )
            )
            yield glyph_data, width, height, bitmap
            codepoint = nextChar(byref(self), codepoint, byref(i))

Face = POINTER(FaceRecord)

#############
## methods ##
#############

init = lib.FT_Init_FreeType
init.restype = Error
init.argtypes = [PLibrary]

newFace = lib.FT_New_Face
newFace.restype = Error
newFace.argtypes = [Library, PChar, Long, POINTER(Face)]

charSize = lib.FT_Set_Char_Size
charSize.restype = Error
charSize.argtypes = [Face, F26Dot6, F26Dot6, UInt, UInt]

pixelSizes = lib.FT_Set_Pixel_Sizes
pixelSizes.restype = Error
pixelSizes.argtypes = [Face, UInt, UInt]

loadChar = lib.FT_Load_Char
loadChar.restype = Error
loadChar.argtypes = [Face, ULong, Int32]

doneFace = lib.FT_Done_Face
doneFace.restype = Error
doneFace.argtypes = [Face]

done = lib.FT_Done_FreeType
done.restype = Error
done.argtypes = [Library]

firstChar = lib.FT_Get_First_Char
firstChar.restype = ULong
firstChar.argtypes = [Face, PUInt]

nextChar = lib.FT_Get_Next_Char
nextChar.restype = ULong
nextChar.argtypes = [Face, ULong, PUInt]

class FreeTypeError(Exception): pass

class Freetype(object):
    def __init__(self):
        self.library = Library()
        if init(byref(self.library)) != 0:
            raise FreeTypeError('failed to init freetype')

    def face(self, filename, size=16):
        handle = Face()
        if newFace(self.library, filename, 0, byref(handle)) != 0:
            raise FreeTypeError('failed to init face: %s' % filename)
        face = handle.contents
        face.init(size)
        return face
