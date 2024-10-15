#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>
#include <time.h>
#include "vl53l8cx_api.h"
#include "platform.h"


static VL53L8CX_Configuration *Dev=NULL;
static VL53L8CX_ResultsData *Results=NULL;



uint8_t init_and_start_vl53l8cx(void)
{
    uint8_t status=255, isAlive;

    printf("qqqqq init\n");
    Dev = (VL53L8CX_Configuration *) malloc(sizeof(VL53L8CX_Configuration));
    memset(Dev, 0, sizeof(VL53L8CX_Configuration));
    Dev->platform.address = 0x29;
    

    Results = (VL53L8CX_ResultsData *) malloc(sizeof(VL53L8CX_ResultsData));
    memset(Results, 0, sizeof(VL53L8CX_ResultsData));

    status = vl53l8cx_is_alive(&Dev, &isAlive);
	if(!isAlive || status)
	{
		printf("VL53L8CX not detected at requested address\n");
		return status;
	}

    status = vl53l8cx_init(&Dev);
	if (status)
	{
		printf("VL53L8CX ULD Loading failed\n");
		return status;
	}

	printf("VL53L8CX ULD ready ! (Version : %s)\n", VL53L8CX_API_REVISION);

    // status = vl53l8cx_set_resolution(Dev, VL53L8CX_RESOLUTION_8X8);
    // if(status) {
    //     return status;
    // }

    // status = vl53l8cx_set_ranging_frequency_hz(Dev, 10);
    // if(status) {
    //     return status;
    // }

    // status = vl53l8cx_set_integration_time_ms(Dev, 50);
    // if(status) {
    //     return status;
    // }

    // status = vl53l8cx_set_target_order(Dev, VL53L8CX_TARGET_ORDER_CLOSEST);
    // if(status) {
    //     return status;
    // }

    status = vl53l8cx_start_ranging(Dev);
    
    return status;
}

uint8_t read_vl53l8cx_distance(void)
{
    uint8_t status;
    uint8_t isReady;

    do {
        status = vl53l8cx_check_data_ready(Dev, &isReady);
        if(status) {
            return status;
        }
    } while (!isReady);

    status = vl53l8cx_get_ranging_data(Dev, Results);
    if(status) {
        return status;
    }


    int16_t p_distance = Results->distance_mm[4*8 + 4];  

    return p_distance;
}