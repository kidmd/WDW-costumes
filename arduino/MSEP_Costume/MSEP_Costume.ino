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
#define BACK_LEDS          100     // 100 LEDs on back of costume shirt
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
#define RAPID_ROLL_CALL_TOTAL_MS 4000 // 4.0-second Rapid Attendance Roll Call (500ms x 7 floats + 500ms unison finale)

enum StandaloneShowMode {
    SHOW_MODE_AUTONOMOUS_SEQUENCE = 0,
    SHOW_MODE_FLEET_SYNC          = 1,
    SHOW_MODE_FLEET_30S_ROUTINE   = 2,
    SHOW_MODE_RAPID_ROLL_CALL     = 3,
    SHOW_MODE_CORRAL_STANDBY      = 4
};

StandaloneShowMode currentStandaloneMode = SHOW_MODE_CORRAL_STANDBY;
StandaloneShowMode previousStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
uint32_t fleetRoutineStartTime = 0;
uint8_t fleetRoutineCycle = 0;
uint32_t rapidRollCallStartTime = 0;
uint32_t autonomousShowStartTime = 0;

void broadcastFleetRoutinePacket(uint8_t mode, uint32_t masterMillis) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = mode; // 0x30 = Start/Sync 30s Routine, 0x00 = Stop early, 0x50 = Standby, 0x51 = Wake
    packet.masterMillis = masterMillis;
    packet.activeFloat = myFloatNumber;
    packet.waveHead = 0;
    esp_now_send(broadcastMac, (uint8_t*)&packet, sizeof(packet));
}

void broadcastStandbyPacket(uint8_t mode) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = mode; // 0x50 = Standby, 0x51 = Wake
    packet.masterMillis = millis();
    packet.activeFloat = myFloatNumber;
    packet.waveHead = 0;
    esp_now_send(broadcastMac, (uint8_t*)&packet, sizeof(packet));
}

void renderCorralStandby(uint32_t t) {
    // Ultra-low power starlight shimmer (<120mA draw) with visible midnight float-glow
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
    
    // Clearly visible deep midnight base glow (25% float color)
    CRGB dimBase = CRGB(
        max((int)(baseColor.r * 0.25), 10),
        max((int)(baseColor.g * 0.25), 10),
        max((int)(baseColor.b * 0.25), 10)
    );
    fill_solid(leds, FRONT_LEDS, dimBase);

    // Calm, very slow (~5s period), sparse starlight twinkle on ~5% of LEDs
    CRGB subtleWarm = CRGB(
        min(255, dimBase.r + 45),
        min(255, dimBase.g + 38),
        min(255, dimBase.b + 20)
    );

    for (int i = 0; i < FRONT_LEDS; i++) {
        uint8_t wave = sin8((t / 20) + (i * 47)); // very slow (~5.1s cycle), scattered pixels
        if (wave > 242) { // only top ~5% peak
            uint8_t blendAmt = (wave - 242) * 19; // 0..247 smooth ramp
            leds[i] = blend(dimBase, subtleWarm, blendAmt);
        }
    }
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

void broadcastRapidRollCallPacket() {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = 0x44; // 0x44 = 4s Rapid Attendance Roll Call
    packet.masterMillis = 0;
    packet.activeFloat = myFloatNumber;
    packet.waveHead = 0;
    esp_now_send(broadcastMac, (uint8_t*)&packet, sizeof(packet));
}

void startRapidRollCall(uint32_t now) {
    if (currentStandaloneMode != SHOW_MODE_RAPID_ROLL_CALL) {
        previousStandaloneMode = currentStandaloneMode;
    }
    currentStandaloneMode = SHOW_MODE_RAPID_ROLL_CALL;
    rapidRollCallStartTime = now;
    Serial.printf("[ROLL CALL] ⚡ 4-Second Rapid Attendance Roll Call started! (Initiator: Float %d)\n", myFloatNumber);
}

void renderRapidRollCall(uint32_t elapsedMs) {
    if (elapsedMs < 3500) {
        // Individual float slots: 0 to 6 (500ms each)
        uint8_t activeSlot = elapsedMs / 500; // 0..6
        uint8_t activeFloat = activeSlot + 1; // 1..7

        if (myFloatNumber == activeFloat) {
            // It's our turn! Illuminate brightly in our float's signature color
            CRGB color = FLEET_ROSTER_INFO[activeSlot].color;
            fill_solid(leds, FRONT_LEDS, color);
        } else {
            // Other floats stay completely dark so active runner is spotlighted!
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    } else if (elapsedMs < 4000) {
        // Unison finale: Double Emerald Green flash across all 7 floats!
        uint32_t finaleMs = elapsedMs - 3500;
        if ((finaleMs < 200) || (finaleMs >= 300 && finaleMs < 500)) {
            fill_solid(leds, FRONT_LEDS, CRGB(0, 255, 80)); // Electric Emerald Green
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    } else {
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }

    duplicateFrontToBack();
    FastLED.show();
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
            } else if (packet.mode == 0x44) {
                // 4-Second Rapid Attendance Roll Call commanded by peer
                startRapidRollCall(millis() - packet.masterMillis);
                Serial.printf("[ESP-NOW] ⚡ Rapid Attendance Roll Call triggered by Float %d\n", packet.activeFloat);
            } else if (packet.mode == 0x50) {
                // Corral Standby Mode commanded by Leader/Peer
                currentStandaloneMode = SHOW_MODE_CORRAL_STANDBY;
                Serial.printf("[ESP-NOW] 🌙 Switched to Corral Standby Mode by Float %d\n", packet.activeFloat);
            } else if (packet.mode == 0x51) {
                // Wake from Corral Standby commanded by Leader/Peer
                if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
                    currentStandaloneMode = previousStandaloneMode;
                    autonomousShowStartTime = millis();
                }
                Serial.printf("[ESP-NOW] ☀️ Woke from Corral Standby Mode by Float %d\n", packet.activeFloat);
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
                leds[fwStart + idx] = CRGB::Black;
            }
        } else if (tau < 1650) {
            // Phase 3: Shimmering fade-out / crackle
            uint32_t fadeMs = tau - 1250;
            uint8_t alpha = map(fadeMs, 0, 400, 255, 0);
            if (random8() < alpha) {
                CRGB spark = (step % 2 == 0) ? CRGB(255, 220, 150) : rayColor;
                spark.nscale8_video(alpha);
                leds[fwStart + idx] = spark;
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
    } else {
        // Follower Node: Sync animation to received packets
        if (packetReceived && (now - lastPacketTime < 3000)) {
            uint32_t syncedTime = localSyncTime + (now - lastLocalTick);
            switch (currentPacket.mode) {
                case 0: renderMarqueeChase(syncedTime); break;
                case 1: renderParadeSparkle(syncedTime); break;
                case 2: renderTwinkle(syncedTime); break;
                case 3: renderTravelingWave(currentPacket.activeFloat, currentPacket.waveHead); break;
            }
        } else {
            // Fallback standalone animation if packet lost > 3 seconds
            renderParadeSparkle(now);
            if ((now / 2000) % 2 == 0) {
                digitalWrite(STATUS_LED_PIN, (now / 150) % 2);
            } else {
                digitalWrite(STATUS_LED_PIN, LOW);
            }
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
        fill_solid(leds, NUM_LEDS, CRGB(240, 240, 240));
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, HIGH);
        delay(140);
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

        // 2. Status LED slow pulse
        if ((loopNow / 300) % 2 == 0) {
            uint32_t subCycle = loopNow % 300;
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

// ============================================================================
// AMBIENT FALLBACK RENDERER (used between timeline cues and on empty timelines)
// Respects AMBIENT_FALLBACK_PATTERN compiled from the simulator ambient tab selection
// ============================================================================
static inline CRGB getSparkleColor() {
#if defined(COSTUME_SPARKLE_STYLE) && (COSTUME_SPARKLE_STYLE == 1)
    return CRGB(255, 255, 255); // Diamond cool white
#elif defined(COSTUME_SPARKLE_STYLE) && (COSTUME_SPARKLE_STYLE == 2)
    return CRGB(255, 215, 40);  // Pixie dust golden amber
#else
    return CRGB(255, 240, 200); // 2700K incandescent filament warm white
#endif
}

void renderAmbientFallback(uint32_t now) {
    uint32_t beatMs = 60000 / max((uint16_t)20, (uint16_t)COSTUME_SPEED_BPM);
#if defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_BREATHING_GLOW)
    uint8_t breath = beatsin8(COSTUME_SPEED_BPM / 2, 40, 255);
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_COMET)
    uint32_t passMs = max((uint32_t)900, (uint32_t)(beatMs * 3 / 2));
    uint8_t cometHead = (uint8_t)(((uint64_t)now * FRONT_LEDS / passMs) % FRONT_LEDS);
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_SCANNER)
    uint8_t scanPos = beatsin8(COSTUME_SPEED_BPM / 2, 0, FRONT_LEDS - 1);
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_COLOR_WIPE)
    uint32_t wipeCycle = now % (beatMs * 4);
    float wipeProg = (float)wipeCycle / (float)(beatMs * 4);
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_PISTON_CHUG)
    uint8_t chugStep = ((now / max((uint32_t)20, beatMs / 2)) % 4);
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_FLASHLIGHT)
    uint32_t speedTime = (uint64_t)now * COSTUME_SPEED_BPM / 60;
    uint8_t roamWarp = (uint8_t)(speedTime / 8);
#if defined(COSTUME_AMBIENT_DIRECTION) && (COSTUME_AMBIENT_DIRECTION < 0)
    uint8_t roamX = 128 + ((int8_t)(sin8(roamWarp * 2) - 128) * 85 / 128) - ((int8_t)(sin8(roamWarp * 5) - 128) * 35 / 128);
#else
    uint8_t roamX = 128 + ((int8_t)(sin8(roamWarp * 2) - 128) * 85 / 128) + ((int8_t)(sin8(roamWarp * 5) - 128) * 35 / 128);
#endif
    uint8_t roamY = 128 + ((int8_t)(cos8(roamWarp * 2) - 128) * 80 / 128) + ((int8_t)(sin8(roamWarp * 4) - 128) * 40 / 128);
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_MOUSE_SCAMPER)
    uint32_t scamperMs = max((uint32_t)800, (uint32_t)(beatMs * 3 / 2));
    uint8_t scamperT = (uint8_t)(((uint64_t)now * 256 / scamperMs) * 2);
#if defined(COSTUME_AMBIENT_DIRECTION) && (COSTUME_AMBIENT_DIRECTION < 0)
    uint8_t mouseX = 128 + ((int8_t)(sin8(scamperT * 2) - 128) * 85 / 128) - ((int8_t)(sin8(scamperT * 5) - 128) * 35 / 128);
#else
    uint8_t mouseX = 128 + ((int8_t)(sin8(scamperT * 2) - 128) * 85 / 128) + ((int8_t)(sin8(scamperT * 5) - 128) * 35 / 128);
#endif
    uint8_t mouseY = 128 + ((int8_t)(cos8(scamperT * 2) - 128) * 80 / 128) + ((int8_t)(sin8(scamperT * 4) - 128) * 40 / 128);
#endif

    for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(COSTUME_AMBIENT_COLOR_MODE) && (COSTUME_AMBIENT_COLOR_MODE == 1)
        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
        CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#elif defined(COSTUME_AMBIENT_COLOR_MODE) && (COSTUME_AMBIENT_COLOR_MODE == 2)
        CRGB baseColor = CRGB(255, 210, 120);
#elif defined(COSTUME_AMBIENT_COLOR_MODE) && (COSTUME_AMBIENT_COLOR_MODE == 3) && defined(AMBIENT_CUSTOM_COLOR_RGB)
        CRGB baseColor = AMBIENT_CUSTOM_COLOR_RGB;
#elif defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
        CRGB baseColor = ARTWORK_PALETTE[i];
#else
        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
        CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#endif

#if defined(COSTUME_AMBIENT_DIRECTION) && (COSTUME_AMBIENT_DIRECTION < 0)
        int effIdx = FRONT_LEDS - 1 - i;
#else
        int effIdx = i;
#endif

#if defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_PHOTO_MODE)
        leds[i] = baseColor;
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_BREATHING_GLOW)
        baseColor.nscale8_video(breath);
        leds[i] = baseColor;
        if (COSTUME_SPARKLE_RATE > 0 && random16(10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100)) {
            leds[i] = getSparkleColor();
        }
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_COMET)
        int dist = (cometHead - effIdx + FRONT_LEDS) % FRONT_LEDS;
        if (dist < 18) {
            uint8_t fade = 255 - (dist * 14);
            CRGB c = baseColor;
            c.nscale8_video(fade);
            if (dist == 0) c += CRGB(120, 120, 120);
            leds[i] = c;
        } else {
            CRGB dim = baseColor;
            dim.nscale8_video(20);
            leds[i] = dim;
        }
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_SCANNER)
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
        uint8_t ledX = pgm_read_byte(&SPATIAL_X_BYTE[i]);
        uint8_t scanPos = beatsin8(COSTUME_SPEED_BPM / 2, 10, 245);
        int dist = abs((int)ledX - (int)scanPos);
        if (dist < 26) {
            uint8_t fade = 255 - (dist * 9);
            CRGB c = baseColor;
            c.nscale8_video(fade);
            if (dist < 8) c += CRGB(100, 100, 100);
            leds[i] = c;
        } else {
            CRGB dim = baseColor;
            dim.nscale8_video(25);
            leds[i] = dim;
        }
#else
        int dist = abs(effIdx - scanPos);
        if (dist < 6) {
            uint8_t fade = 255 - (dist * 42);
            CRGB c = baseColor;
            c.nscale8_video(fade);
            if (dist == 0) c += CRGB(100, 100, 100);
            leds[i] = c;
        } else {
            CRGB dim = baseColor;
            dim.nscale8_video(25);
            leds[i] = dim;
        }
#endif
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_COLOR_WIPE)
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
        uint8_t effRank = pgm_read_byte(&SPATIAL_RANK_Y[i]);
#if defined(COSTUME_AMBIENT_DIRECTION) && (COSTUME_AMBIENT_DIRECTION < 0)
        effRank = (FRONT_LEDS - 1) - effRank;
#endif
#else
        int effRank = effIdx;
#endif
        if (wipeProg < 0.40f) {
            float litHead = (wipeProg / 0.40f) * FRONT_LEDS;
            leds[i] = (effRank <= (int)litHead) ? baseColor : CRGB::Black;
        } else if (wipeProg < 0.58f) {
            leds[i] = baseColor;
        } else if (wipeProg < 0.88f) {
            float offHead = ((wipeProg - 0.58f) / 0.30f) * FRONT_LEDS;
            leds[i] = (effRank <= (int)offHead) ? CRGB::Black : baseColor;
        } else {
            leds[i] = CRGB::Black;
        }
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_PIXIE_DUST)
        uint8_t wave = beatsin8(COSTUME_SPEED_BPM / 4, 80, 210, 0, i * 4);
        baseColor.nscale8_video(wave);
        uint16_t sparkleThreshold = map(COSTUME_SPEED_BPM, 20, 180, 6, 28);
        if (random16(1000) < sparkleThreshold) {
            leds[i] = getSparkleColor();
        } else {
            leds[i] = baseColor;
        }
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_FILAMENT_GLOW)
        uint32_t speedTime = (uint64_t)now * COSTUME_SPEED_BPM / 60;
        uint8_t drift = inoise8(i * 40, speedTime / 16);
        uint8_t bright = map(drift, 0, 255, 170, 255);
        baseColor.nscale8_video(bright);
        baseColor.r = qadd8(baseColor.r, 20);
        baseColor.b = qsub8(baseColor.b, 35);
        leds[i] = baseColor;
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_CANDLE_FLICKER)
        uint32_t speedTime = (uint64_t)now * COSTUME_SPEED_BPM / 60;
        uint8_t flick = inoise8(i * 35, speedTime / 18);
        uint8_t bright = map(flick, 0, 255, 110, 255);
        CRGB flame = CRGB(255, 150, 30);
        flame.nscale8_video(bright);
        leds[i] = flame;
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_TIDAL_RIPPLE)
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
        uint8_t rad = pgm_read_byte(&SPATIAL_RADIUS_BYTE[i]);
        uint8_t wave = beatsin8(COSTUME_SPEED_BPM / 2, 40, 255, 0, rad);
        baseColor.nscale8_video(wave);
        leds[i] = baseColor;
#else
        uint8_t wave = beatsin8(COSTUME_SPEED_BPM / 2, 40, 255, 0, abs(i - (FRONT_LEDS / 2)) * 8);
        baseColor.nscale8_video(wave);
        leds[i] = baseColor;
#endif
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_PISTON_CHUG)
        if (chugStep == 0 || chugStep == 2) {
            leds[i] = baseColor + CRGB(70, 70, 70);
        } else {
            baseColor.nscale8_video(60);
            leds[i] = baseColor;
        }
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_RAINBOW_CYCLE)
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
        uint8_t ledX = pgm_read_byte(&SPATIAL_X_BYTE[i]);
        uint8_t ledY = pgm_read_byte(&SPATIAL_Y_BYTE[i]);
        uint8_t spatialPos = (uint8_t)(((uint16_t)ledX * 180 + (uint16_t)ledY * 76) / 256);
        uint8_t hueOffset = (uint8_t)(((now) * 256 / beatMs) % 256);
#if defined(COSTUME_AMBIENT_DIRECTION) && (COSTUME_AMBIENT_DIRECTION < 0)
        leds[i] = CHSV(hueOffset - spatialPos, 240, 255);
#else
        leds[i] = CHSV(hueOffset + spatialPos, 240, 255);
#endif
#else
#if defined(COSTUME_AMBIENT_DIRECTION) && (COSTUME_AMBIENT_DIRECTION < 0)
        uint8_t hueOffset = (uint8_t)(((now) * 256 / beatMs) % 256);
        leds[i] = CHSV(hueOffset - (i * 256 / FRONT_LEDS), 240, 255);
#else
        uint8_t hueOffset = (uint8_t)(((now) * 256 / beatMs) % 256);
        leds[i] = CHSV(hueOffset + (i * 256 / FRONT_LEDS), 240, 255);
#endif
#endif
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_MARQUEE)
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
        uint8_t effRank = pgm_read_byte(&SPATIAL_RANK_Y[i]);
#else
        uint8_t effRank = i;
#endif
#if defined(COSTUME_AMBIENT_DIRECTION) && (COSTUME_AMBIENT_DIRECTION < 0)
        uint8_t step = 3 - (((now * 3) / beatMs) % 3);
#else
        uint8_t step = ((now * 3) / beatMs) % 3;
#endif
        if ((effRank + step) % 3 == 0) {
            leds[i] = CRGB(255, 200, 40);
        } else {
            leds[i] = CRGB(15, 12, 5);
        }
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_FLASHLIGHT)
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
        uint8_t ledX = pgm_read_byte(&SPATIAL_X_BYTE[i]);
        uint8_t ledY = pgm_read_byte(&SPATIAL_Y_BYTE[i]);
        int16_t dx = (int16_t)ledX - (int16_t)roamX;
        int16_t dy = (int16_t)ledY - (int16_t)roamY;
        uint16_t distSq = (dx * dx + dy * dy);
        if (distSq < 550) {
            uint8_t fade = 255 - (distSq * 255 / 550);
            CRGB c = baseColor;
            c.nscale8_video(fade);
            if (distSq < 110) c += CRGB(100, 100, 100);
            leds[i] = c;
        } else {
            CRGB dim = baseColor;
            dim.nscale8_video(20);
            leds[i] = dim;
        }
#else
        int dist = abs(effIdx - ((now / max((uint32_t)10, beatMs / 8)) % FRONT_LEDS));
        if (dist < 8) {
            uint8_t fade = 255 - (dist * 30);
            CRGB c = baseColor;
            c.nscale8_video(fade);
            if (dist == 0) c += CRGB(100, 100, 100);
            leds[i] = c;
        } else {
            CRGB dim = baseColor;
            dim.nscale8_video(20);
            leds[i] = dim;
        }
#endif
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_MOUSE_SCAMPER)
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
        uint8_t ledX = pgm_read_byte(&SPATIAL_X_BYTE[i]);
        uint8_t ledY = pgm_read_byte(&SPATIAL_Y_BYTE[i]);
        int16_t dx = (int16_t)ledX - (int16_t)mouseX;
        int16_t dy = (int16_t)ledY - (int16_t)mouseY;
        uint16_t distSq = (dx * dx + dy * dy);
        if (distSq < 280) {
            uint8_t fade = 255 - (distSq * 255 / 280);
            CRGB c = baseColor;
            c.nscale8_video(fade);
            if (distSq < 45) c += CRGB(140, 140, 140);
            leds[i] = c;
        } else {
            CRGB dim = baseColor;
            dim.nscale8_video(20);
            leds[i] = dim;
        }
#else
        int dist = abs(effIdx - ((now / max((uint32_t)10, beatMs / 8)) % FRONT_LEDS));
        if (dist < 8) {
            uint8_t fade = 255 - (dist * 30);
            CRGB c = baseColor;
            c.nscale8_video(fade);
            if (dist == 0) c += CRGB(140, 140, 140);
            leds[i] = c;
        } else {
            CRGB dim = baseColor;
            dim.nscale8_video(20);
            leds[i] = dim;
        }
#endif
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_OFF)
        leds[i] = CRGB::Black;
#else
        // Default: Steady Sparkle – artwork colors with occasional starlight
        leds[i] = baseColor;
        if (COSTUME_SPARKLE_RATE > 0 && random16(10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100)) {
            leds[i] = getSparkleColor();
        }
#endif
    }
}

void runAutonomousShowSequence(uint32_t now) {
#if defined(ACTIVE_COSTUME_PATTERN) && (ACTIVE_COSTUME_PATTERN == COSTUME_PATTERN_FIREWORKS)
    renderFireworks(now);
    duplicateFrontToBack();
    FastLED.show();
    delay(15);
    return;
#endif

    if (autonomousShowStartTime == 0) {
        autonomousShowStartTime = now;
    }
    uint32_t seqTime = (now - autonomousShowStartTime) % SHOW_LOOP_MS;

#if defined(ACTIVE_COSTUME_PATTERN) && (ACTIVE_COSTUME_PATTERN == COSTUME_PATTERN_AUTONOMOUS_90S)
    // ------------------------------------------------------------------------
    // 90-SECOND THEATRICAL SHOW ROUTINE (Compiled Timeline Cues)
    // ------------------------------------------------------------------------
#if defined(HAS_CUSTOM_SEQUENCE_CUES) && HAS_CUSTOM_SEQUENCE_CUES
    bool cueHandled = false;
    for (int c = 0; c < CUSTOM_SEQUENCE_CUE_COUNT; c++) {
        uint32_t sMs = pgm_read_dword(&CUSTOM_SEQUENCE_CUES[c].startMs);
        uint32_t eMs = pgm_read_dword(&CUSTOM_SEQUENCE_CUES[c].endMs);
        if (seqTime >= sMs && seqTime < eMs) {
            uint8_t eff = pgm_read_byte(&CUSTOM_SEQUENCE_CUES[c].effect);
            uint16_t bpm = pgm_read_word(&CUSTOM_SEQUENCE_CUES[c].speedBpm);
            if (eff == 1) { // breathe / pulse
                uint32_t beatMs = 60000 / max((uint16_t)20, bpm);
                float normTime = (float)(now - autonomousShowStartTime) / (float)beatMs;
                float sine = sinf(normTime * 6.2831853f) * 0.5f + 0.5f;
                // High contrast smooth pulse from 15% dim to 100% radiant full power
                float breathFactor = 0.15f + 0.85f * sine;
                uint8_t breathScale = (uint8_t)(breathFactor * 255.0f);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB baseColor = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                    baseColor.nscale8_video(breathScale);
                    leds[i] = baseColor;
                }
            } else if (eff == 2) { // fire_breath
                renderFireworks(now);
            } else if (eff == 3) { // traveling_wave
                uint32_t waveTimer = now % 3000;
                uint8_t waveHeadPos = map(waveTimer, 0, 3000, 0, FRONT_LEDS - 1);
                renderTravelingWave(myFloatNumber, waveHeadPos);
            } else if (eff == 4) { // chase / marquee
                uint8_t step = (now / 120) % FRONT_LEDS;
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    int dist = (i - step + FRONT_LEDS) % FRONT_LEDS;
                    if (dist < 8) {
                        leds[i] = CRGB(255, 255, 220);
                    } else {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                        CRGB dim = ARTWORK_PALETTE[i];
#else
                        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                        CRGB dim = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                        dim.nscale8_video(60);
                        leds[i] = dim;
                    }
                }
            } else if (eff == 5) { // photo_mode / off — solid artwork, zero sparkle
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    leds[i] = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    leds[i] = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                    // No sparkle — perfect for photo moments
                }
            } else if (eff == 6) { // fireworks
                renderFireworks(now);
            } else if (eff == 7) { // flash_slow — slow on/off blink (bpm controls speed)
                uint32_t beatMs = 60000 / max((uint16_t)20, bpm);
                bool lit = (((now - autonomousShowStartTime) / beatMs) % 2 == 0);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB baseColor = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                    leds[i] = lit ? baseColor : CRGB::Black;
                }
            } else if (eff == 8) { // comet / chase
                uint32_t beatMs = 60000 / max((uint16_t)20, bpm);
                uint8_t cometHead = ((now / max((uint32_t)10, beatMs / 8)) % FRONT_LEDS);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    int dist = (cometHead - i + FRONT_LEDS) % FRONT_LEDS;
                    if (dist < 10) {
                        uint8_t fade = 255 - (dist * 25);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                        CRGB c = ARTWORK_PALETTE[i];
#else
                        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                        CRGB c = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                        c.nscale8_video(fade);
                        if (dist == 0) c += CRGB(120, 120, 120);
                        leds[i] = c;
                    } else {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                        CRGB dim = ARTWORK_PALETTE[i];
#else
                        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                        CRGB dim = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                        dim.nscale8_video(25);
                        leds[i] = dim;
                    }
                }
            } else if (eff == 9) { // scanner
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
                uint8_t scanPos = beatsin8(bpm / 2, 10, 245);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    uint8_t ledX = pgm_read_byte(&SPATIAL_X_BYTE[i]);
                    int dist = abs((int)ledX - (int)scanPos);
                    if (dist < 26) {
                        uint8_t fade = 255 - (dist * 9);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                        CRGB c = ARTWORK_PALETTE[i];
#else
                        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                        CRGB c = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                        c.nscale8_video(fade);
                        if (dist < 8) c += CRGB(100, 100, 100);
                        leds[i] = c;
                    } else {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                        CRGB dim = ARTWORK_PALETTE[i];
#else
                        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                        CRGB dim = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                        dim.nscale8_video(25);
                        leds[i] = dim;
                    }
                }
#else
                uint8_t scanPos = beatsin8(bpm / 2, 0, FRONT_LEDS - 1);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    int dist = abs(i - scanPos);
                    if (dist < 6) {
                        uint8_t fade = 255 - (dist * 42);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                        CRGB c = ARTWORK_PALETTE[i];
#else
                        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                        CRGB c = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                        c.nscale8_video(fade);
                        if (dist == 0) c += CRGB(100, 100, 100);
                        leds[i] = c;
                    } else {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                        CRGB dim = ARTWORK_PALETTE[i];
#else
                        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                        CRGB dim = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                        dim.nscale8_video(25);
                        leds[i] = dim;
                    }
                }
#endif
            } else if (eff == 10) { // write_on_off / color_wipe
                uint32_t totalCycleMs = (60000 / max((uint16_t)20, bpm)) * 4;
                uint32_t progressMs = (now - autonomousShowStartTime) % totalCycleMs;
                float progress = (float)progressMs / (float)totalCycleMs;
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB baseColor = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#endif
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
                    uint8_t effRank = pgm_read_byte(&SPATIAL_RANK_Y[i]);
#else
                    uint8_t effRank = i;
#endif
                    if (progress < 0.40f) {
                        float litHead = (progress / 0.40f) * FRONT_LEDS;
                        leds[i] = (effRank <= (int)litHead) ? baseColor : CRGB::Black;
                    } else if (progress < 0.58f) {
                        leds[i] = baseColor;
                    } else if (progress < 0.88f) {
                        float offHead = ((progress - 0.58f) / 0.30f) * FRONT_LEDS;
                        leds[i] = (effRank <= (int)offHead) ? CRGB::Black : baseColor;
                    } else {
                        leds[i] = CRGB::Black;
                    }
                }
            } else if (eff == 11) { // pixie_dust
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    uint8_t wave = beatsin8(bpm / 3, 40, 180, 0, i * 4);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB c = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB c = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                    c.nscale8_video(wave);
                    if (random16(1000) < 22) {
                        leds[i] = CRGB(255, 255, 240);
                    } else {
                        leds[i] = c;
                    }
                }
            } else if (eff == 12) { // filament_glow
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    uint8_t drift = inoise8(i * 40, now / 20);
                    uint8_t bright = map(drift, 0, 255, 170, 255);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB c = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB c = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                    c.nscale8_video(bright);
                    c.r = qadd8(c.r, 20);
                    c.b = qsub8(c.b, 35);
                    leds[i] = c;
                }
            } else if (eff == 13) { // candle_flicker
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    uint8_t flick = inoise8(i * 60, now / 8);
                    uint8_t bright = map(flick, 0, 255, 60, 255);
                    CRGB flame = CRGB(255, 150, 30);
                    flame.nscale8_video(bright);
                    leds[i] = flame;
                }
            } else if (eff == 14) { // tidal_ripple
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    uint8_t rad = pgm_read_byte(&SPATIAL_RADIUS_BYTE[i]);
                    uint8_t wave = beatsin8(bpm / 2, 40, 255, 0, rad);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB c = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB c = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                    c.nscale8_video(wave);
                    leds[i] = c;
                }
#else
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    uint8_t wave = beatsin8(bpm / 2, 40, 255, 0, abs(i - (FRONT_LEDS / 2)) * 8);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB c = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB c = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                    c.nscale8_video(wave);
                    leds[i] = c;
                }
#endif
            } else if (eff == 15) { // piston_chug
                uint32_t beatMs = 60000 / max((uint16_t)20, bpm);
                uint8_t chugStep = ((now / max((uint32_t)20, beatMs / 2)) % 4);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB baseColor = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                    if (chugStep == 0 || chugStep == 2) {
                        leds[i] = baseColor + CRGB(70, 70, 70);
                    } else {
                        baseColor.nscale8_video(60);
                        leds[i] = baseColor;
                    }
                }
            } else if (eff == 16) { // rainbow_cycle — flowing chromatic wave
                uint8_t hueOffset = (uint8_t)(((now - autonomousShowStartTime) * 256 / (60000 / max((uint16_t)20, bpm))) % 256);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
                    uint8_t ledX = pgm_read_byte(&SPATIAL_X_BYTE[i]);
                    uint8_t ledY = pgm_read_byte(&SPATIAL_Y_BYTE[i]);
                    uint8_t spatialPos = (uint8_t)(((uint16_t)ledX * 180 + (uint16_t)ledY * 76) / 256);
                    leds[i] = CHSV(hueOffset + spatialPos, 240, 255);
#else
                    leds[i] = CHSV(hueOffset + (i * 256 / FRONT_LEDS), 240, 255);
#endif
                }
            } else if (eff == 17) { // off / blackout
                fill_solid(leds, FRONT_LEDS, CRGB::Black);
            } else if (eff == 18) { // flashlight / searchlight roam
                uint32_t speedTime = (uint64_t)(now - autonomousShowStartTime) * bpm / 60;
                uint8_t roamWarp = (uint8_t)(speedTime / 8);
                uint8_t roamX = 128 + ((int8_t)(sin8(roamWarp * 2) - 128) * 85 / 128) + ((int8_t)(sin8(roamWarp * 5) - 128) * 35 / 128);
                uint8_t roamY = 128 + ((int8_t)(cos8(roamWarp * 2) - 128) * 80 / 128) + ((int8_t)(sin8(roamWarp * 4) - 128) * 40 / 128);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB baseColor = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#endif
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
                    uint8_t ledX = pgm_read_byte(&SPATIAL_X_BYTE[i]);
                    uint8_t ledY = pgm_read_byte(&SPATIAL_Y_BYTE[i]);
                    int16_t dx = (int16_t)ledX - (int16_t)roamX;
                    int16_t dy = (int16_t)ledY - (int16_t)roamY;
                    uint16_t distSq = (dx * dx + dy * dy);
                    if (distSq < 550) {
                        uint8_t fade = 255 - (distSq * 255 / 550);
                        CRGB c = baseColor;
                        c.nscale8_video(fade);
                        if (distSq < 110) c += CRGB(100, 100, 100);
                        leds[i] = c;
                    } else {
                        CRGB dim = baseColor;
                        dim.nscale8_video(20);
                        leds[i] = dim;
                    }
#else
                    leds[i] = baseColor;
#endif
                }
            } else if (eff == 19) { // mouse_scamper — single dot + sharp meteor tail following 2D smooth trajectory
                uint32_t scamperMs = max((uint32_t)800, (uint32_t)(60000 / max((uint16_t)20, bpm) * 3 / 2));
                uint8_t scamperT = (uint8_t)(((uint64_t)(now - autonomousShowStartTime) * 256 / scamperMs) * 2);
                uint8_t mouseX = 128 + ((int8_t)(sin8(scamperT * 2) - 128) * 85 / 128) + ((int8_t)(sin8(scamperT * 5) - 128) * 35 / 128);
                uint8_t mouseY = 128 + ((int8_t)(cos8(scamperT * 2) - 128) * 80 / 128) + ((int8_t)(sin8(scamperT * 4) - 128) * 40 / 128);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB baseColor = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#endif
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
                    uint8_t ledX = pgm_read_byte(&SPATIAL_X_BYTE[i]);
                    uint8_t ledY = pgm_read_byte(&SPATIAL_Y_BYTE[i]);
                    int16_t dx = (int16_t)ledX - (int16_t)mouseX;
                    int16_t dy = (int16_t)ledY - (int16_t)mouseY;
                    uint16_t distSq = (dx * dx + dy * dy);
                    if (distSq < 280) {
                        uint8_t fade = 255 - (distSq * 255 / 280);
                        CRGB c = baseColor;
                        c.nscale8_video(fade);
                        if (distSq < 45) c += CRGB(140, 140, 140);
                        leds[i] = c;
                    } else {
                        CRGB dim = baseColor;
                        dim.nscale8_video(20);
                        leds[i] = dim;
                    }
#else
                    int dist = abs(i - ((now / max((uint32_t)10, scamperMs / 8)) % FRONT_LEDS));
                    if (dist < 8) {
                        uint8_t fade = 255 - (dist * 30);
                        CRGB c = baseColor;
                        c.nscale8_video(fade);
                        if (dist == 0) c += CRGB(140, 140, 140);
                        leds[i] = c;
                    } else {
                        CRGB dim = baseColor;
                        dim.nscale8_video(20);
                        leds[i] = dim;
                    }
#endif
                }
            } else { // 0: steady_sparkle / default
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    leds[i] = ARTWORK_PALETTE[i];
#else
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    leds[i] = FLEET_ROSTER_INFO[floatIdx].color;
#endif
                    if (COSTUME_SPARKLE_RATE > 0 && random16(10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100)) {
                        leds[i] = CRGB(255, 255, 240);
                    }
                }
            }
            cueHandled = true;
            break;
        }
    }
    if (!cueHandled) {
        renderAmbientFallback(now); // Gaps between cues: use configured ambient program
    }
#else
    renderAmbientFallback(now); // Empty timeline: use configured ambient program
#endif
#elif defined(ACTIVE_COSTUME_PATTERN) && (ACTIVE_COSTUME_PATTERN == COSTUME_PATTERN_BREATHING_GLOW)
    // Continuous Breathing Glow
    uint8_t breath = beatsin8(COSTUME_SPEED_BPM / 2, 120, 255);
    for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
        CRGB baseColor = ARTWORK_PALETTE[i];
#else
        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
        CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#endif
        baseColor.nscale8_video(breath);
        leds[i] = baseColor;
        if (COSTUME_SPARKLE_RATE > 0 && random16(10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100)) {
            leds[i] = CRGB(255, 255, 240);
        }
    }
#elif defined(ACTIVE_COSTUME_PATTERN) && (ACTIVE_COSTUME_PATTERN == COSTUME_PATTERN_PHOTO_MODE)
    // Continuous Photo Mode (Static Artwork)
    for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
        leds[i] = ARTWORK_PALETTE[i];
#else
        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
        leds[i] = FLEET_ROSTER_INFO[floatIdx].color;
#endif
    }
#elif defined(ACTIVE_COSTUME_PATTERN) && (ACTIVE_COSTUME_PATTERN == COSTUME_PATTERN_MARQUEE)
    renderMarqueeChase(now);
#elif defined(ACTIVE_COSTUME_PATTERN) && (ACTIVE_COSTUME_PATTERN == COSTUME_PATTERN_TRAVELING_WAVE)
    uint32_t waveTimer = now % 3000;
    uint8_t waveHeadPos = map(waveTimer, 0, 3000, 0, FRONT_LEDS - 1);
    renderTravelingWave(myFloatNumber, waveHeadPos);
#else
    // ------------------------------------------------------------------------
    // DEFAULT SOLO PATTERN: Continuous Sampled Artwork + Starlight Sparkles (Option A)
    // ------------------------------------------------------------------------
    for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
        leds[i] = ARTWORK_PALETTE[i];
#else
        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
        leds[i] = FLEET_ROSTER_INFO[floatIdx].color;
#endif
        if (COSTUME_SPARKLE_RATE > 0 && random16(10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100)) {
            leds[i] = CRGB(255, 255, 240);
        }
    }
#endif

    duplicateFrontToBack();

    for (int i = NUM_LEDS; i < MAX_LEDS_CAPACITY; i++) {
        leds[i] = CRGB::Black;
    }

    FastLED.show();
    delay(15);
}

void render30sFleetRoutine(uint32_t elapsedMs) {
    if (elapsedMs < 6000) {
        renderMarqueeChase(elapsedMs);
    } else if (elapsedMs < 12000) {
        renderParadeSparkle(elapsedMs);
    } else if (elapsedMs < 18000) {
        renderTwinkle(elapsedMs);
    } else if (elapsedMs < 25000) {
        uint32_t waveTimer = elapsedMs - 12000;
        uint8_t activeFloat = (waveTimer / 1000) + 1;
        uint32_t floatTime = waveTimer % 1000;
        uint8_t waveHeadPos = map(floatTime, 0, 1000, 0, FRONT_LEDS - 1);
        renderTravelingWave(activeFloat, waveHeadPos);
    } else if (elapsedMs < 30000) {
        renderFireworks(elapsedMs);
    } else {
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }

    duplicateFrontToBack();
    FastLED.show();
}

// ============================================================================
// ARDUINO MAIN SETUP
// ============================================================================
void setup() {
    Serial.begin(115200);
    delay(500);

    Serial.println("\n========================================================");
    Serial.println("  🏰 MAIN STREET ELECTRICAL PARADE - LED COSTUME FLEET");
    Serial.println("  Walt Disney World 10K Synchronized Control System");
    Serial.println("  Repository: https://github.com/kidmd/WDW-costumes");
    Serial.println("========================================================\n");

    // Disable brownout detector during high current spikes
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

    pinMode(STATUS_LED_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, LOW);

    pinMode(BUTTON_PIN, INPUT_PULLUP);

    // 1. Initialize Wi-Fi in Station Mode (no router connection required for ESP-NOW)
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(50);

    // Also attempt connecting to local Wi-Fi if credentials configured (Fast non-blocking 1.5s check)
#if defined(WIFI_SSID) && defined(WIFI_PASSWORD)
    String ssid = WIFI_SSID;
    if (ssid.length() > 0 && ssid != "YourWiFiNetwork") {
        Serial.printf("[WIFI] Connecting to '%s'...\n", WIFI_SSID);
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        uint32_t t0 = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - t0 < 1500) {
            delay(50);
            digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
        }
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("[WIFI] Connected! IP Address: %s\n", WiFi.localIP().toString().c_str());
        digitalWrite(STATUS_LED_PIN, HIGH);
    } else {
        digitalWrite(STATUS_LED_PIN, LOW);
        Serial.println("[WIFI] Offline mode active (ESP-NOW direct fleet sync ready).");
#if defined(AP_SSID)
        // Also enable SoftAP so laptops can connect directly without home router
        WiFi.mode(WIFI_AP_STA);
        WiFi.softAP(AP_SSID, AP_PASSWORD);
        Serial.printf("[WIFI] Standalone Hotspot Active: '%s' (IP: %s)\n", AP_SSID, WiFi.softAPIP().toString().c_str());
#endif
    }
#else
    Serial.println("[WIFI] Running in direct offline mode (ESP-NOW ready).");
#endif

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
    // - Leader (Float 1):
    //   - Power-on: Boots directly into Corral Standby Mode (<120mA)
    //   - Single Tap in Standby: Wakes ENTIRE FLEET to active parade mode (Mode 0x51)
    //   - Single Tap in Active Run: Starts/stops 30s Theatrical Fleet Show (Mode 0x30 / 0x00)
    //   - Double Tap: Triggers 4s Rapid Attendance Roll Call wave across entire fleet (Mode 0x44)
    //   - Triple Tap: Drops ENTIRE FLEET into Corral Standby Mode (Mode 0x50)
    // - Followers (Floats 2-7):
    //   - Single Tap in Standby: Wakes THAT RUNNER ONLY locally
    //   - Single Tap in Active Run: Ignored (zero fleet disruption)
    //   - Double Tap: Ignored (roll call reserved for Leader)
    //   - Triple Tap: Drops THAT RUNNER ONLY into Corral Standby Mode
    // - Long Hold (>= 5.0s): Float ID Configuration Mode (1 to 7)
    static bool buttonWasPressed = false;
    static uint32_t buttonDownTime = 0;
    static uint32_t lastButtonReleaseTime = 0;
    static bool longHoldHandled = false;
    static uint8_t pendingTapCount = 0;
    static uint32_t firstTapReleaseTime = 0;

    bool isButtonPressed = (digitalRead(BUTTON_PIN) == LOW);

    if (isButtonPressed && !buttonWasPressed) {
        buttonWasPressed = true;
        buttonDownTime = now;
        longHoldHandled = false;
    } else if (isButtonPressed && buttonWasPressed) {
        uint32_t holdElapsed = now - buttonDownTime;
        if (!longHoldHandled) {
            if (holdElapsed >= 5000) {
                longHoldHandled = true;
                pendingTapCount = 0; // Cancel any pending taps
                handleFloatConfigMode();
                buttonWasPressed = false;
                return;
            } else if (holdElapsed >= 1000) {
                // Progressive charging indicator (1 to 4 LEDs lit in white)
                uint8_t chargeCount = (holdElapsed / 1000); // 1, 2, 3, or 4
                if (chargeCount > 4) chargeCount = 4;

                // Show charging indicator on first 'chargeCount' LEDs, remaining LEDs black
                for (int i = 0; i < FRONT_LEDS; i++) {
                    if (i < chargeCount) {
                        leds[i] = CRGB(255, 255, 255); // Crisp full-white charging indicator
                    } else {
                        leds[i] = CRGB::Black;
                    }
                }
                duplicateFrontToBack();
                FastLED.show();
                return; // Stop loop here so baseline show does not overwrite charging LEDs!
            }
        }
    } else if (!isButtonPressed && buttonWasPressed) {
        buttonWasPressed = false;
        uint32_t pressDuration = now - buttonDownTime;

        if (pressDuration >= 1000 && !longHoldHandled) {
            Serial.printf("[BUTTON] Hold aborted after %u ms -> returning to baseline with zero changes.\n", pressDuration);
        }

        // Tap handling: recognize intentional taps under 600ms (50ms hardware debounce)
        if (!longHoldHandled && pressDuration >= 50 && pressDuration < 600) {
            if (pendingTapCount == 2 && (now - firstTapReleaseTime <= 600)) {
                // TRIPLE TAP DETECTED!
                pendingTapCount = 0;
                lastButtonReleaseTime = now;

                currentStandaloneMode = SHOW_MODE_CORRAL_STANDBY;
                for (int f = 0; f < 3; f++) {
                    fill_solid(leds, NUM_LEDS, CRGB(30, 60, 255)); // 3 Soft Indigo pulses
                    FastLED.show();
                    digitalWrite(STATUS_LED_PIN, HIGH);
                    delay(80);
                    fill_solid(leds, NUM_LEDS, CRGB::Black);
                    FastLED.show();
                    digitalWrite(STATUS_LED_PIN, LOW);
                    delay(60);
                }

                if (isLeader) {
                    broadcastStandbyPacket(0x50);
                    Serial.println("[LEADER] 🌙 Triple Tap -> Dropped ENTIRE FLEET into Corral Standby Mode!");
                } else {
                    Serial.printf("[FOLLOWER] Float %d Triple Tap -> Dropped locally into Corral Standby Mode.\n", myFloatNumber);
                }
            } else if (pendingTapCount == 1 && (now - firstTapReleaseTime <= 400)) {
                // SECOND TAP DETECTED -> DOUBLE TAP!
                pendingTapCount = 2; // Arm for possible 3rd tap within 600ms total
                lastButtonReleaseTime = now;
            } else {
                // FIRST TAP DETECTED -> wait for potential second/third tap
                pendingTapCount = 1;
                firstTapReleaseTime = now;
                lastButtonReleaseTime = now;
            }
        }
    }

    // Evaluate pending multi-tap once window expires and button is not currently held
    if (pendingTapCount > 0 && !isButtonPressed && (now - firstTapReleaseTime > 400)) {
        uint8_t tapType = pendingTapCount;
        pendingTapCount = 0;

        if (tapType == 1) {
            // SINGLE TAP EVALUATION
            if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
                // WAKE UP FROM CORRAL STANDBY
                currentStandaloneMode = previousStandaloneMode;
                autonomousShowStartTime = now;

                // Visual confirmation: 1 Emerald Green flash
                fill_solid(leds, NUM_LEDS, CRGB(0, 255, 80));
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, HIGH);
                delay(150);
                fill_solid(leds, NUM_LEDS, CRGB::Black);
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, LOW);

                if (isLeader) {
                    broadcastStandbyPacket(0x51); // Wake entire fleet!
                    Serial.println("[LEADER] ☀️ Single Tap -> Woke ENTIRE FLEET from Corral Standby!");
                } else {
                    Serial.printf("[FOLLOWER] Float %d Single Tap -> Woke locally from Corral Standby.\n", myFloatNumber);
                }
            } else if (isLeader) {
                // LEADER ACTIVE RUN TOGGLE: 30s Fleet Show Routine
                if (currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE || currentStandaloneMode == SHOW_MODE_RAPID_ROLL_CALL) {
                    currentStandaloneMode = previousStandaloneMode;
                    broadcastFleetRoutinePacket(0x00, 0);
                    Serial.println("[LEADER] Early stop triggered via BOOT button -> returning to baseline.");
                    
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
                    fleetRoutineCycle++;
                    fleetRoutineStartTime = now;
                    previousStandaloneMode = currentStandaloneMode;
                    currentStandaloneMode = SHOW_MODE_FLEET_30S_ROUTINE;
                    broadcastFleetRoutinePacket(0x30, 0);
                    Serial.printf("[LEADER] 30s Fleet Show started via BOOT button! (Cycle #%u)\n", fleetRoutineCycle);
                }
            } else {
                Serial.printf("[FOLLOWER] Float %d single tap ignored while running (Show trigger reserved for Leader).\n", myFloatNumber);
            }
        } else if (tapType == 2) {
            // DOUBLE TAP EVALUATION (LEADER ONLY)
            if (isLeader) {
                startRapidRollCall(now);
                broadcastRapidRollCallPacket();
                Serial.println("[LEADER] ⚡ 4-Second Rapid Attendance Roll Call started!");
            } else {
                Serial.printf("[FOLLOWER] Float %d double tap ignored (Roll call wave reserved for Leader).\n", myFloatNumber);
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
            } else if (buffer[4] == 0x03 && len >= 6) {
                // Opcode 0x03: Corral Roll Call & Radar Diagnostics
                uint8_t cmd = buffer[5];
                uint8_t targetFloatId = (len >= 7) ? buffer[6] : 0;
                if (cmd == 0x02) {
                    // Identify Flash
                    if (targetFloatId == 0 || targetFloatId == myFloatNumber) {
                        triggerIdentifyFlash();
                    }
                } else if (cmd == 0x03) {
                    // ⚡ Rapid Attendance Roll Call
                    startRapidRollCall(millis());
                    broadcastRapidRollCallPacket();
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
        if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
            renderCorralStandby(now);
            duplicateFrontToBack();
            FastLED.show();
            delay(20);
        } else if (currentStandaloneMode == SHOW_MODE_RAPID_ROLL_CALL) {
            uint32_t elapsedMs = now - rapidRollCallStartTime;
            if (elapsedMs < RAPID_ROLL_CALL_TOTAL_MS) {
                renderRapidRollCall(elapsedMs);
            } else {
                currentStandaloneMode = previousStandaloneMode;
                fill_solid(leds, NUM_LEDS, CRGB::Black);
                FastLED.show();
                Serial.println("[ROLL CALL] ⚡ Rapid Attendance Roll Call complete -> returned to baseline.");
            }
        } else if (currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE) {
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
