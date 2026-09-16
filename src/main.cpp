#include <Arduino.h>
#include <FastLED.h>
#include <esp_now.h>
#include <WiFi.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// ============================================================================
// HARDWARE & PIN DEFINITIONS
// ============================================================================
#define DATA_PIN        16      // 8th pin down on the right
#define LED_TYPE        WS2812B
#define COLOR_ORDER     GRB
#define NUM_LEDS        50      // LEDs per strand
#define STATUS_LED_PIN  2       // Onboard Blue LED (Heartbeat / Sync Indicator)

#define MAX_BRIGHTNESS  45
#define MAX_MILLIAMPS   800

CRGB leds[NUM_LEDS];

// ============================================================================
// KNOWN MAC ADDRESSES FOR THE FLEET
// ============================================================================
// Add more as we register the rest of the 7 floats!
const char* MAC_LEADER_FLOAT1   = "B0:CB:D8:C8:49:84"; // Board 1: Title Drum (Leader)
const char* MAC_FOLLOWER_FLOAT2 = "A4:F0:0F:64:33:A0"; // Board 2: Casey Jr. Train (Follower)

// ============================================================================
// ESP-NOW SYNC PACKET DEFINITION
// ============================================================================
struct __attribute__((packed)) ParadeSyncPacket {
    uint8_t  magic;          // 0xEE verification byte
    uint8_t  mode;           // 0: Marquee, 1: Sparkle, 2: Twinkle, 3: Traveling Wave
    uint32_t masterMillis;   // Synchronized timebase (ms)
    uint8_t  activeFloat;    // For traveling wave (1 = Float 1, 2 = Float 2)
    uint8_t  waveHead;       // 0-49 pixel position of traveling wave
};

ParadeSyncPacket currentPacket;
bool isLeader = false;
uint8_t myFloatNumber = 2; // Default to Float 2 if unknown

// Follower timing & timeout tracking
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
// ANIMATIONS
// ============================================================================

// Mode 0: Synchronized Golden Marquee Chase
// All floats chase with the exact same phase and frequency
void renderMarqueeChase(uint32_t t) {
    uint8_t offset = (t / 110) % 3;
    for (int i = 0; i < NUM_LEDS; i++) {
        if ((i + offset) % 3 == 0) {
            leds[i] = CRGB(255, 147, 41); // Incandescent amber/gold
        } else {
            leds[i] = CRGB::Black;
        }
    }
}

// Mode 1: Synchronized Float Palette Sparkle
// Float 1 showcases Title Drum Gold, Float 2 showcases Casey Jr. Red/White accents
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

// Mode 2: Synchronized Starlight Twinkle
void renderTwinkle(uint32_t t) {
    fadeToBlackBy(leds, NUM_LEDS, 25);
    // Deterministic pseudo-random twinkle derived from synchronized clock
    uint16_t seed = (t / 35) + (myFloatNumber * 100);
    if ((seed % 7) == 0) {
        int pos = (seed * 13) % NUM_LEDS;
        leds[pos] = CRGB(255, 220, 160);
    }
}

// Mode 3: Traveling Parade Wave Across Floats!
// The wave shoots down Float 1... then jumps and shoots down Float 2!
void renderTravelingWave(uint8_t activeFloat, uint8_t waveHead) {
    // Ambient soft glow on floats that don't have the active wave
    fill_solid(leds, NUM_LEDS, CRGB(15, 8, 2));

    if (myFloatNumber == activeFloat) {
        // The wave is currently on THIS float!
        int head = waveHead;
        if (head >= 0 && head < NUM_LEDS) {
            leds[head] = CRGB(255, 255, 255); // Brilliant white center
            if (head > 0) leds[head - 1] = CRGB(255, 180, 40);
            if (head > 1) leds[head - 2] = CRGB(200, 80, 10);
            if (head < NUM_LEDS - 1) leds[head + 1] = CRGB(255, 180, 40);
            if (head < NUM_LEDS - 2) leds[head + 2] = CRGB(200, 80, 10);
        }
    }
}

// ============================================================================
// SETUP
// ============================================================================
void setup() {
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable transient brownout detector during startup
    Serial.begin(115200);
    pinMode(STATUS_LED_PIN, OUTPUT);
    delay(500);

    Serial.println("\n========================================================");
    Serial.println("  MAIN STREET ELECTRICAL PARADE - ESP-NOW WIRELESS FLEET");
    Serial.println("========================================================");

    // 1. Initialize Wi-Fi in Station mode
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    String myMac = WiFi.macAddress();
    Serial.printf("[INFO] My MAC Address: %s\n", myMac.c_str());

    // 2. Auto-assign Role based on MAC Address
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

    // 3. Initialize ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("[ERROR] ESP-NOW initialization failed!");
        return;
    }
    Serial.println("[INFO] ESP-NOW Initialized successfully.");

    if (isLeader) {
        // Register broadcast peer
        esp_now_peer_info_t peerInfo = {};
        memcpy(peerInfo.peer_addr, broadcastMac, 6);
        peerInfo.channel = 0;
        peerInfo.encrypt = false;
        if (esp_now_add_peer(&peerInfo) == ESP_OK) {
            Serial.println("[INFO] Broadcast peer registered.");
        }
    } else {
        // Register receive callback
        esp_now_register_recv_cb(onDataReceive);
        Serial.println("[INFO] Receive callback registered. Listening for Leader...");
    }

    // 4. Initialize FastLED
    FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS)
           .setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(MAX_BRIGHTNESS);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_MILLIAMPS);

    Serial.println("[INFO] Setup complete! Starting sync loop...\n");
}

// ============================================================================
// MAIN LOOP
// ============================================================================
void loop() {
    uint32_t now = millis();

    if (isLeader) {
        // --------------------------------------------------------------------
        // LEADER LOGIC: Controls the Master Clock and Broadcasts to Followers
        // --------------------------------------------------------------------
        static uint32_t lastBroadcast = 0;
        uint32_t cycleTime = now % 48000; // 48-second master loop
        uint8_t mode = cycleTime / 12000; // 12 seconds per mode (0, 1, 2, 3)

        // Calculate traveling wave positions (Mode 3)
        // 0 to 1.5s: Float 1 runs wave. 1.5s to 3.0s: Float 2 runs wave.
        uint8_t waveActiveFloat = 1;
        uint8_t waveHeadPos = 0;
        if (mode == 3) {
            uint32_t waveTimer = now % 3000; // 3-second cycle for 2 floats
            if (waveTimer < 1500) {
                waveActiveFloat = 1;
                waveHeadPos = map(waveTimer, 0, 1500, 0, NUM_LEDS - 1);
            } else {
                waveActiveFloat = 2;
                waveHeadPos = map(waveTimer - 1500, 0, 1500, 0, NUM_LEDS - 1);
            }
        }

        // Broadcast sync packet every 40 ms (25 times per second)
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

        // Render Leader animations locally
        switch (mode) {
            case 0: renderMarqueeChase(now); break;
            case 1: renderParadeSparkle(now); break;
            case 2: renderTwinkle(now); break;
            case 3: renderTravelingWave(waveActiveFloat, waveHeadPos); break;
        }

        // Heartbeat LED
        digitalWrite(STATUS_LED_PIN, (now / 500) % 2);

    } else {
        // --------------------------------------------------------------------
        // FOLLOWER LOGIC: Synchronizes to Leader Broadcasts
        // --------------------------------------------------------------------
        bool isConnected = (now - lastPacketTime < 2500); // 2.5s signal timeout

        // Update local extrapolated sync time
        localSyncTime += (now - lastLocalTick);
        lastLocalTick = now;

        uint8_t mode = isConnected ? currentPacket.mode : ((now / 10000) % 4);
        uint32_t activeTime = isConnected ? localSyncTime : now;

        switch (mode) {
            case 0: 
                renderMarqueeChase(activeTime); 
                break;
            case 1: 
                renderParadeSparkle(activeTime); 
                break;
            case 2: 
                renderTwinkle(activeTime); 
                break;
            case 3: 
                if (isConnected) {
                    renderTravelingWave(currentPacket.activeFloat, currentPacket.waveHead);
                } else {
                    renderMarqueeChase(now); // Standalone fallback
                }
                break;
        }

        // Status LED on Follower:
        // SOLID ON = Connected to Leader!
        // FAST BLINK = Searching for Leader (Disconnected)
        if (isConnected) {
            digitalWrite(STATUS_LED_PIN, HIGH);
        } else {
            digitalWrite(STATUS_LED_PIN, (now / 150) % 2);
        }
    }

    FastLED.show();
    delay(15);
}
