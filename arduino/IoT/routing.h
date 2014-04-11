#ifndef __ROUTING_H
#define __ROUTING_H

void routing_initialize();
void routing_register(uint32_t, uint8_t);
uint8_t routing_should_route(uint32_t, uint8_t);

#endif