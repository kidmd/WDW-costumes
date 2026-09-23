// ============================================================================
// MAIN STREET ELECTRICAL PARADE - ARDUINO IDE COMPATIBLE SKETCH
// ============================================================================
// HOW TO FLASH IN ARDUINO IDE (For Brothers & Makers):
// 1. Open this file (MSEP_Costume.ino) in Arduino IDE.
// 2. Install FastLED:
//    - Go to Sketch -> Include Library -> Manage Libraries...
//    - Search for "FastLED" and click "Install" (by Daniel Garcia).
// 3. Select ESP32 Board:
//    - Go to Tools -> Board -> esp32 -> "ESP32 Dev Module"
// 4. Select COM Port:
//    - Connect your ESP32 via USB and choose its port in Tools -> Port.
// 5. Click the "Upload" arrow button (top-left).
// ============================================================================

#include <Arduino.h>
#include <FastLED.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <esp_now.h>
#include <Preferences.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

#if __has_include("costume_config.h")
#include "costume_config.h"
#endif

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

#ifndef FRONT_LEDS
#define FRONT_LEDS          100     // 100 LEDs on front of costume shirt
#endif

#ifndef BACK_LEDS
#define BACK_LEDS           100     // 100 LEDs on back of costume shirt
#endif

#ifndef NUM_LEDS
#define NUM_LEDS            200     // 200 total LEDs (100 front + 100 back)
#endif
#define MAX_LEDS_CAPACITY   256     // Buffer capacity supporting 200 LEDs
#ifndef MAX_BRIGHTNESS
#define MAX_BRIGHTNESS      60      // Bench/wearable safe brightness
#endif
#define MAX_MILLIAMPS       2000    // 2.0A limit for 200 LEDs on wearable power bank

CRGB leds[MAX_LEDS_CAPACITY];

// Duplicate front 100 LEDs to back 100 LEDs so entire 200-LED costume illuminates identically
inline void duplicateFrontToBack() {
    for (int i = 0; i < FRONT_LEDS && (FRONT_LEDS + i) < NUM_LEDS && (FRONT_LEDS + i) < MAX_LEDS_CAPACITY; i++) {
        leds[FRONT_LEDS + i] = leds[i];
    }
}

Preferences preferences;

// 7-Runner Fleet Metadata & Signature Colors
struct FloatMeta {
    const char* name;
    const char* tag;
    CRGB color;
};

const FloatMeta FLEET_ROSTER_INFO[7] = {
    { "Title Drum",     "LEADER",     CRGB(255, 180, 20)  }, // Float 1 (Gold/Amber)
    { "Casey Jr.",      "FOLLOWER",   CRGB(230, 40, 50)   }, // Float 2 (Red)
    { "Elliott",        "FOLLOWER",   CRGB(0, 255, 100)   }, // Float 3 (Green)
    { "Mushroom",       "FOLLOWER",   CRGB(160, 40, 220)  }, // Float 4 (Purple)
    { "Cinderella",     "FOLLOWER",   CRGB(50, 180, 240)  }, // Float 5 (Cyan)
    { "Pirate Ship",    "FOLLOWER",   CRGB(255, 120, 0)   }, // Float 6 (Orange)
    { "Snail Finale",   "FOLLOWER",   CRGB(255, 20, 140)  }  // Float 7 (Pink)
};

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
    uint8_t  activeFloat;    // For traveling wave (1 to 7)
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
    for (int i = 0; i < FRONT_LEDS; i++) {
        if ((i + offset) % 3 == 0) {
            leds[i] = CRGB(255, 147, 41); // Incandescent amber/gold
        } else {
            leds[i] = CRGB::Black;
        }
    }
}

void renderParadeSparkle(uint32_t t) {
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB baseCol = FLEET_ROSTER_INFO[floatIdx].color;
    CRGB palette[3] = {
        baseCol,
        CRGB(255, 230, 180), // Warm incandescent starlight accent
        CRGB(baseCol.r / 2, baseCol.g / 2, baseCol.b / 2) // Deep jewel shadow
    };

    uint8_t step = (t / 180) % 3;
    for (int i = 0; i < FRONT_LEDS; i++) {
        leds[i] = palette[(i + step) % 3];
    }
}

void renderTwinkle(uint32_t t) {
    fill_solid(leds, FRONT_LEDS, CRGB(20, 10, 2));
    uint16_t seed = (t / 35) + (myFloatNumber * 100);
    if ((seed % 7) == 0) {
        int pos = (seed * 13) % FRONT_LEDS;
        leds[pos] = CRGB(255, 220, 160);
    }
}

void renderTravelingWave(uint8_t activeFloat, uint8_t waveHead) {
    fill_solid(leds, FRONT_LEDS, CRGB(15, 8, 2));
    if (myFloatNumber == activeFloat) {
        int head = waveHead;
        if (head >= 0 && head < FRONT_LEDS) {
            leds[head] = CRGB(255, 255, 255);
            if (head > 0) leds[head - 1] = CRGB(255, 180, 40);
            if (head > 1) leds[head - 2] = CRGB(200, 80, 10);
            if (head < FRONT_LEDS - 1) leds[head + 1] = CRGB(255, 180, 40);
            if (head < FRONT_LEDS - 2) leds[head + 2] = CRGB(200, 80, 10);
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
            // 7-second master wave across all 7 floats (1000ms per runner)
            uint32_t waveTimer = now % 7000;
            waveActiveFloat = (waveTimer / 1000) + 1; // 1 to 7
            uint32_t floatTime = waveTimer % 1000;
            waveHeadPos = map(floatTime, 0, 1000, 0, FRONT_LEDS - 1);
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

    // Duplicate front 100 LEDs to back 100 LEDs for full 200-LED costume!
    duplicateFrontToBack();

    // Clear any extra LEDs beyond strand count
    for (int i = NUM_LEDS; i < MAX_LEDS_CAPACITY; i++) {
        leds[i] = CRGB::Black;
    }

    FastLED.show();
    delay(15);
}

void configureEspNowRole() {
    isLeader = (myFloatNumber == 1);
    if (isLeader) {
        Serial.printf("[ROLE] *** LEADER (Float 1 - %s) ***\n", FLEET_ROSTER_INFO[0].name);
        esp_now_peer_info_t peerInfo = {};
        memcpy(peerInfo.peer_addr, broadcastMac, 6);
        peerInfo.channel = 0;
        peerInfo.encrypt = false;
        if (!esp_now_is_peer_exist(broadcastMac)) {
            esp_now_add_peer(&peerInfo);
        }
        Serial.println("[INFO] ESP-NOW Broadcast peer registered for Leader.");
    } else {
        Serial.printf("[ROLE] >>> FOLLOWER (Float %d - %s) <<<\n", 
                      myFloatNumber, FLEET_ROSTER_INFO[myFloatNumber - 1].name);
        esp_now_register_recv_cb(onDataReceive);
        Serial.println("[INFO] ESP-NOW Receive callback registered for Follower.");
    }
}

// ============================================================================
// HARDWARE BUTTON & STANDALONE SHOW SEQUENCE (Autonomous Float Mode)
// ============================================================================
#define BUTTON_PIN          0       // BOOT button on standard ESP32 DevKit
#define SHOW_LOOP_MS        90000   // 90-second autonomous theatrical sequence

enum StandaloneShowMode {
    SHOW_MODE_AUTONOMOUS_SEQUENCE = 0,
    SHOW_MODE_FLEET_SYNC          = 1
};

StandaloneShowMode currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;

// Interactive Float ID Configuration via BOOT Button (Held for 3 seconds)
void handleFloatConfigMode() {
    Serial.println("\n========================================================");
    Serial.println("  >>> ENTERED FLOAT ID CONFIGURATION MODE <<<");
    Serial.println("  Tap BOOT button to cycle Float 1 -> 7");
    Serial.println("  Leave untouched for 4 seconds to save & exit");
    Serial.println("========================================================");

    // Entry alert: Flash white 3 times
    for (int f = 0; f < 3; f++) {
        fill_solid(leds, NUM_LEDS, CRGB(200, 200, 200));
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, HIGH);
        delay(100);
        fill_solid(leds, NUM_LEDS, CRGB::Black);
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, LOW);
        delay(100);
    }

    // Wait until button is released
    while (digitalRead(BUTTON_PIN) == LOW) {
        delay(10);
    }
    delay(200);

    uint32_t lastActionTime = millis();
    bool configActive = true;
    bool buttonPressed = false;
    uint32_t btnPressTime = 0;

    while (configActive) {
        uint32_t loopNow = millis();

        // 1. Render current float indicator on LED strip
        fill_solid(leds, MAX_LEDS_CAPACITY, CRGB::Black);
        CRGB floatCol = FLEET_ROSTER_INFO[myFloatNumber - 1].color;
        for (int i = 0; i < myFloatNumber && i < FRONT_LEDS; i++) {
            leds[i] = floatCol;
        }
        duplicateFrontToBack();
        FastLED.show();

        // 2. Blink onboard blue status LED to match float count (N blinks, then pause)
        uint32_t blinkCycle = loopNow % (myFloatNumber * 300 + 800);
        if (blinkCycle < (uint32_t)(myFloatNumber * 300)) {
            uint32_t subCycle = blinkCycle % 300;
            digitalWrite(STATUS_LED_PIN, (subCycle < 150) ? HIGH : LOW);
        } else {
            digitalWrite(STATUS_LED_PIN, LOW);
        }

        // 3. Handle button tap to cycle float ID
        bool isDown = (digitalRead(BUTTON_PIN) == LOW);
        if (isDown && !buttonPressed) {
            buttonPressed = true;
            btnPressTime = loopNow;
        } else if (!isDown && buttonPressed) {
            buttonPressed = false;
            if (loopNow - btnPressTime > 40) { // Debounced
                myFloatNumber = (myFloatNumber % 7) + 1;
                lastActionTime = loopNow;
                Serial.printf("[CONFIG] Tapped -> Float %d: %s (%s)\n",
                              myFloatNumber,
                              FLEET_ROSTER_INFO[myFloatNumber - 1].name,
                              FLEET_ROSTER_INFO[myFloatNumber - 1].tag);
            }
        }

        // 4. Auto-save & Exit after 4 seconds of inactivity
        if (loopNow - lastActionTime >= 4000) {
            configActive = false;
        }

        delay(10);
    }

    // Save permanently to Preferences (NVS flash)
    preferences.putUChar("float_id", myFloatNumber);
    Serial.printf("[CONFIG] Saved Float %d (%s) permanently to NVS flash!\n",
                  myFloatNumber, FLEET_ROSTER_INFO[myFloatNumber - 1].name);

    // Reconfigure ESP-NOW role
    configureEspNowRole();

    // Exit alert: Flash green 4 times
    for (int s = 0; s < 4; s++) {
        fill_solid(leds, NUM_LEDS, CRGB(0, 255, 80));
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, HIGH);
        delay(80);
        fill_solid(leds, NUM_LEDS, CRGB::Black);
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, LOW);
        delay(80);
    }
    Serial.println("[CONFIG] Configuration saved! Returned to normal operation.\n");
}

void runAutonomousShowSequence(uint32_t now) {
    uint32_t seqTime = now % SHOW_LOOP_MS;

#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
    // ------------------------------------------------------------------------
    // CUSTOM ARTWORK PALETTE (Sampled from Simulator Artwork)
    // ------------------------------------------------------------------------
    // Phase 1 (0 - 30s): Steady custom artwork colors with starlight sparkle
    // Phase 2 (30 - 60s): Theatrical breathing glow pulsing on the custom palette
    // Phase 3 (60 - 75s): Dynamic traveling chase across the costume
    // Phase 4 (75 - 90s): Solo electrical parade wave
    if (seqTime < 30000) {
        for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
            leds[i] = ARTWORK_PALETTE[i];
            if (COSTUME_SPARKLE_RATE > 0 && random16(10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100)) {
                leds[i] = CRGB(255, 255, 240);
            }
        }
    } else if (seqTime < 60000) {
        uint8_t breath = beatsin8(COSTUME_SPEED_BPM / 2, 120, 255);
        for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
            CRGB baseColor = ARTWORK_PALETTE[i];
            baseColor.nscale8_video(breath);
            leds[i] = baseColor;
            if (COSTUME_SPARKLE_RATE > 0 && random16(10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100)) {
                leds[i] = CRGB(255, 255, 240);
            }
        }
    } else if (seqTime < 75000) {
        uint8_t step = (now / 120) % FRONT_LEDS;
        for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
            int dist = (i - step + FRONT_LEDS) % FRONT_LEDS;
            if (dist < 8) {
                leds[i] = CRGB(255, 255, 220); // Bright chasing beam
            } else {
                CRGB dim = ARTWORK_PALETTE[i];
                dim.nscale8_video(60);
                leds[i] = dim;
            }
        }
    } else {
        uint32_t waveTimer = now % 3000;
        uint8_t waveHeadPos = map(waveTimer, 0, 3000, 0, FRONT_LEDS - 1);
        renderTravelingWave(myFloatNumber, waveHeadPos);
    }
#else
    // ------------------------------------------------------------------------
    // CHARACTER FLOAT THEMED SHOW (When no custom palette is compiled)
    // ------------------------------------------------------------------------
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB charColor = FLEET_ROSTER_INFO[floatIdx].color;

    // Phase 1 (0 - 30s): Character Signature Color Glow with Starlight Twinkle
    // Phase 2 (30 - 60s): Gentle Breathing Glow on Float Colors
    // Phase 3 (60 - 75s): Incandescent Marquee Chase
    // Phase 4 (75 - 90s): Solo Electrical Wave
    if (seqTime < 30000) {
        fill_solid(leds, FRONT_LEDS, charColor);
        for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
            leds[i].nscale8_video(180);
            if (random16(10000) < 150) { // 1.5% subtle starlight
                leds[i] = CRGB(255, 255, 240);
            }
        }
    } else if (seqTime < 60000) {
        uint8_t breath = beatsin8(30, 80, 255);
        for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
            CRGB col = charColor;
            col.nscale8_video(breath);
            leds[i] = col;
            if (random16(10000) < 150) {
                leds[i] = CRGB(255, 255, 240);
            }
        }
    } else if (seqTime < 75000) {
        renderMarqueeChase(now);
    } else {
        uint32_t waveTimer = now % 3000;
        uint8_t waveHeadPos = map(waveTimer, 0, 3000, 0, FRONT_LEDS - 1);
        renderTravelingWave(myFloatNumber, waveHeadPos);
    }
#endif

    // Duplicate front 100 LEDs to back 100 LEDs for full 200-LED costume!
    duplicateFrontToBack();

    // Status LED gentle breath during autonomous sequence
    uint8_t breathLed = ((seqTime / 1000) % 2 == 0) ? HIGH : LOW;
    digitalWrite(STATUS_LED_PIN, breathLed);

    // Clear any extra LEDs beyond strand count
    for (int i = NUM_LEDS; i < MAX_LEDS_CAPACITY; i++) {
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
    pinMode(BUTTON_PIN, INPUT_PULLUP);
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

    // 3. Initialize ESP-NOW Peer-to-Peer & Load Float ID from NVS Flash
    preferences.begin("msep", false);
    uint8_t savedFloatId = preferences.getUChar("float_id", 0);

    String myMac = WiFi.macAddress();
    Serial.printf("[INFO] My MAC Address: %s\n", myMac.c_str());

    if (savedFloatId >= 1 && savedFloatId <= 7) {
        myFloatNumber = savedFloatId;
        Serial.printf("[NVS] Loaded saved Float ID: %d (%s - %s)\n", 
                      myFloatNumber, FLEET_ROSTER_INFO[myFloatNumber - 1].name, FLEET_ROSTER_INFO[myFloatNumber - 1].tag);
    } else {
        // Fallback to MAC-based default if never configured via button
        if (myMac.equalsIgnoreCase(MAC_LEADER_FLOAT1)) {
            myFloatNumber = 1;
            Serial.println("[MAC] Matched Board 1 -> Float 1 (Leader - Title Drum)");
        } else if (myMac.equalsIgnoreCase(MAC_FOLLOWER_FLOAT2)) {
            myFloatNumber = 2;
            Serial.println("[MAC] Matched Board 2 -> Float 2 (Casey Jr.)");
        } else {
            myFloatNumber = 2;
            Serial.println("[MAC] Unregistered MAC -> Defaulting to Float 2 (Casey Jr.)");
            Serial.println("[TIP] Hold BOOT button for 3s anytime to set your Float Number (1 to 7)!");
        }
    }

    if (esp_now_init() != ESP_OK) {
        Serial.println("[ERROR] ESP-NOW initialization failed!");
    } else {
        Serial.println("[INFO] ESP-NOW Initialized successfully.");
        configureEspNowRole();
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

    // 1. Hardware Button (BOOT button on GPIO 0)
    // Short Tap (20ms - 2500ms): Toggle between Autonomous Show and Fleet Sync
    // Long Hold (>= 3 seconds): Enter Float ID Configuration Mode (1 to 7)
    static bool buttonWasPressed = false;
    static uint32_t buttonDownTime = 0;
    static bool longHoldHandled = false;

    bool isButtonPressed = (digitalRead(BUTTON_PIN) == LOW);

    if (isButtonPressed && !buttonWasPressed) {
        buttonWasPressed = true;
        buttonDownTime = now;
        longHoldHandled = false;
    } else if (isButtonPressed && buttonWasPressed) {
        if (!longHoldHandled && (now - buttonDownTime >= 3000)) {
            longHoldHandled = true;
            handleFloatConfigMode();
        }
    } else if (!isButtonPressed && buttonWasPressed) {
        buttonWasPressed = false;
        uint32_t pressDuration = now - buttonDownTime;
        if (!longHoldHandled && pressDuration >= 20 && pressDuration < 2500) {
            if (currentStandaloneMode == SHOW_MODE_AUTONOMOUS_SEQUENCE) {
                currentStandaloneMode = SHOW_MODE_FLEET_SYNC;
                Serial.println("[MODE] Button pressed -> Switched to: ESP-NOW Fleet Sync");
                // Visual confirmation on costume LED strip: 2 Amber/Gold flashes
                for (int f = 0; f < 2; f++) {
                    fill_solid(leds, NUM_LEDS, CRGB(255, 140, 0));
                    FastLED.show();
                    digitalWrite(STATUS_LED_PIN, HIGH);
                    delay(120);
                    fill_solid(leds, NUM_LEDS, CRGB::Black);
                    FastLED.show();
                    digitalWrite(STATUS_LED_PIN, LOW);
                    delay(80);
                }
            } else {
                currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                Serial.println("[MODE] Button pressed -> Switched to: Autonomous Float Show Sequence");
                // Visual confirmation on costume LED strip: 2 Cyan flashes
                for (int f = 0; f < 2; f++) {
                    fill_solid(leds, NUM_LEDS, CRGB(0, 220, 255));
                    FastLED.show();
                    digitalWrite(STATUS_LED_PIN, HIGH);
                    delay(120);
                    fill_solid(leds, NUM_LEDS, CRGB::Black);
                    FastLED.show();
                    digitalWrite(STATUS_LED_PIN, LOW);
                    delay(80);
                }
            }
        }
    }

    // 2. Check for incoming live stream packets from Python Simulator
    int packetSize = udp.parsePacket();
    if (packetSize > 0) {
        uint8_t buffer[512];
        int len = udp.read(buffer, sizeof(buffer));
        if (len >= 7 && 
            buffer[0] == 'M' && buffer[1] == 'S' && buffer[2] == 'E' && buffer[3] == 'P' &&
            buffer[4] == 0x01) {
            
            uint16_t frameLeds = (buffer[5] << 8) | buffer[6];
            int ledsToUpdate = min((int)frameLeds, (int)FRONT_LEDS);
            
            int pIdx = 7;
            for (int i = 0; i < ledsToUpdate && (pIdx + 2) < len; i++) {
                leds[i].r = buffer[pIdx++];
                leds[i].g = buffer[pIdx++];
                leds[i].b = buffer[pIdx++];
            }

            // Duplicate front 100 LEDs to back 100 LEDs for full 200-LED costume!
            duplicateFrontToBack();
            
            for (int i = NUM_LEDS; i < MAX_LEDS_CAPACITY; i++) {
                leds[i] = CRGB::Black;
            }
            
            FastLED.show();
            lastStreamPacketTime = now;
            isLiveStreaming = true;
            digitalWrite(STATUS_LED_PIN, HIGH); // Solid blue during active stream
            return; // Stay in live streaming mode!
        }
    }

    // 3. Check if live stream recently ended (> 2.5 seconds timeout)
    if (isLiveStreaming && (now - lastStreamPacketTime > 2500)) {
        isLiveStreaming = false;
        Serial.println("[MODE] Live stream ended. Resuming standalone mode.");
    }

    // 4. If simulator is NOT streaming, run the selected standalone mode!
    if (!isLiveStreaming) {
        if (currentStandaloneMode == SHOW_MODE_AUTONOMOUS_SEQUENCE) {
            runAutonomousShowSequence(now);
        } else {
            runFleetSync(now);
        }
    }
}
