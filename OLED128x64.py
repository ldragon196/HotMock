#!/usr/bin/python3
#
# OLED128x64.py
#
# Created on: April 23, 2021
# Author: LongHD
#
# Reference https://github.com/Seeed-Studio/OLED_Display_128X64
# https://wiki.seeedstudio.com/Grove-OLED_Display_0.96inch/
# NOTE: run $pip3 install Pillow
#

#------------------------------------------------------------------------------------------------------#

import time
from i2c.i2c import I2C
from PIL import Image, ImageDraw, ImageOps

#------------------------------------------------------------------------------------------------------#

OLED_I2C_ADDRESS                       = 0x3C # The device i2c address in default

OLED_COMMAND_MODE                      = 0x80
OLED_DATA_MODE                         = 0x40
OLED_DISPLAY_OFF                       = 0xAE
OLED_DISPLAY_ON                        = 0xAF
OLED_NORMAL_DISPLAY                    = 0xA6
OLED_INVERSE_DISPLAY                   = 0xA7
OLED_ENABLE_SCROLL                     = 0x2F
OLED_DISABLE_SCROLL                    = 0x2E
OLED_SET_BRIGHTNESS                    = 0x81

# Scroll type
OLED_SCROLL_LEFT                       = 0x00
OLED_SCROLL_RIGHT                      = 0x01

# Scroll speed
OLED_SCROLL_2_FRAMES                   = 0x7
OLED_SCROLL_3_FRAMES                   = 0x4
OLED_SCROLL_4_FRAMES                   = 0x5
OLED_SCROLL_5_FRAMES                   = 0x0
OLED_SCROLL_25_FRAMES                  = 0x6
OLED_SCROLL_64_FRAMES                  = 0x1
OLED_SCROLL_128_FRAMES                 = 0x2
OLED_SCROLL_256_FRAMES                 = 0x3

BASIC_FONT =    [[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x00, 0x5F, 0x00, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x00, 0x07, 0x00, 0x07, 0x00, 0x00, 0x00],
                [0x00, 0x14, 0x7F, 0x14, 0x7F, 0x14, 0x00, 0x00],
                [0x00, 0x24, 0x2A, 0x7F, 0x2A, 0x12, 0x00, 0x00],
                [0x00, 0x23, 0x13, 0x08, 0x64, 0x62, 0x00, 0x00],
                [0x00, 0x36, 0x49, 0x55, 0x22, 0x50, 0x00, 0x00],
                [0x00, 0x00, 0x05, 0x03, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x1C, 0x22, 0x41, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x41, 0x22, 0x1C, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x08, 0x2A, 0x1C, 0x2A, 0x08, 0x00, 0x00],
                [0x00, 0x08, 0x08, 0x3E, 0x08, 0x08, 0x00, 0x00],
                [0x00, 0xA0, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x00],
                [0x00, 0x60, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x20, 0x10, 0x08, 0x04, 0x02, 0x00, 0x00],
                [0x00, 0x3E, 0x51, 0x49, 0x45, 0x3E, 0x00, 0x00],
                [0x00, 0x00, 0x42, 0x7F, 0x40, 0x00, 0x00, 0x00],
                [0x00, 0x62, 0x51, 0x49, 0x49, 0x46, 0x00, 0x00],
                [0x00, 0x22, 0x41, 0x49, 0x49, 0x36, 0x00, 0x00],
                [0x00, 0x18, 0x14, 0x12, 0x7F, 0x10, 0x00, 0x00],
                [0x00, 0x27, 0x45, 0x45, 0x45, 0x39, 0x00, 0x00],
                [0x00, 0x3C, 0x4A, 0x49, 0x49, 0x30, 0x00, 0x00],
                [0x00, 0x01, 0x71, 0x09, 0x05, 0x03, 0x00, 0x00],
                [0x00, 0x36, 0x49, 0x49, 0x49, 0x36, 0x00, 0x00],
                [0x00, 0x06, 0x49, 0x49, 0x29, 0x1E, 0x00, 0x00],
                [0x00, 0x00, 0x36, 0x36, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x00, 0xAC, 0x6C, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x08, 0x14, 0x22, 0x41, 0x00, 0x00, 0x00],
                [0x00, 0x14, 0x14, 0x14, 0x14, 0x14, 0x00, 0x00],
                [0x00, 0x41, 0x22, 0x14, 0x08, 0x00, 0x00, 0x00],
                [0x00, 0x02, 0x01, 0x51, 0x09, 0x06, 0x00, 0x00],
                [0x00, 0x32, 0x49, 0x79, 0x41, 0x3E, 0x00, 0x00],
                [0x00, 0x7E, 0x09, 0x09, 0x09, 0x7E, 0x00, 0x00],
                [0x00, 0x7F, 0x49, 0x49, 0x49, 0x36, 0x00, 0x00],
                [0x00, 0x3E, 0x41, 0x41, 0x41, 0x22, 0x00, 0x00],
                [0x00, 0x7F, 0x41, 0x41, 0x22, 0x1C, 0x00, 0x00],
                [0x00, 0x7F, 0x49, 0x49, 0x49, 0x41, 0x00, 0x00],
                [0x00, 0x7F, 0x09, 0x09, 0x09, 0x01, 0x00, 0x00],
                [0x00, 0x3E, 0x41, 0x41, 0x51, 0x72, 0x00, 0x00],
                [0x00, 0x7F, 0x08, 0x08, 0x08, 0x7F, 0x00, 0x00],
                [0x00, 0x41, 0x7F, 0x41, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x20, 0x40, 0x41, 0x3F, 0x01, 0x00, 0x00],
                [0x00, 0x7F, 0x08, 0x14, 0x22, 0x41, 0x00, 0x00],
                [0x00, 0x7F, 0x40, 0x40, 0x40, 0x40, 0x00, 0x00],
                [0x00, 0x7F, 0x02, 0x0C, 0x02, 0x7F, 0x00, 0x00],
                [0x00, 0x7F, 0x04, 0x08, 0x10, 0x7F, 0x00, 0x00],
                [0x00, 0x3E, 0x41, 0x41, 0x41, 0x3E, 0x00, 0x00],
                [0x00, 0x7F, 0x09, 0x09, 0x09, 0x06, 0x00, 0x00],
                [0x00, 0x3E, 0x41, 0x51, 0x21, 0x5E, 0x00, 0x00],
                [0x00, 0x7F, 0x09, 0x19, 0x29, 0x46, 0x00, 0x00],
                [0x00, 0x26, 0x49, 0x49, 0x49, 0x32, 0x00, 0x00],
                [0x00, 0x01, 0x01, 0x7F, 0x01, 0x01, 0x00, 0x00],
                [0x00, 0x3F, 0x40, 0x40, 0x40, 0x3F, 0x00, 0x00],
                [0x00, 0x1F, 0x20, 0x40, 0x20, 0x1F, 0x00, 0x00],
                [0x00, 0x3F, 0x40, 0x38, 0x40, 0x3F, 0x00, 0x00],
                [0x00, 0x63, 0x14, 0x08, 0x14, 0x63, 0x00, 0x00],
                [0x00, 0x03, 0x04, 0x78, 0x04, 0x03, 0x00, 0x00],
                [0x00, 0x61, 0x51, 0x49, 0x45, 0x43, 0x00, 0x00],
                [0x00, 0x7F, 0x41, 0x41, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x02, 0x04, 0x08, 0x10, 0x20, 0x00, 0x00],
                [0x00, 0x41, 0x41, 0x7F, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x04, 0x02, 0x01, 0x02, 0x04, 0x00, 0x00],
                [0x00, 0x80, 0x80, 0x80, 0x80, 0x80, 0x00, 0x00],
                [0x00, 0x01, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x20, 0x54, 0x54, 0x54, 0x78, 0x00, 0x00],
                [0x00, 0x7F, 0x48, 0x44, 0x44, 0x38, 0x00, 0x00],
                [0x00, 0x38, 0x44, 0x44, 0x28, 0x00, 0x00, 0x00],
                [0x00, 0x38, 0x44, 0x44, 0x48, 0x7F, 0x00, 0x00],
                [0x00, 0x38, 0x54, 0x54, 0x54, 0x18, 0x00, 0x00],
                [0x00, 0x08, 0x7E, 0x09, 0x02, 0x00, 0x00, 0x00],
                [0x00, 0x18, 0xA4, 0xA4, 0xA4, 0x7C, 0x00, 0x00],
                [0x00, 0x7F, 0x08, 0x04, 0x04, 0x78, 0x00, 0x00],
                [0x00, 0x00, 0x7D, 0x00, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x80, 0x84, 0x7D, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x7F, 0x10, 0x28, 0x44, 0x00, 0x00, 0x00],
                [0x00, 0x41, 0x7F, 0x40, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x7C, 0x04, 0x18, 0x04, 0x78, 0x00, 0x00],
                [0x00, 0x7C, 0x08, 0x04, 0x7C, 0x00, 0x00, 0x00],
                [0x00, 0x38, 0x44, 0x44, 0x38, 0x00, 0x00, 0x00],
                [0x00, 0xFC, 0x24, 0x24, 0x18, 0x00, 0x00, 0x00],
                [0x00, 0x18, 0x24, 0x24, 0xFC, 0x00, 0x00, 0x00],
                [0x00, 0x00, 0x7C, 0x08, 0x04, 0x00, 0x00, 0x00],
                [0x00, 0x48, 0x54, 0x54, 0x24, 0x00, 0x00, 0x00],
                [0x00, 0x04, 0x7F, 0x44, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x3C, 0x40, 0x40, 0x7C, 0x00, 0x00, 0x00],
                [0x00, 0x1C, 0x20, 0x40, 0x20, 0x1C, 0x00, 0x00],
                [0x00, 0x3C, 0x40, 0x30, 0x40, 0x3C, 0x00, 0x00],
                [0x00, 0x44, 0x28, 0x10, 0x28, 0x44, 0x00, 0x00],
                [0x00, 0x1C, 0xA0, 0xA0, 0x7C, 0x00, 0x00, 0x00],
                [0x00, 0x44, 0x64, 0x54, 0x4C, 0x44, 0x00, 0x00],
                [0x00, 0x08, 0x36, 0x41, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x00, 0x7F, 0x00, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x41, 0x36, 0x08, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x02, 0x01, 0x01, 0x02, 0x01, 0x00, 0x00],
                [0x00, 0x02, 0x05, 0x05, 0x02, 0x00, 0x00, 0x00]]


#------------------------------------------------------------------------------------------------------#

class OLED128x64:
    # Config default in horizontal mode and normal display
    def __init__(self, i2c, address = OLED_I2C_ADDRESS):
        self.__i2c = i2c
        self.__address = address
        
        self.width = 128
        self.height = 64
        self.pages = int(self.height / 8)
        self.image = Image.new('1', (self.width, self.height))
        self.canvas = ImageDraw.Draw(self.image) # this is a "draw" object for preparing display contents

        self.off()
        time.sleep(.005)
        self.clear()
        self.horizontal_mode()
        self.inverse(False)
        time.sleep(.005)
        self.on()

    # Send data to display
    def __send_data(self, datas):
        data = [OLED_DATA_MODE, datas]
        self.__i2c.i2c_write_data(self.__address, data)
    
    # Send command to config
    def __command(self, command):
        data = [OLED_COMMAND_MODE, command]
        self.__i2c.i2c_write_data(self.__address, data)

    def __send_frame(self, frame):
        for i in range(0, len(frame), 31):
            self.__i2c.i2c_write_block_data(self.__address, OLED_DATA_MODE, list(frame[i:i+31]))

    #--------------------------------------------------------------------------------------------------#

    # Display on
    def on(self):
        self.__command(OLED_DISPLAY_ON)

    # Display off
    def off(self):
        self.__command(OLED_DISPLAY_OFF)

    # Clear screen
    def clear(self):
        self.off()
        for i in range(8):
            self.set_cursor(0, i)
            self.print(' ' * 16)
        self.on()
        self.set_cursor(0, 0)

    # Enable/ Disable scroll
    def enable_scroll(self):
        self.__command(OLED_ENABLE_SCROLL)

    def disable_scroll(self):
        self.__command(OLED_DISABLE_SCROLL)

    # Config horizontal scroll
    # direction: left or right (See "Scroll type" constant)
    # start_row, end_row: row enable scroll
    #                     range 0 - 7
    # speed: scroll speed (See "Scroll speed" constant)
    def config_scroll(self, direction, start_row, end_row, speed):
        if direction == OLED_SCROLL_LEFT:
            self.__command(0x26)          # Scroll Right
        else:
            self.__command(0x27)          # Scroll Left

        self.__command(0x00)
        self.__command(start_row)
        self.__command(speed)
        self.__command(end_row)
        self.__command(0x00)
        self.__command(0xFF)

    # Display normal or inverse
    def inverse(self, enable):
       self.__command(OLED_INVERSE_DISPLAY if enable else OLED_NORMAL_DISPLAY) 

    # Set horizontal mode
    def horizontal_mode(self):
        self.__command(0x20)              # set addressing mode
        self.__command(0x00)              # set horizontal addressing mode

    # Set page mode
    def page_mode(self):
        self.__command(0x20)              # set addressing mode
        self.__command(0x02)              # set page addressing mode

    # Set display brightness
    # brightness range 0 - 255
    def set_brightness(self, brightness):
        self.__command(OLED_SET_BRIGHTNESS)
        self.__command(brightness & 0xFF)

    #--------------------------------------------------------------------------------------------------#

    # Set cursor location
    # column range: 0 - 15
    # row: range 0 - 7
    def set_cursor(self, col, row):
        self.__command(0xB0 + row)                    # set page address
        self.__command(0x00 + ((col << 3) & 0x0F))    # set column lower address
        self.__command(0x10 + ((col >> 1) & 0x0F))    # set column higher address

    # Display char at cursor location
    def putc(self, c):
        C_add = ord(c)
        if C_add < 32 or C_add > 127:     # Ignore non-printable ASCII characters
            c = ' '
            C_add = ord(c)
        
        for i in range(0, 8):
            self.__send_data(BASIC_FONT[C_add-32][i])

    # Display string
    def print(self, text):
        for c in text:
            self.putc(c)

    # Display image at location
    # path: Image path
    # x, y: location
    def display_image(self, path, x, y):
        # self.clear()      # Clear display

        # Open image
        logo = Image.open(path).convert('1')    # Convert to mode '1'
        logo = ImageOps.mirror(logo)            # Flip image because when display, image is flipped

        # Clear old data and draw new image
        self.canvas.rectangle((0, 0, self.width - 1, self.height - 1), outline = 0, fill = 0)
        self.canvas.bitmap((self.width - logo.width - x, y), logo, fill = 1)

        # Send image frame to oled
        pix = list(self.image.getdata())
        step = self.width * 8
        buf = []
        for y in range(0, self.pages * step, step):
            i = y + self.width - 1
            while i >= y:
                byte = 0
                for n in range(0, step, self.width):
                    byte |= (pix[i + n] & 0x01) << 8
                    byte >>= 1

                buf.append(byte)
                i -= 1

        self.__send_frame(buf) # push out the whole lot

#-------------------------- Example --------------------------

i2c = I2C()
oled = OLED128x64(i2c)
# oled.disable_scroll()
# oled.config_scroll(OLED_SCROLL_RIGHT, 0, 7, OLED_SCROLL_4_FRAMES)
# oled.page_mode()
# oled.horizontal_mode()
# oled.set_brightness(255)
# oled.set_cursor(0, 0)
# oled.print("Hello")
# oled.set_cursor(0, 5)
# oled.print("Hoang Duc Long")
# time.sleep(1)
oled.display_image('image/kaito_kid.png', 0, 0)
time.sleep(3)
oled.display_image('image/earth.png', 32, 0)
time.sleep(3)
oled.display_image('image/pi_logo.png', 32, 0)