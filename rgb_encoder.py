#!/usr/bin/python3
#
# rgb_encoder.py
#
# Created on: April 27, 2021
# Author: LongHD
#
# Joystick
# Reference https://github.com/m5stack/M5Stack/tree/master/examples/Unit/JOYSTICK
# https://docs.m5stack.com/en/unit/joystick
#

#------------------------------------------------------------------------------------------------------#

from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

RGB_ENCODER_I2C_ADDRESS                   = 0x0F # The device i2c address in default

#------------------------------------------------------------------------------------------------------#

class RGBLED:
    # Sensor with default address
    def __init__(self, i2c, address = RGB_ENCODER_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address

    