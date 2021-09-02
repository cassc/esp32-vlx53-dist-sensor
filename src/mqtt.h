#ifndef __E32_VLX_MQTT__
#define __E32_VLX_MQTT__

extern "C" {
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"
}
#include <WiFi.h>
#include <AsyncMqttClient.h>
#include "net.h"

#define MQTT_HOST IPAddress(10, 0, 0, 78)
#define MQTT_PORT 1883

void setupMqtt();
int publisthMqtt(const char* payload);
bool isMqttConnected();


#endif
