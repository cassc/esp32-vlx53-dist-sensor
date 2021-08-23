// Set to 0 to use VL53L0 sensor
#define USE_SENSOR_L0 1

// Set to 1 to increase L0 sensor max detection distance
#define L0_SENSOR_ENHANCE 0

#if USE_SENSOR_L0
#include <VL53L0X.h>
#else
#include <VL53L1X.h>
#endif
#include <Wire.h>

#include "mqtt.h"
String mac;

// Minimum distance change (mm) to send data by MQTT
const int MIN_DIST_CHANGE_TO_SEND_DATA = 1;

// PINs for the distance sensor
const int GPIO_SDA = 5;
const int GPIO_SCL = 17;

// PINs for LEDs
const int LED_NET = 22;
const int LED_MQ = 19;
const int LED_DATA = 23;

uint16_t dist = 0;
#if USE_SENSOR_L0
VL53L0X sensor;
#else
VL53L1X sensor;
#endif

const int DIST_READ_INTERVAL_MS = 50;

char mqMsgBuf[128];

void startDistanceSensor()
{
  Wire.begin(GPIO_SDA, GPIO_SCL);

  sensor.setTimeout(500);

  while (!sensor.init())
  {
    Serial.println("Failed to detect and initialize sensor!");
    Serial.println("Please check you are using VLX53L0X!");
    delay(2000);
  }

#if USE_SENSOR_L0 && L0_SENSOR_ENHANCE
  // Configuration to increase max measure range
  // increase range, lower accuracy
  sensor.setSignalRateLimit(0.1);
  // increase range
  sensor.setVcselPulsePeriod(VL53L0X::VcselPeriodPreRange, 18);
  sensor.setVcselPulsePeriod(VL53L0X::VcselPeriodFinalRange, 14);
  // increase measurement speed
  sensor.setMeasurementTimingBudget(20000);
#endif

  sensor.startContinuous(DIST_READ_INTERVAL_MS);
}

// Setup led pins
void setupPins()
{
  auto pins = {LED_MQ, LED_NET, LED_DATA};

  for (auto pin : pins)
  {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
}

void setup()
{
  delay(1000);
  Serial.begin(115200);

  setupPins();

  startDistanceSensor();

  setUpNetwork();

  setupMqtt();
}

void loop()
{

  byte hasWifi = WiFi.isConnected();
  byte hasMqtt = hasWifi && isMqttConnected();

  digitalWrite(LED_NET, hasWifi);
  digitalWrite(LED_MQ, hasMqtt);

  portalLoop();

  auto d = sensor.readRangeContinuousMillimeters();

  if (sensor.timeoutOccurred())
  {
    Serial.println("TIMEOUT");
    return;
  }

  if (d != dist)
  {
    digitalWrite(LED_DATA, HIGH);
    if (hasMqtt && (abs(d - dist) > MIN_DIST_CHANGE_TO_SEND_DATA))
    {
      sprintf(mqMsgBuf, "{\"dist\": %d, \"tpe\": \"dist\"}", d);
      publisthMqtt(mqMsgBuf);
    }
  }
  else
  {
    digitalWrite(LED_DATA, LOW);
  }

  dist = d;
}
