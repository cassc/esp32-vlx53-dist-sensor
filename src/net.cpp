#include "net.h"
WebServer server;
AutoConnect portal(server);
AutoConnectAux hello;
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
    config.ota = AC_OTA_BUILTIN;
    // Allow config after AP configuration
    config.retainPortal = true;
    hello.load(HELLO_PAGE);
#ifdef E32_USE_STATIC_IP
    config.staip = E32_STATIC_IP;
    config.staGateway = E32_STATIC_GATEWAY;
    config.staNetmask = E32_STATIC_MASK;
    config.dns1 = E32_STATIC_DNS;
#endif

    config.autoReconnect = true;

    // portal.join({hello});
    portal.config(config);

    if (portal.begin())
    {
        Serial.println("WiFi connected: " + WiFi.localIP().toString());
    }
}

void setUpNetwork()
{

    startAutoConnect();
    mac = WiFi.macAddress();
    mac.replace(":", "");
}

void portalLoop()
{
    portal.handleClient();
}
