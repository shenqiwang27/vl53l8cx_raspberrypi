CC = $(CROSS_COMPILE)gcc
RM = rm

#CFLAGS = -O0 -g -Wall -c
CFLAGS = -O2 -Wall -fPIC -c

OUTPUT_DIR = bin
OBJ_DIR = obj

ROOT_DIR := $(shell pwd)
API_DIR := $(ROOT_DIR)/Api

TARGET_LIB = $(OUTPUT_DIR)/vl53l8cx_python

INCLUDES = \
	-I$(ROOT_DIR) \
	-I$(API_DIR)/inc
	

PYTHON_INCLUDES = \
    -I/usr/include/python3.11

VPATH = \
	$(API_DIR)/src \
	$(ROOT_DIR)/python_lib 

LIB_SRCS = \
	vl53l8cx_plugin_detection_thresholds.c \
	vl53l8cx_plugin_motion_indicator.c \
	vl53l8cx_plugin_xtalk.c \
	vl53l8cx_api.c \
	platform.c \
	vl53l8cx_python.c


LIB_OBJS  = $(LIB_SRCS:%.c=$(OBJ_DIR)/%.o)

.PHONY: all
all: ${TARGET_LIB}

$(TARGET_LIB): $(LIB_OBJS)
	mkdir -p $(dir $@)
	$(CC) -shared $^ $(PYTHON_INCLUDES) $(INCLUDES) -lpthread -o $@.so

$(OBJ_DIR)/%.o:%.c
	mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(PYTHON_INCLUDES) $(INCLUDES) $< -o $@

.PHONY: clean
clean:
	-${RM} -rf ./$(OUTPUT_DIR)/*  ./$(OBJ_DIR)/*

