#!/usr/bin/python3
#
# SHT35.py
#
# Created on: April 20, 2021
# Author: LongHD
#
# Temperature and humidity sensor
# Reference https://github.com/Seeed-Studio/Seeed_SHT35
# https://www.mouser.com/datasheet/2/682/Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital-971521.pdf
#

#------------------------------------------------------------------------------------------------------#

from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

SHT35_I2C_ADDRESS                       = 0x45 # The device i2c address in default

SOFT_RESET_CMD                          = 0x30A2
HIGH_REP_WITH_STRH                      = 0x2C06

#------------------------------------------------------------------------------------------------------#

class SHT35:
    def __init__(self, i2c, address = SHT35_I2C_ADDRESS):
        self.__address = address
        self.__i2c = i2c
        self.soft_reset()
    
    # Send UINT16 command
    def __send_command(self, cmd):
        data = [(cmd >> 8) & 0xFF, cmd & 0xFF]
        self.__i2c.i2c_write_data(self.__address, data)

    # Calculator temperature from hex value
    def __get_temp(self, temp_hex):
        return (temp_hex / 65535.00) * 175 - 45
    
    # Calculator humidity from hex value
    def __get_humi(self, humi_hex):
        return (humi_hex / 65535.0) * 100.0

    # Check CRC8 (See "4.12 Checksum Calculation in datasheet" for more detail)
    def __check_crc8(self, data):
        POLYNOMIAL = 0x31       # Polynomial
        crc = 0xFF              # Initialization
        size = len(data)

        for i in range(size):
            crc ^= data[i] & 0xFF

            for j in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ POLYNOMIAL) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    #--------------------------------------------------------------------------------------------------#

    # Reset sensor (See "Table 13 Soft reset command" for more detail)
    def soft_reset(self):
        self.__send_command(SOFT_RESET_CMD)

    # Read measure result see "Table 8 Measurement commands in single shot mode"
    # config: to enable/ disable Clock stretching and config Repeatability high/ medium/ low
    # ex: 0x2C06 mean  high repeatability measurement with clock stretching enabled
    # return temperature and humidity
    # if error check crc, return None
    def read_measure_data(self, config = HIGH_REP_WITH_STRH):
        # Send config and read 6 bytes result
        write = [(config >> 8) & 0xFF, config & 0xFF]
        read = self.__i2c.i2c_read_write_data(self.__address, write, 6)

        # format: temp MSB : temp LSB : CRC8 : humi MSB : humi LSB : CRC8
        temp = None
        if self.__check_crc8([read[0], read[1]]) == read[2]:
            temp = self.__get_temp((read[0] * 256) + read[1])
        
        humi = None
        if self.__check_crc8([read[3], read[4]]) == read[5]:
            humi = self.__get_humi((read[3] * 256) + read[4])

        return temp, humi


#-------------------------- Example --------------------------

"""
import time

i2c = I2C()
sht35 = SHT35(i2c)
time.sleep(.01)

while True:
    temp, humi = sht35.read_measure_data(HIGH_REP_WITH_STRH)
    if temp != None:
        print("Temperature {:.2f}".format(temp))
    else:
        print("Read temperature failure")

    if humi != None:
        print("Humidity {:.2f}".format(humi))
    else:
        print("Read humidity failure")
    
    time.sleep(1)
"""