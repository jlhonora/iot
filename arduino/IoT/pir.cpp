#include "pir.h"
#include <JeeLib.h>

void do_pir_count(void);

volatile uint16_t pir_count_value = 0;

// The PIR count integral is only supported for 
// ports 1 or 2
#if PIR_PORT <= 2
volatile uint32_t pir_count_integral = 0;
#else
#warning "Discarding PIR integral, use PIR_PORT <= 2"
#endif

#define DEBOUNCE_MILLIS 200
volatile unsigned long last_millis = 0;

void attempt_pir_count(void) {
	// Rollover isn't too bad here, maybe an extra count
	if ((unsigned long) (millis() - last_millis) > DEBOUNCE_MILLIS) {
		do_pir_count();
		last_millis = millis();
	}
}

void do_pir_count(void) {
  pir_count_value++;
#if PIR_PORT <= 2
  pir_count_integral++;
#endif
}

void reset_pir_count(void) {
  pir_count_value = 0;
}
