
import time
from VL53L8CX import VL53L8CX
from ctypes import *


tof = VL53L8CX()

tof.init_and_start_ranging()
for count in range(1,1001):
    distance = tof.read_distance()
    if (distance > 0):
        print ("%d mm, %d cm, %d" % (distance, (distance/10), count))


