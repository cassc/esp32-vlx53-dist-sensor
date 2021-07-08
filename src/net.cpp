#include "net.h"

WebServer Server;
AutoConnect    Portal(Server);

String getIp(){
    return String(WiFi.localIP());
}

void rootPage() {
  auto content = String(mac) + "\n" + getIp();
  Server.send(200, "text/plain", content);
}

void startAutoConnect(){
  Server.on("/", rootPage);
  if (Portal.begin()) {
    Serial.println("WiFi connected: " + WiFi.localIP().toString());
  }
}

void setUpNetwork(){
  startAutoConnect();
  mac = WiFi.macAddress();
  mac.replace(":", "");
}
