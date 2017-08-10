#!/usr/bin/python
import os
from PIL import Image  # pillow

class SenseHat(object):


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

    def display_message( self,
            text_string,
            x_pos=0,
            y_pos=0,
            text_colour=[255, 255, 255],
            back_colour=[0, 0, 0]
        ):

        """
        Sets a string of text on the LED matrix at the specified 
        location and colours
        """