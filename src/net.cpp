#include "net.h"

WebServer Server;
AutoConnect    Portal(Server);


void rootPage() {
  char content[] = "Hello, world";
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
