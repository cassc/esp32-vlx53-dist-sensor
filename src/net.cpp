#include "net.h"


WiFiUDP udp;
char udpInBuf[64];


String getIp()
{
    return WiFi.localIP().toString();
}


void startWifi(){
    WiFi.mode(WIFI_AP_STA);
    WiFi.begin("cocwifi", "M@k3Pl@ysc@p3");

    auto startTs = millis();
    while (WiFi.status() != WL_CONNECTED) {
      Serial.print('.');
      delay(1000);
      if (millis() - startTs > 30000){
        Serial.println("Failed to connect to wifi, restart now");
        ESP.restart();
      }
    }
}

void setUpNetwork()
{
    mac = WiFi.macAddress();
    mac.replace(":", "");

    Serial.println("Connecting WiFi ...");
    Serial.printf("MAC: %s\r\n", mac.c_str());
    Serial.printf("VERSION: %d\r\n", VERSION);

    // startAutoConnect();
    startWifi();
}



int sendUDP(const char *msg)
{
    Serial.printf("UDP Send: %s\r\n", msg);
    if (udp.beginPacket(UDP_HOST, UDP_PORT) && udp.println(msg))
    {
        return udp.endPacket();
    }
    return 0;
}

int handleUDPReply()
{
    if (!udp.parsePacket())
    {
        return 0;
    }

    auto len = udp.read(udpInBuf, 64);
    if (len > 0)
    {
        udpInBuf[len] = '\0';
    }

    auto dist = String(udpInBuf).toInt();
    setMinDist(dist);

    return 1;
}

void setMinDist(long dist)
{
    Serial.println(String("Setting min dist: ") + dist);
    if (dist)
    {
        min_dist = dist;
    }
    else
    {
        Serial.println(String("Ignore min dist setting: ") + dist);
    }
}
