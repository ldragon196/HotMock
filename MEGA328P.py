#!/usr/bin/python3
#
# MEGA328P.py
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

MEGA328P_I2C_ADDRESS                      = 0x52 # The device i2c address in default

#------------------------------------------------------------------------------------------------------#

class MEGA328P:
    # Sensor with default address
    def __init__(self, i2c, address = MEGA328P_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address

    # Get sensor values
    # Return x, y and button value
    # x range (0 - 255), y range (0 - 255), button press: 1, release: 0
    def get_value(self):
        # read 3 bytes from sensor
        read = self.__i2c.i2c_read_data(self.__address, 3)
        x = read[0]
        y = read[1]
        button = read[2]

        return x, y, button
    
#-------------------------- Example --------------------------

"""
from time import sleep

i2c = I2C()
mega328p = MEGA328P(i2c)
while True:
    print(mega328p.get_value())
    sleep(1)
"""