#!/usr/bin/python3
#
# ADXL345.py
#
# Created on: April 27, 2021
# Author: LongHD
#
# ACCEL sensor
# Reference https://github.com/jakalada/Arduino-ADXL345
# http://www.analog.com/media/en/technical-documentation/data-sheets/ADXL345.pdf
# http://www.analog.com/media/jp/technical-documentation/data-sheets/ADXL345_jp.pdf
#

#------------------------------------------------------------------------------------------------------#

from time import sleep
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

ADXL345_I2C_ADDRESS                       = 0x53 # The device i2c address in default

# Please refer to the sensor datasheet.
# Register Map
# Order is "Type, Reset Value, Description".
REG_DEVID                                 = 0x00    # R,     11100101,   Device ID
REG_THRESH_TAP                            = 0x1D    # R/W,   00000000,   Tap threshold
REG_OFSX                                  = 0x1E    # R/W,   00000000,   X-axis offset
REG_OFSY                                  = 0x1F    # R/W,   00000000,   Y-axis offset
REG_OFSZ                                  = 0x20    # R/W,   00000000,   Z-axis offset
REG_DUR                                   = 0x21    # R/W,   00000000,   Tap duration
REG_LATENT                                = 0x22    # R/W,   00000000,   Tap latency 
REG_WINDOW                                = 0x23    # R/W,   00000000,   Tap window
REG_THRESH_ACT                            = 0x24    # R/W,   00000000,   Activity threshold
REG_THRESH_INACT                          = 0x25    # R/W,   00000000,   Inactivity threshold
REG_TIME_INACT                            = 0x26    # R/W,   00000000,   Inactivity time
REG_ACT_INACT_CTL                         = 0x27    # R/W,   00000000,   Axis enable control for activity and inactiv ity detection
REG_THRESH_FF                             = 0x28    # R/W,   00000000,   Free-fall threshold
REG_TIME_FF                               = 0x29    # R/W,   00000000,   Free-fall time
REG_TAP_AXES                              = 0x2A    # R/W,   00000000,   Axis control for single tap/double tap
REG_ACT_TAP_STATUS                        = 0x2B    # R,     00000000,   Source of single tap/double tap
REG_BW_RATE                               = 0x2C    # R/W,   00001010,   Data rate and power mode control
REG_POWER_CTL                             = 0x2D    # R/W,   00000000,   Power-saving features control
REG_INT_ENABLE                            = 0x2E    # R/W,   00000000,   Interrupt enable control
REG_INT_MAP                               = 0x2F    # R/W,   00000000,   Interrupt mapping control
REG_INT_SOUCE                             = 0x30    # R,     00000010,   Source of interrupts
REG_DATA_FORMAT                           = 0x31    # R/W,   00000000,   Data format control
REG_DATAX0                                = 0x32    # R,     00000000,   X-Axis Data 0
REG_DATAX1                                = 0x33    # R,     00000000,   X-Axis Data 1
REG_DATAY0                                = 0x34    # R,     00000000,   Y-Axis Data 0
REG_DATAY1                                = 0x35    # R,     00000000,   Y-Axis Data 1
REG_DATAZ0                                = 0x36    # R,     00000000,   Z-Axis Data 0
REG_DATAZ1                                = 0x37    # R,     00000000,   Z-Axis Data 1
REG_FIFO_CTL                              = 0x38    # R/W,   00000000,   FIFO control
REG_FIFO_STATUS                           = 0x39    # R,     00000000,   FIFO status

# Data Rate
ADXL345_RATE_3200HZ                       = 0x0F    # 3200 Hz
ADXL345_RATE_1600HZ                       = 0x0E    # 1600 Hz
ADXL345_RATE_800HZ                        = 0x0D    # 800 Hz
ADXL345_RATE_400HZ                        = 0x0C    # 400 Hz
ADXL345_RATE_200HZ                        = 0x0B    # 200 Hz
ADXL345_RATE_100HZ                        = 0x0A    # 100 Hz
ADXL345_RATE_50HZ                         = 0x09    # 50 Hz
ADXL345_RATE_25HZ                         = 0x08    # 25 Hz
ADXL345_RATE_12_5HZ                       = 0x07    # 12.5 Hz
ADXL345_RATE_6_25HZ                       = 0x06    # 6.25 Hz
ADXL345_RATE_3_13HZ                       = 0x05    # 3.13 Hz
ADXL345_RATE_1_56HZ                       = 0x04    # 1.56 Hz
ADXL345_RATE_0_78HZ                       = 0x03    # 0.78 Hz
ADXL345_RATE_0_39HZ                       = 0x02    # 0.39 Hz
ADXL345_RATE_0_20HZ                       = 0x01    # 0.20 Hz
ADXL345_RATE_0_10HZ                       = 0x00    # 0.10 Hz

# Range
ADXL345_RANGE_2G                          = 0x00    # +-2 g
ADXL345_RANGE_4G                          = 0x01    # +-4 g
ADXL345_RANGE_8G                          = 0x02    # +-8 g
ADXL345_RANGE_16G                         = 0x03    # +-16 g

#------------------------------------------------------------------------------------------------------#

class ADXL345:
    # Sensor with default address
    def __init__(self, i2c, address = ADXL345_I2C_ADDRESS, srange = ADXL345_RANGE_16G):
        self.__i2c = i2c
        self.__address = address
        self.__range = srange

        self.set_range(srange)
        self.set_rate(ADXL345_RATE_200HZ)
        self.start()

    # Write register
    def __write_reg(self, reg, value):
        self.__i2c.i2c_write_block_data(self.__address, reg, [value])
    
    # Read bytes from register
    def __read_reg(self, reg, size):
        self.__i2c.i2c_write_byte(self.__address, reg)
        return self.__i2c.i2c_read_data(self.__address, size)

    #--------------------------------------------------------------------------------------------------#

    # Convert value to SI
    def convert(self, value):
        res = 0
        if self.__range == ADXL345_RANGE_2G:
            res = 2
        elif self.__range == ADXL345_RANGE_4G:
            res = 4
        elif self.__range == ADXL345_RANGE_8G:
            res = 8
        elif self.__range == ADXL345_RANGE_16G:
            res = 16
        else:
            return 0
        
        return (res * value * 2) / 1024.0
    
    # Set data rate
    # See constant "Data rate"
    # Ex: ADXL345_RATE_3200HZ
    #     ...
    #     ADXL345_RATE_0_10HZ
    def set_rate(self, rate):
        # Low power = 0
        self.__write_reg(REG_BW_RATE, rate & 0xFF)

    # Set range
    # See constant "Range"
    # +-2 g, +-4 g, +-8 g, +-16 g
    def set_range(self, srange):
        # range 0 - 3
        self.__write_reg(REG_DATA_FORMAT, srange & 0x03)
        self.__range = srange

    # Get device id
    # Can used for check device available
    # Default id: 0xE5 (229)
    def get_device_id(self):
        return self.__read_reg(REG_DEVID, 1)[0]

    #--------------------------------------------------------------------------------------------------#

    # Start measure value
    # Disable auto sleep
    # See datasheet for more detail
    def start(self):
        # bit measure = 1
        self.__write_reg(REG_POWER_CTL, 0x01 << 3)
    
    # Stop measure value
    # Reset to default
    def stop(self):
        # bit measure = 0
        self.__write_reg(REG_POWER_CTL, 0x00)

    # Get xyz values
    # See "Register 0x32 to Register 0x37—DATAX0, DATAX1,DATAY0, DATAY1, DATAZ0, DATAZ1 (Read Only)" in datasheet
    # DATAx0 as the least significant byte and DATAx1 as the most significant byte
    # Return value of ax, ay, az (unit g (1g = 9.8 m/s^2))
    # Normal x = 0g, y = 0g, z = 1g
    def get_accel(self):
        read = self.__read_reg(REG_DATAX0, 6)
        # Little endian
        x = int.from_bytes([read[0], read[1]], byteorder = 'little', signed = True)
        y = int.from_bytes([read[2], read[3]], byteorder = 'little', signed = True)
        z = int.from_bytes([read[4], read[5]], byteorder = 'little', signed = True)

        return self.convert(x), self.convert(y), self.convert(z)

    
    # Get direction
    # Return up (z max), down (z min), right (x max), left (x min), front (y max), back (y min)
    def get_direction(self):
        x, y, z = self.get_accel()
        THRESHOLD = 0.3

        if x > THRESHOLD and x > y and x > z:
            return "Right"
        elif x < -THRESHOLD and x < y and x < z:
            return "Left"

        elif y > THRESHOLD and y > x and y > z:
            return "Front"
        elif y < -THRESHOLD and y < x and y < z:
            return "Back"

        elif z > THRESHOLD and z > x and z > y:
            return "Up"
        elif z < -THRESHOLD and z < x and z < y:
            return "Down"
        
        else:
            return "Unknow"

    # Get sensor is vibration or not
    # Time sleep between 2 measure depends on data rate
    # Return true if is vibration
    def is_vibration(self):
        values1 = list(self.get_accel())
        sleep(0.1)  # wait new sample
        values2 = list(self.get_accel())
        sleep(0.1)  # wait new sample
        values3 = list(self.get_accel())

        delta = 0
        for i in range(3):
            delta += abs(values2[i] - values1[i]) + abs(values3[i] - values2[i])

        return delta > 0.5

#-------------------------- Example --------------------------

"""
i2c = I2C()
adxl345 = ADXL345(i2c)
while True:
    print(adxl345.get_accel())
    print(adxl345.get_direction())
    print(adxl345.is_vibration())
    sleep(0.1)

adxl345.stop()
"""