#!/usr/bin/python3
#
# TCS3472.py
#
# Created on: April 22, 2021
# Author: LongHD
#
# Reference https://github.com/Seeed-Studio/Grove_I2C_Color_Sensor_TCS3472
# https://github.com/SeeedDocument/Grove-I2C_Color_Sensor/raw/master/res/TCS3472%20Datasheet.pdf
#

#------------------------------------------------------------------------------------------------------#

from time import sleep
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

TCS3472_I2C_ADDRESS                       = 0x29 # The device i2c address in default

TCS34725_COMMAND_BIT                      = 0x80

TCS34725_ENABLE                           = 0x00
TCS34725_ENABLE_AIEN                      = 0x10    # RGBC Interrupt Enable
TCS34725_ENABLE_WEN                       = 0x08    # Wait enable - Writing 1 activates the wait timer
TCS34725_ENABLE_AEN                       = 0x02    # RGBC Enable - Writing 1 actives the ADC, 0 disables it
TCS34725_ENABLE_PON                       = 0x01    # Power on - Writing 1 activates the internal oscillator, 0 disables it
TCS34725_ATIME                            = 0x01    # Integration time
TCS34725_WTIME                            = 0x03    # Wait time (if TCS34725_ENABLE_WEN is asserted
TCS34725_WTIME_2_4MS                      = 0xFF    # WLONG0 = 2.4ms   WLONG1 = 0.029s
TCS34725_WTIME_204MS                      = 0xAB    # WLONG0 = 204ms   WLONG1 = 2.45s 
TCS34725_WTIME_614MS                      = 0x00    # WLONG0 = 614ms   WLONG1 = 7.4s  
TCS34725_AILTL                            = 0x04    # Clear channel lower interrupt threshold
TCS34725_AILTH                            = 0x05
TCS34725_AIHTL                            = 0x06    # Clear channel upper interrupt threshold
TCS34725_AIHTH                            = 0x07
TCS34725_PERS                             = 0x0C    # Persistence register - basic SW filtering mechanism for interrupts
TCS34725_PERS_NONE                        = 0b0000  # Every RGBC cycle generates an interrupt
TCS34725_PERS_1_CYCLE                     = 0b0001  # 1 clean channel value outside threshold range generates an interrupt
TCS34725_PERS_2_CYCLE                     = 0b0010  # 2 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_3_CYCLE                     = 0b0011  # 3 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_5_CYCLE                     = 0b0100  # 5 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_10_CYCLE                    = 0b0101  # 10 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_15_CYCLE                    = 0b0110  # 15 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_20_CYCLE                    = 0b0111  # 20 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_25_CYCLE                    = 0b1000  # 25 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_30_CYCLE                    = 0b1001  # 30 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_35_CYCLE                    = 0b1010  # 35 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_40_CYCLE                    = 0b1011  # 40 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_45_CYCLE                    = 0b1100  # 45 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_50_CYCLE                    = 0b1101  # 50 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_55_CYCLE                    = 0b1110  # 55 clean channel values outside threshold range generates an interrupt
TCS34725_PERS_60_CYCLE                    = 0b1111  # 60 clean channel values outside threshold range generates an interrupt
TCS34725_CONFIG                           = 0x0D
TCS34725_CONFIG_WLONG                     = 0x02    # Choose between short and long (12x wait times via TCS34725_WTIME
TCS34725_CONTROL                          = 0x0F    # Set the gain level for the sensor
TCS34725_ID                               = 0x12    # 0x44 = TCS34721/TCS34725, 0x4D = TCS34723/TCS34727
TCS34725_STATUS                           = 0x13
TCS34725_STATUS_AINT                      = 0x10    # RGBC Clean channel interrupt
TCS34725_STATUS_AVALID                    = 0x01    # Indicates that the RGBC channels have completed an integration cycle
TCS34725_CDATAL                           = 0x14    # Clear channel data
TCS34725_CDATAH                           = 0x15
TCS34725_RDATAL                           = 0x16    # Red channel data
TCS34725_RDATAH                           = 0x17
TCS34725_GDATAL                           = 0x18    # Green channel data
TCS34725_GDATAH                           = 0x19
TCS34725_BDATAL                           = 0x1A    # Blue channel data
TCS34725_BDATAH                           = 0x1B

# Integration time
TCS34725_INTEGRATIONTIME_2_4MS            = 0xFF    # 2.4ms - 1 cycle    - Max Count: 1024
TCS34725_INTEGRATIONTIME_24MS             = 0xF6    # 24ms  - 10 cycles  - Max Count: 10240
TCS34725_INTEGRATIONTIME_50MS             = 0xEB    # 50ms  - 20 cycles  - Max Count: 20480
TCS34725_INTEGRATIONTIME_101MS            = 0xD5    # 101ms - 42 cycles  - Max Count: 43008
TCS34725_INTEGRATIONTIME_154MS            = 0xC0    # 154ms - 64 cycles  - Max Count: 65535
TCS34725_INTEGRATIONTIME_700MS            = 0x00    # 700ms - 256 cycles - Max Count: 65535

# Gain
TCS34725_GAIN_1X                          = 0x00    # No gain
TCS34725_GAIN_4X                          = 0x01    # 4x gain
TCS34725_GAIN_16X                         = 0x02    # 16x gain
TCS34725_GAIN_60X                         = 0x03    # 60x gain

#------------------------------------------------------------------------------------------------------#

class TCS3472:
    def __init__(self, i2c, address = TCS3472_I2C_ADDRESS, it = TCS34725_INTEGRATIONTIME_700MS, gain = TCS34725_GAIN_1X):
        self.__i2c = i2c
        self.__address = address
        self.set_integration_time(it)
        self.set_gain(gain)
        self.enable()
        self.__delay()

    # Write byte to register
    # reg: register address
    # value: byte to write
    def __command(self, reg, value):
        data = [TCS34725_COMMAND_BIT | reg, value]
        self.__i2c.i2c_write_data(self.__address, data)

    # Read byte from register
    # reg: register address
    def __read8(self, reg):
        self.__i2c.i2c_write_data(self.__address, TCS34725_COMMAND_BIT | reg)
        return self.__i2c.i2c_read_byte(self.__address)

    # Read UINT16 (2 bytes) from register
    # reg: register address
    def __read16(self, reg):
        self.__i2c.i2c_write_byte(self.__address, TCS34725_COMMAND_BIT | reg)
        read = self.__i2c.i2c_read_data(self.__address, 2)
        return ((read[1] << 8) | read[0]) & 0xFFFF

    # Set a delay for the integration time
    # This is only necessary in the case where enabling and then immediately trying to read values back
    # This is because setting AEN triggers an automatic integration, so if a read RGBC is
    # performed too quickly, the data is not yet valid and all 0's are returned
    def __delay(self):
        if self.__integ == TCS34725_INTEGRATIONTIME_2_4MS:
            sleep(0.003)
        elif self.__integ == TCS34725_INTEGRATIONTIME_24MS:
            sleep(0.024)
        elif self.__integ == TCS34725_INTEGRATIONTIME_50MS:
            sleep(0.050)
        elif self.__integ == TCS34725_INTEGRATIONTIME_101MS:
            sleep(0.101)
        elif self.__integ == TCS34725_INTEGRATIONTIME_154MS:
            sleep(0.154)
        elif self.__integ == TCS34725_INTEGRATIONTIME_700MS:
            sleep(0.700)

    #--------------------------------------------------------------------------------------------------#

    # Enables the device
    def enable(self):
        self.__command(TCS34725_ENABLE, TCS34725_ENABLE_PON)
        sleep(.003)
        self.__command(TCS34725_ENABLE, TCS34725_ENABLE_PON | TCS34725_ENABLE_AEN)

    # Disables the device (putting it in lower power sleep mode)
    def disable(self):
        reg = self.__read8(TCS34725_ENABLE)
        reg &= ~(TCS34725_ENABLE_PON | TCS34725_ENABLE_AEN)
        # Turn the device off to save power
        self.__command(TCS34725_ENABLE, reg)

    # Sets the integration time for the TC34725
    # See constant "Integration time"
    # example: TCS34725_INTEGRATIONTIME_2_4MS
    def set_integration_time(self, it):
        # Update the timing register
        self.__command(TCS34725_ATIME, it)
        self.__integ = it
    
    # Adjusts the gain on the TCS34725 (adjusts the sensitivity to light)
    # See constant "Gain"
    # example: TCS34725_GAIN_1X
    def set_gain(self, gain):
        # Update the timing register
        self.__command(TCS34725_CONTROL, gain)
        self.__gain = gain

    #--------------------------------------------------------------------------------------------------#

    # Reads the raw red, green, blue and clear channel values
    # Wait for measurement and convertation
    # Retur r, g, b, c raw data
    def get_raw_data(self):
        r = self.__read16(TCS34725_RDATAL)
        g = self.__read16(TCS34725_GDATAL)
        b = self.__read16(TCS34725_BDATAL)
        c = self.__read16(TCS34725_CDATAL)
        self.__delay()

        return [r, g, b, c]
    
    # Converts the raw R/G/B values to color temperature in degrees Kelvin
    # Return the results in degrees Kelvin
    # r, g, b: raw data read from sensor
    def calculate_color_temperature(self, r, g, b):
        if r == 0 and g == 0 and b == 0:
            return None
        # Map RGB values to their XYZ counterparts
        # Based on 6500K fluorescent, 3000K fluorescent and 60W incandescent values for a wide range
        # Note: Y = Illuminance or lux
        X = (-0.14282 * r) + (1.54924 * g) + (-0.95641 * b)
        Y = (-0.32466 * r) + (1.57837 * g) + (-0.73191 * b)
        Z = (-0.68202 * r) + (0.77073 * g) + (0.56332 * b)

        # Calculate the chromaticity co-ordinates
        xc = (X) / (X + Y + Z)
        yc = (Y) / (X + Y + Z)

        # Use McCamy's formula to determine the CCT
        n = (xc - 0.3320) / (0.1858 - yc)

        # Calculate the final CCT
        cct = (449.0 * pow(n, 3)) + (3525.0 * pow(n, 2)) + (6823.3 * n) + 5520.33

        return int(cct)

    # Converts the raw R/G/B values to lux
    # r, g, b: raw data read from sensor
    def calculate_lux(self, r, g, b):
        # This only uses RGB ... how can we integrate clear or calculate lux
        # based exclusively on clear since this might be more reliable?
        lux = (-0.32466 * r) + (1.57837 * g) + (-0.73191 * b)

        return int(lux)

    # Converts the raw R/G/B values to rgb
    # r, g, b: raw data read from sensor
    def calculate_rgb(self, r, g, b, c):
        if r == 0 and g == 0 and b == 0:
            return None, None, None
        
        red = int(r * 255 / c)
        green = int(g * 255 / c)
        blue = int(b * 255 / c)
        
        return red, green, blue

    # Read and Converts the raw R/G/B values to rgb
    # Return rgb value
    def get_rgb(self):
        r, g, b, c = tcs3472.get_raw_data()
        return tcs3472.calculate_rgb(r, g, b, c)


#-------------------------- Example --------------------------

"""
i2c = I2C()
tcs3472 = TCS3472(i2c)

# Read multipe
# r, g, b, c = tcs3472.get_raw_data()
# k = tcs3472.calculate_color_temperature(r, g, b)
# lux = tcs3472.calculate_lux(r, g, b)
# red, green, blue = tcs3472.calculate_rgb(r, g, b, c)
# print("k " + str(k))
# print("lux " + str(lux))

while True:
    red, green, blue = tcs3472.get_rgb()
    print("r " + hex(red) + ", g " + hex(green) + ", b " + hex(blue))
    sleep(1)
"""