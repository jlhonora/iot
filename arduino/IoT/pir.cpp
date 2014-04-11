#include "pir.h"
volatile uint16_t pir_count_value = 0;
// The PIR count integral is only supported for 
// ports 1 or 2
#if PIR_PORT <= 2
volatile uint32_t pir_count_integral = 0;
#else
#warning "Discarding PIR integral, use PIR_PORT <= 2"
#endif
void do_pir_count(void) {
  pir_count_value++;
#if PIR_PORT <= 2
  pir_count_integral++;
#endif
}

void reset_pir_count(void) {
  pir_count_value = 0;
}
