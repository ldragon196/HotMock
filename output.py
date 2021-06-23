#!/usr/bin/python3
#
# output.py
#
# Created on: June 23, 2021
# Author: LongHD
#
# PCA9685BS (PWM output driver)
# Reference https://pdf1.alldatasheet.com/datasheet-pdf/view/293579/NXP/PCA9685BS.html
#

#------------------------------------------------------------------------------------------------------#

from i2c.i2c import I2C
from time import sleep

#------------------------------------------------------------------------------------------------------#

PCA9685_I2C_ADDRESS        = 0x40     # The device i2c address in default

# Registers
MODE1                      = 0x00
MODE2                      = 0x01
SUBADR1                    = 0x02
SUBADR2                    = 0x03
SUBADR3                    = 0x04
PRESCALE                   = 0xFE
LED0_ON_L                  = 0x06
LED0_ON_H                  = 0x07
LED0_OFF_L                 = 0x08
LED0_OFF_H                 = 0x09
ALL_LED_ON_L               = 0xFA
ALL_LED_ON_H               = 0xFB
ALL_LED_OFF_L              = 0xFC
ALL_LED_OFF_H              = 0xFD

# Bits
RESTART                    = 0x80
SLEEP                      = 0x10
ALLCALL                    = 0x01
INVRT                      = 0x10
OUTDRV                     = 0x04

# Frequency
PCA9685_MIN_FREQ           = 40
PCA9685_MAX_FREQ           = 1000

#------------------------------------------------------------------------------------------------------#

class PCA9685:
    # Sensor with default address
    def __init__(self, i2c, address = PCA9685_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address

    # Write one byte to register with address
    def __write8(self, reg, byte):
        self.__i2c.i2c_write_block_data(self.__address, reg, [byte])

    # Read data from register
    def __read8(self, reg):
        self.__i2c.i2c_write_data(self.__address, [reg])
        return self.__i2c.i2c_read_byte(self.__address)

    #--------------------------------------------------------------------------------------------------#

    # Reset device
    def reset(self):
        self.__write8(MODE1, 0x06)    # SWRST

    # Set the PWM frequency for the entire chip, from 40Hz to 1000Hz
    def set_frequency(self, frequency):
        # Valid frequency
        if frequency < PCA9685_MIN_FREQ:
            frequency = PCA9685_MIN_FREQ
        if frequency > PCA9685_MAX_FREQ:
            frequency = PCA9685_MAX_FREQ

        # Calculate prescale
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        prescale = int(math.floor(prescaleval + 0.5))

        oldmode = self.__read8(MODE1)
        newmode = (oldmode & 0x7F) | 0x10    # sleep
        self.__write8(MODE1, newmode)        # go to sleep for configuration
        self.__write8(PRESCALE, prescale)    # set prescale
        self.__write8(MODE1, oldmode)

        sleep(0.01)
        self.__write8(MODE1, oldmode | 0x80)

    # Set a single pwm channel, see 7.3.3 LED output and PWM control
    # Start periods - 0 .... 4095 - End periods
    # Value of on/off from 0 to 4095 (12-bit resolution)
    # channel from 0 - 15
    # on: time start PWM count from start, off: time stop PWM count from start. So pulse width is off - on
    # Ex: on = 100, off = 4000 -> in on period LOW from 0 - 99, and HIGH from 100 - 4000 and then LOW from 4001 to 4095
    def set_pwm(self, channel, on, off):
        self.__write8(LED0_ON_L + 4 * channel, on & 0xFF)
        self.__write8(LED0_ON_H + 4 * channel, on >> 8)
        self.__write8(LED0_OFF_L + 4 * channel, off & 0xFF)
        self.__write8(LED0_OFF_H + 4 * channel, off >> 8)

    # Set all pwm channel, see 7.3.3 LED output and PWM control
    def set_all_pwm(self, on, off):
        self.__write8(ALL_LED_ON_L, on & 0xFF)
        self.__write8(ALL_LED_ON_H, on >> 8)
        self.__write8(ALL_LED_OFF_L, off & 0xFF)
        self.__write8(ALL_LED_OFF_H, off >> 8)

#-------------------------- Example --------------------------

"""
i2c = I2C()
pca9685 = PCA9685(i2c)
pca9685.reset()

while True:
    pca9685.set_pwm(0, 0, 1000)
    sleep(1)
    pca9685.set_pwm(1, 1000, 4096)
    sleep(1)
"""