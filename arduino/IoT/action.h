#ifndef __ACTION_H
#define __ACTION_H
#include <stdint.h>
#include <stdlib.h>
#include "common.h"
#include "network.h"
#include "config.h"

#if defined(ACTION_NODE)
// Represents an action to be executed
// in the node
typedef struct Action_t {
  uint16_t hold_for; // The interval (in seconds) to execute the action
  uint8_t  port   : 4;   // The port to be acted upon (0-4)
  uint8_t  valid  : 1;   // Is the action still valid?
  uint8_t  status;       // The status value
  uint8_t  id;           // The action id (to avoid duplicate actions)
} Action;

void append_action(uint8_t action_port, uint8_t port_status, uint16_t hold_for);
void app_receive_action(uint8_t *data, uint8_t data_length);
void process_actions(uint32_t elapsed);
#define MAX_ACTIONS 3
#define HOLD_FOREVER 65535
#endif // if defined(ACTION_NODE)

uint32_t action_get_dst_id(uint8_t * data, uint8_t data_length);

#if defined(ACTION_MASTER)
void action_usart_process_rx(void);
#endif // defined(ACTION_MASTER) 

#endif
