#!/usr/bin/python3
#
# BMP280.py
#
# Created on: April 28, 2021
# Author: LongHD
#
# Grove Temperature and Barometer Sensor
# Reference https://github.com/Seeed-Studio/Grove_BMP280
#

#------------------------------------------------------------------------------------------------------#

from time import sleep
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

BMP280_I2C_ADDRESS                      = 0x77 # The device i2c address in default

BMP280_REG_DIG_T1                       = 0x88
BMP280_REG_DIG_T2                       = 0x8A
BMP280_REG_DIG_T3                       = 0x8C

BMP280_REG_DIG_P1                       = 0x8E
BMP280_REG_DIG_P2                       = 0x90
BMP280_REG_DIG_P3                       = 0x92
BMP280_REG_DIG_P4                       = 0x94
BMP280_REG_DIG_P5                       = 0x96
BMP280_REG_DIG_P6                       = 0x98
BMP280_REG_DIG_P7                       = 0x9A
BMP280_REG_DIG_P8                       = 0x9C
BMP280_REG_DIG_P9                       = 0x9E

BMP280_REG_CHIPID                       = 0xD0
BMP280_REG_VERSION                      = 0xD1
BMP280_REG_SOFTRESET                    = 0xE0

BMP280_REG_CONTROL                      = 0xF4
BMP280_REG_CONFIG                       = 0xF5
BMP280_REG_PRESSUREDATA                 = 0xF7
BMP280_REG_TEMPDATA                     = 0xFA

#------------------------------------------------------------------------------------------------------#

class BMP280:
    def __init__(self, i2c, address = BMP280_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address
        self.T_Fine = 0

        # Config
        self.dig_T = [0] * 3
        for i in range(3):
            self.dig_T[i] = self.__read_s16_le(BMP280_REG_DIG_T1 + (i * 2))

        self.dig_P = [0] * 9
        for i in range(9):
            self.dig_P[i] = self.__read_s16_le(BMP280_REG_DIG_P1 + (i * 2))

        self.__write_reg(BMP280_REG_CONTROL, 0x3F)

    # Write data to register
    def __write_reg(self, reg, value):
        self.__i2c.i2c_write_block_data(self.__address, reg, [value])

    # Read UINT8
    def __read_u8(self, reg):
        self.__i2c.i2c_write_byte(self.__address, reg)
        return self.__i2c.i2c_read_byte(self.__address)

    # Read UINT16 big endian
    def __read_u16(self, reg):
        self.__i2c.i2c_write_byte(self.__address, reg)
        read = self.__i2c.i2c_read_data(self.__address, 2)

        return int.from_bytes([read[0], read[1]], byteorder = 'big', signed = False)

    # Read UINT16 little endian
    def __read_u16_le(self, reg):
        self.__i2c.i2c_write_byte(self.__address, reg)
        read = self.__i2c.i2c_read_data(self.__address, 2)

        return int.from_bytes([read[0], read[1]], byteorder = 'little', signed = False)

    # Read INT16 big endian
    def __read_s16(self, reg):
        self.__i2c.i2c_write_byte(self.__address, reg)
        read = self.__i2c.i2c_read_data(self.__address, 2)

        return int.from_bytes([read[0], read[1]], byteorder = 'big', signed = True)
    
    # Read INT16 little endian
    def __read_s16_le(self, reg):
        self.__i2c.i2c_write_byte(self.__address, reg)
        read = self.__i2c.i2c_read_data(self.__address, 2)

        return int.from_bytes([read[0], read[1]], byteorder = 'little', signed = True)

    # Read UINT24 big endian
    def __read_u24(self, reg):
        self.__i2c.i2c_write_byte(self.__address, reg)
        read = self.__i2c.i2c_read_data(self.__address, 3)

        return int.from_bytes([read[0], read[1], read[2]], byteorder = 'big', signed = False)

    #--------------------------------------------------------------------------------------------------#

    # Get device id
    # Default 0x58
    def get_device_id(self):
        return self.__read_u8(BMP280_REG_CHIPID)
    
    # Get temperature value
    # Return: The temperature in degress celcius
    def get_temperature(self):
        adc = self.__read_u24(BMP280_REG_TEMPDATA)
        adc = adc >> 4

        var1 = ( ((adc >> 3) - (self.dig_T[0] << 1)) *  self.dig_T[1]) >> 11
        var2 = pow((adc >> 4) - self.dig_T[0], 2) >> 12
        var2 = (var2 * self.dig_T[2]) >> 14
        self.T_Fine = var1 + var2
        T = (self.T_Fine * 5 + 128) >> 8

        return T / 100

    # Get pressure value
    # Return: Barometric pressure in Pa
    def get_pressure(self):
        # Call getTemperature to get t_fine
        self.get_temperature()

        adc = self.__read_u24(BMP280_REG_PRESSUREDATA)
        adc = adc >> 4

        var1 = self.T_Fine - 128000
        var2 = pow(var1, 2) * self.dig_P[5]
        var2 = var2 + ((var1 * self.dig_P[4]) << 17)
        var2 = var2 + (self.dig_P[3] << 35)
        var1 = ( (pow(var1, 2) * self.dig_P[2]) >> 8 ) + ((var1 * self.dig_P[1]) << 12)
        var1 = ((1 << 47) + var1) * self.dig_P[0] >> 33

        if var1 == 0:
            return 0
        
        P = 1048576 - adc
        P = (((P << 31) - var2) * 3125) / var1
        var1 = (self.dig_P[8] * pow(P / 8192, 2)) / 33554432 # >> 25
        var2 = (self.dig_P[7] * P) / 524288
        P = ((P + var1 + var2) / 256) + (self.dig_P[7] * 16)

        return int(P / 256)

#-------------------------- Example --------------------------

"""
i2c = I2C()
bmp280 = BMP280(i2c)
print(bmp280.get_device_id())

while True:
    sleep(1)
    print(bmp280.get_temperature())
    print(bmp280.get_pressure())
"""