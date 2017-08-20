#!/usr/bin/python

class SenseHat(object):
    
    @property
    def rotation(self):
        return 0

    def set_pixels(self, x,y, pixel):
        print x, y, pixel