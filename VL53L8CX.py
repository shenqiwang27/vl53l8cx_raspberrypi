#!/usr/bin/python

import time,os
from ctypes import *
from smbus2 import SMBus
i2cbus = SMBus(1)

def i2c_read(self, address, reg, data_p, length):
    ret_val = 0
    try:
        result = i2cbus.read_i2c_block_data(address, reg, length)
        for i in range(length):
            data_p[i] = result[i]
    except IOError:
        ret_val = -1
    return ret_val


def i2c_write(address, reg, data_p, length):
    ret_val = 0
    data = [data_p[i] for i in range(length)]
    try:
        i2cbus.write_i2c_block_data(address, reg, data)
    except IOError:
        ret_val = -1
    return ret_val


tof_lib = CDLL("./bin/vl53l8cx_python.so")


I2C_FUNC = CFUNCTYPE(c_int, c_uint16, c_uint16, 
                                    POINTER(c_uint8), c_uint32)

i2c_read_func = I2C_FUNC(i2c_read)
i2c_write_func = I2C_FUNC(i2c_write)
tof_lib.VL53L8CX_set_i2c(i2c_read_func, i2c_write_func)

class VL53L8CX:
    def __init__(self, device_address=0x52):
        # self.
        self.device_address = device_address
        
 
        print('before init')
        tof_lib.init_and_start_vl53l8cx()
        print('finish init')
    
    
    def read_distance(self):
        is_ready = c_uint8(0)
        while is_ready.value == 0:
            tof_lib.vl53l8cx_check_data_ready(byref(self.dev), byref(is_ready))
            time.sleep(0.01)
        
        tof_lib.vl53l8cx_get_ranging_data(byref(self.dev), byref(self.results))
        return self.results.distance_mm[4*8 + 4] 