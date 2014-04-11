#include <avr/wdt.h>
#include "network.h"
#include "common.h"
#include "routing.h"
#include "config.h"
#include "action.h"

static uint8_t network_crc(uint8_t *, uint8_t);

extern char debug_str[DEBUG_STR_LEN];

typedef  struct network_buffer_status{
  uint8_t used        : 1;
  uint8_t retry_count : 3;
  uint8_t dummy       : 4;
  uint8_t length      : 8;
} network_buffer_status_t;

RFM12B *radio;

uint32_t node_id = NODEID;
uint8_t packet_seq = 0;

volatile uint8_t ack_received = 0;

uint8_t network_buffer[RX_BUFFER_SIZE][66];
network_buffer_status_t network_buffer_usage[RX_BUFFER_SIZE];

void app_receive(uint8_t *, uint8_t);

static uint8_t network_crc(uint8_t *data, uint8_t length)
{
  uint8_t crc = 0x00;
  while(length--)
    crc ^= data[length];
  return crc;
}

static void network_send_ack(uint32_t *source, uint8_t seq)
{
  uint8_t ack_packet[6];
  ack_packet[0] = ACK_PACKET;
  memmove(ack_packet + 1, source, 3);
  ack_packet[4] = seq;
  ack_packet[5] = network_crc(ack_packet, 5);
  (*radio).Send(0, ack_packet, 6, false);
  (*radio).SendWait(SLEEP_MODE_STANDBY);
  (*radio).ReceiveStart();
}

void network_process_queue(void)
{
  bool do_app_receive;
  bool do_send_ack;
  bool do_route;
  
  uint8_t busy_buffer;
  for(busy_buffer = 0; busy_buffer < RX_BUFFER_SIZE; busy_buffer++){
    do_app_receive = false;
    do_send_ack = false;
    do_route = false;
    if (network_buffer_usage[busy_buffer].used == 1){
      uint8_t length = network_buffer_usage[busy_buffer].length;
      uint8_t packet_type;
      uint32_t source, relay_source = 0;
      memmove(&relay_source, network_buffer[busy_buffer] + 1, 3);
      uint8_t seq, relay_seq = network_buffer[busy_buffer][4];
      
      uint8_t data_length = network_buffer[busy_buffer][5];
      uint8_t *data = network_buffer[busy_buffer] + 6;
      uint8_t offset = 0;
      // The packet header contains:
	  // 1-byte: packet type
	  // 3-byte: source id
	  // 1-byte: seq
      // 1-byte: length
      do {
        // Should check length before processing
        packet_type = network_buffer[busy_buffer][offset];
        source = 0;
        memmove(&source, network_buffer[busy_buffer] + 1 + offset, 3);
        seq = network_buffer[busy_buffer][4 + offset];
        offset += 6;
      } while(packet_type == ROUTE_PACKET);
      // If I didn't send the packet (source != node_id) 
      // then there are two options:
      //  - It's an ACTION_PACKET for me
      //  - Otherwise route the packet if I'm a relay
      if(source != node_id) {
        // Check if I'm the destination of an ACTION_PACKET
        if(packet_type == ACTION_PACKET && 
          node_id == action_get_dst_id((uint8_t *) &(network_buffer[busy_buffer][offset]), length)) {
          #if not defined(LISTEN_ONLY)
          do_send_ack = true;
          do_route = true;
          #endif
          do_app_receive = true;
        // If I'm not the destination of the action packet then
        // send an ack, register the routing and send the
        // packet if I'm a relay
        } else if(routing_should_route(source, seq)){
          if (packet_type == DATA_PACKET   || 
              packet_type == ROUTE_PACKET  || 
              packet_type == ACTION_PACKET || 
              packet_type == LOGGER_PACKET){
            #if not defined(LISTEN_ONLY)
            do_send_ack = true;
			do_route = true;
            #endif
          }
          routing_register(source, seq);
          do_app_receive = true;
        }
      }
      if(do_send_ack) {
        network_send_ack(&relay_source, relay_seq);
      }
      #ifdef RELAY
      if(length < 59 && do_route){
        network_send(network_buffer[busy_buffer], length, ROUTE_PACKET);
      }
      #endif
      // Manage the packet at the application layer and
      // mark the buffer as unused
      if(do_app_receive) {
        app_receive(network_buffer[busy_buffer], length);
      }
      network_buffer_usage[busy_buffer].used = 0;
    }
  }
}

extern char debug_str[DEBUG_STR_LEN];
void network_initialize(RFM12B *radio_ext, uint8_t always_on)
{
  #if defined(MASTER) || defined(RELAY)
  routing_initialize();
  #endif
  radio = radio_ext;
  memset(network_buffer_usage, 0, sizeof(network_buffer_usage));

  // The internal node ID of the RF12 uses 5 bits. 0 and 31
  // are reserved, so we must check these cases. If the masked
  // value of the node ID yields 0 or 31 then we fix the node
  // id to 1. Randomizing the node ID would mess up the routing.
  uint8_t rf12_nodeid = NODEID & RF12_HDR_MASK;
  if(rf12_nodeid == 0 || rf12_nodeid == 31) {
    rf12_nodeid = 1;
  }
  (*radio).Initialize(rf12_nodeid, RF12_433MHZ, NETWORKID);

  if (always_on)
    (*radio).ReceiveStart();
  else
    (*radio).Sleep();

  // Randomize first packet seq
  power_adc_enable();
  randomSeed(analogRead(A4));
  power_adc_disable();
  packet_seq = random(255);

  // Print node ID
  sprintf(debug_str, "NW %d", NODEID);
  debug(debug_str);
}

// Cannot be declared static, it is called from the
// RF12 library
void network_receive(uint8_t *buffer, uint8_t length)
{

  uint8_t crc = network_crc(buffer, length - 1);
  if (crc != buffer[length - 1]){
    return;
  }

  if (buffer[0] == ACK_PACKET) {
    uint32_t source = 0;
    memmove(&source, buffer + 1, 3);
    if(source == node_id && buffer[4] == packet_seq) {
      ack_received = 1;
    }
    return;
  }

  uint8_t free_buffer = 0;
  for(free_buffer = 0; free_buffer < RX_BUFFER_SIZE; free_buffer++)
    if (network_buffer_usage[free_buffer].used == 0)
      break;
  if(free_buffer == RX_BUFFER_SIZE)
    return;

  network_buffer_usage[free_buffer].used = 1;
  network_buffer_usage[free_buffer].length = length;
  network_buffer_usage[free_buffer].retry_count = 0;
  memmove(network_buffer[free_buffer], buffer, length);
}

bool network_send(uint8_t *data, uint8_t length, uint8_t packet_type)
{
  uint8_t packet[length + 7];
  packet[0] = packet_type;
  memmove(packet + 1, &node_id, 3);
  packet[4] = packet_seq;
  packet[5] = length;
  memmove(packet + 6, data, length);

  packet[length + 6] = network_crc(packet, length + 6);

  uint8_t total_length = length + 7;

  led_activity(true);
  wdt_enable(WDTO_2S);
  bool sent = false;
  uint8_t retry_count = 3;
  #ifdef ENDNODE
  (*radio).Wakeup();
  #endif
  #if defined(MINIMUM_POWER)
  (*radio).Send(0, packet, total_length, false);
  (*radio).SendWait(SLEEP_MODE_STANDBY);
  #else
  while(retry_count-- && !sent){
    uint32_t now = millis();
    if(retry_count < 2)
      while(millis() - now < (packet_seq % 8) * 40){}

    ack_received = 0;
    
    (*radio).Send(0, packet, total_length, false);
    (*radio).SendWait(SLEEP_MODE_STANDBY);
    (*radio).ReceiveStart();

    now = millis();
    while(millis() - now < 30){
      if(ack_received){
        sent = true;
        #if defined (ACTION_MASTER)
        if(packet_type == ACTION_PACKET) {
          // Print the action_id
          // sprintf(debug_str, "Action %u sent", data[3]);
          // Print the action packet
          uint32_t destination = 0;
          memmove(&destination, data, 3);
          uint8_t action_id = data[3];
          uint8_t port = data[4];
          uint8_t status = data[5];
          uint16_t hold_for = 0;
          memmove(&hold_for, data + 6, 2);
          sprintf(debug_str, "Action #%lu,%u,%u,%u,%u sent", destination, action_id, port, status, hold_for);
          debug(debug_str);
        }
        #endif
        break;
      }   
    }   
  }
  #endif // MINIMUM_POWER
  wdt_disable();
  #ifdef ENDNODE
  (*radio).Sleep();
  #endif
  packet_seq++;
  led_activity(false);
  return sent;
}
