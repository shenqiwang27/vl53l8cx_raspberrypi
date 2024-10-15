from smbus2 import SMBus

i2cbus = SMBus(1)
data = [0]

try:
    i2cbus.write_i2c_block_data(0x29, 0x7fff, data)
except IOError:
    print('write IOError')
    ret_val = -1
    
try:
    i2cbus.read_byte_data(0x29, 0x7fff)
except IOError:
    print('read IOError')
    ret_val = -1