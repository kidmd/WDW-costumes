#include <Arduino.h>
#include <FastLED.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <esp_now.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

#if __has_include("wifi_config.h")
#include "wifi_config.h"
#endif

// ============================================================================
// HARDWARE & PIN DEFINITIONS
// ============================================================================
#define DATA_PIN            16      // 8th pin down on the right
#define LED_TYPE            WS2812B
#ifndef COLOR_ORDER
#define COLOR_ORDER         RGB     // Calibrated hardware color order (Red, Green, Blue)
#endif
#define STATUS_LED_PIN      2       // Onboard Blue LED

#define PARADE_NUM_LEDS     50      // Standard parade float strand count
#define MAX_LEDS_CAPACITY   120     // Buffer capacity for custom 100-LED simulator designs
#define MAX_BRIGHTNESS      60      // Bench/wearable safe brightness
#define MAX_MILLIAMPS       1200    // 1.2A power bank / wall charger limit

CRGB leds[MAX_LEDS_CAPACITY];

// ============================================================================
// WI-FI & UDP LIVE STREAMING STATE
// ============================================================================
WiFiUDP udp;
bool isLiveStreaming = false;
uint32_t lastStreamPacketTime = 0;

#ifndef UDP_STREAM_PORT
#define UDP_STREAM_PORT 4210
#endif

// ============================================================================
// KNOWN MAC ADDRESSES FOR THE FLEET (Milestone 2)
// ============================================================================
const char* MAC_LEADER_FLOAT1   = "B0:CB:D8:C8:49:84"; // Board 1: Title Drum (Leader)
const char* MAC_FOLLOWER_FLOAT2 = "A4:F0:0F:64:33:A0"; // Board 2: Casey Jr. Train (Follower)

struct __attribute__((packed)) ParadeSyncPacket {
    uint8_t  magic;          // 0xEE verification byte
    uint8_t  mode;           // 0: Marquee, 1: Sparkle, 2: Twinkle, 3: Traveling Wave
    uint32_t masterMillis;   // Synchronized timebase (ms)
    uint8_t  activeFloat;    // For traveling wave (1 = Float 1, 2 = Float 2)
    uint8_t  waveHead;       // 0-49 pixel position of traveling wave
};

ParadeSyncPacket currentPacket;
bool isLeader = false;
uint8_t myFloatNumber = 2;

volatile bool packetReceived = false;
uint32_t lastPacketTime = 0;
uint32_t localSyncTime = 0;
uint32_t lastLocalTick = 0;

uint8_t broadcastMac[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

// ============================================================================
// ESP-NOW RECEIVE CALLBACK (Follower)
// ============================================================================
void onDataReceive(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
    if (len == sizeof(ParadeSyncPacket)) {
        ParadeSyncPacket packet;
        memcpy(&packet, incomingData, sizeof(packet));
        if (packet.magic == 0xEE) {
            currentPacket = packet;
            packetReceived = true;
            lastPacketTime = millis();
            localSyncTime = packet.masterMillis;
            lastLocalTick = millis();
        }
    }
}

// ============================================================================
// PARADE LIGHTING ANIMATIONS (Default Mode)
// ============================================================================
void renderMarqueeChase(uint32_t t) {
    uint8_t offset = (t / 110) % 3;
    for (int i = 0; i < PARADE_NUM_LEDS; i++) {
        if ((i + offset) % 3 == 0) {
            leds[i] = CRGB(255, 147, 41); // Incandescent amber/gold
        } else {
            leds[i] = CRGB::Black;
        }
    }
}

void renderParadeSparkle(uint32_t t) {
    static const CRGB paletteDrum[] = {
        CRGB(255, 160, 20), CRGB(255, 230, 180), CRGB(255, 120, 10)
    };
    static const CRGB paletteCasey[] = {
        CRGB(255, 25, 0), CRGB(255, 230, 180), CRGB(0, 190, 255)
    };

    uint8_t step = (t / 180) % 3;
    for (int i = 0; i < PARADE_NUM_LEDS; i++) {
        if (myFloatNumber == 1) {
            leds[i] = paletteDrum[(i + step) % 3];
        } else {
            leds[i] = paletteCasey[(i + step) % 3];
        }
    }
}

void renderTwinkle(uint32_t t) {
    fill_solid(leds, PARADE_NUM_LEDS, CRGB(20, 10, 2));
    uint16_t seed = (t / 35) + (myFloatNumber * 100);
    if ((seed % 7) == 0) {
        int pos = (seed * 13) % PARADE_NUM_LEDS;
        leds[pos] = CRGB(255, 220, 160);
    }
}

void renderTravelingWave(uint8_t activeFloat, uint8_t waveHead) {
    fill_solid(leds, PARADE_NUM_LEDS, CRGB(15, 8, 2));
    if (myFloatNumber == activeFloat) {
        int head = waveHead;
        if (head >= 0 && head < PARADE_NUM_LEDS) {
            leds[head] = CRGB(255, 255, 255);
            if (head > 0) leds[head - 1] = CRGB(255, 180, 40);
            if (head > 1) leds[head - 2] = CRGB(200, 80, 10);
            if (head < PARADE_NUM_LEDS - 1) leds[head + 1] = CRGB(255, 180, 40);
            if (head < PARADE_NUM_LEDS - 2) leds[head + 2] = CRGB(200, 80, 10);
        }
    }
}

// ============================================================================
// PARADE FLEET LOOP (Autonomous / ESP-NOW)
// ============================================================================
void runFleetSync(uint32_t now) {
    if (isLeader) {
        static uint32_t lastBroadcast = 0;
        uint32_t cycleTime = now % 48000;
        uint8_t mode = cycleTime / 12000;

        uint8_t waveActiveFloat = 1;
        uint8_t waveHeadPos = 0;
        if (mode == 3) {
            uint32_t waveTimer = now % 3000;
            if (waveTimer < 1500) {
                waveActiveFloat = 1;
                waveHeadPos = map(waveTimer, 0, 1500, 0, PARADE_NUM_LEDS - 1);
            } else {
                waveActiveFloat = 2;
                waveHeadPos = map(waveTimer - 1500, 0, 1500, 0, PARADE_NUM_LEDS - 1);
            }
        }

        // Broadcast ESP-NOW packet at 25 Hz
        if (now - lastBroadcast >= 40) {
            lastBroadcast = now;
            ParadeSyncPacket packet;
            packet.magic = 0xEE;
            packet.mode = mode;
            packet.masterMillis = now;
            packet.activeFloat = waveActiveFloat;
            packet.waveHead = waveHeadPos;
            esp_now_send(broadcastMac, (uint8_t *)&packet, sizeof(packet));
        }

        switch (mode) {
            case 0: renderMarqueeChase(now); break;
            case 1: renderParadeSparkle(now); break;
            case 2: renderTwinkle(now); break;
            case 3: renderTravelingWave(waveActiveFloat, waveHeadPos); break;
        }

        // Heartbeat LED (1 Hz)
        digitalWrite(STATUS_LED_PIN, (now / 500) % 2);

    } else {
        // Follower Node
        bool isConnected = (now - lastPacketTime < 2500);
        localSyncTime += (now - lastLocalTick);
        lastLocalTick = now;

        uint8_t mode = isConnected ? currentPacket.mode : ((now / 10000) % 4);
        uint32_t activeTime = isConnected ? localSyncTime : now;

        switch (mode) {
            case 0: renderMarqueeChase(activeTime); break;
            case 1: renderParadeSparkle(activeTime); break;
            case 2: renderTwinkle(activeTime); break;
            case 3: 
                if (isConnected) {
                    renderTravelingWave(currentPacket.activeFloat, currentPacket.waveHead);
                } else {
                    renderMarqueeChase(now);
                }
                break;
        }

        if (isConnected) {
            digitalWrite(STATUS_LED_PIN, HIGH);
        } else {
            digitalWrite(STATUS_LED_PIN, (now / 150) % 2);
        }
    }

    // Clear any extra LEDs beyond 50
    for (int i = PARADE_NUM_LEDS; i < MAX_LEDS_CAPACITY; i++) {
        leds[i] = CRGB::Black;
    }

    FastLED.show();
    delay(15);
}

// ============================================================================
// MAIN SETUP
// ============================================================================
void setup() {
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable transient brownout detector during startup
    Serial.begin(115200);
    pinMode(STATUS_LED_PIN, OUTPUT);
    delay(300);

    Serial.println("\n========================================================");
    Serial.println("  MAIN STREET ELECTRICAL PARADE - UNIFIED FIRMWARE");
    Serial.println("  (Auto: ESP-NOW Fleet Sync + Real-Time Wi-Fi Streaming)");
    Serial.println("========================================================");

    // 1. Initialize Wi-Fi in Station Mode
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(100);

    // Optional: Connect to Home Wi-Fi if credentials are configured
#if defined(WIFI_SSID)
    String ssid = WIFI_SSID;
    if (ssid.length() > 0 && ssid != "YourWiFiNetwork") {
        Serial.printf("[WIFI] Connecting to Home Wi-Fi '%s'...\n", WIFI_SSID);
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        uint32_t t0 = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - t0 < 3500) {
            delay(100);
            Serial.print(".");
            digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
        }
        Serial.println();
    }
#endif

    if (WiFi.status() == WL_CONNECTED) {
        Serial.print("[WIFI] Connected! IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("[WIFI] Running in direct offline mode (ESP-NOW + Local Broadcast ready).");
#if defined(AP_SSID)
        // Also enable SoftAP so laptops can connect directly without home router
        WiFi.mode(WIFI_AP_STA);
        WiFi.softAP(AP_SSID, AP_PASSWORD);
        Serial.printf("[WIFI] Standalone Hotspot Active: '%s' (IP: %s)\n", AP_SSID, WiFi.softAPIP().toString().c_str());
#endif
    }

    // 2. Start UDP Stream Listener (Port 4210)
    udp.begin(UDP_STREAM_PORT);
    Serial.printf("[UDP] Listening for simulator streaming packets on port %d\n", UDP_STREAM_PORT);

    // 3. Initialize ESP-NOW Peer-to-Peer
    String myMac = WiFi.macAddress();
    Serial.printf("[INFO] My MAC Address: %s\n", myMac.c_str());

    if (myMac.equalsIgnoreCase(MAC_LEADER_FLOAT1)) {
        isLeader = true;
        myFloatNumber = 1;
        Serial.println("[ROLE] *** LEADER (Float 1 - Title Drum) ***");
    } else if (myMac.equalsIgnoreCase(MAC_FOLLOWER_FLOAT2)) {
        isLeader = false;
        myFloatNumber = 2;
        Serial.println("[ROLE] >>> FOLLOWER (Float 2 - Casey Jr.) <<<");
    } else {
        isLeader = false;
        myFloatNumber = 2;
        Serial.println("[ROLE] Unregistered MAC - Defaulting to Follower (Float 2)");
    }

    if (esp_now_init() != ESP_OK) {
        Serial.println("[ERROR] ESP-NOW initialization failed!");
    } else {
        Serial.println("[INFO] ESP-NOW Initialized successfully.");
        if (isLeader) {
            esp_now_peer_info_t peerInfo = {};
            memcpy(peerInfo.peer_addr, broadcastMac, 6);
            peerInfo.channel = 0;
            peerInfo.encrypt = false;
            if (esp_now_add_peer(&peerInfo) == ESP_OK) {
                Serial.println("[INFO] ESP-NOW Broadcast peer registered.");
            }
        } else {
            esp_now_register_recv_cb(onDataReceive);
            Serial.println("[INFO] ESP-NOW Receive callback registered. Listening for Leader...");
        }
    }

    // 4. Initialize FastLED
    FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, MAX_LEDS_CAPACITY)
           .setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(MAX_BRIGHTNESS);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_MILLIAMPS);

    Serial.println("[INFO] Setup complete! Starting default parade loop...\n");
}

// ============================================================================
// MAIN LOOP: AUTO-SWITCHES BETWEEN SIMULATOR STREAM & ESP-NOW PARADE FLEET
// ============================================================================
void loop() {
    uint32_t now = millis();

    // 1. Check for incoming live stream packets from Python Simulator
    int packetSize = udp.parsePacket();
    if (packetSize > 0) {
        uint8_t buffer[512];
        int len = udp.read(buffer, sizeof(buffer));
        if (len >= 7 && 
            buffer[0] == 'M' && buffer[1] == 'S' && buffer[2] == 'E' && buffer[3] == 'P' &&
            buffer[4] == 0x01) {
            
            uint16_t frameLeds = (buffer[5] << 8) | buffer[6];
            int ledsToUpdate = min((int)frameLeds, (int)MAX_LEDS_CAPACITY);
            
            int pIdx = 7;
            for (int i = 0; i < ledsToUpdate && (pIdx + 2) < len; i++) {
                leds[i].r = buffer[pIdx++];
                leds[i].g = buffer[pIdx++];
                leds[i].b = buffer[pIdx++];
            }
            
            for (int i = ledsToUpdate; i < MAX_LEDS_CAPACITY; i++) {
                leds[i] = CRGB::Black;
            }
            
            FastLED.show();
            lastStreamPacketTime = now;
            isLiveStreaming = true;
            digitalWrite(STATUS_LED_PIN, HIGH); // Solid blue during active stream
            return; // Stay in live streaming mode!
        }
    }

    // 2. Check if live stream recently ended (> 2.5 seconds timeout)
    if (isLiveStreaming && (now - lastStreamPacketTime > 2500)) {
        isLiveStreaming = false;
        Serial.println("[MODE] Live stream ended. Resuming ESP-NOW Parade Fleet sync.");
    }

    // 3. If simulator is NOT streaming, run the synchronized ESP-NOW parade loop!
    if (!isLiveStreaming) {
        runFleetSync(now);
    }
}
