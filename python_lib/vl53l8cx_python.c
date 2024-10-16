#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>
#include <time.h>
#include "vl53l8cx_api.h"
#include "platform.h"


VL53L8CX_Configuration Dev;
VL53L8CX_ResultsData Results;



uint8_t init_and_start_vl53l8cx(void)
{
    uint8_t status=255, isAlive;

    
    Dev.platform.address = 0x29;
    Dev.platform.fd = open("/dev/i2c-1", O_RDWR);
    if (Dev.platform.fd < 0)
	{
		perror("Failed to open i2c bus.");
		return 1;
	}
	if (ioctl(Dev.platform.fd, I2C_SLAVE, 0x29) < 0) 
	{
		perror("Failed to acquire bus access.");
		close(Dev.platform.fd);
		return status;
	}

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

    status = vl53l8cx_set_resolution(&Dev, VL53L8CX_RESOLUTION_8X8);
    if(status) {
        return status;
    }

    status = vl53l8cx_set_ranging_frequency_hz(&Dev, 15);
    if(status) {
        return status;
    }

    // status = vl53l8cx_set_integration_time_ms(&Dev, 50);
    // if(status) {
    //     return status;
    // }

    // status = vl53l8cx_set_target_order(&Dev, VL53L8CX_TARGET_ORDER_CLOSEST);
    // if(status) {
    //     return status;
    // }

    status = vl53l8cx_start_ranging(&Dev);
    
    return status;
}

int16_t* read_vl53l8cx_distance(void)
{
    uint8_t status;
    uint8_t isReady;

    do {
        status = vl53l8cx_check_data_ready(&Dev, &isReady);
        if(status) {
            return status;
        }
    } while (!isReady);

    status = vl53l8cx_get_ranging_data(&Dev, &Results);
    if(status) {
        return status;
    }
    return Results.distance_mm;

}