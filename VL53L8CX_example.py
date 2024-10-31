
import time
import VL53L8CX
from ctypes import *
import numpy as np
import json
import cv2


tof = VL53L8CX.VL53L8CX()

count =0


def print_8x8_grid(list1, list2):
  
    print("\033[2J")  
    print("\033[H", end="")  

    for i in range(8):
        for j in range(8):
            index = i * 8 + j
            value1 = list1[index] / 1000
            value2 = list2[index] 
            print(f"{value1:7.3f}/{value2:3d}", end=" ")
        print()

    print(flush=True)


while True:
    count +=1
    distance, target_status = tof.read_distance()
    # print(distance)
    distance_array = [distance[i] for i in range(64)]
    target_status_array = [target_status[i] for i in range(64)]
    print_8x8_grid(distance_array,target_status_array)
    
    distance_array = np.array(distance_array)
    target_status_array = np.array(target_status_array)
    distance_array = np.where(target_status_array != 5, 4000, distance_array)
    
    distance_matrix = np.clip(np.where(distance_array < 0, 4000, distance_array), 0, 4000)
    
    distance_matrix = distance_matrix / 4000
    distance_matrix = np.uint8(distance_matrix * 255)
    distance_matrix = np.array(distance_matrix).reshape(8, 8)
    
    # 显示图像
    cv2.imshow('Distance Matrix', distance_matrix)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    # print(json.dumps(distance_matrix.tolist()))



