#!/usr/bin/env python3

import sys

state = [[0, 0, 0] for _ in range(64)]
top_left = (0, 0)

TERM_COLOURS = {
    (0, 0, 0): 40,
    (170, 0, 0): 41,
    (0, 170, 0): 42,
    (170, 85, 0): 43,
    (0, 0, 170): 44,
    (170, 0, 170): 45,
    (0, 170, 170): 46,
    (170, 170, 170): 47,
    (85, 85, 85): 100,
    (255, 85, 85): 101,
    (85, 255, 85): 102,
    (255, 255, 85): 103,
    (85, 85, 255): 104,
    (255, 85, 255): 105,
    (85, 255, 255): 106,
    (255, 255, 255): 107,
}

def _find_closest_colour(r, g, b):
    min_dist = 3 * 255**2
    min_color = (0, 0, 0)
    for (cr, cg, cb) in TERM_COLOURS.keys():
        score = (cr - r)**2 + (cg - g)**2 + (cb - b)**2
        if score < min_dist:
            min_dist = score
            min_color = (cr, cg, cb)
    return min_color


class SenseHat:
    def __init__(self):
        self.low_light = True

    def _print(self):
        for i, pixel in enumerate(self._get()):
            col = _find_closest_colour(*pixel)
            print('\x1b[97;{}m \x1b[39;49m'.format(TERM_COLOURS[col]), end='')
            if i % 8 == 7:
                print()

    def _get(self) -> list:
        """Return state w.r.t. to top_left rotation"""
        if top_left == (0, 0):
            return state[:]
        elif top_left == (8, 0):
            return [state[i * 8 + j] for i in range(8) for j in range(7, -1, -1)]
        elif top_left == (8, 8):
            return state[::-1]
        else:
            return [state[i*8 + j] for i in range(7, -1, -1) for j in range(8)]

    @staticmethod
    def _check_colour(r, g, b):
        if not (0 <= r < 256):
            raise ValueError('Expected r-value of [0, 256), got {}'.format(r))
        elif not (0 <= g < 256):
            raise ValueError('Expected g-value of [0, 256), got {}'.format(g))
        elif not (0 <= b < 256):
            raise ValueError('Expected b-value of [0, 256), got {}'.format(b))

    def set_rotation(self, r: int, redraw: bool = True):
        """If you're using the Pi upside down or sideways
        you can use this function to correct the orientation
        of the image being shown.
        """
        if r not in {0, 90, 180, 270}:
            raise ValueError('Expected 0, 90, 180, or 270 for `r`, got {}'.format(r))

        global top_left
        top_left = (int(r in {0, 270}) * 8, int(r > 100) * 8)
        if redraw:
            self._print()

    def flip_h(self, redraw: bool = True) -> list:
        """Flips the image on the LED matrix horizontally."""
        global top_left
        top_left = (8 - top_left[0], top_left[1])
        self._print()
        return self._get()


    def flip_v(self, redraw: bool = True) -> list:
        """Flips the image on the LED matrix vertically."""
        global top_left
        top_left = (top_left[0], 8 - top_left[1])
        self._print()
        return self._get()

    def set_pixels(self, pixel_list: list):
        """Updates the entire LED matrix based on a 64 length list of pixel values."""
        if len(pixel_list) != 64:
            raise ValueError("Expected {} pixels, only got {}".format(len(pixel_list)))
        for pixel in pixel_list:
            if len(pixel) != 3 or not all(0 <= c < 256 for c in pixel):
                raise ValueError("Expected 3 values of [0, 256), got {}".format(repr(pixel)))

        global state
        state = pixel_list
        self._print()

    def get_pixels(self) -> list:
        """The get_pixels function provides a correct representation of
        how the pixels end up in frame buffer memory
        after you've called set_pixels.
        """
        return self._get()

    def set_pixel(self, x: int, y: int, *args):
        """Sets an individual LED matrix pixel at the specified X-Y
        coordinate to the specified colour.
        """
        global state

        if not (0 <= x <= 7):
            raise ValueError('Expected element of [0, 7], got {}'.format(x))
        if not (0 <= y <= 7):
            raise ValueError('Expected element of [0, 7], got {}'.format(y))

        if len(args) == 3:
            r, g, b = args[0], args[1], args[2]
        elif len(args) == 1:
            r, g, b = args[0]
        else:
            raise ValueError('Invalid number of arguments for set_pixel')

        if not (0 <= r < 256):
            raise ValueError('Expected value of [0, 256), got {}'.format(r))
        elif not (0 <= g < 256):
            raise ValueError('Expected value of [0, 256), got {}'.format(g))
        elif not (0 <= b < 256):
            raise ValueError('Expected value of [0, 256), got {}'.format(b))

        state[x * 8 + y] = [r, g, b]
        self._print()

    def get_pixel(self, x: int, y: int) -> list:
        """Please read the docs of get_pixels"""
        global state

        if not (0 <= x <= 7):
            raise ValueError('Expected element of [0, 7], got {}'.format(x))
        if not (0 <= y <= 7):
            raise ValueError('Expected element of [0, 7], got {}'.format(y))

        return self._get[x * 8 + y]

    def load_image(self, file_path: str, redraw: bool = True) -> list:
        """Loads an image file, converts it to RGB format and displays
        it on the LED matrix. The image must be 8 x 8 pixels in size.
        """
        print('Sorry, load_image(…) is unsupported. Nothing happens …', file=sys.stderr)
        return self._get()

    def clear(self, *args):
        """Sets the entire LED matrix to a single colour, defaults to blank / off."""
        if len(args) == 0:
            r, g, b = 0, 0, 0
        elif len(args) == 1:
            r, g, b = args[0]
        elif len(args) == 3:
            r, g, b = args[0], args[1], args[2]
        else:
            raise ValueError('Invalid number of arguments for clear')

        _check_colour(r, g, b)

        global state
        for i in range(64):
            state[i] = [r, g, b]

        self._print()

    def show_message(self, text_string: str, scroll_speed: float = 0.1, text_colour: list = [255, 255, 255], back_colour: list = [0, 0, 0]):
        """Scrolls a text message from right to left across the LED matrix and
        at the specified speed, in the specified colour and background colour.
        """
        _check_colour(*text_colour)
        _check_colour(*back_colour)
        print('Sorry, show_message(…) is unsupported. Nothing happens …', file=sys.stderr)

    def show_letter(self, s: str, text_colour: list = [255, 255, 255], back_colour: list = [0, 0, 0]):
        """Scrolls a text message from right to left across the LED matrix and
        at the specified speed, in the specified colour and background colour.
        """
        if len(s) != 1:
            raise ValueError("show_letter expected one letter, got {}".format(repr(s)))

        _check_colour(*text_colour)
        _check_colour(*back_colour)

        print('Sorry, show_letter(…) is unsupported. Nothing happens …', file=sys.stderr)

    # TODO gamma
