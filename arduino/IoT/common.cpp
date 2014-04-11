#include <JeeLib.h>
#include <avr/sleep.h>
#include <avr/power.h>
#include "config.h"

void sleep_mseconds(uint32_t sleep_time)
{
  while (sleep_time > 0) {
    if (sleep_time >= 250) {
      Sleepy::loseSomeTime(250);
      sleep_time -= 250;
    } else {
      Sleepy::loseSomeTime(sleep_time);
      sleep_time = 0;
    }
  }
}

uint8_t led_activity_disabled = 0;
void led_activity(bool status) {
  if(led_activity_disabled) return;
  #if defined(MINIMUM_POWER)
  // The LED in the beenode board lights up when a 0 is written to it
  #ifdef BEENODE
  digitalWrite(ACTIVITY_LED, true);
  #else
  digitalWrite(ACTIVITY_LED, false);
  #endif
  return;
  #endif
  #ifdef BEENODE
  digitalWrite(ACTIVITY_LED, status == false);
  #endif
  #ifdef JEENODE
  digitalWrite(ACTIVITY_LED, status == true);
  #endif
}

void led_boot() {
  uint8_t i;
  for (i = 0; i < 3; i++) {
    led_activity(true);
    Sleepy::loseSomeTime(50);
    led_activity(false);
    Sleepy::loseSomeTime(50);  
  }
  led_activity_disabled = 1;
}

int freeRam() {
  extern int __heap_start, *__brkval; 
  uint8_t v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}

void debug(const char *line) {
  #ifndef NO_DEBUG
  Serial.println(line);
  Serial.flush();
  #endif
}

void disable_irq() {
  EIMSK &= ~(_BV(INT1));
}

void enable_irq() {
  EIMSK |= _BV(INT1);
}
/** Restarts program but does not 
  * reset the peripherals and registers */
void beenode_reset(void) {
  asm volatile ("  jmp 0");
}

extern char debug_str[DEBUG_STR_LEN];
void hex_print(uint8_t * data, uint8_t data_length) {
  #ifndef NODEBUG
  unsigned int ii;
  for(ii = 0; ii < data_length; ii++) {
    sprintf(debug_str, "%02X ", data[ii]);
    Serial.print(debug_str);
  }
  Serial.println();
  Serial.flush();
  #endif
}

int8_t arr_indexof(uint8_t * arr, uint8_t arr_len, uint8_t character) {
  int8_t index = 0;
  while(index < arr_len) {
    if(arr[index] == character) break;
    index++;
  }
  return index;
} 

/** Initialize unused ports to inputs,
 *  pullup disabled */
void io_init(void) {
  /*digitalWrite(12, INPUT);
  digitalWrite(11, INPUT);
  digitalWrite(10, INPUT);
  digitalWrite(9, INPUT);
  digitalWrite(27, INPUT); // PC4
  digitalWrite(28, INPUT); // PC5
  digitalWrite(24, INPUT); // PC1
  digitalWrite(25, INPUT); // PC2*/
}

void low_power_init(void) {
  // Power reduction for:
  // Timer2
  // ADC
  // TWI (Two-Wire-Interface, I2C)
  power_timer2_disable();
  power_adc_disable();
  power_twi_disable();
}
