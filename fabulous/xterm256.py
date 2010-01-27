"""Implements Support for 256-color Terminals
"""

import logging


CUBE_STEPS = [0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF]
BASIC16 = ((0, 0, 0), (205, 0, 0), (0, 205, 0), (205, 205, 0),
           (0, 0, 238), (205, 0, 205), (0, 205, 205), (229, 229, 229),
           (127, 127, 127), (255, 0, 0), (0, 255, 0), (255, 255, 0),
           (92, 92, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255))


def xterm_to_rgb(xcolor):
    assert 0 <= xcolor <= 255
    if xcolor < 16:
        # basic colors
        return BASIC16[xcolor]
    elif 16 <= xcolor <= 231:
        # color cube
        xcolor -= 16
        return (CUBE_STEPS[(xcolor / 36) % 6],
                CUBE_STEPS[(xcolor / 6) % 6],
                CUBE_STEPS[xcolor % 6])
    elif 232 <= xcolor <= 255:
        # gray tone
        c = 8 + (xcolor - 232) * 0x0A
        return (c, c, c)


COLOR_TABLE = [xterm_to_rgb(i) for i in xrange(256)]
def rgb_to_xterm(r, g, b):
    """
    OMG there is like no easy way to optimize this!!!  Someone smarter
    than me should read this:

    http://algolist.manual.ru/graphics/quant/qoverview.php
    """
    if r < 5 and g < 5 and b < 5:
        return 16
    best_match = 0
    smallest_distance = 10000000000
    for c in xrange(16, 256):
        d = (COLOR_TABLE[c][0] - r) ** 2 + \
            (COLOR_TABLE[c][1] - g) ** 2 + \
            (COLOR_TABLE[c][2] - b) ** 2
        if d < smallest_distance:
            smallest_distance = d
            best_match = c
    return best_match


def compile_speedup():
    """Tries to compile/link the C version of this module

    Like it really makes a huge difference.  With a little bit of luck
    this should *just work* for you.

    You need:

    - Python >= 2.5 for ctypes library
    - gcc (sudo apt-get install gcc)

    """
    import os, ctypes
    from os.path import join, dirname, getmtime, exists
    library = join(dirname(__file__), '_xterm256.so')
    sauce = join(dirname(__file__), '_xterm256.c')
    if not exists(library) or getmtime(sauce) > getmtime(library):
        build = "gcc -fPIC -shared -o %s %s" % (library, sauce)
        assert os.system(build) == 0
    xterm256_c = ctypes.cdll.LoadLibrary(library)
    xterm256_c.init()
    def xterm_to_rgb(xcolor):
        res = xterm256_c.rgb_to_xterm_i(xcolor)
        return ((res >> 16) & 0xFF, (res >> 8) & 0xFF, res & 0xFF)
    return (xterm256_c.rgb_to_xterm, xterm_to_rgb)


try:
    (rgb_to_xterm, xterm_to_rgb) = compile_speedup()
except:
    logging.exception("Failed to compile xterm256 speedup code")
