#include <VL53L1X.h>
#include <Wire.h>

#include "mqtt.h"
String mac;

// PINs for the distance sensor
const int GPIO_SCL = 17;
const int GPIO_SDA = 5;

const bool ENABLE_NET = false;

uint16_t dist = 0;
VL53L1X sensor;
const int DIST_READ_INTERVAL_MS = 50;

char mqMsgBuf[128];

void startDistanceSensor()
{
  Wire.begin(GPIO_SDA, GPIO_SCL);

  sensor.setTimeout(500);

  while (!sensor.init())
  {
    Serial.println("Failed to detect and initialize sensor!");
    delay(500);
  }

  // Configuration to increase max measure range
  // increase range, lower accuracy
/*   sensor.setSignalRateLimit(0.1);
  // increase range
  sensor.setVcselPulsePeriod(VL53L0X::VcselPeriodPreRange, 18);
  sensor.setVcselPulsePeriod(VL53L0X::VcselPeriodFinalRange, 14);
  // increase measurement speed
  sensor.setMeasurementTimingBudget(20000);
 */
  sensor.startContinuous(DIST_READ_INTERVAL_MS);
}

void setup()
{
  delay(1000);
  Serial.begin(115200);

  startDistanceSensor();

  if (ENABLE_NET){
    setUpNetwork();
    setupMqtt();
  }

}

void loop()
{
  if (ENABLE_NET){
    portalLoop();
  }

  auto d = sensor.readRangeContinuousMillimeters();

  if (sensor.timeoutOccurred())
  {
    Serial.println("TIMEOUT");
    return;
  }

  if (abs(d-dist) > 5)
  {
    sprintf(mqMsgBuf, "{\"dist\": %d, \"tpe\": \"dist\"}", d);
    Serial.println(mqMsgBuf);
    if (ENABLE_NET){
      publisthMqtt(mqMsgBuf);
    }
    dist = d;
  }

}
