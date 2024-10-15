
import time
import VL53L8CX
from ctypes import *


tof = VL53L8CX.VL53L8CX()

count =0
while True:
    count +=1
    distance = tof.read_distance()
    if (distance > 0):
        print ("%d mm, %d cm, %d" % (distance, (distance/10), count))


