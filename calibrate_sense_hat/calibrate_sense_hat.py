#!/usr/bin/python
import os
from PIL import Image  # pillow
from sense_hat import SenseHat
import numpy as np
import time
import sys, errno
# from sklearn.externals import joblib


class BlxSenseHat(object):


    def __init__(
            self,
            text_assets='calibrate_sense_hat_text',
            model_name='filename'
        ):
        self._text_dict = {}
       
        # Load text assets
        dir_path = os.path.dirname(__file__)
        self._load_text_assets(
            os.path.join(dir_path, '%s.png' % text_assets),
            os.path.join(dir_path, '%s.txt' % text_assets)
        )

        # Load trained model
        self._load_model(
            os.path.join(dir_path,'../model/%s.pkl' % model_name)
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


    def _load_model(self, model_file):
        """
        Internal. Loads a trained model that predicts the direction 
        based on the orientation readings.
        """

        # self._clf = joblib.load(model_file)



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
        
        if self._sense_hat.rotation - 90 < 0:
            self._sense_hat.rotation = 270
        else:
            self._sense_hat.rotation = self._sense_hat.rotation - 90

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

        self._sense_hat.rotation = previous_rotation

    def _getPixelValue(self, val):
        # takes a value between 0-33.3333
        # Returns an array of RGB colors ranging between White -> Blue
        # Values Close to 0 are mapped to White 
        # Values clost to 33.333 are mapped to Blue
        # It should be a gradient between white to blue for 0 -> 33.333
        # return black if val <= 0
        
        
        if val <= 0:
            return [0,0,0]

        if val > .33333:
            return [0,0,255]
        
        color = int(255 - np.round(765 * val ))
        return [color,color,255]
    
    
    def _getPixelsValue(self, val):
        # takes a value between 0-1
        # returns an array that represents rgb values for three pixels
        # The pixels 'Fill up' from 0 to 1
        # values between [0:1/3) will fill up the first pixel
        # values between [1/3:2/3) will have the first pixel 'full' and filling the second
        # values between [2/3:1] will have the first two pixels 'full' and the third one filling
        # pixels are black until they start filling
        
        delimeter = 1.0 / 3.0
        
        if(int(val / delimeter) <= 0):
            return [self._getPixelValue(val),[0,0,0],[0,0,0]]
        
        if(int(val / delimeter) == 1):
            return [[0,0,255],self._getPixelValue(val % delimeter),[0,0,0]]
        
        if(int(val / delimeter) == 2):
            return [[0,0,255],[0,0,255],self._getPixelValue(val % delimeter)]
        
        if(int(val / delimeter) >= 3):
            return [[0,0,255],[0,0,255],[0,0,255]]
    
    def _predict_direction(self, orientation):

        probs = self._clf.predict_proba(orientation)

        return probs

    def _show_prediction(self, orientation):

        munged = self._convert_orientation(orientation)
        probs = self._clf.predict_proba(munged)
        self._set_predicted_pixels(probs)

    def _set_predicted_pixels(self, probs):

        # Set top Pixels
        x = 3
        y = 3
        
        prob = probs[0][0]
        pixels = self._getPixelsValue(prob)

        for i in range(3):
            self._sense_hat.set_pixels(x, y-i, pixels[i])

        # Set right pixels
        x = 4
        y = 3
        prob = probs[0][1]
        pixels = self._getPixelsValue(prob)
        for i in range(3):
            self._sense_hat.set_pixels(x+i, y, pixels[i])


        # Set bottom pixels
        x = 4
        y = 4
        prob = probs[0][2]
        pixels = self._getPixelsValue(prob)
        for i in range(3):
            self._sense_hat.set_pixels(x, y+i, pixels[i])

        # Set left pixels
        x = 3
        y = 4
        prob = probs[0][3]
        pixels = self._getPixelsValue(prob)
        for i in range(3):
            self._sense_hat.set_pixels(x-i, y, pixels[i])

    def convert_orientation(self, orientation, shift=0):
    
        orientation = np.array([raw_orientation['pitch'], raw_orientation['roll'], raw_orientation['yaw'],  ])
           
        orientation = np.round(orientation).astype(int)
        idx = np.where(orientation >180)
        orientation[idx] = orientation[idx] - 360
        orientation[-1]  = 90 - orientation[-1]  
        
        return orientation

    def calibrate(self, duration):

        X = (128, 0, 0)
        O = (0, 0, 0)

        arrow = [
            O, O, O, X, X, O, O, O,
            O, O, X, X, X, X, O, O,
            O, X, X, O, O, X, X, O,
            X, X, O, O, O, O, X, X,
            X, O, O, O, O, O, O, X,
            O, O, O, O, O, O, O, O,
            O, O, O, O, O, O, O, O,
            O, O, O, O, O, O, O, O
        ]

        self.show_message("Calibrating")

        for t in range(5):
            self._sense_hat.show_letter(str(5-t))
            print(str(5-t))
            time.sleep(.33)

        self._sense_hat.set_rotation(0)
        self._sense_hat.set_pixels(arrow)
        self._log_sensors(0, duration)
       
        self._sense_hat.set_rotation(90, True)
        self._sense_hat.set_pixels(arrow)
        self._log_sensors(90, duration)

        self._sense_hat.set_rotation(180, True)
        self._sense_hat.set_pixels(arrow)
        self._log_sensors(180, duration)

        self._sense_hat.set_rotation(270, True)
        self._sense_hat.set_pixels(arrow)
        self._log_sensors(270, duration)

        self._sense_hat.set_rotation(0)
        self.show_message("Done")

    def _log_sensors(self, direction, duration):

        for i in range(duration * 10):

            orientation = self._sense_hat.get_orientation()

            # Print Prediction
            self._show_prediction(orientation)

            sys.stdout.write(str(direction) + ', ' + str(orientation["pitch"]) + ', ' + str(orientation["roll"]) + ', ' + str(orientation["yaw"]) + '\n')
            time.sleep(.1)

