#ifndef __CONFIG_H
#define __CONFIG_H

#define NODEID 1
#define NETWORKID 100

//Opcion de Placa

//#define JEENODE
#define BEENODE

//Opcion de funcionalidad

#define MASTER
//#define MASTER_SENSING
// If defined, the node does not send
// ACKs to the network
// #define LISTEN_ONLY
// #define RELAY
// #define RELAY_SENSING
// #define ENDNODE

//Define to get datalogging behaviour
//#define DATALOGGING

////////////////
//Constantes
//Unidades de 1 ms (15000 milisegundos)
#define SLEEP_TIME 15000LLU
#define SLEEP_TIME_S (SLEEP_TIME/1000)
#define ACTION_TIME 1000LLU
#define ACTION_TIME_S (ACTION_TIME/1000)

//DHT
#define DHT_PORT 0
#define DHT_PIN 4

// Include a PIR, water sensor or
// other interrupt-and-count peripheral
// It is included in the analog values, so in the API
// it should be defined in port 7 (port 4 analog)
#define PIR_PORT 0

//DS18B20
#define DS18B20_PORT 0
#define DS18B20_PIN 4

// When MINIMUM_POWER is defined,
// the LEDs are not turned on, there are
// no radio ACKs.
// #define MINIMUM_POWER

//Action features
#define ACTION
#if defined(ACTION)
  #if defined(MASTER)
    #define ACTION_MASTER
  #else
    #define ACTION_NODE
  #endif
#endif

#if defined(MINIMUM_POWER)
  #if defined(ACTION)
  #error "Cannot define Action and Minimum Power features"
  #endif
  
  #if not defined(ENDNODE)
  #error "Minimum power can only be impleneted in an endnode"
  #endif
#endif

//Digital pins of jeenode
//Port 0 -> Sensor disabled
//Port 1 => A0, D4
//Port 2 => A1, D5
//Port 3 => A2, D6
//Port 4 => A3, D7

#if defined(MASTER)
#define RX_BUFFER_SIZE 13
#define ROUTING_TABLE_SIZE 15
#endif

#if defined(RELAY) or defined(ACTION_NODE)
#define RX_BUFFER_SIZE 13
#define ROUTING_TABLE_SIZE 15
#endif

#ifdef ENDNODE
#define RX_BUFFER_SIZE 0
#define ROUTING_TABLE_SIZE 0
#endif


#ifdef BEENODE
#define ACTIVITY_LED 9
#define BATTERY_PIN 6
#endif

#ifdef JEENODE
#define ACTIVITY_LED 6
#define BATTERY_PIN 5
#endif

// For serial gateway functionality
#define SERIAL_IDLE      0x01
#define SERIAL_RECEIVING 0x02
#define SERIAL_AVAILABLE 0x04
#define URX_BUFFER_SIZE 50

#define DEBUG_STR_LEN 50

#if defined(ACTION_MASTER)
#define USE_SERIAL_PORT_INPUT
#endif

#endif
