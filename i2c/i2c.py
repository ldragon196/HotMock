#!/usr/bin/python

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
    def i2c_write_data(self, address, data):
        msg = i2c_msg.write(address, data)
        self.bus.i2c_rdwr(msg)

    # Write byte to register (cmd)
    # I2C read n bytes from register address (cmd)
    # Address: Slave address
    # Cmd: command or register address
    # Data: number of byte to write
    def i2c_write_block_data(self, address, cmd, data):
        self.bus.write_i2c_block_data(address, cmd, data)

    #--------------------------------------------------------------------------#

    # I2C read byte from slave
    # Address: Slave address
    def i2c_read_byte(self, address):
        return self.bus.read_byte(address)
    
    # I2C read n bytes from register address (cmd)
    # Address: Slave address
    # Cmd: command or register address
    # Size: number of byte to read
    def i2c_read_block_data(self, address, cmd, size):
        return self.bus.read_i2c_block_data(address, cmd, size)

    #--------------------------------------------------------------------------#
    
    # I2C read and write operations in a transactions with repeated start
    # Address: Slave address
    # Write_list: List of data to write
    #             If None -> only read
    # Read_size: number of byte to read
    def i2c_read_write_data(self, address, write_list, read_size):
        read = i2c_msg.read(address, read_size)
        if write_list != None:
            write = i2c_msg.write(address, write_list)
            self.bus.i2c_rdwr(write, read)
        else:
            self.bus.i2c_rdwr(read)
        
        return list(read)