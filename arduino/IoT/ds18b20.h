#include <inttypes.h>

#ifndef _DS18B20_H
#define _DS18B20_H

uint8_t ds18b20_initialize();
uint16_t ds18b20_read_value(uint8_t index);

#endif
