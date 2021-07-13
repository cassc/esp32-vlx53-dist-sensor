# Distance sensor


Reads distance from a VL53L0X sensor and sends the distance through MQTT when the change of measured distance is greater than 10mm.

## MQTT topic and payloads

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

## Reset WiFi connection

Open `http://[IP]/_ac` in browser.


## Configure WiFi without manually typing
First connect to ESP AP using PC, then send the following command, replacing
`SSID` and `PASSWORD` with the target WiFi credentials:

```bash
curl -v --data-binary "SSID=[SSID]&Passphrase=[PASSWORD]&dhcp=en&apply=Apply"  http://172.217.28.1/_ac/connect
# Example
curl -v --data-binary "SSID=MAKE&Passphrase=wemakedigital&dhcp=en&apply=Apply"  http://172.217.28.1/_ac/connect
```

You can also configure static IP at the same time:

```bash
curl -v --data-binary "SSID=MAKE&Passphrase=wemakedigital&sip=10.0.2.133&gw=10.0.2.1&nm=255.255.255.0&ns1=10.0.2.1&ns2=8.8.8.8&apply=Apply" http://172.217.28.1/_ac/connect
```
