#!/usr/bin/python3
#
# motor_driver.py
#
# Created on: April 28, 2021
# Author: LongHD
#
# Motor driver
# Reference https://github.com/Seeed-Studio/Grove_I2C_Motor_Driver_v1_3
# https://www.st.com/resource/en/datasheet/l298.pdf
#

#------------------------------------------------------------------------------------------------------#

from time import sleep
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

MOTOR_DRIVER_I2C_ADDRESS                = 0x0F # The device i2c address in default

MOTOR_SPEED_SET                         = 0x82
PWM_FREQUENCE_SET                       = 0x84
DIRECTION_SET                           = 0xaa
MOTOR_A_SET                             = 0xa1
MOTOR_B_SET                             = 0xa5
NOTHING                                 = 0x01

# Motor ID
MOTOR1 			                        = 1
MOTOR2 			                        = 2

# Motor Direction
BOTH_CLOCK_WISE                         = 0x0a
BOTH_ANTI_CLOCK_WISE                    = 0x05
M1_CW_M2_ACW                            = 0x06
M1_ACW_M2_CW                            = 0x09

# Motor Direction
CLOCK_WISE                              = 1
ANTI_CLOCK_WISE                         = -1

# Prescaler Frequence
F_31372Hz                               = 0x01
F_3921Hz                                = 0x02
F_490Hz                                 = 0x03
F_122Hz                                 = 0x04
F_30Hz                                  = 0x05

# Delay wait setup
DELAY_MS                                = 0.005

#------------------------------------------------------------------------------------------------------#

class MotorDriver:
    def __init__(self, i2c, address = MOTOR_DRIVER_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address
        self.speed1 = 0
        self.speed2 = 0
        self.direction1 = CLOCK_WISE
        self.direction2 = CLOCK_WISE
        self.step = 0

        self.set_frequence(F_3921Hz)

    # Write command to motor
    # Cmd write
    # Data list of values
    def __command(self, cmd, data):
        self.__i2c.i2c_write_block_data(self.__address, cmd, data)

    #--------------------------------------------------------------------------------------------------#

    # Set the direction of 2 motors
    # direction: See "Motor Direction" constants
    def set_direction(self, direction):
        # Need to send this byte as the third byte(no meaning)
        data = [direction, NOTHING]

        self.__command(DIRECTION_SET, data)
        sleep(DELAY_MS)

    # Set the frequence of PWM(cycle length = 510, system clock = 16MHz)
    # frequence: See "Prescaler Frequence" constants
    def set_frequence(self, frequence):
        if frequence < F_31372Hz or frequence > F_30Hz:
            return
        
        # Need to send this byte as the third byte(no meaning)
        data = [frequence, NOTHING]
        self.__command(PWM_FREQUENCE_SET, data)
        sleep(DELAY_MS)

    # Set the speed of a motor, speed is equal to duty cycle here
    # motor id: MOTOR1, MOTOR2
    # speed: -100 ~ 100%, when speed > 0, dc motor runs clockwise and when speed < 0
    #        dc motor runs anticlockwise
    def set_speed(self, motor, speed):
        direction = CLOCK_WISE if speed >= 0 else ANTI_CLOCK_WISE

        # Convert percentage value to 0 - 255
        speed = abs(speed)
        if speed > 100:
            speed = 100
        speed = int(speed * 255/ 100) & 0xFF

        if motor == MOTOR1:
            self.direction1 = direction
            self.speed1 = speed
        elif motor == MOTOR2:
            self.direction2 = direction
            self.speed2 = speed
        else:
            return

        if self.direction1 == CLOCK_WISE and  self.direction2 == CLOCK_WISE:
            self.set_direction(BOTH_CLOCK_WISE)
        elif self.direction1 == ANTI_CLOCK_WISE and  self.direction2 == ANTI_CLOCK_WISE:
            self.set_direction(BOTH_ANTI_CLOCK_WISE)
        elif self.direction1 == CLOCK_WISE and  self.direction2 == ANTI_CLOCK_WISE:
            self.set_direction(M1_CW_M2_ACW)
        elif self.direction1 == ANTI_CLOCK_WISE and  self.direction2 == CLOCK_WISE:
            self.set_direction(M1_ACW_M2_CW)
        else:
            return

        # Set speed
        data = [self.speed1, self.speed2]
        self.__command(MOTOR_SPEED_SET, data)
        sleep(DELAY_MS)

    # Drive a stepper motor
    # Step: -1024 ~ 1024, when step > 0, dc motor runs clockwise and when step < 0
    #       dc motor runs anticlockwise
    def stepper_run(self, step):
        direction = CLOCK_WISE if step >= 0 else ANTI_CLOCK_WISE
        self.step = step

        self.direction1
        # Range
        step = abs(step)
        if step > 1024:
            step = 1024

        # Run dc motor with max percentage
        self.speed1 = 255
        self.speed2 = 255
        data = [self.speed1, self.speed2]
        self.__command(MOTOR_SPEED_SET, data)
        sleep(DELAY_MS)

        if direction == CLOCK_WISE:
            for i in range(step):
                self.set_direction(0b0001)
                self.set_direction(0b0011)
                self.set_direction(0b0010)
                self.set_direction(0b0110)
                self.set_direction(0b0100)
                self.set_direction(0b1100)
                self.set_direction(0b1000)
                self.set_direction(0b1001)
        else:
            for i in range(step):
                self.set_direction(0b1000)
                self.set_direction(0b1100)
                self.set_direction(0b0100)
                self.set_direction(0b0110)
                self.set_direction(0b0010)
                self.set_direction(0b0011)
                self.set_direction(0b0001)
                self.set_direction(0b1001)

#-------------------------- Example --------------------------

"""
i2c = I2C()
motor = MotorDriver(i2c)

motor.set_speed(MOTOR1, 50)
motor.stepper_run(512)

print(motor.speed1)
print(motor.speed2)
print(motor.direction1)
print(motor.direction2)

print(motor.step)
"""