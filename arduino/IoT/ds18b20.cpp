#include <Jeelib.h>
#include "ds18b20.h"
#include "common.h"
#include "config.h"

#include <OneWire.h>
#include <DallasTemperature.h>

OneWire oneWire(DS18B20_PIN);
DallasTemperature sensors(&oneWire);

extern char debug_str[DEBUG_STR_LEN];
uint8_t n_sensors = 0;

uint8_t get_resolution(DallasTemperature * sensors) {
  DeviceAddress address;
  (*sensors).getAddress(address, 0);
  return (*sensors).getResolution(address);
}

uint8_t ds18b20_initialize()
{
  sensors.begin();
  n_sensors = sensors.getDeviceCount();
  sprintf(debug_str, "N%d", n_sensors);
  debug(debug_str);
  if(n_sensors > 4) n_sensors = 4; 
  uint8_t resolution = get_resolution(&sensors);
  if(resolution > 12 || resolution < 9) {
    debug("reset");
    sleep_mseconds(100);
    beenode_reset();
  }
  return n_sensors;
}

uint16_t ds18b20_read_value(uint8_t index)
{
  sensors.requestTemperatures();
  uint16_t value = ((uint16_t)(sensors.getTempCByIndex(index) * 100) + 5500);
  return value;
}
