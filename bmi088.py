#!/usr/bin/python3
# Author: LocHV

from time import sleep
from i2c.i2c import I2C

BMI088_ACC_ADDRESS    =      0x19

BMI088_ACC_CHIP_ID   =       0x00 # Default value 0x1E
BMI088_ACC_ERR_REG   =       0x02
BMI088_ACC_STATUS    =       0x03

BMI088_ACC_X_LSB     =      0x12
BMI088_ACC_X_MSB     =      0x13
BMI088_ACC_Y_LSB     =      0x14
BMI088_ACC_Y_MSB     =      0x15
BMI088_ACC_Z_LSB     =       0x16
BMI088_ACC_Z_MSB     =       0x17

BMI088_ACC_SENSOR_TIME_0 =   0x18
BMI088_ACC_SENSOR_TIME_1 =   0x19
BMI088_ACC_SENSOR_TIME_2 =   0x1A

BMI088_ACC_INT_STAT_1   =    0x1D

BMI088_ACC_TEMP_MSB     =    0x22
BMI088_ACC_TEMP_LSB     =     0x23

BMI088_ACC_CONF        =     0x40
BMI088_ACC_RANGE       =     0x41

BMI088_ACC_INT1_IO_CTRL  =   0x53
BMI088_ACC_INT2_IO_CTRL  =   0x54
BMI088_ACC_INT_MAP_DATA  =   0x58

BMI088_ACC_SELF_TEST     =   0x6D

BMI088_ACC_PWR_CONF     =    0x7C
BMI088_ACC_PWR_CTRl     =    0x7D

BMI088_ACC_SOFT_RESET   =    0x7E

BMI088_GYRO_ADDRESS     =        0x69

BMI088_GYRO_CHIP_ID     =        0x00 # Default value 0x0F

BMI088_GYRO_RATE_X_LSB     =     0x02
BMI088_GYRO_RATE_X_MSB     =     0x03
BMI088_GYRO_RATE_Y_LSB     =     0x04
BMI088_GYRO_RATE_Y_MSB     =     0x05
BMI088_GYRO_RATE_Z_LSB     =     0x06
BMI088_GYRO_RATE_Z_MSB     =     0x07

BMI088_GYRO_INT_STAT_1     =     0x0A

BMI088_GYRO_RANGE          =     0x0F
BMI088_GYRO_BAND_WIDTH     =     0x10

BMI088_GYRO_LPM_1          =     0x11

BMI088_GYRO_SOFT_RESET     =     0x14

BMI088_GYRO_INT_CTRL       =     0x15
BMI088_GYRO_INT3_INT4_IO_CONF =  0x16
BMI088_GYRO_INT3_INT4_IO_MAP  =  0x18

BMI088_GYRO_SELF_TEST      =     0x3C
#Sensor type
ACC = 0x00
GYRO = 0x01 
# measurement rage AccScale
RANGE_3G = 0x00
RANGE_6G = 0x01
RANGE_12G = 0x02
RANGE_24G = 0x03


#Acc Ord
ODR_12 = 0x05
ODR_25 = 0x06
ODR_50 = 0x07
ODR_100 = 0x08
ODR_200 = 0x09
ODR_400 = 0x0A
ODR_800 = 0x0B
ODR_1600 = 0x0C


#Acc Power
ACC_ACTIVE = 0x00
ACC_SUSPEND = 0x03

#measurement rage GyroScale

RANGE_2000 = 0x00
RANGE_1000 = 0x01
RANGE_500 = 0x02
RANGE_250 = 0x03
RANGE_125 = 0x04

#output data rate GyroOdr
ODR_2000_BW_532 = 0x0
ODR_2000_BW_230 = 0x01
ODR_1000_BW_116 = 0x02
ODR_400_BW_47 = 0x03
ODR_200_BW_23 = 0x04
ODR_100_BW_12 = 0x05
ODR_200_BW_64 = 0x06
ODR_100_BW_32 = 0x07

#Gyro Power
GYRO_NORMAL = 0x00
GYRO_SUSPEND = 0x80
GYRO_DEEP_SUSPEND = 0x20




class BMI088(object):
    def __init__(self, i2c, accRange = RANGE_6G,accDataRate = ODR_100, gyroRange = RANGE_2000, gyroDataRate = ODR_2000_BW_532): 
        self.i2c = i2c
        self.devAddrAcc = BMI088_ACC_ADDRESS
        self.devAddrGyro = BMI088_GYRO_ADDRESS
        self.accRange = 0
        self.gyroRange = 0

        self.setAccScaleRange(RANGE_6G)
        self.setAccOutputDataRate(ODR_100)
        self.setAccPoweMode(ACC_ACTIVE)

        self.setGyroScaleRange(RANGE_2000)
        self.setGyroOutputDataRate(ODR_2000_BW_532)
        self.setGyroPoweMode(GYRO_NORMAL)

        sleep(0.2)


    def isConnection(self):
        return ((self.getAccID() == 0x1E) and (self.getGyroID() == 0x0F))


    def resetAcc(self):
        self.write8(ACC, BMI088_ACC_SOFT_RESET, 0xB6)


    def resetGyro(self):
        self.write8(GYRO, BMI088_GYRO_SOFT_RESET, 0xB6)


    def getAccID(self):
        return self.read8(ACC, BMI088_GYRO_CHIP_ID)


    def getGyroID(self):
        return self.read8(GYRO, BMI088_GYRO_CHIP_ID)


    def setAccPoweMode(self,mode):
        if (mode == ACC_ACTIVE):
            self.write8(ACC, BMI088_ACC_PWR_CTRl, 0x04)
            self.write8(ACC, BMI088_ACC_PWR_CONF, 0x00)
        if (mode == ACC_SUSPEND):
            self.write8(ACC, BMI088_ACC_PWR_CONF, 0x03)
            self.write8(ACC, BMI088_ACC_PWR_CTRl, 0x00)
    


    def setGyroPoweMode(self, mode):
        if (mode == GYRO_NORMAL):
            self.write8(GYRO, BMI088_GYRO_LPM_1, GYRO_NORMAL & 0xFF) 
        if (mode == GYRO_SUSPEND) :
            self.write8(GYRO, BMI088_GYRO_LPM_1, GYRO_SUSPEND & 0xFF) 
        if (mode == GYRO_DEEP_SUSPEND):
            self.write8(GYRO, BMI088_GYRO_LPM_1, GYRO_DEEP_SUSPEND & 0xFF)
    


    def setAccScaleRange(self, range):
        if (range == RANGE_3G):
            self.accRange = 3
        if (range == RANGE_6G):
            self.accRange = 6
        if (range == RANGE_12G):
            self.accRange = 12
        if (range == RANGE_24G):
            self.accRange = 24
    
        self.write8(ACC, BMI088_ACC_RANGE, range & 0xFF)


    def setAccOutputDataRate(self, odr) :
        data = 0
        data = self.read8(ACC, BMI088_ACC_CONF)
        data = data & 0xF0
        data = data | (odr & 0xFF)

        self.write8(ACC, BMI088_ACC_CONF, data)


    def setGyroScaleRange(self, range) :
        if (range == RANGE_2000):
            self.gyroRange = 2000
        if (range == RANGE_1000):
            self.gyroRange = 1000
        if (range == RANGE_500):
            self.gyroRange = 500
        if (range == RANGE_250):
            self.gyroRange = 250
        if (range == RANGE_125):
            self.gyroRange = 125
    

        self.write8(GYRO, BMI088_GYRO_RANGE, range & 0xFF)


    def setGyroOutputDataRate(self, odr) :
        self.write8(GYRO, BMI088_GYRO_BAND_WIDTH, odr & 0xFF)


    def getAcceleration(self) :
        buf = self.read(ACC, BMI088_ACC_X_LSB, 6)

        ax = int.from_bytes([buf[0], buf[1]], byteorder = 'little', signed = True)
        ay = int.from_bytes([buf[2], buf[3]], byteorder = 'little', signed = True)
        az = int.from_bytes([buf[4], buf[5]], byteorder = 'little', signed = True)
        
        x = self.accRange * ax / 32768
        y = self.accRange * ay / 32768
        z = self.accRange * az / 32768

        return x,y,z

    def getAccelerationX(self):
        ax = self.read16(ACC, BMI088_ACC_X_LSB)

        value = self.accRange * ax / 32768

        return value


    def getAccelerationY(self):
        ay = self.read16(ACC, BMI088_ACC_Y_LSB)

        value = self.accRange * ay / 32768

        return value


    def getAccelerationZ(self):
        az = self.read16(ACC, BMI088_ACC_Z_LSB)

        value = self.accRange * az / 32768

        return value


    def getGyroscope(self) :
        buf = self.read(GYRO, BMI088_GYRO_RATE_X_LSB, 6)

        gx = int.from_bytes(buf[0:2], byteorder = 'little', signed = True)
        gy = int.from_bytes(buf[2:4], byteorder = 'little', signed = True)
        gz = int.from_bytes(buf[4:6], byteorder = 'little', signed = True)


        x = self.gyroRange * gx / 32768
        y = self.gyroRange * gy / 32768
        z = self.gyroRange * gz / 32768

        return x,y,z

    def getGyroscopeX(self):
        gx = self.read16(GYRO, BMI088_GYRO_RATE_X_LSB)

        value = self.gyroRange * gx / 32768

        return value


    def getGyroscopeY(self):
        gy = self.read16(GYRO, BMI088_GYRO_RATE_Y_LSB)

        value = self.gyroRange * gy / 32768

        return value


    def getGyroscopeZ(self):
        gz = self.read16(GYRO, BMI088_GYRO_RATE_Z_LSB)

        value = self.gyroRange * gz / 32768

        return value


    def getTemperature(self):
        data = self.read16Be(ACC, BMI088_ACC_TEMP_MSB)

        data = data >> 5

        if (data > 1023):
            data = data - 2048
        
        return (data / 8 + 23) 


    def write8(self, dev, reg, val) :
        if (dev):
            addr = self.devAddrGyro
        else:
            addr = self.devAddrAcc

        self.i2c.i2c_write_block_data(addr,reg,[val])

    def read8(self, dev, reg) :
        if (dev):
            addr = self.devAddrGyro
        else:
            addr = self.devAddrAcc

        return self.i2c.i2c_read_block_data(addr,reg,1)[0]


    def read16(self, dev, reg):
        if (dev):
            addr = self.devAddrGyro
        else:
            addr = self.devAddrAcc
        
        data = self.i2c.i2c_read_block_data(addr,reg,2)

        return int.from_bytes(data[0:2], byteorder = 'little', signed = True)


    def read16Be(self, dev, reg):
        addr = 0

        if (dev):
            addr = self.devAddrGyro
        else:
            addr = self.devAddrAcc
        
        data = self.i2c.i2c_read_block_data(addr,reg,2)
        return int.from_bytes(data[0:2], byteorder = 'big', signed = True)


    def read(self, dev, reg, len):
        addr = 0
        if (dev):
            addr = self.devAddrGyro
        else:
            addr = self.devAddrAcc
        
        buf = self.i2c.i2c_read_block_data(addr,reg,len)
        return buf

    # Get direction
    # Return up (z max), down (z min), right (x max), left (x min), front (y max), back (y min)
    def get_direction(self):
        x, y, z = self.getAcceleration()
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
        values1 = list(self.getAcceleration())
        sleep(0.1)  # wait new sample
        values2 = list(self.getAcceleration())
        sleep(0.1)  # wait new sample
        values3 = list(self.getAcceleration())

        delta = 0
        for i in range(3):
            delta += abs(values2[i] - values1[i]) + abs(values3[i] - values2[i])

        return delta > 0.5

"""
i2c = I2C()
s = BMI088(i2c)

while True:
    print(s.getAcceleration())
    print(s.getGyroscope())
    print(s.getTemperature())
    print(s.is_vibration())
    print(s.get_direction())
    sleep(0.1)
"""
