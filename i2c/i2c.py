#!/usr/bin/python3

from smbus2 import SMBus, i2c_msg

# https://smbus2.readthedocs.io/en/latest/
# https://pypi.org/project/smbus2/
# sudo apt-get install -y python-smbus
# sudo apt-get install -y i2c-tools
# sudo i2cdetect -y 1

class I2C:
    def __init__(self):
        self.bus = SMBus()
        self.bus.open(bus = 1)

    def __del__(self):
        self.bus.close()

    #--------------------------------------------------------------------------#

    # I2C write byte to slave
    def i2c_write_byte(self, address, byte):
        self.bus.write_byte(address, byte)

    # Write multiple bytes to slave
    # data: list of byte
    def i2c_write_data(self, address, data):
        msg = i2c_msg.write(address, data)
        self.bus.i2c_rdwr(msg)

    # Write byte to register (reg)
    # I2C read n bytes from register address (reg)
    # Address: Slave address
    # Reg: command or register address
    # Data: number of byte to write
    def i2c_write_block_data(self, address, reg, data):
        self.bus.write_i2c_block_data(address, reg, data)

    #--------------------------------------------------------------------------#

    # I2C read byte from slave
    # Address: Slave address
    # Return a byte
    def i2c_read_byte(self, address):
        return self.bus.read_byte(address)
    
    # I2C read multiple bytes from slave
    # Address: Slave address
    # Number of byte
    # Return list of bytes
    def i2c_read_data(self, address, size):
        read = i2c_msg.read(address, size)
        self.bus.i2c_rdwr(read)
        return list(read)
    
    # I2C read n bytes from register address (reg)
    # Address: Slave address
    # Reg: command or register address
    # Size: number of byte to read
    # Return list of bytes
    def i2c_read_block_data(self, address, reg, size):
        return self.bus.read_i2c_block_data(address, reg, size)

    #--------------------------------------------------------------------------#
    
    # I2C read and write operations in a transactions with repeated start
    # Address: Slave address
    # Write_list: List of data to write
    # Read_size: number of byte to read
    # Return list of bytes
    def i2c_read_write_data(self, address, write_list, read_size):
        read = i2c_msg.read(address, read_size)
        write = i2c_msg.write(address, write_list)
        self.bus.i2c_rdwr(write, read)
        
        return list(read)
