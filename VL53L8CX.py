#!/usr/bin/python

import time
from ctypes import *
# from smbus2 import SMBus

VL53L8CX_GOOD_ACCURACY_MODE      = 0   # Good Accuracy mode
VL53L8CX_BETTER_ACCURACY_MODE    = 1   # Better Accuracy mode
VL53L8CX_BEST_ACCURACY_MODE      = 2   # Best Accuracy mode
VL53L8CX_LONG_RANGE_MODE         = 3   # Longe Range mode
VL53L8CX_HIGH_SPEED_MODE         = 4   # High Speed mode

# i2cbus = SMBus(1)

class VL53L8CX:
    def __init__(self, bus_number=1, device_address=0x52):
        # self.i2cbus = SMBus(bus_number)
        self.device_address = device_address
        
        
        self.lib = CDLL("./bin/vl53l8cx_python.so")
        
        
        class VL53L8CX_Configuration(Structure):
            _fields_ = [("platform", c_void_p),
                        ("streamcount", c_uint8)]
        
        class VL53L8CX_ResultsData(Structure):
            _fields_ = [("distance_mm", c_int16 * 64)]
        
        self.dev = VL53L8CX_Configuration()
        self.results = VL53L8CX_ResultsData()
        
        
        I2C_FUNC = CFUNCTYPE(c_int, c_uint16, c_uint16, 
                                    POINTER(c_uint8), c_uint32)
        self.i2c_read_func = I2C_FUNC(self.i2c_read)
        self.i2c_write_func = I2C_FUNC(self.i2c_write)
        
        
        self.lib.vl53l8cx_init(byref(self.dev))
        self.lib.vl53l8cx_set_i2c_address(byref(self.dev), self.device_address)
    
    def i2c_read(self, address, reg, data_p, length):
        ret_val = 0
        try:
            result = self.i2cbus.read_i2c_block_data(address, reg, length)
            for i in range(length):
                data_p[i] = result[i]
        except IOError:
            ret_val = -1
        return ret_val

    def i2c_write(self, address, reg, data_p, length):
        ret_val = 0
        data = [data_p[i] for i in range(length)]
        try:
            self.i2cbus.write_i2c_block_data(address, reg, data)
        except IOError:
            ret_val = -1
        return ret_val
    
    def init_and_start_ranging(self):
        self.lib.vl53l8cx_set_resolution(byref(self.dev), 64) 
        self.lib.vl53l8cx_set_ranging_frequency_hz(byref(self.dev), 10)
        self.lib.vl53l8cx_set_integration_time_ms(byref(self.dev), 50)
        self.lib.vl53l8cx_set_target_order(byref(self.dev), 1)  
        self.lib.vl53l8cx_start_ranging(byref(self.dev))
    
    def read_distance(self):
        is_ready = c_uint8(0)
        while is_ready.value == 0:
            self.lib.vl53l8cx_check_data_ready(byref(self.dev), byref(is_ready))
            time.sleep(0.01)
        
        self.lib.vl53l8cx_get_ranging_data(byref(self.dev), byref(self.results))
        return self.results.distance_mm[4*8 + 4] 