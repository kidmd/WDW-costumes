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

// HARDWARE BUTTON DEFINITIONS
#define BUTTON_1_PIN        4       // Primary Show Director button (External tact switch to GND)
#define BUTTON_2_PIN        33      // Auxiliary Photo / Sleep button (External tact switch to GND)
#define BUTTON_BOOT_PIN     0       // BOOT button on standard ESP32 DevKit (Fallback in parallel with Button 1)
#define SHOW_LOOP_MS        90000   // 90-second autonomous theatrical sequence
#define FLEET_ROUTINE_TOTAL_MS 30000 // Auto-updated for 30s Grand Electrical Parade Show (30.0s)
#define RAPID_ROLL_CALL_TOTAL_MS 4000 // 4.0-second Rapid Attendance Roll Call (500ms x 7 floats + 500ms unison finale)

enum StandaloneShowMode {
    SHOW_MODE_AUTONOMOUS_SEQUENCE = 0,
    SHOW_MODE_FLEET_SYNC          = 1,
    SHOW_MODE_FLEET_30S_ROUTINE   = 2,
    SHOW_MODE_RAPID_ROLL_CALL     = 3,
    SHOW_MODE_CORRAL_STANDBY      = 4,
    SHOW_MODE_PHOTO_STATIC        = 5   // 📸 Castle Photo Mode: solid steady hero illumination
};

inline bool isButton1Down() {
    return (digitalRead(BUTTON_1_PIN) == LOW) || (digitalRead(BUTTON_BOOT_PIN) == LOW);
}

inline bool isButton2Down() {
    return (digitalRead(BUTTON_2_PIN) == LOW);
}

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

void broadcastPhotoModePacket(uint8_t mode) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = mode; // 0x46 = Photo Mode ON, 0x47 = Photo Mode OFF
    packet.masterMillis = millis();
    packet.activeFloat = myFloatNumber;
    packet.waveHead = 0;
    esp_now_send(broadcastMac, (uint8_t*)&packet, sizeof(packet));
}

void renderCastlePhotoMode() {
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB heroColor = FLEET_ROSTER_INFO[floatIdx].color;
    fill_solid(leds, FRONT_LEDS, heroColor);
    duplicateFrontToBack();
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
                if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
                    previousStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                } else if (currentStandaloneMode != SHOW_MODE_FLEET_30S_ROUTINE) {
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
            } else if (packet.mode == 0x46) {
                // Castle Photo Mode ON commanded by Leader/Peer
                if (currentStandaloneMode != SHOW_MODE_PHOTO_STATIC) {
                    previousStandaloneMode = currentStandaloneMode;
                }
                currentStandaloneMode = SHOW_MODE_PHOTO_STATIC;
                Serial.printf("[ESP-NOW] 📸 Castle Photo Mode engaged across fleet by Float %d\n", packet.activeFloat);
            } else if (packet.mode == 0x47) {
                // Castle Photo Mode OFF commanded by Leader/Peer
                if (currentStandaloneMode == SHOW_MODE_PHOTO_STATIC) {
                    currentStandaloneMode = previousStandaloneMode;
                }
                Serial.printf("[ESP-NOW] 📸 Castle Photo Mode disengaged by Float %d -> returned to parade mode\n", packet.activeFloat);
            } else if (packet.mode == 0x50) {
                // Corral Standby Mode commanded by Leader/Peer
                currentStandaloneMode = SHOW_MODE_CORRAL_STANDBY;
                Serial.printf("[ESP-NOW] 🌙 Switched to Corral Standby Mode by Float %d\n", packet.activeFloat);
            } else if (packet.mode == 0x51) {
                // Wake from Corral Standby commanded by Leader/Peer into Solo Show Mode
                if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
                    currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                    previousStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                    autonomousShowStartTime = millis();
                }
                Serial.printf("[ESP-NOW] ☀️ Woke from Corral Standby into Solo Show Mode by Float %d\n", packet.activeFloat);
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
    isLeader = (myFloatNumber == 1 || myFloatNumber == 7);
    
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

    if (myFloatNumber == 1) {
        Serial.printf("[ROLE] *** PRIMARY LEADER (Float 1 - %s) *** (ESP-NOW Tx/Rx ready)\n", FLEET_ROSTER_INFO[0].name);
    } else if (myFloatNumber == 7) {
        Serial.printf("[ROLE] *** CO-LEADER / REAR MARSHAL (Float 7 - %s) *** (ESP-NOW Tx/Rx ready)\n", FLEET_ROSTER_INFO[6].name);
    } else {
        Serial.printf("[ROLE] >>> FOLLOWER (Float %d - %s) <<< (ESP-NOW Tx/Rx ready)\n", 
                      myFloatNumber, FLEET_ROSTER_INFO[myFloatNumber - 1].name);
    }
}

// ============================================================================
// HARDWARE BUTTON & STANDALONE SHOW SEQUENCE (Autonomous Float Mode)
// ============================================================================

// Interactive Float ID Configuration via Button 1 (Held for 5 seconds)
void handleFloatConfigMode() {
    Serial.println("\n========================================================");
    Serial.println("  >>> ENTERED FLOAT ID CONFIGURATION MODE <<<");
    Serial.println("  Tap Button 1 (or BOOT) to cycle Float 1 -> 7");
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

    // Wait until Button 1 is released
    while (isButton1Down()) {
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

        // 3. Handle button tap to cycle float ID (Button 1 or BOOT)
        bool isDown = isButton1Down();
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
    uint32_t scamperPassMs = max((uint32_t)700, (uint32_t)(beatMs * 3 / 2));
    uint8_t tCurr = (uint8_t)(((uint64_t)now * 256 / scamperPassMs) * 2);
#if defined(COSTUME_AMBIENT_DIRECTION) && (COSTUME_AMBIENT_DIRECTION < 0)
    int8_t mouseDir = -1;
#else
    int8_t mouseDir = 1;
#endif
    uint8_t headX = 128 + ((int8_t)(sin8(tCurr * 11 / 10 * mouseDir) - 128) * 85 / 128) + ((int8_t)(sin8(tCurr * 23 / 10) - 128) * 35 / 128);
    uint8_t headY = 128 + ((int8_t)(cos8(tCurr * 8 / 10) - 128) * 80 / 128) + ((int8_t)(sin8(tCurr * 19 / 10 * mouseDir) - 128) * 40 / 128);
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
        int16_t dx = (int16_t)ledX - (int16_t)headX;
        int16_t dy = (int16_t)ledY - (int16_t)headY;
        uint16_t dHeadSq = (dx * dx + dy * dy);

        // Check historical path behind the head (long graceful tail)
        uint8_t maxTailFade = 0;
        for (uint8_t s = 1; s <= 16; s++) {
            uint8_t tPast = tCurr - (s * 5 * mouseDir);
            uint8_t pastX = 128 + ((int8_t)(sin8(tPast * 11 / 10 * mouseDir) - 128) * 85 / 128) + ((int8_t)(sin8(tPast * 23 / 10) - 128) * 35 / 128);
            uint8_t pastY = 128 + ((int8_t)(cos8(tPast * 8 / 10) - 128) * 80 / 128) + ((int8_t)(sin8(tPast * 19 / 10 * mouseDir) - 128) * 40 / 128);
            int16_t pdx = (int16_t)ledX - (int16_t)pastX;
            int16_t pdy = (int16_t)ledY - (int16_t)pastY;
            uint16_t pDistSq = (pdx * pdx + pdy * pdy);
            if (pDistSq < 130) {
                uint8_t tube = 255 - (pDistSq * 255 / 130);
                uint8_t age = 255 - (s * 12);
                uint8_t cand = ((uint16_t)tube * age) / 255;
                if (cand > maxTailFade) maxTailFade = cand;
            }
        }

        if (dHeadSq < 45) {
            CRGB c = baseColor + CRGB(150, 150, 150);
            leds[i] = c;
        } else if (maxTailFade > 15) {
            CRGB c = baseColor;
            c.nscale8_video(maxTailFade);
            leds[i] = c;
        } else {
            CRGB dim = baseColor;
            dim.nscale8_video(20);
            leds[i] = dim;
        }
#else
        int dist = (tCurr - effIdx + FRONT_LEDS) % FRONT_LEDS;
        if (dist < 12) {
            CRGB c = baseColor;
            c.nscale8_video(255 - dist * 20);
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
            } else if (eff == 19) { // mouse_scamper — single dot + directional meteor tail tracking 2D location
                uint32_t scamperPassMs = max((uint32_t)700, (uint32_t)(60000 / max((uint16_t)20, bpm) * 3 / 2));
                uint8_t tCurr = (uint8_t)(((uint64_t)(now - autonomousShowStartTime) * 256 / scamperPassMs) * 2);
                uint8_t headX = 128 + ((int8_t)(sin8(tCurr * 11 / 10) - 128) * 85 / 128) + ((int8_t)(sin8(tCurr * 23 / 10) - 128) * 35 / 128);
                uint8_t headY = 128 + ((int8_t)(cos8(tCurr * 8 / 10) - 128) * 80 / 128) + ((int8_t)(sin8(tCurr * 19 / 10) - 128) * 40 / 128);
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
                    int16_t dx = (int16_t)ledX - (int16_t)headX;
                    int16_t dy = (int16_t)ledY - (int16_t)headY;
                    uint16_t dHeadSq = (dx * dx + dy * dy);

                    uint8_t maxTailFade = 0;
                    for (uint8_t s = 1; s <= 16; s++) {
                        uint8_t tPast = tCurr - (s * 5);
                        uint8_t pastX = 128 + ((int8_t)(sin8(tPast * 11 / 10) - 128) * 85 / 128) + ((int8_t)(sin8(tPast * 23 / 10) - 128) * 35 / 128);
                        uint8_t pastY = 128 + ((int8_t)(cos8(tPast * 8 / 10) - 128) * 80 / 128) + ((int8_t)(sin8(tPast * 19 / 10) - 128) * 40 / 128);
                        int16_t pdx = (int16_t)ledX - (int16_t)pastX;
                        int16_t pdy = (int16_t)ledY - (int16_t)pastY;
                        uint16_t pDistSq = (pdx * pdx + pdy * pdy);
                        if (pDistSq < 130) {
                            uint8_t tube = 255 - (pDistSq * 255 / 130);
                            uint8_t age = 255 - (s * 12);
                            uint8_t cand = ((uint16_t)tube * age) / 255;
                            if (cand > maxTailFade) maxTailFade = cand;
                        }
                    }

                    if (dHeadSq < 45) {
                        CRGB c = baseColor + CRGB(150, 150, 150);
                        leds[i] = c;
                    } else if (maxTailFade > 15) {
                        CRGB c = baseColor;
                        c.nscale8_video(maxTailFade);
                        leds[i] = c;
                    } else {
                        CRGB dim = baseColor;
                        dim.nscale8_video(20);
                        leds[i] = dim;
                    }
#else
                    int dist = (tCurr - i + FRONT_LEDS) % FRONT_LEDS;
                    if (dist < 12) {
                        CRGB c = baseColor;
                        c.nscale8_video(255 - dist * 20);
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
    pinMode(BUTTON_1_PIN, INPUT_PULLUP);
    pinMode(BUTTON_2_PIN, INPUT_PULLUP);
    pinMode(BUTTON_BOOT_PIN, INPUT_PULLUP);
    delay(300);

    Serial.println("\n--------------------------------------------------------");
    Serial.println("  [HARDWARE DIAGNOSTIC] BUTTON PIN STARTUP READINGS:");
    Serial.printf("  - BUTTON 1 (GPIO %d):  %s\n", BUTTON_1_PIN, (digitalRead(BUTTON_1_PIN) == LOW) ? "LOW [PRESSED / SHORTED TO GND] ⚠️" : "HIGH [OPEN / NORMAL]");
    Serial.printf("  - BUTTON 2 (GPIO %d): %s\n", BUTTON_2_PIN, (digitalRead(BUTTON_2_PIN) == LOW) ? "LOW [PRESSED / SHORTED TO GND] ⚠️" : "HIGH [OPEN / NORMAL]");
    Serial.printf("  - BOOT PIN (GPIO %d):  %s\n", BUTTON_BOOT_PIN, (digitalRead(BUTTON_BOOT_PIN) == LOW) ? "LOW [PRESSED / SHORTED TO GND] ⚠️" : "HIGH [OPEN / NORMAL]");
    Serial.println("--------------------------------------------------------\n");

    Serial.println("\n========================================================");
    Serial.println("  MAIN STREET ELECTRICAL PARADE - UNIFIED FIRMWARE");
    Serial.println("  (Auto: ESP-NOW Fleet Sync + Real-Time Wi-Fi Streaming)");
    Serial.println("========================================================");

    // 1. Initialize Wi-Fi in Station Mode
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(50);

    // Optional: Connect to Home Wi-Fi if credentials are configured (Fast non-blocking 1.5s check)
#if defined(WIFI_SSID)
    String ssid = WIFI_SSID;
    if (ssid.length() > 0 && ssid != "YourWiFiNetwork") {
        Serial.printf("[WIFI] Connecting to Wi-Fi '%s'...\n", WIFI_SSID);
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        uint32_t t0 = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - t0 < 1500) {
            delay(50);
            digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
        }
    }
#endif

    if (WiFi.status() == WL_CONNECTED) {
        digitalWrite(STATUS_LED_PIN, HIGH); // Solid blue LED = Connected to Home Wi-Fi!
        Serial.print("[WIFI] Connected! IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        digitalWrite(STATUS_LED_PIN, LOW); // LED OFF = Direct Offline / Battery Mode
        Serial.println("[WIFI] Offline mode active (ESP-NOW direct fleet sync ready).");
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

    // ========================================================================
    // 1. DUAL HARDWARE BUTTON CONTROLLER (Button 1: GPIO 4/0, Button 2: GPIO 33)
    // ========================================================================

    // --- 0. STARTUP SAFETY GUARD & PIN ARMING ---
    // Prevents entering Float ID Config or Standby if pins are grounded/shorted at power-on.
    // Pins must be read as HIGH (released) at least once before arming press/hold detection.
    static bool b1Armed = false;
    static bool b2Armed = false;
    static uint32_t lastStuckWarning = 0;

    bool b1Raw = isButton1Down();
    bool b2Raw = isButton2Down();

    if (!b1Armed) {
        if (!b1Raw) {
            b1Armed = true;
            Serial.println("[BUTTON] Button 1 armed (pin released HIGH).");
        } else if (now - lastStuckWarning > 2500) {
            lastStuckWarning = now;
            Serial.printf("[HARDWARE WARNING] Button 1 is grounded LOW at boot (GPIO %d or BOOT GPIO %d)! Check wiring for short to GND.\n",
                          BUTTON_1_PIN, BUTTON_BOOT_PIN);
        }
    }

    if (!b2Armed) {
        if (!b2Raw) {
            b2Armed = true;
            Serial.println("[BUTTON] Button 2 armed (pin released HIGH).");
        } else if (now - lastStuckWarning > 2500) {
            lastStuckWarning = now;
            Serial.printf("[HARDWARE WARNING] Button 2 is grounded LOW at boot (GPIO %d)! Check wiring for short to GND.\n",
                          BUTTON_2_PIN);
        }
    }

    // --- BUTTON 1: PRIMARY SHOW DIRECTOR (GPIO 4 + BOOT GPIO 0) ---
    // - Leader Single Tap: In sleep -> Wakes fleet into Solo Show Mode; While awake -> Toggle 30s fleet routine
    // - Follower Single Tap: In sleep -> Wakes locally into Solo Show Mode; While awake -> Local sequence
    // - Leader Double Tap (< 400ms): 4-Second Rapid Attendance Roll Call (Mode 0x44)
    // - Long Hold (>= 5.0s): Float ID Configuration Mode (1s-4s white charging meter)
    static bool b1WasPressed = false;
    static uint32_t b1DownTime = 0;
    static bool b1LongHoldHandled = false;
    static uint8_t b1PendingTaps = 0;
    static uint32_t b1FirstTapReleaseTime = 0;

    bool b1Pressed = b1Armed && b1Raw;

    if (b1Pressed && !b1WasPressed) {
        b1WasPressed = true;
        b1DownTime = now;
        b1LongHoldHandled = false;
        Serial.println("[BUTTON 1] Press detected (LOW)...");
    } else if (b1Pressed && b1WasPressed) {
        uint32_t holdElapsed = now - b1DownTime;
        if (!b1LongHoldHandled) {
            if (holdElapsed >= 5000) {
                b1LongHoldHandled = true;
                b1PendingTaps = 0;
                handleFloatConfigMode();
                b1WasPressed = false;
                return;
            } else if (holdElapsed >= 1000) {
                // Progressive charging indicator (1 to 4 LEDs lit in crisp white)
                uint8_t chargeCount = (holdElapsed / 1000);
                if (chargeCount > 4) chargeCount = 4;

                for (int i = 0; i < FRONT_LEDS; i++) {
                    leds[i] = (i < chargeCount) ? CRGB(255, 255, 255) : CRGB::Black;
                }
                duplicateFrontToBack();
                FastLED.show();
                return;
            }
        }
    } else if (!b1Pressed && b1WasPressed) {
        b1WasPressed = false;
        uint32_t pressDuration = now - b1DownTime;
        Serial.printf("[BUTTON 1] Released (duration: %u ms)\n", pressDuration);

        if (pressDuration >= 1000 && !b1LongHoldHandled) {
            Serial.printf("[BUTTON 1] Hold aborted after %u ms -> returning to baseline with zero changes.\n", pressDuration);
        }

        if (!b1LongHoldHandled && pressDuration >= 50 && pressDuration < 600) {
            if (b1PendingTaps == 1 && (now - b1FirstTapReleaseTime <= 400)) {
                // DOUBLE TAP DETECTED
                b1PendingTaps = 0;
                if (isLeader) {
                    startRapidRollCall(now);
                    broadcastRapidRollCallPacket();
                    Serial.println("[LEADER] ⚡ 4-Second Rapid Attendance Roll Call started via Button 1 double-tap!");
                } else {
                    Serial.printf("[FOLLOWER] Float %d Button 1 double tap ignored (Roll call wave reserved for Leader).\n", myFloatNumber);
                }
            } else {
                b1PendingTaps = 1;
                b1FirstTapReleaseTime = now;
            }
        }
    }

    // Evaluate Button 1 single tap once double-tap window expires (400ms)
    if (b1PendingTaps > 0 && !b1Pressed && (now - b1FirstTapReleaseTime > 400)) {
        b1PendingTaps = 0;

        if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
            if (isLeader) {
                // Leader: Wake ENTIRE FLEET into Solo Show Mode (parade baseline, does NOT start 30s fleet routine)
                previousStandaloneMode = SHOW_MODE_CORRAL_STANDBY;
                currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                autonomousShowStartTime = now;

                fill_solid(leds, NUM_LEDS, CRGB(0, 255, 80)); // Emerald Green flash
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, HIGH);
                delay(150);
                fill_solid(leds, NUM_LEDS, CRGB::Black);
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, LOW);

                broadcastStandbyPacket(0x51); // Wake entire fleet into solo show mode
                Serial.println("[LEADER] ☀️ First Tap in Standby -> Woke ENTIRE FLEET into Solo Show Mode! (Tap again while awake to start 30s Fleet Show)");
            } else {
                // Follower: Wake LOCALLY to baseline solo show animation (do NOT start theatrical fleet routine)
                currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                autonomousShowStartTime = now;

                fill_solid(leds, NUM_LEDS, CRGB(0, 255, 80)); // Emerald Green flash
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, HIGH);
                delay(150);
                fill_solid(leds, NUM_LEDS, CRGB::Black);
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, LOW);

                Serial.printf("[FOLLOWER] Float %d Single Tap -> Woke locally from Corral Standby into Solo Show Mode.\n", myFloatNumber);
            }
        } else if (isLeader) {
            // Leader active toggle
            if (currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE || currentStandaloneMode == SHOW_MODE_RAPID_ROLL_CALL) {
                currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                broadcastFleetRoutinePacket(0x00, 0);
                Serial.println("[LEADER] Early stop triggered via Button 1 -> returning to baseline.");

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
                Serial.printf("[LEADER] 30s Fleet Show started via Button 1! (Cycle #%u)\n", fleetRoutineCycle);
            }
        } else {
            // Follower active toggle
            if (currentStandaloneMode == SHOW_MODE_PHOTO_STATIC) {
                currentStandaloneMode = previousStandaloneMode;
                Serial.printf("[FOLLOWER] Float %d Button 1 tap -> Exited Photo Mode back to parade sequence.\n", myFloatNumber);
            } else {
                Serial.printf("[FOLLOWER] Float %d Button 1 tap while running (Fleet show broadcast reserved for Leader).\n", myFloatNumber);
            }
        }
    }

    // --- BUTTON 2: AUXILIARY / PHOTO & STANDBY SWITCH (GPIO 33) ---
    // - Leader Single Tap: Toggle Castle Photo Mode across ENTIRE FLEET
    // - Follower Single Tap: Toggle Castle Photo Mode LOCALLY only
    // - Double & Triple Taps: Disabled
    // - Long Hold (>= 3.0s): Leader puts ENTIRE FLEET into Corral Standby; Follower puts local costume into Corral Standby
    static bool b2WasPressed = false;
    static uint32_t b2DownTime = 0;
    static bool b2HoldHandled = false;

    bool b2Pressed = b2Armed && b2Raw;

    if (b2Pressed && !b2WasPressed) {
        b2WasPressed = true;
        b2DownTime = now;
        b2HoldHandled = false;
        Serial.println("[BUTTON 2] Press detected (LOW)...");
    } else if (b2Pressed && b2WasPressed) {
        uint32_t holdElapsed = now - b2DownTime;
        if (!b2HoldHandled) {
            if (holdElapsed >= 3000) {
                // 3-SECOND LONG HOLD: ENTER CORRAL STANDBY / SLEEP
                b2HoldHandled = true;

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

                currentStandaloneMode = SHOW_MODE_CORRAL_STANDBY;

                if (isLeader) {
                    broadcastStandbyPacket(0x50);
                    Serial.println("[LEADER] 🌙 Button 2 Held 3s -> Dropped ENTIRE FLEET into Corral Standby Mode!");
                } else {
                    Serial.printf("[FOLLOWER] Float %d Button 2 Held 3s -> Dropped locally into Corral Standby Mode.\n", myFloatNumber);
                }
                b2WasPressed = false;
                return;
            } else if (holdElapsed >= 1000) {
                // Soft indigo/blue progressive charging meter on first 3 pixels
                uint8_t chargeCount = (holdElapsed / 1000);
                if (chargeCount > 3) chargeCount = 3;
                for (int i = 0; i < FRONT_LEDS; i++) {
                    leds[i] = (i < chargeCount) ? CRGB(30, 60, 255) : CRGB::Black;
                }
                duplicateFrontToBack();
                FastLED.show();
                return;
            }
        }
    } else if (!b2Pressed && b2WasPressed) {
        b2WasPressed = false;
        uint32_t pressDuration = now - b2DownTime;
        Serial.printf("[BUTTON 2] Released (duration: %u ms)\n", pressDuration);

        if (pressDuration >= 1000 && !b2HoldHandled) {
            Serial.printf("[BUTTON 2] Sleep hold aborted after %u ms -> returning to baseline with zero changes.\n", pressDuration);
        }

        // Tap handling: immediate trigger on release since multi-taps are disabled
        if (!b2HoldHandled && pressDuration >= 50 && pressDuration < 600) {
            if (isLeader) {
                // Leader: Toggle Castle Photo Mode across ENTIRE FLEET
                if (currentStandaloneMode == SHOW_MODE_PHOTO_STATIC) {
                    currentStandaloneMode = previousStandaloneMode;
                    broadcastPhotoModePacket(0x47);
                    Serial.println("[LEADER] 📸 Button 2 Tap -> Castle Photo Mode turned OFF for ENTIRE FLEET!");
                } else {
                    previousStandaloneMode = currentStandaloneMode;
                    currentStandaloneMode = SHOW_MODE_PHOTO_STATIC;
                    broadcastPhotoModePacket(0x46);
                    Serial.println("[LEADER] 📸 Button 2 Tap -> Castle Photo Mode turned ON for ENTIRE FLEET!");
                }
            } else {
                // Follower: Toggle Castle Photo Mode LOCALLY only
                if (currentStandaloneMode == SHOW_MODE_PHOTO_STATIC) {
                    currentStandaloneMode = previousStandaloneMode;
                    Serial.printf("[FOLLOWER] Float %d Button 2 Tap -> Castle Photo Mode turned OFF (local only).\n", myFloatNumber);
                } else {
                    previousStandaloneMode = currentStandaloneMode;
                    currentStandaloneMode = SHOW_MODE_PHOTO_STATIC;
                    Serial.printf("[FOLLOWER] Float %d Button 2 Tap -> Castle Photo Mode turned ON (local only).\n", myFloatNumber);
                }
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
        if (currentStandaloneMode == SHOW_MODE_PHOTO_STATIC) {
            renderCastlePhotoMode();
            FastLED.show();
            digitalWrite(STATUS_LED_PIN, HIGH);
            delay(20);
        } else if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
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
