#!/usr/bin/python3
#
# cardkb.py
#
# Created on: April 27, 2021
# Author: LongHD
#
# Keyboard
# Reference https://github.com/m5stack/M5-ProductExampleCodes/tree/master/Unit/CARDKB
#

#------------------------------------------------------------------------------------------------------#

from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

CARDKB_I2C_ADDRESS                        = 0x5F # The device i2c address in default

#------------------------------------------------------------------------------------------------------#

class CARDKB:
    # Sensor with default address
    def __init__(self, i2c, address = CARDKB_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address

    # Get keyboard state
    # Return key is pressed (char value)
    # See https://github.com/m5stack/M5-ProductExampleCodes/blob/master/Unit/CARDKB/cardkb_key_value.xlsx
    # Note: sensor only return value after key is released
    def get_key(self):
        # read 1 byte from keyborad
        read = self.__i2c.i2c_read_data(self.__address, 1)
        return chr(read[0])
    
#-------------------------- Example --------------------------

"""
from time import sleep

i2c = I2C()
keyboard = CARDKB(i2c)
while True:
    c = keyboard.get_key()
    if(c != '\0'):
        print(c)
        sleep(0.01)
"""