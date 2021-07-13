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

bool useAutoConnect = false;

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
    if (E32_USE_STATIC_IP)
    {
        config.staip = E32_STATIC_IP;
        config.staGateway = E32_STATIC_GATEWAY;
        config.staNetmask = E32_STATIC_MASK;
        config.dns1 = E32_STATIC_DNS;
    }

    config.autoReconnect = true;

    // portal.join({hello});
    portal.config(config);

    bool success = false;
    if (USE_DEFAULT_WIFI){
        success = portal.begin(DEFAULT_SSID, DEFAULT_PASS, DEFAULT_WIFI_TIMEOUT_MS);
    }else{
        success = portal.begin();
    }

    if (success)
    {
        Serial.println("WiFi connected: " + getIp());
    }
}

void setUpNetwork()
{
    mac = WiFi.macAddress();
    mac.replace(":", "");

    Serial.println("Connecting WiFi ...");
    Serial.printf("MAC: %s\r\n", mac.c_str());

    auto connected = false;
    /* if (USE_DEFAULT_WIFI)
    {
        if (E32_USE_STATIC_IP)
        {
            WiFi.config(E32_STATIC_IP, E32_STATIC_GATEWAY, E32_STATIC_MASK, E32_STATIC_DNS);
        }

        WiFi.begin(DEFAULT_SSID, DEFAULT_PASS);
        long timeout = DEFAULT_WIFI_TIMEOUT_MS;
        while (WiFi.status() != WL_CONNECTED)
        {
            delay(500);
            Serial.print(".");
            timeout -= 500;
            if (timeout < 0){
                break;
            }
        }

        connected = WiFi.status() == WL_CONNECTED;
    } */

    if (!connected)
    {
        useAutoConnect = true;
        WiFi.disconnect();
        startAutoConnect();
    }
    else
    {
        Serial.println("Connected to default WiFI!");
        Serial.println("WiFi connected: " + getIp());
    }
}

void portalLoop()
{
    portal.handleClient();
}
