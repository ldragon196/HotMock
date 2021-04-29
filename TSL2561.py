#!/usr/bin/python3
#
# TSL2561.py
#
# Created on: April 22, 2021
# Author: LongHD
#
# Reference https://github.com/Seeed-Studio/Grove_Digital_Light_Sensor
# https://raw.githubusercontent.com/SeeedDocument/Grove-Digital_Light_Sensor/master/res/TSL2561T.pdf
#

#------------------------------------------------------------------------------------------------------#

from time import sleep
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

TSL2561_I2C_ADDRESS                       = 0x29 # The device i2c address in default

# Register address, see "Register Set" and "Table 2. Register Address" in datasheet for more detail
TSL2561_CONTROL                           = 0x80
TSL2561_TIMING                            = 0x81
TSL2561_INTERRUPT                         = 0x86

TSL2561_CHANNEL0_L                        = 0x8C
TSL2561_CHANNEL0_H                        = 0x8D
TSL2561_CHANNEL1_L                        = 0x8E
TSL2561_CHANNEL1_H                        = 0x8F

# Scale
LUX_SCALE                                 = 14      # scale by 2^14
RATIO_SCALE                               = 9       # scale ratio by 2^9
CH_SCALE                                  = 10      # scale channel values by 2^10
CH_SCALE_INTERG0                          = 0x7517  # 322/11 * 2^CH_SCALE
CH_SCALE_INTERG1                          = 0x0FE7  # 322/81 * 2^CH_SCALE

# See "Simplified Lux Calculation" in datasheet for more detail
K1T                                       = 0x0040  # 0.125 * 2^RATIO_SCALE
B1T                                       = 0x01F2  # 0.0304 * 2^LUX_SCALE
M1T                                       = 0x01BE  # 0.0272 * 2^LUX_SCALE
K2T                                       = 0x0080  # 0.250 * 2^RATIO_SCALE
B2T                                       = 0x0214  # 0.0325 * 2^LUX_SCALE
M2T                                       = 0x02D1  # 0.0440 * 2^LUX_SCALE
K3T                                       = 0x00C0  # 0.375 * 2^RATIO_SCALE
B3T                                       = 0x023F  # 0.0351 * 2^LUX_SCALE
M3T                                       = 0x037B  # 0.0544 * 2^LUX_SCALE
K4T                                       = 0x0100  # 0.50 * 2^RATIO_SCALE
B4T                                       = 0x0270  # 0.0381 * 2^LUX_SCALE
M4T                                       = 0x03FE  # 0.0624 * 2^LUX_SCALE
K5T                                       = 0x0138  # 0.61 * 2^RATIO_SCALE
B5T                                       = 0x016F  # 0.0224 * 2^LUX_SCALE
M5T                                       = 0x01FC  # 0.0310 * 2^LUX_SCALE
K6T                                       = 0x019A  # 0.80 * 2^RATIO_SCALE
B6T                                       = 0x00D2  # 0.0128 * 2^LUX_SCALE
M6T                                       = 0x00FB  # 0.0153 * 2^LUX_SCALE
K7T                                       = 0x029A  # 1.3 * 2^RATIO_SCALE
B7T                                       = 0x0018  # 0.00146 * 2^LUX_SCALE
M7T                                       = 0x0012  # 0.00112 * 2^LUX_SCALE
K8T                                       = 0x029A  # 1.3 * 2^RATIO_SCALE
B8T                                       = 0x0000  # 0.000 * 2^LUX_SCALE
M8T                                       = 0x0000  # 0.000 * 2^LUX_SCALE

K1C                                       = 0x0043  # 0.130 * 2^RATIO_SCALE
B1C                                       = 0x0204  # 0.0315 * 2^LUX_SCALE
M1C                                       = 0x01AD  # 0.0262 * 2^LUX_SCALE
K2C                                       = 0x0085  # 0.260 * 2^RATIO_SCALE
B2C                                       = 0x0228  # 0.0337 * 2^LUX_SCALE
M2C                                       = 0x02C1  # 0.0430 * 2^LUX_SCALE
K3C                                       = 0x00C8  # 0.390 * 2^RATIO_SCALE
B3C                                       = 0x0253  # 0.0363 * 2^LUX_SCALE
M3C                                       = 0x0363  # 0.0529 * 2^LUX_SCALE
K4C                                       = 0x010A  # 0.520 * 2^RATIO_SCALE
B4C                                       = 0x0282  # 0.0392 * 2^LUX_SCALE
M4C                                       = 0x03DF  # 0.0605 * 2^LUX_SCALE
K5C                                       = 0x014D  # 0.65 * 2^RATIO_SCALE
B5C                                       = 0x0177  # 0.0229 * 2^LUX_SCALE
M5C                                       = 0x01DD  # 0.0291 * 2^LUX_SCALE
K6C                                       = 0x019A  # 0.80 * 2^RATIO_SCALE
B6C                                       = 0x0101  # 0.0157 * 2^LUX_SCALE
M6C                                       = 0x0127  # 0.0180 * 2^LUX_SCALE
K7C                                       = 0x029A  # 1.3 * 2^RATIO_SCALE
B7C                                       = 0x0037  # 0.00338 * 2^LUX_SCALE
M7C                                       = 0x002B  # 0.00260 * 2^LUX_SCALE
K8C                                       = 0x029A  # 1.3 * 2^RATIO_SCALE
B8C                                       = 0x0000  # 0.000 * 2^LUX_SCALE
M8C                                       = 0x0000  # 0.000 * 2^LUX_SCALE


#------------------------------------------------------------------------------------------------------#

class TSL2561:
    def __init__(self, i2c, address = TSL2561_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address

        # Initialization
        self.__write_register(TSL2561_CONTROL, 0x03)      # Power up
        self.__write_register(TSL2561_TIMING, 0x00)       # No High Gain (1x), integration time of 13.7 ms
        self.__write_register(TSL2561_INTERRUPT, 0x00)    # Disable interrupt
        self.__write_register(TSL2561_CONTROL, 0x00)      # Power down

    # Read byte from register
    # register: register address to read
    # return read byte
    def __read_register(self, register):
        read = self.__i2c.i2c_read_block_data(self.__address, register, 1)
        return read[0]

    # Write byte to register
    # register: register address to read
    # value: byte to write
    def __write_register(self, register, value):
        self.__i2c.i2c_write_block_data(self.__address, register, [value])

    #--------------------------------------------------------------------------------------------------#

    # Get value from adc channel 0, 1
    # Return UINT16 value (channel 0, channel 1)
    def __get_chx_value(self):
        ch0_l = self.__read_register(TSL2561_CHANNEL0_L)
        ch0_h = self.__read_register(TSL2561_CHANNEL0_H)
        ch1_l = self.__read_register(TSL2561_CHANNEL1_L)
        ch1_h = self.__read_register(TSL2561_CHANNEL1_H)
        
        # Convert to UINT16
        ch0 = ((ch0_h << 8) | ch0_l) & 0xFFFF
        ch1 = ((ch1_h << 8) | ch1_l) & 0xFFFF
        return ch0, ch1

    def __calculation_lux(self, ch0, ch1, gain, interg, itype):
        ch_scale = 0
        if interg == 0:                  # 13.7 ms
            ch_scale = CH_SCALE_INTERG0
        elif interg == 1:                # 100 ms
            ch_scale = CH_SCALE_INTERG
        else:                            # assume no scaling
            ch_scale = 1 << CH_SCALE

        if gain == 0:
            ch_scale = ch_scale << 4     # scale 1X to 16X
        
        channel0 = (ch0 * ch_scale) >> CH_SCALE
        channel1 = (ch1 * ch_scale) >> CH_SCALE

        ratio1 = 0
        if channel0 != 0:
            ratio1 = (channel1 << (RATIO_SCALE + 1)) / channel0
        ratio = (ratio1 + 1) / 2

        b = 0
        m = 0
        # T package
        if itype == 0:
            if (ratio >= 0) and (ratio <= K1T):
                b = B1T
                m = M1T
            elif ratio <= K2T:
                b = B2T
                m = M2T
            elif ratio <= K3T:
                b = B3T
                m = M3T
            elif ratio <= K4T:
                b = B4T
                m = M4T
            elif ratio <= K5T:
                b = B5T
                m = M5T
            elif ratio <= K6T:
                b = B6T
                m = M6T
            elif ratio <= K7T:
                b = B7T
                m = M7T
            elif ratio > K8T:
                b = B8T
                m = M8T
        
        # CS package
        elif itype == 1:
            if (ratio >= 0) and (ratio <= K1C):
                b = B1C
                m = M1C
            elif ratio <= K2C:
                b = B2C
                m = M2C
            elif ratio <= K3C:
                b = B3C
                m = M3C
            elif ratio <= K4C:
                b = B4C
                m = M4C
            elif ratio <= K5C:
                b = B5C
                m = M5C
            elif ratio <= K6C:
                b = B6C
                m = M6C
            elif ratio <= K7C:
                b = B7C
                m = M7C
            elif ratio > K8C:
                b = B8C
                m = M8C

        temp = ((channel0 * b) - (channel1 * m))
        if temp < 0:
            temp = 0
        temp += (1 << (LUX_SCALE - 1))
        lux = temp >> LUX_SCALE
        return lux

    #--------------------------------------------------------------------------------------------------#

    # Return raw value only, not convert to lux
    # ch0: Full Spectrum channel value
    # ch1: Infrared channel value
    def get_raw_value(self):
        self.__write_register(TSL2561_CONTROL, 0x03)      # Power up
        sleep(0.015)                                      # Power up and wait > 13.7 ms for measure
        ch0, ch1 = self.__get_chx_value()                 # Read add channel 0, 1
        self.__write_register(TSL2561_CONTROL, 0x00)      # Power down
        if ch1 == 0:
            return 0, 0
        
        # Ch0 out of range, but ch1 not. the lux is not valid in this situation
        if ch0 / ch1 < 2 and ch0 > 4900:
            return None, None

        return ch0, ch1

    # Get lux value
    # Return lux value
    # If error, return None
    def get_lux(self):
        self.__write_register(TSL2561_CONTROL, 0x03)      # Power up
        sleep(0.015)                                      # Power up and wait > 13.7 ms for measure
        ch0, ch1 = self.__get_chx_value()                 # Read add channel 0, 1
        self.__write_register(TSL2561_CONTROL, 0x00)      # Power down
        if ch1 == 0:
            return 0
        
        # Ch0 out of range, but ch1 not. the lux is not valid in this situation
        if ch0 / ch1 < 2 and ch0 > 4900:
            return None

        lux = self.__calculation_lux(ch0, ch1, 0, 0, 0)   # T package, no gain, 13.7 ms
        return lux

#-------------------------- Example --------------------------

"""
i2c = I2C()
tsl2561 = TSL2561(i2c)
while True:
    print(tsl2561.get_lux())
    print(tsl2561.get_raw_value())
    sleep(1)
"""