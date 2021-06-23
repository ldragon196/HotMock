#!/usr/bin/python3
#
# cardkb.py
#
# Created on: June 23, 2021
# Author: LongHD
#
# LTC2497 (ACD input and I2C interface)
# Reference https://www.mouser.jp/datasheet/2/609/2497fb-1267645.pdf
#

#------------------------------------------------------------------------------------------------------#

from i2c.i2c import I2C
from time import sleep

#------------------------------------------------------------------------------------------------------#

# See Table 4. Address Assignment in datasheet (page 17)
# Address according to CA0, CA1, CA2 pins
# Ex: CA0, CA1, CA2 low -> address = 0x14
LTC2497_I2C_ADDRESS = 0x14     # The device i2c address in default

# Channel Address - Single channel use
# See LTC2497 data sheet, Table 3, Channel Selection
# All channels are uncommented - comment out the channels you do not plan to use
LTC2497_CHANNEL = [0xB0, 0xB8, 0xB1, 0xB9, 0xB2, 0xBA, 0xB3, 0xBB, 0xB4, 0xBC, 0xB5, 0xBD, 0xB6, 0xBE, 0xB7, 0xBF]

# Determine the reference voltage
VREF = 2.5

# To calculate the voltage, the number read in is 3 bytes. The first bit is ignored. 
# Max reading is 2^23 or 8,388,608
MAX_READING = 8388608.0

LANGE = 0x06      # number of bytes to read in the block
TIEMPO = 0.4      # number of seconds to sleep between each channel reading

#------------------------------------------------------------------------------------------------------#

class LTC2497:
    # Sensor with default address
    def __init__(self, i2c, address = LTC2497_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address

    # Get measurement value and detect plugging
    # If input is not plugin, return None
    # Return measurement value
    def get_adc(self, channel):
        channel_cmd = LTC2497_CHANNEL[channel]

        # Command to start conversation
        self.__i2c.i2c_write_byte(self.__address, channel_cmd)
        sleep(TIEMPO)

        # read value
        reading = self.__i2c.i2c_read_block_data(self.__address, channel_cmd, LANGE)
        valor = ((((reading[0] & 0x3F)) << 16)) + ((reading[1] << 8)) + (((reading[2] & 0xE0)))

        # End of conversion of the Channel
        volts = valor * VREF / MAX_READING

        # we found the error
        if( (reading[0] & 0b11000000) == 0b11000000):
            return None
    
        # Measure success
        return volts
    
#-------------------------- Example --------------------------

i2c = I2C()
ltc2497 = LTC2497(i2c)
while True:
    for i in range(16):
        # Get channel 0
        volts = ltc2497.get_adc(i)
        if volts is None:
            print("Channel %d is not openned or volts more than %.2f V" % (i, VREF))
        else:
            print("Channel %d is %.8f Volts" % ((i), volts))
        
        sleep(1)