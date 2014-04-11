#include "action.h"

#if defined(ACTION_NODE)
static uint8_t action_already_appended(uint8_t action_id);
static void action_update_status(Action * action);

/// A Ports array to access I/O ports
extern Port ports[5];
/// An Action array to execute actions
Action action_buffer[MAX_ACTIONS];
/// An auxiliar buffer to use with debug
extern char debug_str[DEBUG_STR_LEN];

/// Append a new action to the @ref action_buffer array
void append_action(uint8_t action_id, uint8_t action_port, uint8_t port_status, uint16_t hold_for) {
  uint8_t free_slot = 0;
  if(action_already_appended(action_id)) {
    debug("Repeated");
    return;
  }
  while(1) {
    // If there's a free slot then we use it
    if(!(action_buffer[free_slot].valid)) {
      // Update action's params
      action_buffer[free_slot].port = action_port;
      action_buffer[free_slot].status = port_status;
      // Change port mode and value right away
	  ports[action_port].mode(OUTPUT);
      action_update_status(&(action_buffer[free_slot]));
      action_buffer[free_slot].id = action_id;
      action_buffer[free_slot].hold_for = hold_for;
      action_buffer[free_slot].valid = 1;
      return;
    }
    // Check if there are no more free slots
    if(++free_slot >= MAX_ACTIONS) {
      debug("Actions full");
      return;
    }
  }
}

/// Check if there's already an action in the action_buffer
/// with this action ID
static uint8_t action_already_appended(uint8_t action_id) {
  uint8_t index;
  for(index = 0; index < MAX_ACTIONS; index++) {
    if(action_buffer[index].valid && (action_buffer[index].id == action_id)) return 1;
  }
  return 0;
}

/// Process incoming actions, usually involving
/// pin I/O changes
/// The action packet has the following format:
///   1-byte packet type (Action = 0xE8)
///   3-byte destination address
///   1-byte action port
///   1-byte port status
///   2-byte hold for (value) seconds
void app_receive_action(uint8_t *data, uint8_t data_length) {
  uint8_t offset = 0;
  uint32_t src_node_id = 0;
  uint32_t dst_node_id = 0;
  // Process the array and put it in friendly
  // variables
  // Get the 3-byte destination address
  uint8_t packet_type = data[offset];
  uint8_t seq         = data[offset + 4];
  uint8_t payload_len = data[offset + 5];

  if(packet_type != ACTION_PACKET) {
    return;
  }

  // Get the 3-byte src/dst address. In this case, the
  // 'src' address is the source node
  memmove(&src_node_id, (uint8_t *) (data + 1 + offset), 3);
  offset += 6;
  dst_node_id = action_get_dst_id((uint8_t *) (data + offset), data_length);
  offset += 3;
  // Check if the packet is for us
  if(dst_node_id != (uint32_t) NODEID) return;

  // Process payload after the destination ID
  // The action_id is the 1st payload byte
  uint8_t action_id = data[offset];
  // The action port is the 2nd payload byte
  uint8_t action_port = data[offset + 1];
  // port status is the 3rd byte
  uint8_t port_status = data[offset + 2];
  // Move the 2-byte hold-for value (in seconds)
  uint16_t hold_for;
  memmove(&hold_for, (uint8_t *) (data + offset + 3), 2);
  // Append to the action queue
  append_action(action_id, action_port, port_status, hold_for);
  // Some debugging
  sprintf(debug_str, "Action from %lu to %lu", src_node_id, dst_node_id);
  debug(debug_str);
  sprintf(debug_str, "%u,%u,%u,%u", action_id, action_port, port_status, hold_for);
  debug(debug_str);
}

void process_actions(uint32_t elapsed_msec) {
  // Limit elapsed_sec to the max value allowed by an uint16_t
  uint16_t elapsed_sec = ((uint32_t) (elapsed_msec / 1000));
  uint8_t elapsed_overflow = ((uint32_t) (elapsed_msec / 1000)) > ((uint32_t) UINT16_MAX);
  uint8_t index = 0;
  do {
    // Check if the action is valid
    if(!(action_buffer[index].valid)) {
      continue;
    }
    // If there's execution time left, then we update
    // the port status
    if(action_buffer[index].hold_for > 0) {
      sprintf(debug_str, "Exec action %d", action_buffer[index].id);
      debug(debug_str);
      sprintf(debug_str, "P:%u,S:%u", action_buffer[index].port, action_buffer[index].status);
      debug(debug_str);
      action_update_status(&(action_buffer[index]));
    } else {
      action_buffer[index].valid = 0;
    }
    // Update execution time
    if(elapsed_overflow) action_buffer[index].hold_for = 0;
    else {
      // If the action should be held forever
      // then we invalidate it, leaving the last
      // digiWrite as the final state of the port
      if(action_buffer[index].hold_for == HOLD_FOREVER) {
        action_buffer[index].valid = 0;
      }
      if(elapsed_sec >= action_buffer[index].hold_for) {
        action_buffer[index].hold_for = 0;
        action_buffer[index].status = 0;
        action_update_status(&(action_buffer[index]));	
        action_buffer[index].valid = 0;
      } else {
        action_buffer[index].hold_for -= elapsed_sec;
      }
    }
  } while(++index < (uint8_t) MAX_ACTIONS);
  return;
}

static void action_update_status(Action * action) {
  // Write a PWM value to the port if status is anything but 0 or 1
  if(action->status > 1) {
    ports[action->port].anaWrite(action->status);
  } else {
    ports[action->port].digiWrite(action->status);
  }
}

#endif // if defined(ACTION_NODE)

// Get the 3-byte src/dst address. In this case, the
// 'src' address is the source node
uint32_t action_get_dst_id(uint8_t * action_data_payload, uint8_t data_length) {
  if(data_length < 9) return 0;
  uint32_t result = 0;
  memmove((uint32_t *) &result, (uint8_t *) (action_data_payload), 3);
  return result;
}

#if defined(ACTION_MASTER)
// The string on which to store the incoming command
uint8_t command[25];
uint8_t command_len = 0;
extern char debug_str[DEBUG_STR_LEN];
// Process incoming data from the serial port
static void action_process_serial_event(void) {
  // Serial.println((char *) command);
  // Check incoming packet type
  if(command[0] != '#') {
    debug("Bad packet");
    return;
  }
  uint8_t index = 1, comma_index = 1;
  // There should be 5 comma separated values in
  // the incoming string, in the following order:
  // #destination,action_id,port,status,hold_for
  comma_index = arr_indexof(command + index, command_len - index, ',');
  command[index + comma_index] = '\0';
  uint32_t destination = atoi((const char *) (command + index));
  index += comma_index + 1;

  comma_index = arr_indexof(command + index, command_len - index, ',');
  command[index + comma_index] = '\0';
  uint8_t action_id = atoi((const char *) (command + index));
  index += comma_index + 1;

  comma_index = arr_indexof(command + index, command_len - index, ',');
  command[index + comma_index] = '\0';
  uint8_t port = atoi((const char *) (command + index));
  if(port > 4 || port < 1) {
    sprintf(debug_str, "Bad port: %u", port);
    debug(debug_str);
    return;
  }
  index += comma_index + 1;

  comma_index = arr_indexof(command + index, command_len - index, ',');
  command[index + comma_index] = '\0';
  uint8_t status = atoi((const char *) (command + index));
  if(status > 255) {
    sprintf(debug_str, "Bad status: %u", status);
    debug(debug_str);
    return;
  }
  index += comma_index + 1;

  comma_index = arr_indexof(command + index, command_len - index, ',');
  command[index + comma_index] = '\0';
  uint16_t hold_for = atoi((const char *) (command + index));

  uint8_t data[8] = {0,0,0,0,0,0,0,0};

  memmove(data, &destination, 3);
  data[3] = action_id;
  data[4] = port;
  data[5] = status;
  memmove(data + 6, &hold_for, 2);
  network_send(data, 8, ACTION_PACKET);
  sprintf(debug_str, "Sending action %lu,%u,%u,%u,%u", destination, action_id, port, status, hold_for);
  debug(debug_str);
}

void action_usart_process_rx(void) {
  delay(50);
  while(Serial.available()) {
    command[command_len++] = (uint8_t) Serial.read();
  }
  if(command_len >= 8) {
    command[command_len] = '\0';
    action_process_serial_event();
    command_len = 0;
  }
}
#endif
