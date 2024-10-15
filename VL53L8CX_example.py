
import time
import VL53L8CX
from ctypes import *


tof = VL53L8CX.VL53L8CX()

count =0


def print_8x8_grid(python_array):
    # Clear the screen
    print("\033[2J")
    
    # Move cursor to home position
    print("\033[H", end="")
    
    # Print the 8x8 grid
    for i in range(8):
        for j in range(8):
            index = i * 8 + j
            print(f"{python_array[index]:4}", end="")
        print()  # New line after each row
    
    # Flush the output
    print(flush=True)


while True:
    count +=1
    distance = tof.read_distance()
    distance_array = [distance[i] for i in range(64)]
    print_8x8_grid(distance_array)


