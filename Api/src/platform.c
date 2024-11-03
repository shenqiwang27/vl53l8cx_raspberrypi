#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include "platform.h"


// static int (*i2c_read_func)(uint8_t address, uint8_t reg,
//                     uint8_t *list, uint8_t length) = NULL;

// // calls write_i2c_block_data(address, reg, list)
// static int (*i2c_write_func)(uint8_t address, uint8_t reg,
//                     uint8_t *list, uint8_t length) = NULL;

// void VL53L8CX_set_i2c(void *read_func, void *write_func)
// {
//     i2c_read_func = read_func;
//     i2c_write_func = write_func;
// }

// static int i2c_write(VL53L8CX_Platform *p_platform, uint8_t cmd,
//                     uint8_t *data, uint8_t len)
// {
//   return i2c_write_func(p_platform->address, cmd, data, len);
// }

// static int i2c_read(VL53L8CX_Platform *p_platform, uint8_t cmd,
//                     uint8_t * data, uint8_t len)
// {
//   return i2c_read_func(p_platform->address, cmd, data, len);
// }

// uint8_t VL53L8CX_RdByte(
// 		VL53L8CX_Platform *p_platform,
// 		uint16_t RegisterAdress,
// 		uint8_t *p_value)
// {
// 	  uint8_t tmp = 0;
//     int ret = i2c_read(p_platform, RegisterAdress, &tmp, 1);
//     *p_value = tmp;
//     // printf("%u\n", tmp);
//     return ret;
// }

// uint8_t VL53L8CX_WrByte(
// 		VL53L8CX_Platform *p_platform,
// 		uint16_t RegisterAdress,
// 		uint8_t value)
// {
//   printf("start VL53L8CX_WrByte\n");
// 	return i2c_write(p_platform, RegisterAdress, &value, 1);
// }

// uint8_t VL53L8CX_WrMulti(
// 		VL53L8CX_Platform *p_platform,
// 		uint16_t RegisterAdress,
// 		uint8_t *p_values,
// 		uint32_t size)
// {	
//   return i2c_write(p_platform, RegisterAdress, p_values, size);
// }

// uint8_t VL53L8CX_RdMulti(
// 		VL53L8CX_Platform *p_platform,
// 		uint16_t RegisterAdress,
// 		uint8_t *p_values,
// 		uint32_t size)
// {
// 	return i2c_read(p_platform, RegisterAdress, p_values, size);
// }

// uint8_t VL53L8CX_Reset_Sensor(
// 		VL53L8CX_Platform *p_platform)
// {
// 	uint8_t status = 0;
	
// 	/* (Optional) Need to be implemented by customer. This function returns 0 if OK */
	
// 	/* Set pin LPN to LOW */
// 	/* Set pin AVDD to LOW */
// 	/* Set pin VDDIO  to LOW */
// 	/* Set pin CORE_1V8 to LOW */
// 	VL53L8CX_WaitMs(p_platform, 100);

// 	/* Set pin LPN to HIGH */
// 	/* Set pin AVDD to HIGH */
// 	/* Set pin VDDIO to HIGH */
// 	/* Set pin CORE_1V8 to HIGH */
// 	VL53L8CX_WaitMs(p_platform, 100);

// 	return status;
// }

// void VL53L8CX_SwapBuffer(
// 		uint8_t 		*buffer,
// 		uint16_t 	 	 size)
// {
// 	uint32_t i, tmp;
	
// 	/* Example of possible implementation using <string.h> */
// 	for(i = 0; i < size; i = i + 4) 
// 	{
// 		tmp = (
// 		  buffer[i]<<24)
// 		|(buffer[i+1]<<16)
// 		|(buffer[i+2]<<8)
// 		|(buffer[i+3]);
		
// 		memcpy(&(buffer[i]), &tmp, 4);
// 	}
// }	

// uint8_t VL53L8CX_WaitMs(
// 		VL53L8CX_Platform *p_platform,
// 		uint32_t TimeMs)
// {
// 	uint8_t status = 0;

//   usleep(TimeMs);
	
// 	return status;
// }


uint8_t VL53L8CX_RdByte(
		VL53L8CX_Platform *p_platform,
		uint16_t RegisterAdress,
		uint8_t *p_value)
{
	uint8_t status = 255;
	unsigned char buffer[2];
	buffer[0] = RegisterAdress >> 8;
	buffer[1] = RegisterAdress & 0xFF;

	if (write(p_platform->fd, buffer, 2) != 2)
	{
		perror("Failed to write to the i2c bus.");
		return status;
	}

	if (read(p_platform->fd, p_value, 1) != 1)
	{
		perror("Failed to read from the i2c bus.");
		return status;
	}

	return 0;
}

uint8_t VL53L8CX_WrByte(
		VL53L8CX_Platform *p_platform,
		uint16_t RegisterAdress,
		uint8_t value)
{
  	uint8_t status = 255;

	unsigned char buffer[3];
	buffer[0] = RegisterAdress >> 8;
	buffer[1] = RegisterAdress & 0xFF;
	buffer[2] = value;

	if (write(p_platform->fd, buffer, 3) != 3)
	{
		perror("Failed to write to the I2C bus");
		return status;
	}

	return 0;
}

uint8_t VL53L8CX_WrMulti(
		VL53L8CX_Platform *p_platform,
		uint16_t RegisterAdress,
		uint8_t *p_values,
		uint32_t size)
{	
  uint8_t status = 255;

	if (size > MAX_I2C_BUFFER_SIZE)
	{
		uint32_t remaining_bytes = size;
		uint32_t offset = 0;
		uint8_t buffer[MAX_I2C_BUFFER_SIZE];
		int chunk_size;

		while (remaining_bytes > 0)
		{
			chunk_size = remaining_bytes > MAX_I2C_BUFFER_SIZE - 2 ? MAX_I2C_BUFFER_SIZE - 2 : remaining_bytes;

			buffer[0] = (RegisterAdress >> 8) & 0xFF;
			buffer[1] = RegisterAdress & 0xFF;

			for (int i = 0; i < chunk_size; ++i)
				buffer[2 + i] = p_values[offset + i];
		
			if (write(p_platform->fd, buffer, chunk_size + 2) != chunk_size + 2)
			{
				perror("Failed to write to the i2c bus");
				return status;
			}

			remaining_bytes -= chunk_size;
			offset += chunk_size;
			RegisterAdress += chunk_size;
		}

	}
	else
	{
		unsigned char buffer[size + 2];
		buffer[0] = RegisterAdress >> 8;
		buffer[1] = RegisterAdress & 0xFF;
		memcpy(buffer + 2, p_values, size);

		int wrsize = write(p_platform->fd, buffer, size + 2); 
		if (wrsize != size + 2)
		{
			perror("Failed to write to the i2c bus.");
			return status;
		}
	}
	
	return 0;
}

uint8_t VL53L8CX_RdMulti(
		VL53L8CX_Platform *p_platform,
		uint16_t RegisterAdress,
		uint8_t *p_values,
		uint32_t size)
{
	uint8_t status = 255;

	unsigned char buffer[2];
	buffer[0] = RegisterAdress >> 8;
	buffer[1] = RegisterAdress & 0xFF;

	if (write(p_platform->fd, buffer, 2) != 2)
	{
		perror("Failed to write to the i2c bus.");
		return status;
	}

	if (read(p_platform->fd, p_values, size) != size)
	{
		perror("Failed to read from the i2c bus.");
		return status;
	}

	return 0;
}

uint8_t VL53L8CX_Reset_Sensor(
		VL53L8CX_Platform *p_platform)
{
	uint8_t status = 0;
	
	/* (Optional) Need to be implemented by customer. This function returns 0 if OK */
	
	/* Set pin LPN to LOW */
	/* Set pin AVDD to LOW */
	/* Set pin VDDIO  to LOW */
	/* Set pin CORE_1V8 to LOW */
	VL53L8CX_WaitMs(p_platform, 100);

	/* Set pin LPN to HIGH */
	/* Set pin AVDD to HIGH */
	/* Set pin VDDIO to HIGH */
	/* Set pin CORE_1V8 to HIGH */
	VL53L8CX_WaitMs(p_platform, 100);

	return status;
}

void VL53L8CX_SwapBuffer(
		uint8_t 		*buffer,
		uint16_t 	 	 size)
{
	uint32_t i, tmp;
	
	/* Example of possible implementation using <string.h> */
	for(i = 0; i < size; i = i + 4) 
	{
		tmp = (
		  buffer[i]<<24)
		|(buffer[i+1]<<16)
		|(buffer[i+2]<<8)
		|(buffer[i+3]);
		
		memcpy(&(buffer[i]), &tmp, 4);
	}
}	

uint8_t VL53L8CX_WaitMs(
		VL53L8CX_Platform *p_platform,
		uint32_t TimeMs)
{
	uint8_t status = 0;

  	usleep(TimeMs);
	
	return status;
}