#!/usr/bin/python3
#
# touch_sensor.py
#
# Created on: April 22, 2021
# Author: LongHD
#
# Reference https://github.com/Seeed-Studio/Grove_I2C_Touch_Sensor
# https://wiki.seeedstudio.com/Grove-I2C_Touch_Sensor/
#

#------------------------------------------------------------------------------------------------------#

from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

TOUCH_SS_I2C_ADDRESS                      = 0x5A # The device i2c address in default

# MPR121 Register Defines
MHD_R                                     = 0x2B
NHD_R                                     = 0x2C
NCL_R                                     = 0x2D
FDL_R                                     = 0x2E
MHD_F                                     = 0x2F
NHD_F                                     = 0x30
NCL_F                                     = 0x31
FDL_F                                     = 0x32
ELE0_T                                    = 0x41
ELE0_R                                    = 0x42
ELE1_T                                    = 0x43
ELE1_R                                    = 0x44
ELE2_T                                    = 0x45
ELE2_R                                    = 0x46
ELE3_T                                    = 0x47
ELE3_R                                    = 0x48
ELE4_T                                    = 0x49
ELE4_R                                    = 0x4A
ELE5_T                                    = 0x4B
ELE5_R                                    = 0x4C
ELE6_T                                    = 0x4D
ELE6_R                                    = 0x4E
ELE7_T                                    = 0x4F
ELE7_R                                    = 0x50
ELE8_T                                    = 0x51
ELE8_R                                    = 0x52
ELE9_T                                    = 0x53
ELE9_R                                    = 0x54
ELE10_T                                   = 0x55
ELE10_R                                   = 0x56
ELE11_T                                   = 0x57
ELE11_R                                   = 0x58
FIL_CFG                                   = 0x5D
ELE_CFG                                   = 0x5E
GPIO_CTRL0                                = 0x73
GPIO_CTRL1                                = 0x74
GPIO_DATA                                 = 0x75
GPIO_DIR                                  = 0x76
GPIO_EN                                   = 0x77
GPIO_SET                                  = 0x78
GPIO_CLEAR                                = 0x79
GPIO_TOGGLE                               = 0x7A
ATO_CFG0                                  = 0x7B
ATO_CFGU                                  = 0x7D
ATO_CFGL                                  = 0x7E
ATO_CFGT                                  = 0x7F

# Global Constants
TOU_THRESH                                = 0x0F
REL_THRESH                                = 0x0A

#------------------------------------------------------------------------------------------------------#

class TouchSensor:
    # See datasheet for more detail
    # https://www.sparkfun.com/datasheets/Components/MPR121.pdf
    def __init__(self, i2c, address = TOUCH_SS_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address
        self.mpr121_setup()

    # Set register
    def __set_register(self, reg, value):
        data = [reg, value]
        self.__i2c.i2c_write_data(self.__address, data)

    # There are 12 electrodes CH0-CH11
    # CH0-CH3 are connected to 4 Touch feelers
    # The CH4-CH11 are for customer expanding the function
    # If you need more, you can make the feelers by yourself
    # The INT pin has to be led out if customers want to use the interrupt pin of MPR121
    # First config parameters
    def mpr121_setup(self):
        # Section A - Controls filtering when data is > baseline
        self.__set_register(MHD_R, 0x01)
        self.__set_register(NHD_R, 0x01)
        self.__set_register(NCL_R, 0x00)
        self.__set_register(FDL_R, 0x00)
        
        # Section B - Controls filtering when data is < baseline
        self.__set_register(MHD_F, 0x01)
        self.__set_register(NHD_F, 0x01)
        self.__set_register(NCL_F, 0xFF)
        self.__set_register(FDL_F, 0x02)

        # Section C - Sets touch and release thresholds for each electrode
        self.__set_register(ELE0_T, TOU_THRESH)
        self.__set_register(ELE0_R, REL_THRESH)
        self.__set_register(ELE1_T, TOU_THRESH)
        self.__set_register(ELE1_R, REL_THRESH)
        self.__set_register(ELE2_T, TOU_THRESH)
        self.__set_register(ELE2_R, REL_THRESH)
        self.__set_register(ELE3_T, TOU_THRESH)
        self.__set_register(ELE3_R, REL_THRESH)
        self.__set_register(ELE4_T, TOU_THRESH)
        self.__set_register(ELE4_R, REL_THRESH)
        self.__set_register(ELE5_T, TOU_THRESH)
        self.__set_register(ELE5_R, REL_THRESH)
        self.__set_register(ELE6_T, TOU_THRESH)
        self.__set_register(ELE6_R, REL_THRESH)
        self.__set_register(ELE7_T, TOU_THRESH)
        self.__set_register(ELE7_R, REL_THRESH)
        self.__set_register(ELE8_T, TOU_THRESH)
        self.__set_register(ELE8_R, REL_THRESH)
        self.__set_register(ELE9_T, TOU_THRESH)
        self.__set_register(ELE9_R, REL_THRESH)
        self.__set_register(ELE10_T, TOU_THRESH)
        self.__set_register(ELE10_R, REL_THRESH)
        self.__set_register(ELE11_T, TOU_THRESH)
        self.__set_register(ELE11_R, REL_THRESH)

        # Section D - Set the Filter Configuration
        self.__set_register(FIL_CFG, 0x04)

        # Section E - Electrode Configuration
        # Set ELE_CFG to 0x00 to return to standby mode
        self.__set_register(ELE_CFG, 0x0C)               # Enables all 12 Electrodes

    #--------------------------------------------------------------------------------------------------#

    # Get raw data (UINT16), 12 state ~ 12 bit (0 - 11) of raw data (16 bits)
    # bit = 1 -> is touched
    # bit = 0 -> is not touched
    def get_touch_raw(self):    
        # Get data from slave
        data = self.__i2c.i2c_read_data(self.__address, 2)
        raw = (data[0] | (data[1] << 8)) & 0xFFFF
        return raw

    # Get list of 12 channels input value
    # If is touched, value = 1 else value = 0
    # Return list of input
    def get_touch_input(self):
        # Get raw data
        touched = self.get_touch_raw()

        # 12 channel is 12 bit (0 - 11)
        touch_input = [0] * 12
        for i in range(12):
            if touched & (1 << i):
                touch_input[i] = 1
            else:
                touch_input[i] = 0
        
        return touch_input

#-------------------------- Example --------------------------

"""
from time import sleep

i2c = I2C()
touch_sensor = TouchSensor(i2c)
while True:
    print(touch_sensor.get_touch_raw())         # Raw data
    print(touch_sensor.get_touch_input())    # List result
    sleep(1)
"""