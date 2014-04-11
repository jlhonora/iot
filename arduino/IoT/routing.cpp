#include <JeeLib.h>
#include "routing.h"
#include "common.h"
#include "config.h"

typedef struct routing_row {
  uint32_t source:24;
  uint8_t seq:8;
  uint32_t time:32;
} routing_row_t;


routing_row_t routing_table[ROUTING_TABLE_SIZE];

void routing_initialize()
{
  memset(routing_table, 0, sizeof(routing_table));
}

void routing_register(uint32_t source, uint8_t seq)
{
  uint8_t latest = 0;
  uint8_t i;
  for(i = 0; i < ROUTING_TABLE_SIZE; i++){
    if(routing_table[i].time <= routing_table[latest].time){
      latest = i;
    }
    if(routing_table[i].source == source)
      break;

  }
  if(i == ROUTING_TABLE_SIZE){
    i = latest;
  }
  routing_table[i].source = source;
  routing_table[i].time = millis();
  routing_table[i].seq = seq;
}


uint8_t routing_should_route(uint32_t source, uint8_t seq)
{
  int16_t seq_diff;
  uint8_t i;
  for(i = 0; i < ROUTING_TABLE_SIZE; i++){
    if(routing_table[i].source == source){
      if(millis() - routing_table[i].time > 150000LU){
        return 1;
      }
      seq_diff = routing_table[i].seq - seq;
      if(seq_diff < 0)
        seq_diff += 256;

      if(seq_diff > 20)
        return 1;
      else
        return 0;
    }
  }
  if(i == ROUTING_TABLE_SIZE){
    return 1;
  }
  return 0; 
}