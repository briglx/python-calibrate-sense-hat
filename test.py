#!/usr/bin/python

from calibrate_sense_hat import BlxSenseHat
from sense_hat import SenseHat

blxsense = BlxSenseHat()
sense = SenseHat()

for i in range(10):
    blxsense.calibrate(i)