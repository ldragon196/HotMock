#!/usr/bin/python3
#
# MMA7660FC.py
#
# Created on: April 26, 2021
# Author: LongHD
#
# Accel and Gyro Sensor
# Reference https://github.com/Seeed-Studio/Accelerometer_MMA7660
# https://files.seeedstudio.com/wiki/Grove-3-Axis_Digital_Accelerometer-1.5g/res/MMA7660FC.pdf
#

#------------------------------------------------------------------------------------------------------#

from time import sleep
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

MMA7660FC_I2C_ADDRESS                       = 0x4C # The device i2c address in default

# MMA7660FC Register Map
MMA7660FC_XOUT						= 0x00 # Output Value X
MMA7660FC_YOUT						= 0x01 # Output Value Y
MMA7660FC_ZOUT						= 0x02 # Output Value Z
MMA7660FC_TILT						= 0x03 # Tilt Status
MMA7660FC_SRST						= 0x04 # Sampling Rate Status
MMA7660FC_SPCNT						= 0x05 # Sleep Count
MMA7660FC_INTSU						= 0x06 # Interrupt Status
MMA7660FC_MODE						= 0x07 # Mode Register
MMA7660FC_SR						= 0x08 # Sample Rate Register
MMA7660FC_PDET						= 0x09 # Tap/Pulse Detection Register
MMA7660FC_PD						= 0x0A # Tap/Pulse Debounce Count Register

# MMA7660FC Mode Register
MMA7660FC_MODE_STANDBY				= 0x00 # Standby Mode
MMA7660FC_MODE_TEST					= 0x04 # Test Mode
MMA7660FC_MODE_ACTIVE				= 0x01 # Active Mode
MMA7660FC_AWE_EN					= 0x08 # Auto-Wake Enabled
MMA7660FC_AWE_DS					= 0x00 # Auto-Wake Disabled
MMA7660FC_ASE_EN					= 0x10 # Auto-Sleep Enabled
MMA7660FC_ASE_DS					= 0x00 # Auto-Sleep Disabled
MMA7660FC_SCPS_16					= 0x20 # Prescaler is divide by 16
MMA7660FC_SCPS_1					= 0x00 # Prescaler is divide by 1
MMA7660FC_IPP_OPEN					= 0x00 # Interrupt output INT is open-drain
MMA7660FC_IPP_PUSH					= 0x40 # Interrupt output INT is push-pull
MMA7660FC_IAH_LOW					= 0x00 # Interrupt output INT is active low
MMA7660FC_IAH_HIGH					= 0x80 # Interrupt output INT is active high

# MMA7660FC Sample Rate Register
MMA7660FC_AMSR_120					= 0x00 # 120 Samples/Second Active and Auto-Sleep Mode
MMA7660FC_AMSR_64					= 0x01 # 64 Samples/Second Active and Auto-Sleep Mode
MMA7660FC_AMSR_32					= 0x02 # 32 Samples/Second Active and Auto-Sleep Mode
MMA7660FC_AMSR_16					= 0x03 # 16 Samples/Second Active and Auto-Sleep Mode
MMA7660FC_AMSR_8					= 0x04 # 8 Samples/Second Active and Auto-Sleep Mode
MMA7660FC_AMSR_4					= 0x05 # 4 Samples/Second Active and Auto-Sleep Mode
MMA7660FC_AMSR_2					= 0x06 # 2 Samples/Second Active and Auto-Sleep Mode
MMA7660FC_AMSR_1					= 0x07 # 1 Samples/Second Active and Auto-Sleep Mode
MMA7660FC_AWSR_32					= 0x00 # 32 Samples/Second Auto-Wake Mode
MMA7660FC_AWSR_16					= 0x08 # 16 Samples/Second Auto-Wake Mode
MMA7660FC_AWSR_8					= 0x10 # 8 Samples/Second Auto-Wake Mode
MMA7660FC_AWSR_1					= 0x18 # 1 Samples/Second Auto-Wake Mode

#------------------------------------------------------------------------------------------------------#

class MMA7660FC:
    def __init__(self, i2c, address = MMA7660FC_I2C_ADDRESS):
        self.__address = address
        self.__i2c = i2c
        
        self.__start()
    
    # Write to register
    def __command(self, register, value):
        self.__i2c.i2c_write_block_data(self.__address, register, [value])

    # Read data from register
    def __read_data(self, reg, size):
        return self.__i2c.i2c_read_block_data(self.__address, reg, size)

    def __start(self):
        # First config
        self.mode(MMA7660FC_MODE_STANDBY)
        self.set_sample_rate(MMA7660FC_AMSR_32)
        mode = MMA7660FC_MODE_ACTIVE | MMA7660FC_AWE_DS | MMA7660FC_ASE_DS | MMA7660FC_SCPS_1 | MMA7660FC_IAH_LOW
        self.mode(mode)
        sleep(0.1)

    #--------------------------------------------------------------------------------------------------#
    
    # Config device mode
    def mode(self, mode):
        self.__command(MMA7660FC_MODE, mode)

    # Config sample rate
    def set_sample_rate(self, rate):
        self.__command(MMA7660FC_SR, rate)

    # Get acceleration value
    # Return x, y, z value (unit g)
    def get_accel(self):
        values = self.__read_data(MMA7660FC_XOUT, 3)

        x = values[0] & 0x3F
        if x > 31:
            x -= 64
        
        y = values[1] & 0x3F
        if y > 31:
            y -= 64

        z = values[2] & 0x3F
        if z > 31:
            z -= 64
        
        # error
        if x == 0 and y == 0 and z == 0:
            self.__start()
            return 0, 0, 0

        return x * 1.5 / 31, y * 1.5 / 31, z * 1.5 / 31
    
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
mma7660fc = MMA7660FC(i2c)

while True:
    x, y, z = mma7660fc.get_accel()
    print("accleration of X/Y/Z:  x " + str(x) + "  y " + str(y) + "  z " + str(z))
    print(mma7660fc.get_direction())
    print(mma7660fc.is_vibration())
    sleep(0.01)
"""