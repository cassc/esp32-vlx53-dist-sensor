#include <VL53L0X.h>
#include <Wire.h>

#include "mqtt.h"
String mac;

// PINs for the distance sensor
const int GPIO_SDA = 5;
const int GPIO_SCL = 17;

uint16_t dist = 0;
VL53L0X sensor;
const int DIST_READ_INTERVAL_MS = 50;

char mqMsgBuf[128];

void startDistanceSensor(){
  Wire.begin(GPIO_SDA, GPIO_SCL);

  sensor.setTimeout(500);

  if (!sensor.init()) {
    Serial.println("Failed to detect and initialize sensor!");
    while (1) {
    }
  }

  // Start continuous back-to-back mode (take readings as
  // fast as possible).  To use continuous timed mode
  // instead, provide a desired inter-measurement period in
  // ms (e.g. sensor.startContinuous(100)).
  sensor.startContinuous(DIST_READ_INTERVAL_MS);

}

void setup() {
  delay(1000);
  Serial.begin(115200);

  startDistanceSensor();

  setUpNetwork();

  setupMqtt();
}

void loop() {

  // This method is required only if you need to keep AutoConnect portal open
  // after WiFi connection success
  portalLoop();

  auto d = sensor.readRangeContinuousMillimeters();

  if (sensor.timeoutOccurred()) {
    Serial.println("TIMEOUT");
    return;
  }

  if (abs(d - dist) > 10){
    sprintf(mqMsgBuf, "{\"dist\": %d, \"tpe\": \"dist\"}", d);
    publisthMqtt(mqMsgBuf);
  }

  dist = d;

}
