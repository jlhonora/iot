#ifndef __PIR_H
#define __PIR_H
#include "common.h"
#include <stdint.h>
#include <avr/eeprom.h>
void attempt_pir_count(void);
void reset_pir_count(void);
void save_pir_count(void);
void load_pir_count(void);

#define EEPROM_PIR_ADDR ((uint32_t *) 0x40)
#endif
