#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <Arduino.h>

// Enter your home Wi-Fi credentials here (or leave blank for standalone mode)
#define WIFI_SSID       "YourWiFiNetwork"
#define WIFI_PASSWORD   "YourPassword"
#define UDP_STREAM_PORT 4210
#define AP_SSID         "MSEP-Costume-AP"
#define AP_PASSWORD     "msep1234"

#define MSEP_MAGIC_0    'M'
#define MSEP_MAGIC_1    'S'
#define MSEP_MAGIC_2    'E'
#define MSEP_MAGIC_3    'P'
#define MSEP_OPCODE_LIVE_FRAME  0x01
#define MSEP_OPCODE_HEARTBEAT   0x02

#endif // WIFI_CONFIG_H
