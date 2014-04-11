#ifndef __COMMON_H
#define __COMMON_F

#include <avr/power.h>

int freeRam();
void debug(const char *);
void sleep_mseconds(uint32_t);
uint64_t clock_time();
void led_activity(bool);
void led_boot();
void enable_system_clock();
void disable_system_clock();

void disable_irq();
void enable_irq();
void beenode_reset(void);

// Initialize unused peripherals
// in low power state
void low_power_init(void);

// Initialize unused IO pins
// as inputs, pullup disabled
void io_init(void);

void hex_print(uint8_t * data, uint8_t data_length);
int8_t arr_indexof(uint8_t * arr, uint8_t arr_len, uint8_t character);

#ifndef UINT16_MAX
#define INT16_MAX 0x7fffL
#define INT16_MIN (-INT16_MAX - 1L)
#define UINT16_MAX (__CONCAT(INT16_MAX, U) * 2UL + 1UL)
#endif

#endif
