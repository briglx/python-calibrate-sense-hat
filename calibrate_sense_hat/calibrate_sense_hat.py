#!/usr/bin/python
import os
from PIL import Image  # pillow
from sense_hat import SenseHat
import numpy as np
import time

class BlxSenseHat(object):


    def __init__(
            self,
            text_assets='calibrate_sense_hat_text'
        ):
        self._text_dict = {}

        # Load text assets
        dir_path = os.path.dirname(__file__)
        self._load_text_assets(
            os.path.join(dir_path, '%s.png' % text_assets),
            os.path.join(dir_path, '%s.txt' % text_assets)
        )

        self._sense_hat = SenseHat()

        pix_map0 = np.array([
             [0,  1,  2,  3,  4,  5,  6,  7],
             [8,  9, 10, 11, 12, 13, 14, 15],
            [16, 17, 18, 19, 20, 21, 22, 23],
            [24, 25, 26, 27, 28, 29, 30, 31],
            [32, 33, 34, 35, 36, 37, 38, 39],
            [40, 41, 42, 43, 44, 45, 46, 47],
            [48, 49, 50, 51, 52, 53, 54, 55],
            [56, 57, 58, 59, 60, 61, 62, 63]
        ], int)

        pix_map90 = np.rot90(pix_map0)
        pix_map180 = np.rot90(pix_map90)
        pix_map270 = np.rot90(pix_map180)

        self._pix_map = {
            0: pix_map0,
            90: pix_map90,
            180: pix_map180,
            270: pix_map270
        }

        self._rotation = 0

    ####
    # Text assets
    ####

    # Text asset files are rotated right through 90 degrees to allow blocks of
    # 32 contiguous pixels to represent one 4 x 8 character. These are stored
    # in a 8 x 380 pixel png image with characters arranged adjacently
    # Consequently we must rotate the pixel map left through 90 degrees to
    # compensate when drawing text

    def _load_text_assets(self, text_image_file, text_file):
        """
        Internal. Builds a character indexed dictionary of pixels used by the
        show_message function below
        """

        text_pixels = self.load_image(text_image_file, False)
        with open(text_file, 'r') as f:
            loaded_text = f.read()
        self._text_dict = {}
        for index, s in enumerate(loaded_text):
            start = index * 32
            end = start + 32
            char = text_pixels[start:end]
            self._text_dict[s] = char

    def load_image(self, file_path, redraw=True):
        """
        Accepts a path to an 4 x 8 image file and updates the LED matrix with
        the image
        """

        if not os.path.exists(file_path):
            raise IOError('%s not found' % file_path)

        img = Image.open(file_path).convert('RGB')
        pixel_list = list(map(list, img.getdata()))

        if redraw:
            self.set_pixels(pixel_list)

        return pixel_list

    def _get_char_pixels(self, s):
        """
        Internal. Safeguards the character indexed dictionary for the
        show_message function below
        """

        if len(s) == 1 and s in self._text_dict.keys():
            return list(self._text_dict[s])
        else:
            return list(self._text_dict['?'])

    def show_message(self, text_string,scroll_speed=.1, text_colour=[255, 255, 255], back_colour=[0, 0, 0]):    
        """
        Scrolls a string of text across the LED matrix using the specified
        speed and colours
        """
        previous_rotation = self._sense_hat.rotation
        self._sense_hat.rotation(self._sense_hat.rotation - 90)
        if self._sense_hat.rotation < 0:
            self._sense_hat.rotation(270)

        scroll_pixels = []
        string_padding = [[0, 0, 0]] * 64
        scroll_pixels.extend(string_padding)

        for s in text_string:
            scroll_pixels.extend(self._get_char_pixels(s))
        scroll_pixels.extend(string_padding)

        # Shift right by 8 pixels per frame to scroll
        scroll_length = len(scroll_pixels) // 8
        for i in range(scroll_length - 8):
            start = i * 8
            end = start + 64
            self._sense_hat.set_pixels(scroll_pixels[start:end])
            time.sleep(scroll_speed)

        self._sense_hat.rotation(previous_rotation)

    
    def calibrate(self):

        self.show_message("Starting calibration...")

        for t in range(5):
            self._sense_hat.show_letter(str(5-t))
            time.sleep(1)

        self.show_message("Done")