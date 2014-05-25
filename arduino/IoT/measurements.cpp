#include <Ports.h>
#include "common.h"
#include "config.h"
#include <dht.h>
#include "ds18b20.h"
#include "pir.h"

dht DHT;

Port port_1(1);
Port port_2(2);
Port port_3(3);
Port port_4(4);

Port ports[] = {NULL, port_1, port_2, port_3, port_4};

void measurements_initialize() {
  uint8_t i;
  for(i = 1; i <= 4 ; i++){
    ports[i].mode(OUTPUT);
    ports[i].mode2(INPUT);
    ports[i].digiWrite(0);
  }
  // Initialize ADC now, give it some
  // time to stabilize before measuring
  power_adc_enable();

  #if DS18B20_PORT > 0
  ds18b20_initialize();
  #endif
  power_adc_disable();

  #if PIR_PORT > 0
  // Initialize the EEPROM-saved value
  load_pir_count();
  // Attach a PIR, water sensor or other
  // interrupt and count sensor to INT1.
  // Execute pir_count whenever this interrupt
  // occurs
  attachInterrupt(INT1, attempt_pir_count, RISING);
  #endif
}

uint16_t measurements_average(uint8_t port, bool analog, bool battery)
{
  //ports[port].digiWrite(1);
  uint16_t value = 0;
  uint8_t i = 16;
  power_adc_enable();
  while(i--){
    //sleep_seconds(1);
    Sleepy::loseSomeTime(4);
    uint16_t temp = 0;
    if(battery){
      temp = analogRead(BATTERY_PIN);
    } else {
      temp = ((analog) ? ports[port].anaRead() : 0/*ports[port].digiRead()*/);
    }
    value += temp;
  }
  power_adc_disable();
  //ports[port].digiWrite(0);
  return (value >> 4);
}

#if DS18B20_PORT > 0 || PIR_PORT > 0
extern uint8_t n_sensors;
extern char debug_str[DEBUG_STR_LEN];
#endif

#if PIR_PORT > 0
extern volatile uint16_t pir_count_value;
#if PIR_PORT <= 2
extern volatile uint32_t pir_count_integral;
#endif
#endif

void measurements_get(uint16_t *values)
{
  uint8_t port;
  for(port = 1; port <= 4; port++){
    if(DS18B20_PORT == port) {
      #if DS18B20_PORT > 0
      uint8_t ii;
      for(ii = 0; ii < n_sensors && port <= 4; ii++) {
        //values[((port-1) << 1)] = 0;
        values[((port-1) << 1) + 1] = ds18b20_read_value(ii);
        sprintf(debug_str, "Sen %d %d", ii, values[((port-1) << 1) + 1]);
        debug(debug_str);
        port++;
      }
      #endif
    } else if(PIR_PORT == port) {
      // The PIR values consists of two measurements:
	  // pir_count_value: counts since last sent packet
	  // pir_count_integral: counts since node startup
      #if PIR_PORT > 0
      sprintf(debug_str, "PIR: %lu", (uint32_t) pir_count_integral);
      debug(debug_str);
      values[((port-1) << 1) + 1] = (uint16_t) pir_count_value;
      // Save integral count to eeprom
      save_pir_count();
      #if PIR_PORT <= 2
	  port++;
      values[((port-1) << 1) + 1] = (uint16_t) (pir_count_integral & 0xFFFF);
	  port++;
      values[((port-1) << 1) + 1] = (uint16_t) ((pir_count_integral >> 16) & 0xFFFF);
      #endif
      #endif
    } else if(DHT_PORT == port){
      #if DHT_PORT > 0
      int chk = DHT.read22(DHT_PIN);
      if(chk == DHTLIB_OK){
        values[((port-1) << 1)] = (uint16_t)((DHT.temperature + 40) * 10);
        values[((port-1) << 1) + 1] = (uint16_t)(DHT.humidity * 10);
      } else {
        values[((port-1) << 1)] = 0;
        values[((port-1) << 1) + 1] = 0;
      }
      #endif
    } else {
      values[((port-1) << 1)] = measurements_average(port, true, false);
      values[((port-1) << 1) + 1] = measurements_average(port, false, false);
    }
  }
  values[8] = measurements_average(0, false, true);
}
