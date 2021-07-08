#include "net.h"
AutoConnect portal;
AutoConnectConfig config("make_tof", "12345678");

String getIp()
{
    return WiFi.localIP().toString();
}

void startAutoConnect()
{
    // Allow config after AP configuration
    config.retainPortal = true;

#ifdef E32_USE_STATIC_IP
    config.staip = E32_STATIC_IP;
    config.staGateway = E32_STATIC_GATEWAY;
    config.staNetmask = E32_STATIC_MASK;
    config.dns1 = E32_STATIC_DNS;
#endif

    config.autoReconnect = true;
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
