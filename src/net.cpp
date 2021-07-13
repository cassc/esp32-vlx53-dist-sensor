#include "net.h"

WebServer server;
AutoConnect portal(server);
AutoConnectAux hello;
AutoConnectUpdate update("10.0.0.3", 8020);
AutoConnectConfig config("make_tof", "12345678");

static const char HELLO_PAGE[] PROGMEM = R"(
{ "title": "Hello world", "uri": "/", "menu": true, "element": [
    { "name": "caption", "type": "ACText", "value": "<h2>Hello, world</h2>",  "style": "text-align:center;color:#2f4f4f;padding:10px;" },
    { "name": "content", "type": "ACText", "value": "In this page, place the custom web page handled by the Sketch application." } ]
}
)";

String getIp()
{
    return WiFi.localIP().toString();
}

void startAutoConnect()
{
    config.ota = AC_OTA_BUILTIN; // Enable OTA through local browser
    config.retainPortal = true;
    config.autoReconnect = true;
    config.autoSave = AC_SAVECREDENTIAL_AUTO;
    hello.load(HELLO_PAGE);
    if (E32_USE_STATIC_IP)
    {
        config.staip = E32_STATIC_IP;
        config.staGateway = E32_STATIC_GATEWAY;
        config.staNetmask = E32_STATIC_MASK;
        config.dns1 = E32_STATIC_DNS;
    }

    // portal.join({hello});
    portal.config(config);

    if (portal.begin())
    {
        Serial.println("WiFi connected: " + getIp());
        // update.attach(portal); // OTA through AutoConnect server
    }
    else
    {
        Serial.println("FATAL: AutoConnect failed!!");
    }
}

void setUpNetwork()
{
    mac = WiFi.macAddress();
    mac.replace(":", "");

    Serial.println("Connecting WiFi ...");
    Serial.printf("MAC: %s\r\n", mac.c_str());
    Serial.printf("VERSION: %d\r\n", VERSION);

    startAutoConnect();
}

void portalLoop()
{
    portal.handleClient();
}
