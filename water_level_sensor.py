#!/usr/bin/python3
#
# water_level_sensor.py
#
# Created on: April 22, 2021
# Author: LongHD
#
# Water level sensor
# Reference https://github.com/SeeedDocument/Grove-Water-Level-Sensor
#

import time
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

ATTINY1_HIGH_ADDR                       = 0x78            # Address to read high 12 sections value
ATTINY2_LOW_ADDR                        = 0x77            # Address to read low 8 sections value

THRESHOLD_DEFAULT                       = 100

#------------------------------------------------------------------------------------------------------#

class WaterLevelSensor:
    # Sensor has 20 sections from 1 - 20 (5 - 100% of 20cm)
    # If the sensor value is greater than the threshold, determine the state active
    def __init__(self, i2c, threshold = THRESHOLD_DEFAULT):
        self.__i2c = i2c
        self.__threshold = threshold

    # Get sensor value of 12 high sections (9 - 12)
    def __get_high_12_section_value(self):
        high_data = self.__i2c.i2c_read_block_data(ATTINY1_HIGH_ADDR, 0, 12)
        time.sleep(0.01)
        return high_data

    # Get sensor value of 8 low sections (1 - 8)
    def __get_low_8_section_value(self):
        low_data = self.__i2c.i2c_read_block_data(ATTINY2_LOW_ADDR, 0, 8)
        time.sleep(0.01)
        return low_data
    
    #--------------------------------------------------------------------------------------------------#

    # Get values of 20 sections
    def get_water_section_value(self):
        low_count = 0
        high_count = 0

        high_data = self.__get_high_12_section_value()
        low_data = self.__get_low_8_section_value()

        return low_data + high_data
    
    # Get water value (0 - 100%)
    # If section 1, 2, 3, 4, 5 value > threshold -> level = 5 * 5 = 25%
    # If section 1, 2, 3, , 5, 6 value > threshold but section 4 < threshold -> level = 3 * 5 = 15%
    def get_water_level(self):
        values = self.get_water_section_value()
        trig_section = 0

        # Check continuous value trigger
        for value in values:
            if value > self.__threshold:
                trig_section += 1
            else:
                break
        
        # Convert to percentage
        return trig_section * 5

    # Set threshold
    # If sensor values > threshold -> active
    # threshold: range(0 - 254)
    def set_threshold(self, threshold):
        # Sensor value max is 255 (0xFF) so thrshold max should less than or equal 254
        if threshold > 254:
            threshold = 254
        self.__threshold = threshold

#-------------------------- Example --------------------------

"""
i2c = I2C()
sensor = WaterLevelSensor(i2c)
sensor.set_threshold(50)
while True:
    level = sensor.get_water_level()
    print("Level = " + str(level) + " %")
    time.sleep(.01)
"""