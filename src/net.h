#ifndef __E32_VLX_NET__
#define __E32_VLX_NET__
#include <WiFi.h>
#include <WebServer.h>
#include <AutoConnect.h>

#define VERSION 20210713

////////////////////////////////////////////////////////////////////////////////
// Configure default WiFi.
#define USE_DEFAULT_WIFI 1
/* #define DEFAULT_SSID "playscape"
#define DEFAULT_PASS "makeplayscape" */
#define DEFAULT_SSID "MAKE"
#define DEFAULT_PASS "wemakedigital"
#define DEFAULT_WIFI_TIMEOUT_MS 5000
////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////
// Configure static IP
#define E32_USE_STATIC_IP 0
#define E32_STATIC_IP IPAddress(10,0,2,133)
#define E32_STATIC_GATEWAY IPAddress(10,0,2,1)
#define E32_STATIC_MASK IPAddress(255,255,255,0)
#define E32_STATIC_DNS IPAddress(10,0,2,1)
////////////////////////////////////////////////////////////////////////////////

extern String mac;
void setUpNetwork();
String getIp();
void portalLoop();

#endif
