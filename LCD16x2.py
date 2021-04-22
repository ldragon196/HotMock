#!/usr/bin/python3
#
# LCD16x2.py
#
# Created on: April 22, 2021
# Author: LongHD
#
# Reference https://github.com/Seeed-Studio/Grove_LCD_RGB_Backlight
# https://wiki.seeedstudio.com/Grove-16x2_LCD_Series/
#

#------------------------------------------------------------------------------------------------------#

import time
from i2c.i2c import I2C

#------------------------------------------------------------------------------------------------------#

LCD16x2_I2C_ADDRESS                       = 0x3E # The device i2c address in default

LCD_TYPE_COMMAND                          = 0x80
LCD_TYPE_PRINT                            = 0x40

# Commands
LCD_CLEARDISPLAY                          = 0x01
LCD_RETURNHOME                            = 0x02
LCD_ENTRYMODESET                          = 0x04
LCD_DISPLAYCONTROL                        = 0x08
LCD_CURSORSHIFT                           = 0x10
LCD_FUNCTIONSET                           = 0x20
LCD_SETCGRAMADDR                          = 0x40
LCD_SETDDRAMADDR                          = 0x80

# Flags for display entry mode
LCD_ENTRYRIGHT                            = 0x00
LCD_ENTRYLEFT                             = 0x02
LCD_ENTRYSHIFTINCREMENT                   = 0x01
LCD_ENTRYSHIFTDECREMENT                   = 0x00

# Flags for display on/off control
LCD_DISPLAYON                             = 0x04
LCD_DISPLAYOFF                            = 0x00
LCD_CURSORON                              = 0x02
LCD_CURSOROFF                             = 0x00
LCD_BLINKON                               = 0x01
LCD_BLINKOFF                              = 0x00

# Flags for display/cursor shift
LCD_DISPLAYMOVE                           = 0x08
LCD_CURSORMOVE                            = 0x00
LCD_MOVERIGHT                             = 0x04
LCD_MOVELEFT                              = 0x00

# flags for function set
LCD_8BITMODE                              = 0x10
LCD_4BITMODE                              = 0x00
LCD_2LINE                                 = 0x08
LCD_1LINE                                 = 0x00
LCD_5x10DOTS                              = 0x04
LCD_5x8DOTS                               = 0x00

#------------------------------------------------------------------------------------------------------#

class LCD16x2:
    # LCD Initialization
    # Cols: Number of column
    # Lines: 1 or 2 lines
    # Big font only when lines = 1
    def __init__(self, i2c, cols = 16, lines = 2, big_font = False):
        self.__i2c = i2c
        self.__address = LCD16x2_I2C_ADDRESS

        self.__config = 0x00
        self.__control = 0x00
        self.__mode = 0x00
        self.config_lcd(cols, lines, big_font)


    # Write a byte
    def __send_byte(self, value):
        self.__i2c.write_byte(self.__address, value)
    
    # Write number of bytes
    # data: list of byte
    def __send_data(self, data):
        self.__i2c.i2c_write_data(self.__address, data)
    
    # Write command
    def __command(self, value):
        data = [LCD_TYPE_COMMAND, value]
        self.__i2c.i2c_write_data(self.__address, data)

    #--------------------------------------------------------------------------------------------------#

    # Clear display, set cursor position to zero
    def clear(self):
        self.__command(LCD_CLEARDISPLAY)
        time.sleep(.002)                  # This command takes a long time

    # Turn the display on (quickly)
    def display(self):
        self.__control |= LCD_DISPLAYON
        self.__command(LCD_DISPLAYCONTROL  | self.__control)

    # Turn the display off (quickly)
    def no_display(self):
        self.__control &= ~LCD_DISPLAYON
        self.__command(LCD_DISPLAYCONTROL  | self.__control)

    # Set cursor position to zero
    def home(self):
        self.__command(LCD_RETURNHOME)
        time.sleep(.002)                  # This command takes a long time

    # Turns the underline cursor on
    def cursor(self):
        self.__control |= LCD_CURSORON
        self.__command(LCD_DISPLAYCONTROL | self.__control)

    # Turns the underline cursor off
    def no_cursor(self):
        self.__control &= ~LCD_CURSORON
        self.__command(LCD_DISPLAYCONTROL | self.__control)

    # Turn on the blinking cursor
    def cursor_blink(self):
        self.__control |= LCD_BLINKON
        self.__command(LCD_DISPLAYCONTROL | self.__control)

    # Turn off the blinking cursor
    def cursor_no_blink(self):
        self.__control &= ~LCD_BLINKON
        self.__command(LCD_DISPLAYCONTROL | self.__control)

    # This is for text that flows Left to Right
    def left_to_right(self):
        self.__mode |= LCD_ENTRYLEFT
        self.__command(LCD_ENTRYMODESET | self.__mode)
    
    # This is for text that flows Right to Left
    def right_to_left(self):
        self.__mode &= ~LCD_ENTRYLEFT
        self.__command(LCD_ENTRYMODESET | self.__mode)
    
    #--------------------------------------------------------------------------------------------------#

    # LCD Initialization
    # Cols: Number of column
    # Lines: 1 or 2 lines
    # Big font only when lines = 1
    def config_lcd(self, cols = 16, lines = 2, big_font = False):
        if lines > 1:
            self.__config |= LCD_2LINE
        
        # For some 1 line displays you can select a 10 pixel high font
        if big_font and lines == 1:
            self.__config |= LCD_5x10DOTS

        # Acscording to datasheet, we need at least 40ms after power rises above 2.7V before sending commands
        time.sleep(.05)

        # This is according to the hitachi HD44780 datasheet
        self.__command(LCD_FUNCTIONSET | self.__config)
        time.sleep(.005)                  # Wait more than 4.1ms

        # Second try
        self.__command(LCD_FUNCTIONSET | self.__config)
        time.sleep(.001)
        
        # Turn the display on with no cursor or blinking default
        self.__control = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.display()

        # Clear it off
        self.clear()

        # Initialize to default text direction (for romance languages)
        self.__mode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        self.__command(LCD_ENTRYMODESET | self.__mode)         # Set the entry mode
    
    # Set cursor
    def set_cursor(self, col, row):
        if row == 0:
            col |= 0x80
        else:
            col |= 0xC0
        
        self.__command(col)

    # Display text
    # Should set cursor or clear() before set text
    # text: String to display
    def print_text(self, text):
        chars = list(text)
        for c in chars:
            data = [LCD_TYPE_PRINT, ord(c)]
            self.__send_data(data)



#-------------------------- Example --------------------------

"""
i2c = I2C()
lcd = LCD16x2(i2c)

lcd.cursor_blink()
lcd.set_cursor(0, 0)
lcd.print_text("Demo")
time.sleep(2)
lcd.cursor_no_blink()

lcd.set_cursor(0, 0)
lcd.print_text("Hello world")
lcd.set_cursor(0, 1)
lcd.print_text("22/04/2021")
time.sleep(2)
lcd.clear()
"""