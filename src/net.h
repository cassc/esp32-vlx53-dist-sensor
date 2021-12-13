#ifndef __E32_VLX_NET__
#define __E32_VLX_NET__
#include <WiFi.h>

#define VERSION 2021213


#define UDP_PORT 5252
#define UDP_HOST "10.0.0.231"

extern String mac;
extern long min_dist;
void setUpNetwork();
String getIp();


int sendUDP(const char* msg);
void setMinDist(long d);
// Handle UDP message, returns 0 if no message received
int handleUDPReply();


#endif
