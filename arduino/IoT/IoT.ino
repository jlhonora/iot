#include <OneWire.h>
#include <DallasTemperature.h>
#include <TimerOne.h>
#include <JeeLib.h>
#include <RFM12B.h>
#include <dht.h>

#include <avr/power.h>
#include <avr/wdt.h>

#include "common.h"
#include "measurements.h"
#include "network.h"

#include "config.h"
#include "pir.h"

#include "action.h"

RFM12B radio_main;

#if defined(RELAY_SENSING) or defined(ENDNODE) or defined(MASTER_SENSING)
uint16_t values[11];
#ifdef DATALOGGING
uint32_t average_values[9];
uint16_t average_samples = 0;
#endif
#endif

ISR(WDT_vect){Sleepy::watchdogEvent();}

#if defined(ACTION_MASTER)
uint8_t serial_rx_state = SERIAL_IDLE;
#endif

char debug_str[DEBUG_STR_LEN];

#if (defined(MASTER) && defined(MASTER_SENSING)) || (defined(RELAY) && defined(RELAY_SENSING)) || defined(ENDNODE)
#define SENSING
#endif

#if defined(RELAY) || defined(MASTER) || defined(ACTION_NODE)
#define RADIO_ALWAYS_ON
#endif

void app_receive(uint8_t *data, uint8_t data_length) {
  // Process incoming 'action' packet
  #if defined(ACTION_NODE)
  app_receive_action(data, data_length);
  #else
  uint8_t seq;
  uint64_t temp = 64;
  uint8_t packet_type;
  uint8_t offset = 0;
  uint32_t relay_id;

  debug("");
  sprintf(debug_str, "RAM %d", freeRam());
  debug(debug_str);
  
  do {
    packet_type = data[offset];
    relay_id = 0;
    memmove(&relay_id, data + 1 + offset, 3);
    seq = data[offset + 4];
    offset += 6;
    if(packet_type == ROUTE_PACKET){
      sprintf(debug_str, "Route from %lu", relay_id);
      debug(debug_str);
    }
  } while(packet_type == ROUTE_PACKET);

  if(packet_type != DATA_PACKET && 
     packet_type != LOGGER_PACKET &&
     packet_type != ACTION_PACKET){
    debug("!DATA PACKET");
    uint8_t i;
    for(i = 0; i < data_length; i++){
      sprintf(debug_str, "%02X", data[i]);
      debug(debug_str);
    }
    debug("");
    return;
  }

  uint16_t *values = (uint16_t *)(data + offset);

  if (packet_type == DATA_PACKET) {
    sprintf(debug_str, "Data %lu s%u", relay_id, seq);
    debug(debug_str);
    //sprintf(debug_str, "Len: %u", data_length);
    //debug(debug_str);
    sprintf(debug_str, "$%lu,%u,%u,%u,%u,%u,%u,%u,%u,%u", 
      relay_id, 
      values[0], 
      values[1], 
      values[2], 
      values[3], 
      values[4], 
      values[5], 
      values[6], 
      values[7], 
      values[8]);
  } else if (packet_type == LOGGER_PACKET){
    sprintf(debug_str, "Log %lu s%u", relay_id, seq);
    debug(debug_str);
    sprintf(debug_str, "!%lu,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u", 
      relay_id, 
      values[9], 
      values[10], 
      values[0], 
      values[1], 
      values[2], 
      values[3], 
      values[4], 
      values[5], 
      values[6], 
      values[7], 
        values[8]);
  }
  debug(debug_str);
  
  #endif // defined(ACTION_NODE)
}

void setup()
{
  //low_power_init();
  Serial.begin(57600);

  debug("Boot");

  #if defined(SENSING)
  measurements_initialize();
  #endif

  #if defined(RADIO_ALWAYS_ON)
  network_initialize(&radio_main, 1);
  #else
  network_initialize(&radio_main, 0);
  #endif
  debug("OK");
  sprintf(debug_str, "RAM %d", freeRam());
  debug(debug_str);
  pinMode(ACTIVITY_LED, OUTPUT);
  led_boot();
  //setting initial values to 0
  #if defined(SENSING) and defined(DATALOGGING)
  memset(average_values, 0, sizeof(average_values));
  #endif
}

// This case applies to {MASTER|RELAY}_SENSING, ENDNODE or ACTION_NODE
#if defined(SENSING) || defined(ACTION_NODE)
// The millis() function returns an unsigned long, which
// corresponds to a uint32_t type
uint32_t last_measurement_time = 0;
uint32_t elapsed = 0;
#endif

void loop()
{
  #if defined(SENSING)
  #if defined(RADIO_ALWAYS_ON)
  if((elapsed = (millis() - last_measurement_time)) > SLEEP_TIME){
  #endif

  measurements_get(values);

  #ifdef MASTER_SENSING
  sprintf(debug_str,"$%u,%u,%u,%u,%u,%u,%u,%u,%u,%u", NODEID, values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8]);
  debug(debug_str);
  #else

  uint8_t i, packet_type = DATA_PACKET;

  bool sent = network_send((uint8_t *)values, sizeof(values), packet_type);
  #if defined(MINIMUM_POWER)
  sent = true;
  #endif
  #if PIR_PORT > 0
  if (sent) reset_pir_count();
  #endif
  #endif // else defined(MASTER_SENSING)
  
  #if defined(RADIO_ALWAYS_ON)
    last_measurement_time = millis();
  }
  #endif

  #endif // defined(SENSING)

  // Process the queue
  #if defined(RADIO_ALWAYS_ON)
  network_process_queue();
  #endif  

  // Decide how much time should I sleep
  #if defined(ENDNODE)
    // If I don't use the serial port, disable it
    // while sleeping (and then enable it)
    #if !defined(USE_SERIAL_PORT_INPUT)
    power_usart0_disable();
    #endif
    // Sleep for SLEEP_TIME milliseconds
    sleep_mseconds(SLEEP_TIME);
    #if !defined(USE_SERIAL_PORT_INPUT)
    power_usart0_enable();
    #endif
  #endif 
}

