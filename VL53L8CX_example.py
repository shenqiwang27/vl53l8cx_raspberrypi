
import time
import VL53L8CX
from ctypes import *
import numpy as np
import json
import cv2


tof = VL53L8CX.VL53L8CX()

count =0


def print_8x8_grid(python_array):
    
    print("\033[2J")
    
    print("\033[H", end="")
    
    # Print the 8x8 grid
    for i in range(8):
        for j in range(8):
            index = i * 8 + j
            value = python_array[index] / 1000  
            print(f"{value:7.3f}", end="")  
        print()  
    
    # Flush the output
    print(flush=True)


while True:
    count +=1
    distance = tof.read_distance()
    # print(distance)
    distance_array = [distance[i] for i in range(64)]
    print_8x8_grid(distance_array)
    
    distance_matrix = np.clip(distance_array, 0, 4000)
    distance_matrix = distance_matrix / 4000
    distance_matrix = np.uint8(distance_matrix*255)
    distance_matrix = np.array(distance_matrix).reshape(  8, 8)
    # print(distance_matrix)
    # resized_image = cv2.resize(distance_matrix, (400, 400), interpolation=cv2.INTER_NEAREST)
    
    cv2.imshow('Distance Matrix', distance_matrix)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    # print(json.dumps(distance_matrix.tolist()))



