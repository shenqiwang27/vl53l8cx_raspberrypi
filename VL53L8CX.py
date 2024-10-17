#!/usr/bin/python

import time,os,sys
import ctypes
from ctypes import *

VL53L8CX_RESOLUTION_8X8 = 64
VL53L8CX_NB_TARGET_PER_ZONE = 1 

class MotionIndicator(ctypes.Structure):
    _fields_ = [
        ("global_indicator_1", ctypes.c_uint32),
        ("global_indicator_2", ctypes.c_uint32),
        ("status", ctypes.c_uint8),
        ("nb_of_detected_aggregates", ctypes.c_uint8),
        ("nb_of_aggregates", ctypes.c_uint8),
        ("spare", ctypes.c_uint8),
        ("motion", ctypes.c_uint32 * 32)
    ]

class VL53L8CX_ResultsData(ctypes.Structure):
    _fields_ = [
        ("silicon_temp_degc", ctypes.c_int8),
        ("ambient_per_spad", ctypes.c_uint32 * VL53L8CX_RESOLUTION_8X8),
        ("nb_target_detected", ctypes.c_uint8 * VL53L8CX_RESOLUTION_8X8),
        ("nb_spads_enabled", ctypes.c_uint32 * VL53L8CX_RESOLUTION_8X8),
        ("signal_per_spad", ctypes.c_uint32 * (VL53L8CX_RESOLUTION_8X8 * VL53L8CX_NB_TARGET_PER_ZONE)),
        ("range_sigma_mm", ctypes.c_uint16 * (VL53L8CX_RESOLUTION_8X8 * VL53L8CX_NB_TARGET_PER_ZONE)),
        ("distance_mm", ctypes.c_int16 * (VL53L8CX_RESOLUTION_8X8 * VL53L8CX_NB_TARGET_PER_ZONE)),
        ("reflectance", ctypes.c_uint8 * (VL53L8CX_RESOLUTION_8X8 * VL53L8CX_NB_TARGET_PER_ZONE)),
        ("target_status", ctypes.c_uint8 * (VL53L8CX_RESOLUTION_8X8 * VL53L8CX_NB_TARGET_PER_ZONE)),
        ("motion_indicator", MotionIndicator)
    ]
tof_lib = CDLL("./bin/vl53l8cx_python.so")
tof_lib.read_vl53l8cx_distance.restype = POINTER(VL53L8CX_ResultsData)

# I2C_FUNC = CFUNCTYPE(c_int, c_uint16, c_uint16, 
#                                     POINTER(c_uint8), c_uint32)

# i2c_read_func = I2C_FUNC(i2c_read)
# i2c_write_func = I2C_FUNC(i2c_write)
# tof_lib.VL53L8CX_set_i2c(i2c_read_func, i2c_write_func)

class VL53L8CX:
    def __init__(self):
        
        
 
        print('before init')
        status = tof_lib.init_and_start_vl53l8cx()
        print('finish init, status is:', status)
        if status !=0:
            print('init failed')
            sys.exit(1)
    
    
    def read_distance(self):
        
        results = tof_lib.read_vl53l8cx_distance()
        print(type(results))
        distance = results.distance_mm
        target_status = results.target_status
        return distance, target_status