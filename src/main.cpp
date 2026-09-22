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

#if __has_include("costume_config.h")
#include "costume_config.h"
#endif

// ============================================================================
// MODE SELECTION:
// 1 = Wi-Fi UDP Live Stream Mode (Real-Time Simulator Tethering)
// 0 = Standalone ESP-NOW Fleet Synchronization Mode (MSEP Race Day)
// ============================================================================
#ifndef ENABLE_WIFI_LIVE_STREAM
#define ENABLE_WIFI_LIVE_STREAM 1
#endif

// ============================================================================
// HARDWARE & PIN DEFINITIONS
// ============================================================================
#define DATA_PIN        16      // 8th pin down on the right
#define LED_TYPE        WS2812B
#ifndef COLOR_ORDER
#define COLOR_ORDER     RGB     // Calibrated hardware color order (Red, Green, Blue)
#endif
#define STATUS_LED_PIN  2       // Onboard Blue LED

#define MAX_LEDS_CAPACITY 120
CRGB leds[MAX_LEDS_CAPACITY];

#if ENABLE_WIFI_LIVE_STREAM == 1

// ============================================================================
// 📡 WI-FI UDP LIVE STREAM RECEIVER MODE
// ============================================================================
WiFiUDP udp;
uint32_t lastPacketReceived = 0;
bool isReceivingStream = false;

void setupWifiReceiver() {
    Serial.println("\n========================================================");
    Serial.println("  MAIN STREET ELECTRICAL PARADE - WI-FI LIVE RECEIVER");
    Serial.println("========================================================");

    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(100);

    bool connected = false;
    String ssid = WIFI_SSID;
    if (ssid.length() > 0 && ssid != "YourWiFiNetwork") {
        Serial.printf("[WIFI] Connecting to Home Wi-Fi '%s'...\n", WIFI_SSID);
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        uint32_t startAttempt = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < 8000) {
            delay(250);
            Serial.print(".");
            digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
        }
        Serial.println();
        if (WiFi.status() == WL_CONNECTED) {
            connected = true;
            Serial.print("[WIFI] Connected! IP Address: ");
            Serial.println(WiFi.localIP());
        } else {
            Serial.println("[WIFI] Connection timed out. Launching fallback SoftAP...");
        }
    }

    if (!connected) {
        WiFi.mode(WIFI_AP);
        WiFi.softAP(AP_SSID, AP_PASSWORD);
        Serial.printf("[WIFI] SoftAP Active! SSID: '%s', Password: '%s'\n", AP_SSID, AP_PASSWORD);
        Serial.print("[WIFI] AP IP Address: ");
        Serial.println(WiFi.softAPIP());
    }

    udp.begin(UDP_STREAM_PORT);
    Serial.printf("[UDP] Listening for pixel packets on port %d\n", UDP_STREAM_PORT);

    FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, MAX_LEDS_CAPACITY)
           .setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(65);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, 1200); // 1.2A safety ceiling

    // Startup flash indicator (quick green blink)
    for (int i = 0; i < 5; i++) leds[i] = CRGB(0, 255, 0);
    FastLED.show();
    delay(200);
    FastLED.clear();
    FastLED.show();
}

void loopWifiReceiver() {
    uint32_t now = millis();
    int packetSize = udp.parsePacket();
    if (packetSize > 0) {
        uint8_t buffer[512];
        int len = udp.read(buffer, sizeof(buffer));
        if (len >= 7 && 
            buffer[0] == MSEP_MAGIC_0 && 
            buffer[1] == MSEP_MAGIC_1 && 
            buffer[2] == MSEP_MAGIC_2 && 
            buffer[3] == MSEP_MAGIC_3) {
            
            uint8_t opcode = buffer[4];
            if (opcode == MSEP_OPCODE_LIVE_FRAME) {
                uint16_t frameLeds = (buffer[5] << 8) | buffer[6];
                int ledsToUpdate = min((int)frameLeds, (int)MAX_LEDS_CAPACITY);
                
                int pIdx = 7;
                for (int i = 0; i < ledsToUpdate && (pIdx + 2) < len; i++) {
                    leds[i].r = buffer[pIdx++];
                    leds[i].g = buffer[pIdx++];
                    leds[i].b = buffer[pIdx++];
                }
                
                // Clear any remaining unaddressed LEDs
                for (int i = ledsToUpdate; i < MAX_LEDS_CAPACITY; i++) {
                    leds[i] = CRGB::Black;
                }
                
                FastLED.show();
                lastPacketReceived = now;
                isReceivingStream = true;
                digitalWrite(STATUS_LED_PIN, HIGH); // Solid blue when actively streaming
            }
        }
    }

    // Standby Mode: If no packets received for > 3.0 seconds, gently breathe amber on first 5 LEDs
    if (now - lastPacketReceived > 3000) {
        isReceivingStream = false;
        uint8_t breath = beatsin8(15, 20, 100);
        for (int i = 0; i < 5; i++) {
            leds[i] = CRGB(breath, breath * 0.6, 0);
        }
        for (int i = 5; i < MAX_LEDS_CAPACITY; i++) {
            leds[i] = CRGB::Black;
        }
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, (now / 500) % 2); // Slow 1 Hz heartbeat
    }
}

#else

// ============================================================================
// 🏆 STANDALONE ESP-NOW FLEET SYNCHRONIZATION MODE (MSEP Race Day)
// ============================================================================
#define NUM_LEDS        50
#define MAX_BRIGHTNESS  45
#define MAX_MILLIAMPS   800

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

void renderMarqueeChase(uint32_t t) {
    uint8_t offset = (t / 110) % 3;
    for (int i = 0; i < NUM_LEDS; i++) {
        if ((i + offset) % 3 == 0) {
            leds[i] = CRGB(255, 147, 41);
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
    for (int i = 0; i < NUM_LEDS; i++) {
        if (myFloatNumber == 1) {
            leds[i] = paletteDrum[(i + step) % 3];
        } else {
            leds[i] = paletteCasey[(i + step) % 3];
        }
    }
}

void renderTwinkle(uint32_t t) {
    fill_solid(leds, NUM_LEDS, CRGB(20, 10, 2));
    uint16_t seed = (t / 35) + (myFloatNumber * 100);
    if ((seed % 7) == 0) {
        int pos = (seed * 13) % NUM_LEDS;
        leds[pos] = CRGB(255, 220, 160);
    }
}

void renderTravelingWave(uint8_t activeFloat, uint8_t waveHead) {
    fill_solid(leds, NUM_LEDS, CRGB(15, 8, 2));
    if (myFloatNumber == activeFloat) {
        int head = waveHead;
        if (head >= 0 && head < NUM_LEDS) {
            leds[head] = CRGB(255, 255, 255);
            if (head > 0) leds[head - 1] = CRGB(255, 180, 40);
            if (head > 1) leds[head - 2] = CRGB(200, 80, 10);
            if (head < NUM_LEDS - 1) leds[head + 1] = CRGB(255, 180, 40);
            if (head < NUM_LEDS - 2) leds[head + 2] = CRGB(200, 80, 10);
        }
    }
}

void setupFleetSync() {
    Serial.println("\n========================================================");
    Serial.println("  MAIN STREET ELECTRICAL PARADE - ESP-NOW WIRELESS FLEET");
    Serial.println("========================================================");

    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    String myMac = WiFi.macAddress();
    Serial.printf("[INFO] My MAC Address: %s\n", myMac.c_str());

    if (myMac.equalsIgnoreCase(MAC_LEADER_FLOAT1)) {
        isLeader = true;
        myFloatNumber = 1;
        Serial.println("[ROLE] Configured as: *** LEADER (Float 1 - Title Drum) ***");
    } else if (myMac.equalsIgnoreCase(MAC_FOLLOWER_FLOAT2)) {
        isLeader = false;
        myFloatNumber = 2;
        Serial.println("[ROLE] Configured as: >>> FOLLOWER (Float 2 - Casey Jr.) <<<");
    } else {
        isLeader = false;
        myFloatNumber = 2;
        Serial.println("[ROLE] Unregistered MAC - Defaulting to Follower (Float 2)");
    }

    if (esp_now_init() != ESP_OK) {
        Serial.println("[ERROR] ESP-NOW initialization failed!");
        return;
    }
    Serial.println("[INFO] ESP-NOW Initialized successfully.");

    if (isLeader) {
        esp_now_peer_info_t peerInfo = {};
        memcpy(peerInfo.peer_addr, broadcastMac, 6);
        peerInfo.channel = 0;
        peerInfo.encrypt = false;
        if (esp_now_add_peer(&peerInfo) == ESP_OK) {
            Serial.println("[INFO] Broadcast peer registered.");
        }
    } else {
        esp_now_register_recv_cb(onDataReceive);
        Serial.println("[INFO] Receive callback registered. Listening for Leader...");
    }

    FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS)
           .setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(MAX_BRIGHTNESS);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_MILLIAMPS);

    Serial.println("[INFO] Setup complete! Starting sync loop...\n");
}

void loopFleetSync() {
    uint32_t now = millis();

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
                waveHeadPos = map(waveTimer, 0, 1500, 0, NUM_LEDS - 1);
            } else {
                waveActiveFloat = 2;
                waveHeadPos = map(waveTimer - 1500, 0, 1500, 0, NUM_LEDS - 1);
            }
        }

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

        digitalWrite(STATUS_LED_PIN, (now / 500) % 2);

    } else {
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

    FastLED.show();
    delay(15);
}

#endif

// ============================================================================
// MAIN SETUP & LOOP
// ============================================================================
void setup() {
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable transient brownout detector during startup
    Serial.begin(115200);
    pinMode(STATUS_LED_PIN, OUTPUT);
    delay(300);

#if ENABLE_WIFI_LIVE_STREAM == 1
    setupWifiReceiver();
#else
    setupFleetSync();
#endif
}

void loop() {
#if ENABLE_WIFI_LIVE_STREAM == 1
    loopWifiReceiver();
#else
    loopFleetSync();
#endif
}
