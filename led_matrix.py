#!/usr/bin/python3
#
# led_matrix.py
#
# Created on: April 20, 2021
# Author: LongHD
#
# Reference https:github.com/Seeed-Studio/Seeed_RGB_LED_Matrix
#

#------------------------------------------------------------------------------------------------------#

from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

RGB_LED_MATRIX_DEF_I2C_ADDR          	= 0x65 # The device i2c address in default

GROVE_TWO_RGB_LED_MATRIX_VID 			= 0x2886 # Vender ID of the device
GROVE_TWO_RGB_LED_MATRIX_PID 			= 0x8005 # Product ID of the device
I2C_CMD_GET_DEV_ID		    			= 0x00 # This command gets device ID information
I2C_CMD_DISP_BAR		    			= 0x01 # This command displays LED bar
I2C_CMD_DISP_EMOJI		    			= 0x02 # This command displays emoji
I2C_CMD_DISP_NUM          				= 0x03 # This command displays number
I2C_CMD_DISP_STR		    			= 0x04 # This command displays string
I2C_CMD_DISP_CUSTOM		    			= 0x05 # This command displays user-defined pictures
I2C_CMD_DISP_OFF		    			= 0x06 # This command cleans the display
I2C_CMD_DISP_ASCII		    			= 0x07 # not use
I2C_CMD_DISP_FLASH						= 0x08 # This command displays pictures which are stored in flash
I2C_CMD_DISP_COLOR_BAR          		= 0x09 # This command displays colorful led bar
I2C_CMD_DISP_COLOR_WAVE         		= 0x0A # This command displays built-in wave animation
I2C_CMD_DISP_COLOR_CLOCKWISE    		= 0x0B # This command displays built-in clockwise animation
I2C_CMD_DISP_COLOR_ANIMATION       		= 0x0C # This command displays other built-in animation
I2C_CMD_DISP_COLOR_BLOCK                = 0x0D # This command displays an user-defined color
I2C_CMD_STORE_FLASH						= 0xA0 # This command stores frames in flash
I2C_CMD_DELETE_FLASH        			= 0xA1 # This command deletes all the frames in flash

I2C_CMD_LED_ON			    			= 0xB0 # This command turns on the indicator LED flash mode
I2C_CMD_LED_OFF			    			= 0xB1 # This command turns off the indicator LED flash mode
I2C_CMD_AUTO_SLEEP_ON	    			= 0xB2 # This command enable device auto sleep mode
I2C_CMD_AUTO_SLEEP_OFF	    			= 0xB3 # This command disable device auto sleep mode (default mode)

I2C_CMD_DISP_ROTATE         			= 0xB4 # This command setting the display orientation
I2C_CMD_DISP_OFFSET         			= 0xB5 # This command setting the display offset

I2C_CMD_SET_ADDR		    			= 0xC0 # This command sets device i2c address
I2C_CMD_RST_ADDR		    			= 0xC1 # This command resets device i2c address
I2C_CMD_TEST_TX_RX_ON       			= 0xE0 # This command enable TX RX pin test mode
I2C_CMD_TEST_TX_RX_OFF      			= 0xE1 # This command disable TX RX pin test mode
I2C_CMD_TEST_GET_VER        			= 0xE2 # This command use to get software version
I2C_CMD_GET_DEVICE_UID      			= 0xF1 # This command use to get chip id

# Orientation type
DISPLAY_ROTATE_0                        = 0
DISPLAY_ROTATE_90                       = 1
DISPLAY_ROTATE_180                      = 2
DISPLAY_ROTATE_270                      = 3

# Color
RED                                     = 0x00
ORANGE                                  = 0x12
YELLOW                                  = 0x18
GREEN                                   = 0x52
CYAN                                    = 0x7F
BLUE                                    = 0xAA
PURPLE                                  = 0xC3
PINK                                    = 0xDC
WHITE                                   = 0xFE
BLACK                                   = 0xFF

#------------------------------------------------------------------------------------------------------#

class LedMatrix:
    def __init__(self, i2c, address = RGB_LED_MATRIX_DEF_I2C_ADDR):
        self.__address = address
        self.__i2c = i2c
    
    # I2C communication
    def __send_byte(self, byte):
        self.__i2c.i2c_write_byte(self.__address, byte)

    def __send_data(self, cmd, data):
        self.__i2c.i2c_write_block_data(self.__address, cmd, data)
    
    def __receive_data(self, cmd, size):
        return self.__i2c.i2c_read_block_data(self.__address, cmd, size)

#------------------------------------------------------------------------------------------------------#

    # Get product ID and vendor ID of device
    def get_device_id(self):
        self.__send_byte(I2C_CMD_GET_DEV_ID)
        data = self.__receive_data(I2C_CMD_GET_DEV_ID, 4)
        
        pid = data[0] + (data[1] * 256)
        vid = data[2] + (data[3] * 256)
        return pid, vid

    # Get device id
    def get_device_uid(self):
        self.__send_byte(I2C_CMD_GET_DEVICE_UID)
        return self.__receive_data(I2C_CMD_GET_DEVICE_UID, 12)

    # Change i2c base address of device
    # new_address: The new i2c base address of device 0x10 - 0x70
    def change_bass_address(self, new_address):
        if new_address < 0x10 or new_address > 0x70:
            new_address = RGB_LED_MATRIX_DEF_I2C_ADDR

        data = [new_address]
        self.__address = new_address
        self.__send_data(I2C_CMD_SET_ADDR, data)

    # Reset slave address to default
    def default_address(self):
        self.__send_byte(I2C_CMD_RST_ADDR)
        self.__address = RGB_LED_MATRIX_DEF_I2C_ADDR

#------------------------------------------------------------------------------------------------------#

    # Display orientation, see orientation constant (DISPLAY_ROTATE_X) which means the display will rotate X
    # This function can be used before or after display
    # DO NOT WORK with display_color_wave(), display_clock_wise(), display_color_animation()
    def set_orientation(self, orientation):
        if orientation > DISPLAY_ROTATE_270:
            orientation = DISPLAY_ROTATE_0
        data = [orientation]
        self.__send_data(I2C_CMD_DISP_ROTATE, data)


    # Setting the display offset of x-axis and y-axis
    # This function can be used before or after display
    # DO NOT WORK with display_color_wave(), display_clock_wise(), display_color_animation()
    # display_number(when number < 0 or number >= 10), display_string (when more than one character)
    # offset_x: The display offset value of horizontal x-axis, range from -8 to 8
    # offset_y: The display offset value of horizontal y-axis, range from -8 to 8
    def set_display_offset(self, x, y):
        x += 8
        y += 8
        if x > 16:
            x = 16
        elif x < 0:
            x = 0

        if y > 16:
            y = 16
        elif y < 0:
            y = 0

        data = [x, y]
        self.__send_data(I2C_CMD_DISP_OFFSET, data)

    
    # Display a bar on RGB LED Matrix
    # bar: 0 - 32. 0 is blank and 32 is full
    # duration: Set the display time(ms) duration. Set it to 0 to not display. Range 0 -65535
    # forever: Set it to true to display forever, and the duration will not work. Or set it to false to display one time
    # color: Set the color of the display, range from 0 to 255. See COLORS constants for more details
    def display_bar(self, bar, duration, forever, color):
        if bar > 32:
            bar = 32
        
        data = [bar, duration & 0xFF, (duration >> 8) & 0xFF, int(forever == True), color]
        self.__send_data(I2C_CMD_DISP_BAR, data)


    # Display emoji on LED matrix
    # emoji: Set a number from 0 to 29 for different emoji
    #           0	smile	10	heart		    20	house
    #			1	laugh	11	small heart		21	tree
    #			2	sad	    12	broken heart	22	flower
    #			3	mad	    13	waterdrop		23	umbrella
    #			4	angry	14	flame		    24	rain
    #			5	cry	    15	creeper		    25	monster
    #			6	greedy	16	mad creeper		26	crab
    #			7	cool	17	sword		    27	duck
    #			8	shy	    18	wooden sword	28	rabbit
    #			9	awkward	19	crystal sword	29	cat
    #			30  up		31  down			32 left
    #			33  right	34  smile face 3
    # duration: Set the display time(ms) duration. Set it to 0 to not display
    # forever: Set it to true to display forever, and the duration_time will not work. Or set it to false to display one time
    def display_emoji(self, emoji, duration, forever):
        if emoji > 34:
            emoji = 34

        data = [emoji, duration & 0xFF, (duration >> 8) & 0xFF, int(forever == True)]
        self.__send_data(I2C_CMD_DISP_EMOJI, data)

    # Display a number(-32768 ~ 32767) on LED matrix
    # number: Set the number you want to display on LED matrix. Number(except 0-9)
    #         will scroll horizontally, the shorter you set the duration time,
    #         the faster it scrolls. The number range from -32768 to +32767, if
    #         you want to display larger number, please use displayString()
    # duration: Set the display time(ms) duration. Set it to 0 to not display
    # forever: Set it to true to display forever, or set it to false to display one time
    # color: Set the color of the display, range from 0 to 255. See COLORS constants for more details
    def display_number(self, number, duration, forever, color):
        data = [number & 0xFF, (number >> 8) & 0xFF, duration & 0xFF, (duration >> 8) & 0xFF, int(forever == True), color]
        self.__send_data(I2C_CMD_DISP_NUM, data)
    
    # Display a string on LED matrix
    # data_str: The string pointer, the maximum length is 28 bytes. String will scroll horizontally when its length is more than 1.
    #           The shorter you set the duration time, the faster it scrolls
    # duration: Set the display time(ms) duration. Set it to 0 to not display
    # forever: Set it to true to display forever, or set it to false to display one time
    # color: Set the color of the display, range from 0 to 255. See COLORS constants for more details
    def display_string(self, data_str, duration, forever, color):
        size = len(data_str)
        if size > 25:
            size = 25
        
        data = [int(forever == True), duration & 0xFF, (duration >> 8) & 0xFF, size, color]
        for byte in data_str:
            data.append(ord(byte))
        self.__send_data(I2C_CMD_DISP_STR, data)

    # Display color block on LED matrix with a given uint32_t rgb color
    # rgb: uint32_t rgb color, such as 0xff0000(red), 0x0000ff(blue)
    # duration: Set the display time(ms) duration. Set it to 0 to not display
    # forever: Set it to true to display forever, or set it to false to display one time
    def display_color_block(self, rgb, duration, forever):
        data = [(rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF, duration & 0xFF, (duration >> 8) & 0xFF, int(forever == True)]
        self.__send_data(I2C_CMD_DISP_COLOR_BLOCK, data)

    # Display a colorful bar on RGB LED Matrix
    # bar: 0 - 32. 0 is blank and 32 is full
    # duration: Set the display time(ms) duration. Set it to 0 to not display
    # forever: Set it to true to display forever, and the duration_time will not work. Or set it to false to display one time
    def display_color_bar(self, bar, duration, forever):
        if bar > 32:
            bar = 32
        data = [bar, duration & 0xFF, (duration >> 8) & 0xFF, int(forever == True)]
        self.__send_data(I2C_CMD_DISP_COLOR_BAR, data)

    # Display a wave on RGB LED Matrix
    # color: Set the color of the display, range from 0 to 255. See COLORS constants for more details
    # duration: Set the display time(ms) duration. Set it to 0 to not display
    # forever: Set it to true to display forever, and the duration_time will not work
    #          Or set it to false to display one time
    def display_color_wave(self, color, duration, forever):
        data = [color, duration & 0xFF, (duration >> 8) & 0xFF, int(forever == True)]
        self.__send_data(I2C_CMD_DISP_COLOR_WAVE, data)

    # Display a clockwise(or anti-clockwise) animation on RGB LED Matrix
    # cw: Set it true to display a clockwise animation, while set it false to display a anti-clockwise
    # is: Set it true to display a 8*8 animation, while set it false to display a 4*4 animation
    # duration: Set the display time(ms) duration. Set it to 0 to not display
    # forever: Set it to true to display forever, and the duration_time will not work
    #          Or set it to false to display one time
    def display_clock_wise(self, cw, big, duration, forever):
        data = [int(cw == True), int(big == True), duration & 0xFF, (duration >> 8) & 0xFF, int(forever == True)]
        self.__send_data(I2C_CMD_DISP_COLOR_CLOCKWISE, data)

    # Display other built-in animations on RGB LED Matrix
    # index: the index of animations
    #         0. big clockwise
    #         1. small clockwise
    #         2. rainbow cycle
    #         3. fire
    #         4. walking child
    #         5. broken heart
    # duration: Set the display time(ms) duration. Set it to 0 to not display
    #           Or set it to false to display one time
    def display_color_animation(self, index, duration, forever):
        data = []
        if index == 0:
            data.append(0)
            data.append(28)
        elif index == 1:
            data.append(29)
            data.append(41)
        elif index == 2:
            data.append(255)
            data.append(255)
        elif index == 3:
            data.append(254)
            data.append(254)
        elif index == 4:
            data.append(42)
            data.append(43)
        elif index == 5:
            data.append(44)
            data.append(52)
        else:
            return    

        data.append(duration & 0xFF)
        data.append((duration >> 8) & 0xFF)
        data.append(int(forever == True))

        self.__send_data(I2C_CMD_DISP_COLOR_ANIMATION, data)

#-------------------------- Example --------------------------

# i2c = I2C()
# ledMatrix = LedMatrix(i2c)
# pid, vid = ledMatrix.get_device_id()
# device_id = ledMatrix.get_device_uid()
# ledMatrix.set_orientation(DISPLAY_ROTATE_90)
# ledMatrix.set_display_offset(2, 5)
# ledMatrix.display_bar(12, 1000, False, GREEN)
# ledMatrix.display_emoji(0, 1000, True)
# ledMatrix.display_number(19, 1000, True, BLUE)
# ledMatrix.display_string("Long", 4000, False, GREEN)
# ledMatrix.display_color_block(0xFF00FF, 0, True)
# ledMatrix.display_color_bar(2, 3000, False)
# ledMatrix.display_color_wave(WHITE, 100, True)
# ledMatrix.display_clock_wise(False, True, 1000, False)
# ledMatrix.display_color_animation(1, 1000, False)