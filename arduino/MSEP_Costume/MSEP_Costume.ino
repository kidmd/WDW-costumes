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
//    - Select COM Port:
//    - Connect your ESP32 via USB and choose its port in Tools -> Port.
// 5. Click the "Upload" arrow button (top-left).
// ============================================================================

#include <Arduino.h>
#include <FastLED.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <esp_now.h>
#include <esp_arduino_version.h>
#include <Preferences.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

#if __has_include("costume_config.h")
#include "costume_config.h"
#endif

#if __has_include("float_config.h")
#include "float_config.h"
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
    { "The Train",      "LEADER",     CRGB(230, 40, 50)   }, // Float 1 (Red)
    { "Title Drum",     "FOLLOWER",   CRGB(255, 180, 20)  }, // Float 2 (Gold/Amber)
    { "The Turtle",     "FOLLOWER",   CRGB(40, 200, 180)  }, // Float 3 (Teal)
    { "The Snail",      "FOLLOWER",   CRGB(255, 20, 140)  }, // Float 4 (Pink)
    { "Cinderella",     "FOLLOWER",   CRGB(50, 180, 240)  }, // Float 5 (Cyan)
    { "Pete's Dragon",  "FOLLOWER",   CRGB(0, 255, 100)   }, // Float 6 (Green)
    { "Flag & Eagle",   "FOLLOWER",   CRGB(60, 120, 255)  }  // Float 7 (Patriotic Blue)
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
const char* MAC_LEADER_FLOAT1   = "B0:CB:D8:C8:49:84"; // Board 1: The Train (Leader)
const char* MAC_FOLLOWER_FLOAT2 = "A4:F0:0F:64:33:A0"; // Board 2: Title Drum (Follower)

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

#define BUTTON_PIN          0       // BOOT button on standard ESP32 DevKit
#define SHOW_LOOP_MS        90000   // 90-second autonomous theatrical sequence
#define FLEET_ROUTINE_TOTAL_MS 30000 // Auto-updated for 30s Grand Electrical Parade Show (30.0s)

enum StandaloneShowMode {
    SHOW_MODE_AUTONOMOUS_SEQUENCE = 0,
    SHOW_MODE_FLEET_SYNC          = 1,
    SHOW_MODE_FLEET_30S_ROUTINE   = 2
};

StandaloneShowMode currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
StandaloneShowMode previousStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
uint32_t fleetRoutineStartTime = 0;
uint8_t fleetRoutineCycle = 0;

void broadcastFleetRoutinePacket(uint8_t mode, uint32_t masterMillis) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = mode; // 0x30 = Start/Sync 30s Routine, 0x00 = Stop early
    packet.masterMillis = masterMillis;
    packet.activeFloat = myFloatNumber;
    packet.waveHead = 0;
    esp_now_send(broadcastMac, (uint8_t*)&packet, sizeof(packet));
}

// ============================================================================
// PRE-RACE CORRAL ROLL CALL & RADAR IDENTIFY FLASH
// ============================================================================
void triggerIdentifyFlash() {
    uint8_t fIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB color = FLEET_ROSTER_INFO[fIdx].color;
    Serial.printf("[RADAR] ✨ Identify Flash triggered for Float %d: %s (%s)!\n", 
                  myFloatNumber, FLEET_ROSTER_INFO[fIdx].name, FLEET_ROSTER_INFO[fIdx].tag);
    for (int f = 0; f < 3; f++) {
        fill_solid(leds, NUM_LEDS, color);
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, HIGH);
        delay(120);
        fill_solid(leds, NUM_LEDS, CRGB::Black);
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, LOW);
        delay(100);
    }
}

void broadcastIdentifyPacket(uint8_t targetFloat) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = 0x42; // Identify Flash Command
    packet.masterMillis = millis();
    packet.activeFloat = targetFloat;
    packet.waveHead = 0;
    esp_now_send(broadcastMac, (uint8_t*)&packet, sizeof(packet));
}

// ============================================================================
// ESP-NOW RECEIVE CALLBACK (Follower & Fleet Peer)
// Compatible with both ESP32 Arduino Core 2.x (const uint8_t*) and Core 3.x+ (esp_now_recv_info_t*)
// ============================================================================
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
void onDataReceive(const esp_now_recv_info_t *esp_now_info, const uint8_t *incomingData, int len) {
#else
void onDataReceive(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
#endif
    if (len == sizeof(ParadeSyncPacket)) {
        ParadeSyncPacket packet;
        memcpy(&packet, incomingData, sizeof(packet));
        if (packet.magic == 0xEE) {
            if (packet.mode == 0x30) {
                // Synchronized Fleet 30s routine trigger
                if (currentStandaloneMode != SHOW_MODE_FLEET_30S_ROUTINE) {
                    previousStandaloneMode = currentStandaloneMode;
                }
                currentStandaloneMode = SHOW_MODE_FLEET_30S_ROUTINE;
                fleetRoutineStartTime = millis() - packet.masterMillis;
                Serial.printf("[ESP-NOW] Fleet 30s Show triggered by Float %d (sync offset: %u ms)\n",
                              packet.activeFloat, packet.masterMillis);
            } else if (packet.mode == 0x00 && currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE) {
                // Early stop commanded by peer
                currentStandaloneMode = previousStandaloneMode;
                Serial.printf("[ESP-NOW] Fleet 30s Show stopped early by Float %d -> reverting to baseline\n",
                              packet.activeFloat);
            } else if (packet.mode == 0x42) {
                // Pre-race Corral Roll Call: Identify Flash command
                if (packet.activeFloat == 0 || packet.activeFloat == myFloatNumber) {
                    triggerIdentifyFlash();
                }
            } else {
                currentPacket = packet;
                packetReceived = true;
                lastPacketTime = millis();
                localSyncTime = packet.masterMillis;
                lastLocalTick = millis();
            }
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

void renderFireworks(uint32_t t) {
    uint32_t cycleMs = 1800;
    uint32_t tau = t % cycleMs;
    uint8_t rays = 5;
    uint8_t ledsPerRay = 4;
    uint8_t fwLeds = rays * ledsPerRay; // 20 LEDs
    uint8_t fwStart = (FRONT_LEDS > fwLeds) ? (FRONT_LEDS - fwLeds) : 0;

    // Ambient glow on background LEDs
    for (int i = 0; i < fwStart; i++) {
        leds[i] = CRGB(20, 10, 5);
        if (random16(10000) < 150) {
            leds[i] = CRGB(255, 230, 180);
        }
    }

    // Firework LEDs in Serpentine order
    for (int idx = 0; idx < fwLeds && (fwStart + idx) < FRONT_LEDS; idx++) {
        uint8_t ray = idx / ledsPerRay;
        uint8_t posInRay = idx % ledsPerRay;
        // Serpentine: odd rays reversed
        uint8_t step = (ray % 2 == 1) ? (ledsPerRay - 1 - posInRay) : posInRay;

        // All rays of a firework group share the exact same uniform color
        CRGB rayColor = CRGB(255, 195, 45); // Golden Amber (#ffb703) signature uniform

        if (tau < 200) {
            // Phase 1: Center ignition flash
            if (step == 0) {
                leds[fwStart + idx] = CRGB(255, 255, 220);
            } else {
                leds[fwStart + idx] = CRGB::Black; // Completely off until ignited
            }
        } else if (tau < 1250) {
            // Phase 2: Outward trail growth
            int progress = map(tau - 200, 0, 1050, 0, (ledsPerRay - 1) * 100);
            int headStep = progress / 100;
            int delta = headStep - step;
            if (delta == 0) {
                // Leading spark head
                leds[fwStart + idx] = CRGB(255, 255, 255);
            } else if (delta > 0) {
                // Leave centermost LEDs on to create trailing line from center!
                if (step == 0) {
                    leds[fwStart + idx] = CRGB(255, 185, 60);
                } else {
                    CRGB ember = rayColor;
                    ember.nscale8_video(max((uint8_t)50, (uint8_t)(255 - delta * 50)));
                    leds[fwStart + idx] = ember;
                }
            } else {
                leds[fwStart + idx] = CRGB::Black; // Ahead of expanding wavefront: completely off
            }
        } else if (tau < 1600) {
            // Phase 3: Tip sparkle crackle
            if (step >= ledsPerRay - 2) {
                if (random16(100) < 40) {
                    leds[fwStart + idx] = CRGB(255, 255, 240);
                } else {
                    leds[fwStart + idx] = CRGB::Black;
                }
            } else if (step == 0) {
                // Persistent trailing anchor while tips crackle
                leds[fwStart + idx] = CRGB(180, 110, 30);
            } else {
                leds[fwStart + idx] = CRGB::Black; // Burned out inner trail: completely off
            }
        } else {
            // Phase 4: Rest / Burst ended - baseline completely unlit / off
            leds[fwStart + idx] = CRGB::Black;
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
    
    // Register broadcast peer so this node can transmit to all fleet costumes
    esp_now_peer_info_t peerInfo = {};
    memcpy(peerInfo.peer_addr, broadcastMac, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;
    if (!esp_now_is_peer_exist(broadcastMac)) {
        esp_now_add_peer(&peerInfo);
    }
    
    // Register receive callback so this node can receive sync packets from any costume
    esp_now_register_recv_cb(onDataReceive);

    if (isLeader) {
        Serial.printf("[ROLE] *** LEADER (Float 1 - %s) *** (ESP-NOW Tx/Rx ready)\n", FLEET_ROSTER_INFO[0].name);
    } else {
        Serial.printf("[ROLE] >>> FOLLOWER (Float %d - %s) <<< (ESP-NOW Tx/Rx ready)\n", 
                      myFloatNumber, FLEET_ROSTER_INFO[myFloatNumber - 1].name);
    }
}

// ============================================================================
// HARDWARE BUTTON & STANDALONE SHOW SEQUENCE (Autonomous Float Mode)
// ============================================================================

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
#if defined(ACTIVE_COSTUME_PATTERN) && (ACTIVE_COSTUME_PATTERN == COSTUME_PATTERN_FIREWORKS)
    renderFireworks(now);
    duplicateFrontToBack();
    FastLED.show();
    delay(15);
    return;
#endif

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
// 30-SECOND SYNCHRONIZED FLEET ROUTINE (One-Shot Grand Parade Show)
// ============================================================================
const CRGB STANDARD_FLEET_COLORS[7] = {
    CRGB(255, 195, 20),   // 0: Belle Gold / Incandescent Amber
    CRGB(40, 200, 255),   // 1: Cinderella Cyan
    CRGB(255, 30, 150),   // 2: Cheshire Pink
    CRGB(20, 255, 110),   // 3: Pete's Dragon Green
    CRGB(240, 50, 50),    // 4: Parade Ruby Red
    CRGB(170, 60, 255),   // 5: Magic Violet
    CRGB(255, 130, 20)    // 6: Citrus Orange
};

// >>>>> BEGIN AUTO-GENERATED FLEET ROUTINE >>>>>
// Auto-Generated FastLED Fleet Choreography Routine
// Show Name: 30s Grand Electrical Parade Show
// Total Duration: 30.0s (30000 ms)
// Generated by Main Street Electrical Parade Simulator

void render30sFleetRoutine(uint32_t elapsedMs) {
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB routineColor = STANDARD_FLEET_COLORS[fleetRoutineCycle % 7];

    if (elapsedMs < 1000) {
        // Block 1: Dramatic Blackout (0.0s - 1.0s)
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }
    else if (elapsedMs < 2500) {
        // Block 2: Forward Traveling Wave (1➔7) (1.0s - 2.5s)
        float waveProgress = (float)(elapsedMs - 1000) / 1500.0f;
        float headPos = waveProgress * 6.0f;
        float dist = fabs((float)floatIdx - headPos);
        float trailLength = 2.0f;

        if (dist <= trailLength) {
            float intensity = 1.0f - (dist / trailLength);
            CRGB col = STANDARD_FLEET_COLORS[(fleetRoutineCycle + 1) % 7];
            col.nscale8_video((uint8_t)(intensity * 255));
            if (dist < 0.45f) {
                col = blend(col, CRGB(255, 245, 220), (uint8_t)((1.0f - (dist / 0.45f)) * 230));
            }
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }
    else if (elapsedMs < 4000) {
        // Block 3: Reverse Traveling Wave (7➔1) (2.5s - 4.0s)
        float waveProgress = (float)(elapsedMs - 2500) / 1500.0f;
        float headPos = 6.0f - (waveProgress * 6.0f);
        float dist = fabs((float)floatIdx - headPos);
        float trailLength = 2.0f;

        if (dist <= trailLength) {
            float intensity = 1.0f - (dist / trailLength);
            CRGB col = routineColor;
            col.nscale8_video((uint8_t)(intensity * 255));
            if (dist < 0.45f) {
                col = blend(col, CRGB(255, 245, 220), (uint8_t)((1.0f - (dist / 0.45f)) * 230));
            }
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }
    else if (elapsedMs < 9000) {
        // Block 4: All-Fleet Majestic Breath (4.0s - 9.0s)
        uint8_t breath = beatsin8(36, 70, 255, fleetRoutineStartTime + 4000);
        CRGB col = routineColor;
        col.nscale8_video(breath);
        if (breath > 240) {
            col = blend(col, CRGB(255, 255, 230), map(breath, 240, 255, 0, 180));
        }
        fill_solid(leds, FRONT_LEDS, col);
    }
    else if (elapsedMs < 11000) {
        // Block 5: Center-Outward Energy Burst (9.0s - 11.0s)
        float burstProgress = (float)(elapsedMs - 9000) / 2000.0f;
        float burstRadius = burstProgress * 3.5f;
        float distFromCenter = fabs((float)floatIdx - 3.0f);
        float ringDist = fabs(distFromCenter - burstRadius);

        if (ringDist < 1.2f) {
            float intensity = 1.0f - (ringDist / 1.2f);
            CRGB col = STANDARD_FLEET_COLORS[(fleetRoutineCycle + 4) % 7];
            col.nscale8_video((uint8_t)(intensity * 255));
            if (ringDist < 0.35f) {
                col = blend(col, CRGB(255, 255, 240), 220);
            }
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }
    else if (elapsedMs < 13500) {
        // Block 6: Odd/Even Marquee Wig-Wag (11.0s - 13.5s)
        uint8_t phase = ((elapsedMs - 11000) / 250) % 2;
        bool isOddFloat = (myFloatNumber % 2 != 0);
        if ((phase == 0 && isOddFloat) || (phase == 1 && !isOddFloat)) {
            fill_solid(leds, FRONT_LEDS, STANDARD_FLEET_COLORS[(fleetRoutineCycle + 5) % 7]);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }
    else if (elapsedMs < 16500) {
        // Block 7: Baton Leapfrog Chase (13.5s - 16.5s)
        uint8_t activeRunner = ((elapsedMs - 13500) / 428) % 7;
        if (floatIdx == activeRunner) {
            fill_solid(leds, FRONT_LEDS, CRGB(255, 245, 220));
        } else {
            CRGB dimBase = FLEET_ROSTER_INFO[floatIdx].color;
            dimBase.nscale8_video(40);
            fill_solid(leds, FRONT_LEDS, dimBase);
        }
    }
    else if (elapsedMs < 17500) {
        // Block 8: Anticipation Blackout (16.5s - 17.5s)
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }
    else if (elapsedMs < 21500) {
        // Block 9: Starlight & Wave Twinkle Storm (17.5s - 21.5s)
        CRGB dimBase = STANDARD_FLEET_COLORS[(fleetRoutineCycle + 8) % 7];
        dimBase.nscale8_video(35);
        fill_solid(leds, FRONT_LEDS, dimBase);
        for (int i = 0; i < FRONT_LEDS; i++) {
            if (random16(1000) < 140) {
                leds[i] = (random8(2) == 0) ? STANDARD_FLEET_COLORS[(fleetRoutineCycle + 8) % 7] : CRGB(255, 255, 240);
            }
        }
    }
    else if (elapsedMs < 24500) {
        // Block 10: Ping-Pong Double Bounce (21.5s - 24.5s)
        float bounceCycle = fmod((float)(elapsedMs - 21500) / (3000.0f / 2.0f), 2.0f);
        float headPos = (bounceCycle < 1.0f) ? (bounceCycle * 6.0f) : ((2.0f - bounceCycle) * 6.0f);
        float dist = fabs((float)floatIdx - headPos);

        if (dist <= 1.8f) {
            float intensity = 1.0f - (dist / 1.8f);
            CRGB col = STANDARD_FLEET_COLORS[(fleetRoutineCycle + 9) % 7];
            col.nscale8_video((uint8_t)(intensity * 255));
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }
    else if (elapsedMs < 29500) {
        // Block 11: Grand Finale Carnival Crescendo (24.5s - 29.5s)
        float p = (float)(elapsedMs - 24500) / 5000.0f;
        uint8_t hue = (uint8_t)(elapsedMs * 3 / 10 + floatIdx * 36);
        fill_solid(leds, FRONT_LEDS, CHSV(hue, 220, 255));
        if (p >= 0.65f && ((elapsedMs / 70) % 2 == 0)) {
            fill_solid(leds, FRONT_LEDS, CRGB(255, 255, 255));
        }
    }
    else if (elapsedMs < 30000) {
        // Block 12: Curtain Blackout & Return (29.5s - 30.0s)
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }
    else {
        // Routine completed: blackout curtain
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }

    // Duplicate front 100 LEDs to back 100 LEDs for full 200-LED costume!
    duplicateFrontToBack();

    // Clear any extra LEDs beyond strand count
    for (int i = NUM_LEDS; i < MAX_LEDS_CAPACITY; i++) {
        leds[i] = CRGB::Black;
    }

    // Status LED blink cadence during fleet routine
    digitalWrite(STATUS_LED_PIN, ((elapsedMs / 200) % 2 == 0) ? HIGH : LOW);

    FastLED.show();
    delay(15);
}
// <<<<< END AUTO-GENERATED FLEET ROUTINE <<<<<

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

#if defined(COMPILED_FLOAT_ID) && (COMPILED_FLOAT_ID >= 1 && COMPILED_FLOAT_ID <= 7)
    // Dedicated Float Build: Automatically configure and save this Float ID to NVS flash
    myFloatNumber = COMPILED_FLOAT_ID;
    preferences.putUChar("float_id", myFloatNumber);
    Serial.printf("[DEDICATED BUILD] Auto-configured and saved Float ID: %d (%s - %s)\n",
                  myFloatNumber, FLEET_ROSTER_INFO[myFloatNumber - 1].name, FLEET_ROSTER_INFO[myFloatNumber - 1].tag);
#else
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
            Serial.println("[MAC] Matched Board 1 -> Float 1 (Leader - The Train)");
        } else if (myMac.equalsIgnoreCase(MAC_FOLLOWER_FLOAT2)) {
            myFloatNumber = 2;
            Serial.println("[MAC] Matched Board 2 -> Float 2 (Title Drum)");
        } else {
            myFloatNumber = 2;
            Serial.println("[MAC] Unregistered MAC -> Defaulting to Float 2 (Title Drum)");
            Serial.println("[TIP] Hold BOOT button for 3s anytime to set your Float Number (1 to 7)!");
        }
        preferences.putUChar("float_id", myFloatNumber);
    }
#endif

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
    // Short Tap (50ms - 2500ms):
    //   - If idle / baseline: Trigger 30-Second Fleet Routine once and broadcast to peers
    //   - If running 30s Fleet Routine: Stop early and return to baseline, broadcast stop to peers
    // Long Hold (>= 3 seconds): Enter Float ID Configuration Mode (1 to 7)
    static bool buttonWasPressed = false;
    static uint32_t buttonDownTime = 0;
    static uint32_t lastButtonReleaseTime = 0;
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

        // 50ms hardware press debounce and 300ms software lockout between button actions
        if (!longHoldHandled && pressDuration >= 50 && pressDuration < 2500 && (now - lastButtonReleaseTime >= 300)) {
            lastButtonReleaseTime = now;

            if (currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE) {
                // STOP EARLY: Return to baseline and broadcast stop to fleet
                currentStandaloneMode = previousStandaloneMode;
                broadcastFleetRoutinePacket(0x00, 0);
                Serial.println("[FLEET] Early stop triggered via BOOT button -> returning to baseline.");
                
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
                // START 30s FLEET ROUTINE: Trigger once and broadcast start to fleet
                fleetRoutineCycle++;
                fleetRoutineStartTime = now;
                previousStandaloneMode = currentStandaloneMode;
                currentStandaloneMode = SHOW_MODE_FLEET_30S_ROUTINE;
                broadcastFleetRoutinePacket(0x30, 0);
                Serial.printf("[FLEET] 30s Fleet Show started via BOOT button! (Cycle #%u)\n", fleetRoutineCycle);
            }
        }
    }

    // 2. Check for incoming live stream packets from Python Simulator
    int packetSize = 0;
    while ((packetSize = udp.parsePacket()) > 0) {
        uint8_t buffer[512];
        int len = udp.read(buffer, sizeof(buffer));
        if (len >= 7 && 
            buffer[0] == 'M' && buffer[1] == 'S' && buffer[2] == 'E' && buffer[3] == 'P') {
            
            bool frameAccepted = false;
            int pIdx = 0;
            uint16_t frameLeds = 0;

            if (buffer[4] == 0x01) {
                // Opcode 0x01: Universal broadcast frame (accepted by any float role)
                frameLeds = (buffer[5] << 8) | buffer[6];
                pIdx = 7;
                frameAccepted = true;
            } else if (buffer[4] == 0x02 && len >= 8) {
                // Opcode 0x02: Addressed Fleet Frame (filtered by float role)
                uint8_t targetFloatId = buffer[5];
                if (targetFloatId == 0 || targetFloatId == myFloatNumber) {
                    frameLeds = (buffer[6] << 8) | buffer[7];
                    pIdx = 8;
                    frameAccepted = true;
                }
            } else if (buffer[4] == 0x03 && len >= 7) {
                // Opcode 0x03: Corral Roll Call & Radar Diagnostics
                uint8_t cmd = buffer[5];
                uint8_t targetFloatId = buffer[6];
                if (targetFloatId == 0 || targetFloatId == myFloatNumber) {
                    if (cmd == 0x02) {
                        // Identify Flash
                        triggerIdentifyFlash();
                    }
                }
            }

            if (frameAccepted) {
                int ledsToUpdate = min((int)frameLeds, (int)FRONT_LEDS);
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
                return; // Handled our frame, stay in live streaming mode!
            }
        }
    }

    // 3. Check if live stream recently ended (> 2.5 seconds timeout)
    if (isLiveStreaming && (now - lastStreamPacketTime > 2500)) {
        isLiveStreaming = false;
        Serial.println("[MODE] Live stream ended. Resuming standalone mode.");
    }

    // 4. If simulator is NOT streaming, run the selected standalone mode!
    if (!isLiveStreaming) {
        if (currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE) {
            uint32_t elapsedMs = now - fleetRoutineStartTime;
            if (elapsedMs < FLEET_ROUTINE_TOTAL_MS) {
                render30sFleetRoutine(elapsedMs);
            } else {
                // Routine complete! Return automatically to regular individual program
                currentStandaloneMode = previousStandaloneMode;
                Serial.printf("[FLEET] %u ms Fleet Routine finished -> auto-returned to individual program.\n", FLEET_ROUTINE_TOTAL_MS);
            }
        } else if (currentStandaloneMode == SHOW_MODE_AUTONOMOUS_SEQUENCE) {
            runAutonomousShowSequence(now);
        } else {
            runFleetSync(now);
        }
    }
}
