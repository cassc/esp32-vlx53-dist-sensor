# Distance sensor

Reads distance from a VL53L0X sensor and sends the distance through MQTT when the change of measured distance is greater than 10mm. Used in Cabinet of Curiousities.

## UDP payloads

Sample UDP json playload:


```json
{
  "dist": 80,
  "tpe": "dist",
  "mac": "MACADDR",
  "rssi": -92
}
```



