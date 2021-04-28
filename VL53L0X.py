#!/usr/bin/python3
#
# VL53L0X.py
#
# Created on: April 27, 2021
# Author: LongHD
#
# ACCEL sensor
# Reference https://docs.m5stack.com/en/unit/tof
# https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/datasheet/hat/VL53L0X_en.pdf
#

#------------------------------------------------------------------------------------------------------#

from time import sleep
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

VL53L0X_I2C_ADDRESS                         = 0x29 # The device i2c address in default

# Constants
VL53L0X_REG_IDENTIFICATION_MODEL_ID         = 0xc0
VL53L0X_REG_IDENTIFICATION_REVISION_ID      = 0xc2
VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD   = 0x50
VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD = 0x70
VL53L0X_REG_SYSRANGE_START                  = 0x00
VL53L0X_REG_RESULT_INTERRUPT_STATUS         = 0x13
VL53L0X_REG_RESULT_RANGE_STATUS             = 0x14

#------------------------------------------------------------------------------------------------------#

class VL53L0X:
    # Sensor with default address
    def __init__(self, i2c, address = VL53L0X_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address

    # Write multiple bytes register
    # Data: list of bytes
    def __write_reg(self, reg, data):
        self.__i2c.i2c_write_block_data(self.__address, reg, data)
    
    # Read bytes from register
    def __read_reg(self, reg, size):
        self.__i2c.i2c_write_byte(self.__address, reg)
        return self.__i2c.i2c_read_data(self.__address, size)

    #--------------------------------------------------------------------------------------------------#
    
    # Get device id
    # Can used for check device available, see "Table 4. Reference registers" in datasheet
    # Default id: 0xEE, 0xAA, 0x10
    def get_device_id(self):
        return self.__read_reg(VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD, 3)

    def read_range(self):
        # Start measurement
        self.__write_reg(VL53L0X_REG_SYSRANGE_START, [0x01])

        count = 0
        # Wait max timeout 1ss
        while count < 100:
            sleep(0.01)
            result = self.__read_reg(VL53L0X_REG_RESULT_RANGE_STATUS, 1)[0]
            if result & 0x01:
                break
            count += 1
        
        # Not ready
        if count >= 100:
            return None

        # Read result from register
        read = self.__read_reg(VL53L0X_REG_RESULT_RANGE_STATUS, 12)

        # ambient = int.from_bytes([read[6], read[7]], byteorder = 'little', signed = False)
        # signal_count = int.from_bytes([read[8], read[9]], byteorder = 'little', signed = False)
        distance = int.from_bytes([read[10], read[11]], byteorder = 'big', signed = False)
        status = (read[0] & 0x78) >> 3

        if status == 0x0B:
            return distance
        else:
            return None

#-------------------------- Example --------------------------


from time import sleep

i2c = I2C()
vl53l0x = VL53L0X(i2c)
while True:
    print(vl53l0x.read_range())
    print(" ")
    sleep(0.2)
