#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>
#include <time.h>
#include "vl53l8cx_api.h"
#include "platform.h"


#define VL53L0X_GOOD_ACCURACY_MODE      0   // Good Accuracy mode
#define VL53L0X_BETTER_ACCURACY_MODE    1   // Better Accuracy mode
#define VL53L0X_BEST_ACCURACY_MODE      2   // Best Accuracy mode
#define VL53L0X_LONG_RANGE_MODE         3   // Longe Range mode
#define VL53L0X_HIGH_SPEED_MODE         4   // High Speed mode

void startRanging(int object_number, int mode, uint8_t i2c_address)
{
    

}


VL53L8CX_Configuration Dev;
VL53L8CX_ResultsData Results;

uint8_t init_and_start_vl53l8cx(void)
{
    uint8_t status;

    status = vl53l8cx_init(&Dev);
    if (status) {
        return status;
    }

    status = vl53l8cx_set_resolution(&Dev, VL53L8CX_RESOLUTION_8X8);
    if (status) {
        return status;
    }

    status = vl53l8cx_set_ranging_frequency_hz(&Dev, 10);
    if (status) {
        return status;
    }

    status = vl53l8cx_set_integration_time_ms(&Dev, 50);
    if (status) {
        return status;
    }

    status = vl53l8cx_set_target_order(&Dev, VL53L8CX_TARGET_ORDER_CLOSEST);
    if (status) {
        return status;
    }

    status = vl53l8cx_start_ranging(&Dev);
    
    return status;
}

uint8_t read_vl53l8cx_distance(int16_t *p_distance)
{
    uint8_t status;
    uint8_t isReady;

    do {
        status = vl53l8cx_check_data_ready(&Dev, &isReady);
        if (status) {
            return status;
        }
    } while (!isReady);

    status = vl53l8cx_get_ranging_data(&Dev, &Results);
    if (status) {
        return status;
    }


    *p_distance = Results.distance_mm[4*8 + 4];  
    
    return VL53L8CX_STATUS_OK;
}