# Distance sensor

Reads distance from a VL53L0X sensor and sends the distance through MQTT when the change of measured distance is greater than 10mm. Used in Cabinet of Curiousities.

## MQTT topic and MQTT/UDP payloads

**When using UDP only the payload is sent to the server.**

* `tof` when device first connects to MQTT, it sends the following payload to this topic:


```json
{
  "ip": "10.0.2.129",
  "mac": "98F4AB6BD460",
  "tpe": "start"
}
```

* `tof/{MAC_ADDRESS}`, for example `tof/98F4AB6BD460`, for broadcasting distance data:

```json
{
  "dist": 80,
  "tpe": "dist"
}
```



