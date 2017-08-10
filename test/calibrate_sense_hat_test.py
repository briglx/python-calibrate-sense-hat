#!/usr/bin/python

from ../calibrate_sense_hat import SenseHat


def set_pixel(x, y, *args):
     pixel = args[0]
     print pixel


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

def set_message(x,y,text_string):
    cur_x = x
    cur_y = y
    for s in text_string:
        pixel_list = get_char_pixels(s)

        for index, pix in enumerate(pixel_list):

            map[index // 8][index % 8] * 2)

            sense.set_pixel(cur_x, cur_y, pixel)
            cur_y = cur_y + 1

H    e    l    l    o

8*4, 8*4, 8*4, 8*4, 8*4 

32   32   32   32   32          (160)

12345678
::::::::
::::::::
::::::::
::::::::


[0...31]