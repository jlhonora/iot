#include <JeeLib.h>
#include <RFM12B.h>

#ifndef __NETWORK_H
#define __NETWORK_H

#define DATA_PACKET 0x10
#define LOGGER_PACKET 0x20
#define SERIAL_PACKET 0x40
#define ACK_PACKET 0x55
#define ROUTE_PACKET 0x92
#define ACTION_PACKET 0xe8

void network_initialize(RFM12B *radio, uint8_t always_on);
bool network_send(uint8_t *data, uint8_t length, uint8_t packet_type);
void network_process_queue(void);

#endif
