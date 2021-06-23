#!/usr/bin/python3
#
# MPU6886.py
#
# Created on: April 26, 2021
# Author: LongHD
#
# Accel and Gyro Sensor
# Reference https://github.com/m5stack/M5-ProductExampleCodes/tree/master/Unit/IMU_Unit
# https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/datasheet/core/MPU-6886-000193%2Bv1.1_GHIC_en.pdf
#

#------------------------------------------------------------------------------------------------------#

from time import sleep
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

MPU6886_I2C_ADDRESS                     = 0x68 # The device i2c address in default

IMU_6886_WHOAMI                         = 0x75
IMU_6886_ACCEL_INTEL_CTRL               = 0x69
IMU_6886_SMPLRT_DIV                     = 0x19
IMU_6886_INT_PIN_CFG                    = 0x37
IMU_6886_INT_ENABLE                     = 0x38
IMU_6886_ACCEL_XOUT_H                   = 0x3B
IMU_6886_ACCEL_XOUT_L                   = 0x3C
IMU_6886_ACCEL_YOUT_H                   = 0x3D
IMU_6886_ACCEL_YOUT_L                   = 0x3E
IMU_6886_ACCEL_ZOUT_H                   = 0x3F
IMU_6886_ACCEL_ZOUT_L                   = 0x40

IMU_6886_TEMP_OUT_H                     = 0x41
IMU_6886_TEMP_OUT_L                     = 0x42

IMU_6886_GYRO_XOUT_H                    = 0x43
IMU_6886_GYRO_XOUT_L                    = 0x44
IMU_6886_GYRO_YOUT_H                    = 0x45
IMU_6886_GYRO_YOUT_L                    = 0x46
IMU_6886_GYRO_ZOUT_H                    = 0x47
IMU_6886_GYRO_ZOUT_L                    = 0x48

IMU_6886_USER_CTRL                      = 0x6A
IMU_6886_PWR_MGMT_1                     = 0x6B
IMU_6886_PWR_MGMT_2                     = 0x6C
IMU_6886_CONFIG                         = 0x1A
IMU_6886_GYRO_CONFIG                    = 0x1B
IMU_6886_ACCEL_CONFIG                   = 0x1C
IMU_6886_ACCEL_CONFIG2                  = 0x1D
IMU_6886_FIFO_EN                        = 0x23

IMU_6886_FIFO_ENABLE                    = 0x23
IMU_6886_FIFO_COUNT                     = 0x72
IMU_6886_FIFO_R_W                       = 0x74
IMU_6886_GYRO_OFFSET                    = 0x13

# Common
G                                       = 9.8
RTA                                     = 57.324841
ATR                                     = 0.0174533
GYRO_GR                                 = 0.0010653

# Ascale
AFS_2G                                  = 0
AFS_4G                                  = 1
AFS_8G                                  = 2
AFS_16G                                 = 3

# Gscale
GFS_250DPS                              = 0
GFS_500DPS                              = 1
GFS_1000DPS                             = 2
GFS_2000DPS                             = 3

#------------------------------------------------------------------------------------------------------#

class MPU6886:
    def __init__(self, i2c, address = MPU6886_I2C_ADDRESS, acscale = AFS_8G, gyscale = GFS_2000DPS):
        self.__i2c = i2c
        self.__address = address
        self.__gyscale = gyscale
        self.__acscale = acscale
        self.__start()

    def __read_data(self, reg, size):
        return self.__i2c.i2c_read_block_data(self.__address, reg, size)

    def __write_data(self, reg, data):
        self.__i2c.i2c_write_block_data(self.__address, reg, data)

    def __start(self):
        self.__write_data(IMU_6886_PWR_MGMT_1, [0x00])
        sleep(.010)
        self.__write_data(IMU_6886_PWR_MGMT_1, [0x01 << 7]) # reset
        sleep(.1)
        self.__write_data(IMU_6886_PWR_MGMT_1, [0x01])      # autoselect clock
        sleep(.010)
        
        self.__write_data(IMU_6886_PWR_MGMT_2, [0x00])      # Enable full Accel and Gyro
        sleep(.010)

        # 1khz output
        self.__write_data(IMU_6886_CONFIG, [0x01])
        sleep(.001)

        # 2 div, FIFO 500hz out
        self.__write_data(IMU_6886_SMPLRT_DIV, [0x01])
        sleep(.001)

        self.__write_data(IMU_6886_INT_ENABLE, [0x00])
        sleep(.001)
        self.__write_data(IMU_6886_ACCEL_CONFIG2, [0x00])
        sleep(.001)
        self.__write_data(IMU_6886_USER_CTRL, [0x00])
        sleep(.001)
        self.__write_data(IMU_6886_FIFO_EN, [0x00])
        sleep(.001)
        self.__write_data(IMU_6886_INT_PIN_CFG, [0x22])
        sleep(.001)
        self.__write_data(IMU_6886_INT_ENABLE, [0x01])
        sleep(.010)
        
        self.__set_gyro_fsr(self.__gyscale)
        self.__set_accel_fsr(self.__acscale)
        sleep(.1)

    # Possible gyro scales (and their register bit settings)
    def __update_gres(self):
        if self.__gyscale == GFS_250DPS:
            self.__gres = 250.0 / 32768.0
        elif self.__gyscale == GFS_500DPS:
            self.__gres = 500.0 / 32768.0
        elif self.__gyscale == GFS_1000DPS:
            self.__gres = 1000.0 / 32768.0
        elif self.__gyscale == GFS_2000DPS:
            self.__gres = 2000.0 / 32768.0

    # Possible accelerometer scales (and their register bit settings) are
    # 2 Gs (00), 4 Gs (01), 8 Gs (10), and 16 Gs  (11)
    # Here's a bit of an algorith to calculate DPS/(ADC tick) based on that 2-bit value
    def __update_ares(self):
        if self.__acscale == AFS_2G:
            self.__ares = 2.0 / 32768.0
        elif self.__acscale == AFS_4G:
            self.__ares = 4.0 / 32768.0
        elif self.__acscale == AFS_8G:
            self.__ares = 8.0 / 32768.0
        elif self.__acscale == AFS_16G:
            self.__ares = 16.0 / 32768.0

    # Set gyro scale
    # scale: GFS_250DPS
    #        GFS_500DPS
    #        GFS_1000DPS
    #        GFS_20000DPS
    def __set_gyro_fsr(self, scale):
        self.__write_data(IMU_6886_GYRO_CONFIG, [scale << 3])
        sleep(.010)
        self.__gyscale = scale
        self.__update_gres()

    # Set accel scale
    # scale: AFS_2G
    #        AFS_4G
    #        AFS_8G
    #        AFS_16G
    def __set_accel_fsr(self, scale):
        self.__write_data(IMU_6886_ACCEL_CONFIG, [scale << 3])
        sleep(.010)
        self.__acscale = scale
        self.__update_ares()

    #--------------------------------------------------------------------------#

    # Get accel adc from register
    def get_accel_adc(self):
        adc = self.__read_data(IMU_6886_ACCEL_XOUT_H, 6)
        # Big endian and signed
        ax = int.from_bytes([adc[0], adc[1]], byteorder = 'big', signed = True)
        ay = int.from_bytes([adc[2], adc[3]], byteorder = 'big', signed = True)
        az = int.from_bytes([adc[4], adc[5]], byteorder = 'big', signed = True)

        if ax == 0 and ay == 0 and az == 0:
            self.__start()
        return ax, ay, az

    # Get gyro adc from register
    def get_gyro_adc(self):
        adc = self.__read_data(IMU_6886_GYRO_XOUT_H, 6)
        # Big endian and unsigned
        gx = int.from_bytes([adc[0], adc[1]], byteorder = 'big', signed = True)
        gy = int.from_bytes([adc[2], adc[3]], byteorder = 'big', signed = True)
        gz = int.from_bytes([adc[4], adc[5]], byteorder = 'big', signed = True)

        if gx == 0 and gy == 0 and gz == 0:
            self.__start()
        return gx, gy, gz

    # Get temperature adc from register
    def get_temperature_adc(self):
        adc = self.__read_data(IMU_6886_TEMP_OUT_H, 2)
        temp = int.from_bytes([adc[0], adc[1]], byteorder = 'big', signed = False)

        return temp

    #--------------------------------------------------------------------------#

    # Get device id
    # Default 0x19
    def get_device_id(self):
        return self.__read_data(IMU_6886_WHOAMI, 1)[0]

    # Get accel values (x, y, z)
    def get_accel(self):
        x, y, z = self.get_accel_adc()
        ax = x * self.__ares
        ay = y * self.__ares
        az = z * self.__ares

        return ax, ay, az
    
    # Get gyro values (x, y, z)
    def get_gyro(self):
        x, y, z = self.get_gyro_adc()
        gx = x * self.__gres
        gy = y * self.__gres
        gz = z * self.__gres

        return gx, gy, gz

    # Get temperature
    def get_temperature(self):
        temp = self.get_temperature_adc()
        temp = (temp / 326.8) + 25

        return temp

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
mpu6886 = MPU6886(i2c)
dev_id = mpu6886.get_device_id()
if dev_id != 0x19:
    print("Cannot detect MPU6886")

while True:
    sleep(0.5)
    ax, ay, az = mpu6886.get_accel()
    print(str(ax) + ", " +  str(ay) + ", " +str(az))
    gx, gy, gz = mpu6886.get_gyro()
    print(str(gx) + ", " +  str(gy) + ", " +str(gz))
    temp = mpu6886.get_temperature()
    print(temp)
    print(mpu6886.is_vibration())
    print(mpu6886.get_direction())
"""