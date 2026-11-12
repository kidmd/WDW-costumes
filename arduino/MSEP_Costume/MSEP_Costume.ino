#include <Arduino.h>
#include <FastLED.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <esp_now.h>
#include <esp_wifi.h>
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

#if __has_include("fleet_palettes.h")
#include "fleet_palettes.h"
#endif

// In dedicated multi-float fleet builds, disable single-costume custom palette override
// so that each float cleanly compiles with its own authentic 100-LED array from fleet_palettes.h
#if defined(FLEET_BUILD) && FLEET_BUILD
#undef HAS_CUSTOM_PALETTE
#define HAS_CUSTOM_PALETTE 0
#endif

#ifndef COSTUME_SPEED_BPM
#define COSTUME_SPEED_BPM 120
#endif

#ifndef COSTUME_SPARKLE_RATE
#define COSTUME_SPARKLE_RATE 1.5
#endif

// ============================================================================
// HARDWARE & PIN DEFINITIONS
// ============================================================================
#define DATA_PIN            16      // 8th pin down on the right
#define LED_TYPE            WS2812B
#if (defined(COSTUME_FULL_562_MODE) && COSTUME_FULL_562_MODE) || (defined(NUM_LEDS) && NUM_LEDS == 562) || (defined(COSTUME_MATRIX_16X16_MODE) && COSTUME_MATRIX_16X16_MODE) || (defined(COMPILED_FLOAT_ID) && (COMPILED_FLOAT_ID == 2 || COMPILED_FLOAT_ID == 6 || COMPILED_FLOAT_ID == 7))
#undef COLOR_ORDER
#define COLOR_ORDER         GRB     // BTF-LIGHTING 16x16 WS2812B matrix and fairy lights use GRB byte order
#define COMPILED_COLOR_ORDER_IS_GRB 1
#elif !defined(COLOR_ORDER)
#define COLOR_ORDER         RGB     // Calibrated hardware color order for 5V WS2812B seed/pebble strings
#define COMPILED_COLOR_ORDER_IS_GRB 0
#else
#define COMPILED_COLOR_ORDER_IS_GRB 0
#endif
#define STATUS_LED_PIN      2       // Onboard Blue LED

#if (defined(COSTUME_FULL_562_MODE) && COSTUME_FULL_562_MODE) || (defined(NUM_LEDS) && NUM_LEDS == 562)
#undef FRONT_LEDS
#define FRONT_LEDS          256     // 16x16 front matrix panel
#undef BACK_LEDS
#define BACK_LEDS           256     // 16x16 back matrix panel
#undef NUM_LEDS
#define NUM_LEDS            562     // 562 total LEDs (256 front + 25 right fairy + 256 back + 25 left fairy)
#define FAIRY_STRAND_LEDS   25      // 25 fairy LEDs on wearer's right + 25 on wearer's left
#else
#ifndef FRONT_LEDS
#define FRONT_LEDS          100     // 100 LEDs on front of costume shirt
#endif

#ifndef BACK_LEDS
#define BACK_LEDS           100     // 100 LEDs on back of costume shirt
#endif

#ifndef NUM_LEDS
#define NUM_LEDS            200     // 200 total LEDs (100 front + 100 back)
#endif
#endif
#define MAX_LEDS_CAPACITY   600     // Buffer capacity supporting up to 562 LEDs in full closed-loop costume architecture
#ifndef MAX_BRIGHTNESS
#define MAX_BRIGHTNESS      60      // Bench/wearable safe brightness
#endif
#define MAX_MILLIAMPS       2000    // 2.0A limit for 200 LEDs on wearable power bank

CRGB leds[MAX_LEDS_CAPACITY];

Preferences preferences;

// 7-Runner Fleet Metadata & Signature Colors
struct FloatMeta {
    const char* name;
    const char* tag;
    CRGB color;
};

const FloatMeta FLEET_ROSTER_INFO[7] = {
    { "The Train",      "LEADER",     CRGB(230, 40, 50)   }, // Float 1 (Red)
    { "Title Drum",     "FOLLOWER",   CRGB(255, 235, 0)   }, // Float 2 (Parade Yellow)
    { "The Turtle",     "FOLLOWER",   CRGB(40, 200, 180)  }, // Float 3 (Teal)
    { "The Snail",      "FOLLOWER",   CRGB(255, 20, 140)  }, // Float 4 (Pink)
    { "Pirate Ship",    "FOLLOWER",   CRGB(230, 25, 25)   }, // Float 5 (Pirate Red & Gold)
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

// Check if current active float uses a BTF-LIGHTING 16x16 (256-pixel) Matrix Panel
inline bool isCurrentFloatMatrix16x16() {
#if (defined(COSTUME_FULL_562_MODE) && COSTUME_FULL_562_MODE) || (defined(NUM_LEDS) && NUM_LEDS == 562)
    return true;
#elif defined(COSTUME_MATRIX_16X16_MODE) && COSTUME_MATRIX_16X16_MODE
    return true;
#elif defined(HAS_FLEET_MATRIX_CONFIG) && HAS_FLEET_MATRIX_CONFIG
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    return pgm_read_byte(&FLOAT_IS_MATRIX_16X16[floatIdx]) != 0;
#else
    return false;
#endif
}

// Duplicate front LEDs to back LEDs (or scatter active LEDs across 16x16 matrix indices 0..255 + 256..511)
enum StandaloneShowMode {
    SHOW_MODE_AUTONOMOUS_SEQUENCE = 0,
    SHOW_MODE_FLEET_SYNC          = 1,
    SHOW_MODE_FLEET_30S_ROUTINE   = 2,
    SHOW_MODE_RAPID_ROLL_CALL     = 3,
    SHOW_MODE_CORRAL_STANDBY      = 4,
    SHOW_MODE_PHOTO_STATIC        = 5,  // 📸 Castle Photo Mode: solid steady hero illumination
    SHOW_MODE_WARM_WHITE_SPARKLE  = 6   // ✨ 3% Incandescent Warm White with starlight sparkles
};

extern StandaloneShowMode currentStandaloneMode;

// ============================================================================
// 🌊 THEATRICAL WAVE PROGRESSION SUITE (562-LED FULL COSTUME)
// ============================================================================
enum WaveProgressionMode : uint8_t {
    WAVE_PROG_WATERFALL       = 0, // Default: Down Front -> Out & Up Front Ribs -> Down Back Ribs -> Up Back Badge
    WAVE_PROG_ORBIT          = 1, // 360° Closed-Loop Continuous Torso Spiral
    WAVE_PROG_RADIAL_BURST   = 2, // Heartbeat Radial Shockwave (Center-Out)
    WAVE_PROG_HORIZON_LIFT   = 3, // Ground-to-Sky Horizon (Upward Altitude)
    WAVE_PROG_DRAGON_WINGS   = 4, // Dragon Wings (Shoulders-Down Cascading Dive)
    WAVE_PROG_LATERAL_ROLL   = 5, // Lateral Barrel Roll (Left-to-Right Scan)
    WAVE_PROG_DUAL_COLLISION = 6  // Dual-Collision Shockwave (Shoulder Clash & Rebound)
};

// Symmetrical theatrical wave progression for 562-LED costume:
// 1. Down Front Panel (0..255): 28% (0..279)
// 2. Out & Up along Front Fairy Lights mirrored (Left & Right): 22% (280..499)
// 3. Down & Over Back Fairy Lights mirrored (Left & Right): 22% (500..719)
// 4. Up Back Panel (281..536): 28% (720..999)
// Accurately models the physical Z-fold accordion bulb sequence of the 50 fairy lights:
// Strand 1 (Wearer's Right, chain 256..280, bulbs 1..25):
//   Front Ribs (13 steps, pos: 280 -> 500): Bulbs [8, 1, 9, 7, 2, 10, 6, 3, 11, 5, 4, 12, 13]
//   Back Ribs  (12 steps, pos: 500 -> 720): Bulbs [14, 15, 22, 21, 16, 23, 20, 17, 24, 19, 18, 25]
// Strand 2 (Wearer's Left, chain 537..561, bulbs 1..25):
//   Front Ribs (12 steps, pos: 280 -> 500): Bulbs [25, 18, 19, 24, 17, 20, 23, 16, 21, 22, 15, 14]
//   Back Ribs  (13 steps, pos: 500 -> 720): Bulbs [13, 12, 4, 5, 11, 3, 6, 10, 2, 7, 9, 1, 8]
// 🌟 Multi-color baseline palettes for Floats 1..7 (Casey: Red/Gold, Drum: Red/Gold, Turtle: Yellow/Blue/Green, Snail: Red/Blue/Green, Pirate: Red/Gold, Dragon: Green/Yellow, America: Red/White/Blue)
static const uint8_t FLOAT_PALETTE_COUNTS[7] PROGMEM = { 2, 2, 3, 3, 2, 2, 3 };

static const CRGB FLOAT_PALETTES[7][3] PROGMEM = {
    { CRGB(255, 0, 0),   CRGB(255, 180, 0),   CRGB(0, 0, 0) },   // Float 1 (Casey Jr.): Bold Red, Gold
    { CRGB(255, 0, 0),   CRGB(255, 180, 0),   CRGB(0, 0, 0) },   // Float 2 (Title Drum): Bold Red, Gold
    { CRGB(255, 215, 0), CRGB(0, 60, 255),    CRGB(0, 220, 40) }, // Float 3 (The Turtle): Yellow, Bold Royal Blue, Emerald Green
    { CRGB(255, 0, 0),   CRGB(0, 60, 255),    CRGB(0, 220, 40) }, // Float 4 (The Snail): Bold Red, Bold Royal Blue, Emerald Green
    { CRGB(255, 0, 0),   CRGB(255, 180, 0),   CRGB(0, 0, 0) },   // Float 5 (The Pirate Ship): Bold Red, Gold
    { CRGB(0, 255, 100), CRGB(255, 215, 0),   CRGB(0, 0, 0) },   // Float 6 (Pete's Dragon): Vivid Elliott Green, Golden Yellow
    { CRGB(255, 0, 0),   CRGB(255, 255, 255), CRGB(0, 0, 255) }  // Float 7 (To Honor America): Bold Patriotic Red, Pure Star White, Deep Royal Blue
};

inline CRGB getFloatPaletteColor(uint8_t floatNum, uint8_t colorIdx = 0) {
    uint8_t fIdx = (floatNum >= 1 && floatNum <= 7) ? (floatNum - 1) : 0;
    uint8_t count = pgm_read_byte(&FLOAT_PALETTE_COUNTS[fIdx]);
    uint8_t cIdx = colorIdx % count;
    return CRGB(
        pgm_read_byte(&FLOAT_PALETTES[fIdx][cIdx].r),
        pgm_read_byte(&FLOAT_PALETTES[fIdx][cIdx].g),
        pgm_read_byte(&FLOAT_PALETTES[fIdx][cIdx].b)
    );
}

// 🌟 Physical Z-fold Accordion Spatial Step Mapping for 25-bulb Fairy Strands
// Maps sequential wire bulb offset (0..24) to physical spatial rank (0..24) along the runner's ribs
// Guarantees exact 3 Red, 3 White, 3 Blue repeating triplets along the body!
static const uint8_t FAIRY_STRAND1_SPATIAL_STEP[25] PROGMEM = {
    1, 4, 7, 10, 9, 6, 3, 0, 2, 5, 8, 11, 12, // Bulbs 1..13 (Front Ribs 0..12)
    13, 14, 17, 20, 23, 22, 19, 16, 15, 18, 21, 24 // Bulbs 14..25 (Back Ribs 13..24)
};

static const uint8_t FAIRY_STRAND2_SPATIAL_STEP[25] PROGMEM = {
    23, 20, 17, 14, 15, 18, 21, 24, 22, 19, 16, 13, 12, // Bulbs 1..13 (Back Ribs 12..24)
    11, 10, 7, 4, 1, 2, 5, 8, 9, 6, 3, 0 // Bulbs 14..25 (Front Ribs 0..11)
};

// Helper to get fairy bulb color in repeating triplets (groups of 3 bulbs) mapped to physical body order
inline CRGB getFloatFairyBulbColor(uint8_t floatNum, uint8_t strandId, uint8_t wireBulbIndex) {
    if (wireBulbIndex >= 25) wireBulbIndex = 24;
    uint8_t step = (strandId == 1) ? pgm_read_byte(&FAIRY_STRAND1_SPATIAL_STEP[wireBulbIndex])
                                   : pgm_read_byte(&FAIRY_STRAND2_SPATIAL_STEP[wireBulbIndex]);
    uint8_t group = (step / 3) % 3;
    return getFloatPaletteColor(floatNum, group);
}

inline CRGB getFloatDefaultFairyColor(uint8_t floatNum = 1) {
    return getFloatPaletteColor(floatNum, 0);
}

static const uint16_t FAIRY_STRAND1_LOOP_POS[25] PROGMEM = {
    298, 353, 408, 463, 445, 390, 335, 280, 317, 372, 427, 482, 500, // Bulbs 1..13 (indices 256..268)
    500, 520, 580, 640, 700, 680, 620, 560, 540, 600, 660, 720        // Bulbs 14..25 (indices 269..280)
};

static const uint16_t FAIRY_STRAND2_LOOP_POS[25] PROGMEM = {
    702, 647, 592, 537, 555, 610, 665, 720, 683, 628, 573, 518, 500, // Bulbs 1..13 (indices 537..549)
    500, 480, 420, 360, 300, 320, 380, 440, 460, 400, 340, 280        // Bulbs 14..25 (indices 550..561)
};

inline uint16_t getCostumePacedLoopPosition(uint16_t index, uint8_t prog = WAVE_PROG_WATERFALL) {
    if (index < 256) {
        // Stage 1: Down the Front Panel (0..255) -> 0..279 (top to bottom)
        uint8_t row = index / 16;
        return (uint16_t)(((uint32_t)row * 280) / 16 + 8);
    } else if (index >= 256 && index <= 280) {
        // Strand 1 Fairy Lights (Wearer's Right, Z-folded 25 bulbs):
        return pgm_read_word(&FAIRY_STRAND1_LOOP_POS[index - 256]);
    } else if (index >= 281 && index <= 536) {
        // Stage 4: Up the Back Panel (281..536) -> 720..999 (bottom to top)
        uint16_t mIdx = index - 281;
        uint8_t row = mIdx / 16;
        uint8_t upRow = 15 - row;
        return (uint16_t)(720 + (((uint32_t)upRow * 280) / 16 + 8));
    } else if (index >= 537 && index <= 561) {
        // Strand 2 Fairy Lights (Wearer's Left, Z-folded 25 bulbs):
        return pgm_read_word(&FAIRY_STRAND2_LOOP_POS[index - 537]);
    }
    return (uint16_t)(((uint32_t)(index % 562) * 1000) / 562);
}

inline int getMatrixActiveLedCount() {
    int activeCount = FRONT_LEDS;
#if !(defined(FLEET_BUILD) && FLEET_BUILD) && defined(MATRIX_WINDOW_LED_COUNT) && defined(MATRIX_BACKLIGHT_LED_COUNT) && ((MATRIX_WINDOW_LED_COUNT + MATRIX_BACKLIGHT_LED_COUNT) > 0)
    activeCount = min((int)FRONT_LEDS, (int)(MATRIX_WINDOW_LED_COUNT + MATRIX_BACKLIGHT_LED_COUNT));
#elif !(defined(FLEET_BUILD) && FLEET_BUILD) && defined(MATRIX_ACTIVE_LED_COUNT)
    activeCount = min((int)FRONT_LEDS, (int)MATRIX_ACTIVE_LED_COUNT);
#elif defined(HAS_FLEET_MATRIX_CONFIG) && HAS_FLEET_MATRIX_CONFIG
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    activeCount = min((int)FRONT_LEDS, (int)pgm_read_byte(&FLOAT_ACTIVE_LED_COUNT[floatIdx]));
#endif
    if (activeCount > 256) activeCount = 256;
    return activeCount;
}

inline void duplicateFrontToBack() {
    if (isCurrentFloatMatrix16x16()) {
        CRGB tempActive[256];
        int activeCount = getMatrixActiveLedCount();
        for (int i = 0; i < activeCount; i++) {
            tempActive[i] = leds[i];
        }
        // Clear all 512 pixels so non-windowed / non-backlit dark cells stay strictly off
        fill_solid(leds, MAX_LEDS_CAPACITY, CRGB::Black);
        uint8_t winCount = 51;
#if !(defined(FLEET_BUILD) && FLEET_BUILD) && defined(MATRIX_WINDOW_LED_COUNT)
        winCount = MATRIX_WINDOW_LED_COUNT;
#elif defined(HAS_FLEET_MATRIX_CONFIG) && HAS_FLEET_MATRIX_CONFIG
        {
            uint8_t fIdxW = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
            winCount = pgm_read_byte(&FLOAT_MATRIX_WINDOW_COUNT[fIdxW]);
        }
#endif
        for (int i = 0; i < activeCount; i++) {
            uint8_t physIdx = i;
#if !(defined(FLEET_BUILD) && FLEET_BUILD) && defined(COSTUME_MATRIX_16X16_MODE) && COSTUME_MATRIX_16X16_MODE
            physIdx = pgm_read_byte(&MATRIX_ACTIVE_INDICES[i]);
#elif defined(HAS_FLEET_MATRIX_CONFIG) && HAS_FLEET_MATRIX_CONFIG
            uint8_t fIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
            if (i < 256) {
                physIdx = pgm_read_byte(&FLOAT_MATRIX_INDICES[fIdx][i]);
            }
#endif
            CRGB c = tempActive[i];
            if (currentStandaloneMode == SHOW_MODE_WARM_WHITE_SPARKLE) {
                bool isSparkle = (c.r > 240 && c.g > 240 && c.b > 240);
                if (isSparkle) {
                    c.nscale8_video(192); // Bright starlight pop (~3x brighter than warm white base)
                } else {
                    c.nscale8_video(64);  // Identical physical level to normal colored backlights (~3.1% duty cycle)
                }
            } else if (i >= winCount) {
                c.nscale8_video(64); // Backlight LEDs at 50% brightness of windowed LEDs
            } else {
                c.nscale8_video(128); // Windowed LEDs
            }
#if !COMPILED_COLOR_ORDER_IS_GRB
            // If compiled with RGB for general pebble strings, swap R & G dynamically for GRB 16x16 matrix
            uint8_t tmpR = c.r;
            c.r = c.g;
            c.g = tmpR;
#endif
            leds[physIdx] = c;
#if (defined(COSTUME_FULL_562_MODE) && COSTUME_FULL_562_MODE) || (defined(NUM_LEDS) && NUM_LEDS == 562)
            // 562-LED closed-loop costume: Front Matrix (0..255), Right Fairy (256..280), Back Matrix (281..536), Left Fairy (537..561)
            if ((281 + (int)physIdx) < MAX_LEDS_CAPACITY) {
                leds[281 + (int)physIdx] = c;
            }
#else
            if ((256 + (int)physIdx) < MAX_LEDS_CAPACITY) {
                leds[256 + (int)physIdx] = c;
            }
#endif
        }

#if (defined(COSTUME_FULL_562_MODE) && COSTUME_FULL_562_MODE) || (defined(NUM_LEDS) && NUM_LEDS == 562)
        // Ensure fairy strands (256..280 on Right, 537..561 on Left) are illuminated across all modes.
        // WS2812B 16x16 panels are native GRB; fairy seed bulbs on this costume are RGB chips.
        // Swapping R and G on fairy bulbs on the GRB stream ensures Red, White, and Blue match 100%!
        if (currentStandaloneMode == SHOW_MODE_PHOTO_STATIC) {
            for (int f = 256; f <= 280; f++) {
                CRGB fc = getFloatFairyBulbColor(myFloatNumber, 1, f - 256);
                leds[f] = CRGB(fc.g, fc.r, fc.b);
            }
            for (int f = 537; f <= 561; f++) {
                CRGB fc = getFloatFairyBulbColor(myFloatNumber, 2, f - 537);
                leds[f] = CRGB(fc.g, fc.r, fc.b);
            }
        } else if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
            for (int f = 256; f <= 280; f++) {
                CRGB fc = getFloatFairyBulbColor(myFloatNumber, 1, f - 256);
                CRGB dimF = CRGB(fc.g, fc.r, fc.b);
                dimF.nscale8_video(35);
                leds[f] = dimF;
            }
            for (int f = 537; f <= 561; f++) {
                CRGB fc = getFloatFairyBulbColor(myFloatNumber, 2, f - 537);
                CRGB dimF = CRGB(fc.g, fc.r, fc.b);
                dimF.nscale8_video(35);
                leds[f] = dimF;
            }
        } else if (currentStandaloneMode == SHOW_MODE_RAPID_ROLL_CALL) {
            CRGB rcCol = tempActive[0];
            CRGB rcWireCol = CRGB(rcCol.g, rcCol.r, rcCol.b);
            for (int f = 256; f <= 280; f++) leds[f] = rcWireCol;
            for (int f = 537; f <= 561; f++) leds[f] = rcWireCol;
        } else {
            // Solo / Autonomous parade mode & Ambient fallback: illuminate unlit fairy bulbs with float palette triplets!
            for (int f = 256; f <= 280; f++) {
                if (leds[f] == CRGB(0,0,0)) {
                    CRGB fc = getFloatFairyBulbColor(myFloatNumber, 1, f - 256);
                    leds[f] = CRGB(fc.g, fc.r, fc.b);
                } else {
                    leds[f] = CRGB(leds[f].g, leds[f].r, leds[f].b);
                }
            }
            for (int f = 537; f <= 561; f++) {
                if (leds[f] == CRGB(0,0,0)) {
                    CRGB fc = getFloatFairyBulbColor(myFloatNumber, 2, f - 537);
                    leds[f] = CRGB(fc.g, fc.r, fc.b);
                } else {
                    leds[f] = CRGB(leds[f].g, leds[f].r, leds[f].b);
                }
            }
        }
#endif
        return;
    }

    for (int i = 0; i < FRONT_LEDS && (FRONT_LEDS + i) < NUM_LEDS && (FRONT_LEDS + i) < MAX_LEDS_CAPACITY; i++) {
        CRGB c = leds[i];
        if (currentStandaloneMode == SHOW_MODE_WARM_WHITE_SPARKLE) {
            bool isSparkle = (c.r > 240 && c.g > 240 && c.b > 240);
            if (isSparkle) {
                c.nscale8_video(192);
            } else {
                c.nscale8_video(64);
            }
            leds[i] = c;
        }
        leds[FRONT_LEDS + i] = c;
    }
    for (int i = NUM_LEDS; i < MAX_LEDS_CAPACITY; i++) {
        leds[i] = CRGB::Black;
    }
}

// Helper to flash a uniform confirmation color across active LEDs (respecting 16x16 matrix layout)
inline void fillActiveCostumeSolid(CRGB color) {
    fill_solid(leds, FRONT_LEDS, color);
    duplicateFrontToBack();
}

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
#define FLEET_ROUTINE_TOTAL_MS 30000 // Auto-updated for 💥 The Supernova Spectacular (30s) (30.0s)
#define RAPID_ROLL_CALL_TOTAL_MS 4000 // 4.0-second Rapid Attendance Roll Call (500ms x 7 floats + 500ms unison finale)



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

#define ESPNOW_WIFI_CHANNEL 1   // Dedicated fixed 2.4GHz walkie-talkie channel for ESP-NOW fleet sync

// Rapid multi-packet burst transmitter to guarantee delivery over unacknowledged broadcast ESP-NOW
inline void sendEspNowBurst(ParadeSyncPacket &packet, uint8_t count = 5, bool advanceMasterMillis = false) {
    uint32_t baseMasterMillis = packet.masterMillis;
    uint32_t tStart = millis();
    for (uint8_t i = 0; i < count; i++) {
        if (advanceMasterMillis) {
            packet.masterMillis = baseMasterMillis + (millis() - tStart);
        }
        esp_now_send(broadcastMac, (uint8_t*)&packet, sizeof(packet));
        if (i + 1 < count) {
            delay(6);
        }
    }
}

void broadcastFleetRoutinePacket(uint8_t mode, uint32_t masterMillis, bool burst = true) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = mode; // 0x30 = Start/Sync 30s Routine, 0x00 = Stop early, 0x50 = Standby, 0x51 = Wake
    packet.masterMillis = masterMillis;
    packet.activeFloat = myFloatNumber;
    packet.waveHead = fleetRoutineCycle;
    sendEspNowBurst(packet, burst ? 5 : 1, (mode == 0x30));
}

void broadcastStandbyPacket(uint8_t mode) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = mode; // 0x50 = Standby, 0x51 = Wake
    packet.masterMillis = millis();
    packet.activeFloat = myFloatNumber;
    packet.waveHead = 0;
    sendEspNowBurst(packet, 5, false);
}

void broadcastPhotoModePacket(uint8_t mode) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = mode; // 0x46 = Photo Mode ON, 0x47 = Photo Mode OFF
    packet.masterMillis = millis();
    packet.activeFloat = myFloatNumber;
    packet.waveHead = 0;
    sendEspNowBurst(packet, 5, false);
}

void renderCastlePhotoMode() {
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    int activeCount = isCurrentFloatMatrix16x16() ? getMatrixActiveLedCount() : FRONT_LEDS;

#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
    #if defined(COMPILED_FLOAT_ID)
    if (myFloatNumber == COMPILED_FLOAT_ID) {
        for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
            leds[i] = (i < activeCount) ? ARTWORK_PALETTE[i] : CRGB::Black;
        }
        duplicateFrontToBack();
        return;
    }
    #else
    for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
        leds[i] = (i < activeCount) ? ARTWORK_PALETTE[i] : CRGB::Black;
    }
    duplicateFrontToBack();
    return;
    #endif
#endif

#if defined(HAS_DEFAULT_FLOAT_PALETTES) && HAS_DEFAULT_FLOAT_PALETTES
    for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
        leds[i] = (i < activeCount && i < 256) ? DEFAULT_FLOAT_PALETTES[floatIdx][i] : ((i < activeCount) ? FLEET_ROSTER_INFO[floatIdx].color : CRGB::Black);
    }
#else
    CRGB heroColor = FLEET_ROSTER_INFO[floatIdx].color;
    fill_solid(leds, FRONT_LEDS, heroColor);
#endif

    duplicateFrontToBack();
}

void broadcastWarmWhitePacket(uint8_t mode) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = mode; // 0x48 = Warm White ON, 0x49 = Warm White OFF
    packet.masterMillis = millis();
    packet.activeFloat = myFloatNumber;
    packet.waveHead = 0;
    sendEspNowBurst(packet, 5, false);
}

void renderWarmWhiteSparkle(uint32_t now) {
    // Balanced Warm Incandescent / ~2500K Vintage Filament Glow
    // Perfectly centered between 2200K candle (too yellow) and 2850K tungsten (too cool)
    // Full unscaled RGB palette - physical 3% duty cycle is governed by 64-scaling in duplicateFrontToBack()
    CRGB baseCol = CRGB(255, 185, 110);

    // Starlight sparkle color: bright pure starlight white
    CRGB sparkleCol = CRGB(255, 255, 255);

    for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
        leds[i] = baseCol;
        if (COSTUME_SPARKLE_RATE > 0 && random16(10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100)) {
            leds[i] = sparkleCol;
        }
    }
    duplicateFrontToBack();
}

void renderCorralStandby(uint32_t t) {
    // 16x16 Matrix Mode: Ultra-low-power standby on active artwork LEDs only (<120mA USB-safe)
    if (isCurrentFloatMatrix16x16()) {
        int activeCount = getMatrixActiveLedCount();
        for (int i = 0; i < activeCount && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
            CRGB c = ARTWORK_PALETTE[i];
#elif defined(HAS_DEFAULT_FLOAT_PALETTES) && HAS_DEFAULT_FLOAT_PALETTES
            uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
            CRGB c = (i < 256) ? DEFAULT_FLOAT_PALETTES[floatIdx][i] : FLEET_ROSTER_INFO[floatIdx].color;
#else
            uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
            CRGB c = FLEET_ROSTER_INFO[floatIdx].color;
#endif
            c.nscale8_video(35); // Soft midnight artwork glow (<100mA total draw)
            leds[i] = c;
        }
        for (int i = activeCount; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
            leds[i] = CRGB::Black;
        }
        duplicateFrontToBack();
        return;
    }

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
        min(255, dimBase.b + 8)
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
        fillActiveCostumeSolid(color);
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, HIGH);
        delay(120);
        fillActiveCostumeSolid(CRGB::Black);
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
    sendEspNowBurst(packet, 3, false);
}

void broadcastRapidRollCallPacket(uint32_t elapsedMs = 0, bool burst = true) {
    ParadeSyncPacket packet;
    packet.magic = 0xEE;
    packet.mode = 0x44; // 0x44 = 4s Rapid Attendance Roll Call
    packet.masterMillis = elapsedMs;
    packet.activeFloat = myFloatNumber;
    packet.waveHead = 0;
    sendEspNowBurst(packet, burst ? 5 : 1, true);
}

void startRapidRollCall(uint32_t now) {
    bool isNewRollCall = (currentStandaloneMode != SHOW_MODE_RAPID_ROLL_CALL);
    if (isNewRollCall) {
        previousStandaloneMode = currentStandaloneMode;
    }
    currentStandaloneMode = SHOW_MODE_RAPID_ROLL_CALL;
    rapidRollCallStartTime = now;
    if (isNewRollCall) {
        Serial.printf("[ROLL CALL] ⚡ 4-Second Rapid Attendance Roll Call started! (Initiator: Float %d)\n", myFloatNumber);
    }
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
                // Synchronized Fleet 30s routine trigger & ongoing sync beacon
                bool wasAlreadyActive = (currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE);
                if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
                    previousStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                } else if (!wasAlreadyActive) {
                    previousStandaloneMode = currentStandaloneMode;
                }
                currentStandaloneMode = SHOW_MODE_FLEET_30S_ROUTINE;
                fleetRoutineCycle = packet.waveHead;
                fleetRoutineStartTime = millis() - packet.masterMillis;
                if (!wasAlreadyActive) {
                    Serial.printf("[ESP-NOW] Fleet 30s Show triggered by Float %d (cycle #%u, sync offset: %u ms)\n",
                                  packet.activeFloat, fleetRoutineCycle, packet.masterMillis);
                }
            } else if (packet.mode == 0x00 && (currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE || currentStandaloneMode == SHOW_MODE_RAPID_ROLL_CALL)) {
                // Early stop commanded by peer
                currentStandaloneMode = previousStandaloneMode;
                Serial.printf("[ESP-NOW] Fleet Show stopped early by Float %d -> reverting to baseline\n",
                              packet.activeFloat);
            } else if (packet.mode == 0x42) {
                // Pre-race Corral Roll Call: Identify Flash command (debounced across burst packets)
                static uint32_t lastIdentifyRxTime = 0;
                if ((packet.activeFloat == 0 || packet.activeFloat == myFloatNumber) && (millis() - lastIdentifyRxTime > 800)) {
                    lastIdentifyRxTime = millis();
                    triggerIdentifyFlash();
                }
            } else if (packet.mode == 0x44) {
                // 4-Second Rapid Attendance Roll Call commanded by peer
                bool wasAlreadyActive = (currentStandaloneMode == SHOW_MODE_RAPID_ROLL_CALL);
                startRapidRollCall(millis() - packet.masterMillis);
                if (!wasAlreadyActive) {
                    Serial.printf("[ESP-NOW] ⚡ Rapid Attendance Roll Call triggered by Float %d\n", packet.activeFloat);
                }
            } else if (packet.mode == 0x46) {
                // Castle Photo Mode ON commanded by Leader/Peer
                if (currentStandaloneMode != SHOW_MODE_PHOTO_STATIC) {
                    previousStandaloneMode = currentStandaloneMode;
                    currentStandaloneMode = SHOW_MODE_PHOTO_STATIC;
                    Serial.printf("[ESP-NOW] 📸 Photo Mode engaged across fleet by Float %d\n", packet.activeFloat);
                }
            } else if (packet.mode == 0x47) {
                // Castle Photo Mode OFF commanded by Leader/Peer
                if (currentStandaloneMode == SHOW_MODE_PHOTO_STATIC) {
                    currentStandaloneMode = previousStandaloneMode;
                    Serial.printf("[ESP-NOW] 📸 Photo Mode disengaged by Float %d -> returned to parade mode\n", packet.activeFloat);
                }
            } else if (packet.mode == 0x48) {
                // 3% Warm White Starlight Mode ON commanded by Leader/Peer
                if (currentStandaloneMode != SHOW_MODE_WARM_WHITE_SPARKLE) {
                    previousStandaloneMode = currentStandaloneMode;
                    // Synchronized fleet confirmation: 2 distinct warm white pulses (150ms ON, 100ms OFF)
                    for (int f = 0; f < 2; f++) {
                        fillActiveCostumeSolid(CRGB(255, 185, 110));
                        FastLED.show();
                        delay(150);
                        fillActiveCostumeSolid(CRGB::Black);
                        FastLED.show();
                        delay(100);
                    }
                    currentStandaloneMode = SHOW_MODE_WARM_WHITE_SPARKLE;
                    Serial.printf("[ESP-NOW] ✨ Warm White Starlight Mode engaged across fleet by Float %d\n", packet.activeFloat);
                }
            } else if (packet.mode == 0x49) {
                // 3% Warm White Starlight Mode OFF commanded by Leader/Peer
                if (currentStandaloneMode == SHOW_MODE_WARM_WHITE_SPARKLE) {
                    currentStandaloneMode = previousStandaloneMode;
                    Serial.printf("[ESP-NOW] ☀️ Exited Warm White Mode into Solo Show by Float %d\n", packet.activeFloat);
                }
            } else if (packet.mode == 0x50) {
                // Corral Standby Mode commanded by Leader/Peer
                if (currentStandaloneMode != SHOW_MODE_CORRAL_STANDBY) {
                    currentStandaloneMode = SHOW_MODE_CORRAL_STANDBY;
                    Serial.printf("[ESP-NOW] 🌙 Switched to Corral Standby Mode by Float %d\n", packet.activeFloat);
                }
            } else if (packet.mode == 0x51) {
                // Wake from Corral Standby, Photo Mode, or Warm White Mode commanded by Leader/Peer into Solo Show Mode
                if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY || currentStandaloneMode == SHOW_MODE_PHOTO_STATIC || currentStandaloneMode == SHOW_MODE_WARM_WHITE_SPARKLE) {
                    currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                    previousStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                    autonomousShowStartTime = millis();
                    Serial.printf("[ESP-NOW] ☀️ Woke into Solo Show Mode by Float %d\n", packet.activeFloat);
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

    // Duplicate front LEDs to back LEDs (or scatter active LEDs across 16x16 matrix)
    duplicateFrontToBack();

    FastLED.show();
    delay(15);
}

void configureEspNowRole() {
    isLeader = (myFloatNumber == 1 || myFloatNumber == 7);
    
    // Register broadcast peer so this node can transmit to all fleet costumes
    esp_now_peer_info_t peerInfo = {};
    memcpy(peerInfo.peer_addr, broadcastMac, 6);
    peerInfo.channel = 0; // 0 = use current locked radio channel (Channel 1)
    peerInfo.ifidx = WIFI_IF_STA;
    peerInfo.encrypt = false;
    if (esp_now_is_peer_exist(broadcastMac)) {
        esp_now_del_peer(broadcastMac);
    }
    esp_now_add_peer(&peerInfo);
    
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
        fillActiveCostumeSolid(CRGB(240, 240, 240));
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, HIGH);
        delay(140);
        fillActiveCostumeSolid(CRGB::Black);
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

    // Exit alert: Flash signature float color 4 times
    uint8_t cfgFloatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB exitColor = FLEET_ROSTER_INFO[cfgFloatIdx].color;
    for (int s = 0; s < 4; s++) {
        fillActiveCostumeSolid(exitColor);
        FastLED.show();
        digitalWrite(STATUS_LED_PIN, HIGH);
        delay(80);
        fillActiveCostumeSolid(CRGB::Black);
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

// ============================================================================
// CATALOG EFFECTS 20..32 (Shared by Ambient Fallback & Show Cue Director)
// ============================================================================
static inline uint8_t catalogHash8(uint32_t n) {
    n = (n ^ 61) ^ (n >> 16);
    n += (n << 3);
    n ^= (n >> 4);
    n *= 0x27d4eb2d;
    n ^= (n >> 15);
    return (uint8_t)(n & 0xFF);
}

bool renderCatalogEffect20to32(uint8_t effId, uint16_t bpm, uint32_t now, uint32_t originMs, int8_t dir) {
    if (effId < 20 || effId > 33) return false;

    uint32_t elapsed = now - originMs;
    uint32_t beatMs = 60000 / max((uint16_t)20, bpm);
    int activeCount = isCurrentFloatMatrix16x16() ? getMatrixActiveLedCount() : FRONT_LEDS;
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB themeColor = FLEET_ROSTER_INFO[floatIdx].color;

    for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
        if (i >= activeCount) {
            leds[i] = CRGB::Black;
            continue;
        }
#if defined(COSTUME_AMBIENT_COLOR_MODE) && (COSTUME_AMBIENT_COLOR_MODE == 1)
        CRGB baseColor = themeColor;
#elif defined(COSTUME_AMBIENT_COLOR_MODE) && (COSTUME_AMBIENT_COLOR_MODE == 2)
        CRGB baseColor = CRGB(255, 210, 120);
#elif defined(COSTUME_AMBIENT_COLOR_MODE) && (COSTUME_AMBIENT_COLOR_MODE == 3) && defined(AMBIENT_CUSTOM_COLOR_RGB)
        CRGB baseColor = AMBIENT_CUSTOM_COLOR_RGB;
#elif defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
        CRGB baseColor = ARTWORK_PALETTE[i];
#elif defined(HAS_DEFAULT_FLOAT_PALETTES) && HAS_DEFAULT_FLOAT_PALETTES
        CRGB baseColor = (i < 256) ? DEFAULT_FLOAT_PALETTES[floatIdx][i] : themeColor;
#else
        CRGB baseColor = themeColor;
#endif
        int effIdx = (dir < 0) ? (activeCount - 1 - i) : i;
        uint16_t norm255 = (activeCount > 1) ? (uint16_t)((effIdx * 255) / (activeCount - 1)) : 128;

        if (effId == 20) { // dragon_sparkle
            CRGB c = blend(baseColor, CRGB(20, 255, 90), 128);
            if (catalogHash8((uint32_t)i * 13 + (elapsed / 90) * 29) < 13) c = CRGB(255, 255, 220);
            leds[i] = c;
        } else if (effId == 21) { // dim_glow
            baseColor.nscale8_video(56);
            leds[i] = baseColor;
        } else if (effId == 22) { // dual_chase
            uint32_t periodMs = max((uint32_t)800, beatMs * 2);
            uint8_t head1 = (uint8_t)(((uint64_t)(elapsed % periodMs) * 255) / periodMs);
            if (dir < 0) head1 = 255 - head1;
            uint8_t head2 = 255 - head1;
            uint8_t d1 = min((uint8_t)abs((int)norm255 - (int)head1), (uint8_t)(255 - abs((int)norm255 - (int)head1)));
            uint8_t d2 = min((uint8_t)abs((int)norm255 - (int)head2), (uint8_t)(255 - abs((int)norm255 - (int)head2)));
            uint8_t i1 = (d1 < 36) ? (uint8_t)(255 - d1 * 7) : 0;
            uint8_t i2 = (d2 < 36) ? (uint8_t)(255 - d2 * 7) : 0;
            uint16_t comb = min((uint16_t)255, (uint16_t)(i1 + i2));
            CRGB c = baseColor;
            c.nscale8_video((uint8_t)(25 + (comb * 230) / 255));
            if (i1 > 128 && i2 > 128) c += CRGB(140, 140, 140);
            leds[i] = c;
        } else if (effId == 23) { // barber_pole
            uint32_t periodMs = max((uint32_t)400, beatMs * 2);
            uint8_t shift = (uint8_t)(((uint64_t)(elapsed % periodMs) * 255) / periodMs);
            uint8_t band = (uint8_t)((norm255 * 4) - (dir >= 0 ? shift : -shift));
            leds[i] = (band < 128) ? baseColor : CRGB(255, 235, 190);
        } else if (effId == 24) { // curtain_wipe
            uint32_t cycleMs = beatMs * 4;
            uint32_t pMs = elapsed % cycleMs;
            uint8_t reveal = (pMs < cycleMs / 2)
                ? (uint8_t)((pMs * 255) / (cycleMs / 2))
                : (uint8_t)(((cycleMs - pMs) * 255) / (cycleMs / 2));
            uint8_t distCenter = (uint8_t)(abs((int)norm255 - 128) * 2);
            bool lit = (dir >= 0) ? (distCenter <= reveal) : (distCenter >= (255 - reveal));
            if (lit) {
                leds[i] = baseColor;
            } else {
                baseColor.nscale8_video(18);
                leds[i] = baseColor;
            }
        } else if (effId == 25) { // random_dissolve
            uint32_t cycleMs = beatMs * 4;
            uint32_t pMs = elapsed % cycleMs;
            uint8_t thresh = catalogHash8((uint32_t)i + 1);
            uint8_t gate = (pMs < cycleMs / 2)
                ? (uint8_t)((pMs * 255) / (cycleMs / 2))
                : (uint8_t)(((cycleMs - pMs) * 255) / (cycleMs / 2));
            if (thresh <= gate) {
                leds[i] = baseColor;
            } else {
                baseColor.nscale8_video(16);
                leds[i] = baseColor;
            }
        } else if (effId == 26) { // lightning_bug
            uint32_t cycleMs = max((uint32_t)1200, beatMs * 3);
            uint8_t offset = catalogHash8((uint32_t)i + 17);
            uint32_t phaseMs = (elapsed + ((uint32_t)offset * cycleMs) / 255) % cycleMs;
            uint8_t tau = (uint8_t)((phaseMs * 255) / cycleMs);
            uint8_t glow = 16;
            if (tau < 26) glow = 16 + (uint8_t)((tau * 239) / 26);
            else if (tau < 153) glow = 16 + (uint8_t)(239 - ((tau - 26) * 239) / 127);
            CRGB c = blend(baseColor, CRGB(190, 255, 45), 153);
            c.nscale8_video(glow);
            leds[i] = c;
        } else if (effId == 27) { // paparazzi
            uint32_t sliceMs = max((uint32_t)60, beatMs / 4);
            uint32_t slice = elapsed / sliceMs;
            if (catalogHash8((uint32_t)i * 31 + slice * 17) < 17) {
                leds[i] = CRGB(255, 250, 230);
            } else {
                baseColor.nscale8_video(30);
                leds[i] = baseColor;
            }
        } else if (effId == 28) { // double_blink
            uint32_t cycleMs = beatMs * 2;
            uint8_t p = (uint8_t)(((elapsed % cycleMs) * 255) / cycleMs);
            bool on = (p < 36) || (p >= 61 && p < 97);
            if (!on) baseColor.nscale8_video(20);
            leds[i] = baseColor;
        } else if (effId == 29) { // heartbeat
            uint8_t p = (uint8_t)(((elapsed % beatMs) * 255) / beatMs);
            uint8_t pulse = 30;
            if (p >= 15 && p < 55) pulse = 255 - abs((int)p - 35) * 11;
            else if (p >= 65 && p < 100) pulse = 200 - abs((int)p - 82) * 9;
            baseColor.nscale8_video(pulse);
            leds[i] = baseColor;
        } else if (effId == 30) { // two_tone_fade
            uint8_t blendAmt = beatsin8(max((uint8_t)10, (uint8_t)(bpm / 2)), 0, 255);
            leds[i] = blend(baseColor, themeColor, blendAmt);
        } else if (effId == 31) { // confetti
            uint32_t sliceMs = max((uint32_t)120, (beatMs * 3) / 5);
            uint32_t slice = elapsed / sliceMs;
            if (catalogHash8((uint32_t)i * 19 + slice * 37) < 56) {
                uint8_t hue = catalogHash8((uint32_t)i * 7 + slice * 53);
                leds[i] = CHSV(hue, 240, 255);
            } else {
                baseColor.nscale8_video(36);
                leds[i] = baseColor;
            }
        } else if (effId == 32) { // cinderella_twinkle
            uint8_t phase = catalogHash8((uint32_t)i + 99);
            uint8_t tw = sin8((uint8_t)((elapsed * bpm) / 300) + phase);
            tw = scale8(tw, tw);
            CRGB accent = (i % 3 == 0) ? CRGB(120, 220, 255) : ((i % 3 == 1) ? CRGB(240, 248, 255) : CRGB(255, 215, 110));
            CRGB c = blend(baseColor, accent, tw);
            c.nscale8_video(64 + scale8(tw, 191));
            leds[i] = c;
        } else if (effId == 33) { // triplet_chase (3-bulb float color blocks chasing continuously)
            int loopLen = max(9, activeCount);
            int32_t shift = (int32_t)((elapsed * 3) / max((uint32_t)400, beatMs * 2)) * (dir >= 0 ? 1 : -1);
            int pos = ((i - shift) % loopLen + loopLen) % loopLen;
            uint8_t group = (uint8_t)((pos / 3) % 3);
            leds[i] = getFloatPaletteColor(myFloatNumber, group);
        }
    }
#if defined(COSTUME_FULL_562_MODE) && COSTUME_FULL_562_MODE
    if (effId == 33 && NUM_LEDS >= 562) {
        int32_t shift = (int32_t)((elapsed * 3) / max((uint32_t)400, beatMs * 2)) * (dir >= 0 ? 1 : -1);
        for (int f = 256; f <= 280; f++) {
            uint8_t step = pgm_read_byte(&FAIRY_STRAND1_SPATIAL_STEP[f - 256]);
            int pos = (((int)step - shift) % 50 + 50) % 50;
            leds[f] = getFloatPaletteColor(myFloatNumber, (uint8_t)((pos / 3) % 3));
        }
        for (int f = 537; f <= 561; f++) {
            uint8_t step = 25 + (24 - pgm_read_byte(&FAIRY_STRAND2_SPATIAL_STEP[f - 537]));
            int pos = (((int)step - shift) % 50 + 50) % 50;
            leds[f] = getFloatPaletteColor(myFloatNumber, (uint8_t)((pos / 3) % 3));
        }
    }
#endif
    return true;
}

void renderAmbientFallback(uint32_t now) {
#if defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN >= 20) && (AMBIENT_FALLBACK_PATTERN <= 33)
    if (renderCatalogEffect20to32(AMBIENT_FALLBACK_PATTERN, COSTUME_SPEED_BPM, now, 0, COSTUME_AMBIENT_DIRECTION)) return;
#endif
    uint32_t beatMs = 60000 / max((uint16_t)20, (uint16_t)COSTUME_SPEED_BPM);
    int activeCount = isCurrentFloatMatrix16x16() ? getMatrixActiveLedCount() : FRONT_LEDS;
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
        if (i >= activeCount) {
            leds[i] = CRGB::Black;
            continue;
        }
#if defined(COSTUME_AMBIENT_COLOR_MODE) && (COSTUME_AMBIENT_COLOR_MODE == 1)
        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
        CRGB baseColor = FLEET_ROSTER_INFO[floatIdx].color;
#elif defined(COSTUME_AMBIENT_COLOR_MODE) && (COSTUME_AMBIENT_COLOR_MODE == 2)
        CRGB baseColor = CRGB(255, 210, 120);
#elif defined(COSTUME_AMBIENT_COLOR_MODE) && (COSTUME_AMBIENT_COLOR_MODE == 3) && defined(AMBIENT_CUSTOM_COLOR_RGB)
        CRGB baseColor = AMBIENT_CUSTOM_COLOR_RGB;
#elif defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
        CRGB baseColor = ARTWORK_PALETTE[i];
#elif defined(HAS_DEFAULT_FLOAT_PALETTES) && HAS_DEFAULT_FLOAT_PALETTES
        uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
        CRGB baseColor = (i < 256) ? DEFAULT_FLOAT_PALETTES[floatIdx][i] : FLEET_ROSTER_INFO[floatIdx].color;
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
#if !(defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE)
        baseColor.r = qadd8(baseColor.r, 20);
        baseColor.b = qsub8(baseColor.b, 35);
#endif
        leds[i] = baseColor;
#elif defined(AMBIENT_FALLBACK_PATTERN) && (AMBIENT_FALLBACK_PATTERN == COSTUME_PATTERN_CANDLE_FLICKER)
        uint32_t speedTime = (uint64_t)now * COSTUME_SPEED_BPM / 60;
        uint8_t flick = inoise8(i * 35, speedTime / 18);
        uint8_t bright = map(flick, 0, 255, 110, 255);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
        CRGB flame = ARTWORK_PALETTE[i];
#else
        CRGB flame = CRGB(255, 150, 30);
#endif
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
#else
        uint8_t spatialPos = (uint8_t)(i * 256 / FRONT_LEDS);
#endif
        uint8_t hueOffset = (uint8_t)(((now) * 256 / beatMs) % 256);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
        uint8_t wave = sin8(hueOffset + spatialPos);
        uint8_t bright = map(wave, 0, 255, 90, 255);
        CRGB c = ARTWORK_PALETTE[i];
        c.nscale8_video(bright);
        if (wave > 220) {
            uint8_t spark = (wave - 220) * 4;
            c += CRGB(spark / 3, spark / 3, spark / 3);
        }
        leds[i] = c;
#else
#if defined(COSTUME_AMBIENT_DIRECTION) && (COSTUME_AMBIENT_DIRECTION < 0)
        leds[i] = CHSV(hueOffset - spatialPos, 240, 255);
#else
        leds[i] = CHSV(hueOffset + spatialPos, 240, 255);
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
#if defined(COSTUME_FULL_562_MODE) && COSTUME_FULL_562_MODE
                uint16_t waveCycleMs = max((uint16_t)1400, (uint16_t)((60000 / max((uint16_t)20, bpm)) * 3));
                uint16_t waveHead = (uint16_t)(((now % waveCycleMs) * 1000) / waveCycleMs);
                for (int i = 0; i < NUM_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    uint16_t pos = getCostumePacedLoopPosition(i);
                    int16_t diff = abs((int16_t)pos - (int16_t)waveHead);
                    int16_t circDist = min(diff, (int16_t)(1000 - diff));
                    if (circDist < 85) { // 8.5% wave width (~4 fairy LEDs, ~45 panel pixels)
                        uint8_t intensity = map(circDist, 0, 85, 255, 60);
                        leds[i] = CRGB(intensity, (uint8_t)(intensity * 0.86), (uint8_t)(intensity * 0.45));
                    } else {
                        leds[i] = CRGB(15, 10, 4);
                    }
                }
#elif defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                uint8_t waveCenter = (uint8_t)(((now / 8) * max((uint16_t)20, bpm) / 120) % 256);
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    CRGB c = ARTWORK_PALETTE[i];
#if defined(HAS_SPATIAL_METRICS) && HAS_SPATIAL_METRICS
                    uint8_t pos = pgm_read_byte(&SPATIAL_X_BYTE[i]);
#else
                    uint8_t pos = (uint8_t)(i * 255 / max(1, FRONT_LEDS - 1));
#endif
                    uint8_t dist = abs((int)pos - (int)waveCenter);
                    if (dist < 48) {
                        uint8_t boost = 255 - (dist * 3);
                        c.nscale8_video(boost);
                        if (dist < 10) c += CRGB(65, 65, 65);
                        leds[i] = c;
                    } else {
                        c.nscale8_video(100); // Preserve 40% true artwork color outside wave crest
                        leds[i] = c;
                    }
                }
#else
                uint32_t waveTimer = now % 3000;
                uint8_t waveHeadPos = map(waveTimer, 0, 3000, 0, FRONT_LEDS - 1);
                renderTravelingWave(myFloatNumber, waveHeadPos);
#endif
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
#if !(defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE)
                    c.r = qadd8(c.r, 20);
                    c.b = qsub8(c.b, 35);
#endif
                    leds[i] = c;
                }
            } else if (eff == 13) { // candle_flicker
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
                    uint8_t flick = inoise8(i * 60, now / 8);
                    uint8_t bright = map(flick, 0, 255, 60, 255);
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    CRGB flame = ARTWORK_PALETTE[i];
#else
                    CRGB flame = CRGB(255, 150, 30);
#endif
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
#else
                    uint8_t spatialPos = (uint8_t)(i * 256 / FRONT_LEDS);
#endif
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    uint8_t wave = sin8(hueOffset + spatialPos);
                    uint8_t bright = map(wave, 0, 255, 90, 255);
                    CRGB c = ARTWORK_PALETTE[i];
                    c.nscale8_video(bright);
                    if (wave > 220) {
                        uint8_t spark = (wave - 220) * 4;
                        c += CRGB(spark / 3, spark / 3, spark / 3);
                    }
                    leds[i] = c;
#else
                    leds[i] = CHSV(hueOffset + spatialPos, 240, 255);
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
            } else if (eff >= 20 && eff <= 33) {
                renderCatalogEffect20to32(eff, bpm, now, autonomousShowStartTime, 1);
            } else { // 0: steady_sparkle / default
                for (int i = 0; i < FRONT_LEDS && i < MAX_LEDS_CAPACITY; i++) {
#if defined(HAS_CUSTOM_PALETTE) && HAS_CUSTOM_PALETTE
                    leds[i] = ARTWORK_PALETTE[i];
#elif defined(HAS_DEFAULT_FLOAT_PALETTES) && HAS_DEFAULT_FLOAT_PALETTES
                    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    leds[i] = (i < 256) ? DEFAULT_FLOAT_PALETTES[floatIdx][i] : FLEET_ROSTER_INFO[floatIdx].color;
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
        if (COSTUME_SPARKLE_RATE > 0 && ((esp_random() % 10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100))) {
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
        if (COSTUME_SPARKLE_RATE > 0 && ((esp_random() % 10000) < (uint16_t)(COSTUME_SPARKLE_RATE * 100))) {
            leds[i] = CRGB(255, 255, 240);
        }
    }
#endif

    // Duplicate front LEDs to back LEDs (or scatter active LEDs across 16x16 matrix)
    duplicateFrontToBack();

    // Status LED gentle breath during autonomous sequence
    uint8_t breathLed = ((seqTime / 1000) % 2 == 0) ? HIGH : LOW;
    digitalWrite(STATUS_LED_PIN, breathLed);

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
// Show Name: 💥 The Supernova Spectacular (30s)
// Total Duration: 30.0s (30000 ms)
// Generated by Main Street Electrical Parade Simulator

void render30sFleetRoutine(uint32_t elapsedMs) {
    uint8_t floatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
    CRGB routineColor = STANDARD_FLEET_COLORS[fleetRoutineCycle % 7];

    if (elapsedMs < 1000) {
        // Block 1: Dramatic Blackout (0.0s - 1.0s)
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }
    else if (elapsedMs < 4500) {
        // Block 2: Dual Collision & Shockwave (1.0s - 4.5s)
        float p = (float)(elapsedMs - 1000) / 3500.0f;
        if (p < 0.45f) {
            float inP = p / 0.45f;
            float headL = inP * 3.0f;
            float headR = 6.0f - (inP * 3.0f);
            float distL = fabs((float)floatIdx - headL);
            float distR = fabs((float)floatIdx - headR);
            float minDist = fminf(distL, distR);
            if (minDist <= 1.4f) {
                float intensity = 1.0f - (minDist / 1.4f);
                CRGB col = (distL < distR) ? STANDARD_FLEET_COLORS[(fleetRoutineCycle + 1) % 7] : CRGB(255, 60, 180);
                col.nscale8_video((uint8_t)(intensity * 255));
                fill_solid(leds, FRONT_LEDS, col);
            } else {
                fill_solid(leds, FRONT_LEDS, CRGB::Black);
            }
        } else if (p < 0.60f) {
            // Impact supernova flash at Float 4 (Peter Pan)
            if (floatIdx == 3) {
                fill_solid(leds, FRONT_LEDS, CRGB(255, 255, 255));
            } else {
                CRGB dimCol = STANDARD_FLEET_COLORS[(fleetRoutineCycle + 1) % 7];
                dimCol.nscale8_video(30);
                fill_solid(leds, FRONT_LEDS, dimCol);
            }
        } else {
            // Rebound shockwave radiating back out
            float shockP = (p - 0.60f) / 0.40f;
            float shockRadius = shockP * 3.2f;
            float distFromCenter = fabs((float)floatIdx - 3.0f);
            float ringDist = fabs(distFromCenter - shockRadius);
            if (ringDist <= 1.2f) {
                float intensity = 1.0f - (ringDist / 1.2f);
                CRGB col = blend(STANDARD_FLEET_COLORS[(fleetRoutineCycle + 1) % 7], CRGB(255, 240, 180), 120);
                col.nscale8_video((uint8_t)(intensity * 255));
                fill_solid(leds, FRONT_LEDS, col);
            } else {
                fill_solid(leds, FRONT_LEDS, CRGB::Black);
            }
        }
    }
    else if (elapsedMs < 7500) {
        // Block 3: Mirror Pair Echo (Butterfly Ripple) (4.5s - 7.5s)
        float p = (float)(elapsedMs - 4500) / 3000.0f;
        int subPhase = (int)(p * 4.0f) % 4;
        float subP = fmodf(p * 4.0f, 1.0f);
        uint8_t pulse = (uint8_t)(sinf(subP * 3.14159f) * 255);
        bool isActivePair = false;
        if (subPhase == 0 && floatIdx == 3) isActivePair = true;
        else if (subPhase == 1 && (floatIdx == 2 || floatIdx == 4)) isActivePair = true;
        else if (subPhase == 2 && (floatIdx == 1 || floatIdx == 5)) isActivePair = true;
        else if (subPhase == 3 && (floatIdx == 0 || floatIdx == 6)) isActivePair = true;

        if (isActivePair) {
            CRGB col = routineColor;
            col.nscale8_video(pulse);
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            CRGB dimCol = routineColor;
            dimCol.nscale8_video(25);
            fill_solid(leds, FRONT_LEDS, dimCol);
        }
    }
    else if (elapsedMs < 11000) {
        // Block 4: Silky Cascade Dissolve (7.5s - 11.0s)
        float p = (float)(elapsedMs - 7500) / 3500.0f;
        float runnerOffset = (float)floatIdx / 7.0f;
        float localRunnerP = fminf(1.0f, fmaxf(0.0f, (p - runnerOffset * 0.5f) / 0.5f));
        uint8_t blendAmt = (uint8_t)(0.5f * (1.0f - cosf(localRunnerP * 3.14159f)) * 255);
        CRGB colA = STANDARD_FLEET_COLORS[(fleetRoutineCycle + 3) % 7];
        CRGB colB = CRGB(0, 220, 255);
        CRGB finalCol = blend(colA, colB, blendAmt);
        fill_solid(leds, FRONT_LEDS, finalCol);
    }
    else if (elapsedMs < 14000) {
        // Block 5: Ping-Pong Double Rebound (11.0s - 14.0s)
        float bounceCycle = fmod((float)(elapsedMs - 11000) / (3000.0f / 2.0f), 2.0f);
        float headPos = (bounceCycle < 1.0f) ? (bounceCycle * 6.0f) : ((2.0f - bounceCycle) * 6.0f);
        float dist = fabs((float)floatIdx - headPos);

        if (dist <= 1.8f) {
            float intensity = 1.0f - (dist / 1.8f);
            CRGB col = STANDARD_FLEET_COLORS[(fleetRoutineCycle + 4) % 7];
            col.nscale8_video((uint8_t)(intensity * 255));
            fill_solid(leds, FRONT_LEDS, col);
        } else {
            fill_solid(leds, FRONT_LEDS, CRGB::Black);
        }
    }
    else if (elapsedMs < 15000) {
        // Block 6: Anticipation Silence (14.0s - 15.0s)
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }
    else if (elapsedMs < 18500) {
        // Block 7: Fairy Dust Waterfall Cascade (15.0s - 18.5s)
        float p = (float)(elapsedMs - 15000) / 3500.0f;
        float center = p * 6.0f;
        float dist = fabs((float)floatIdx - center);
        CRGB baseCol = STANDARD_FLEET_COLORS[(fleetRoutineCycle + 6) % 7];
        baseCol.nscale8_video(30);
        fill_solid(leds, FRONT_LEDS, baseCol);
        if (dist <= 1.5f) {
            float intensity = 1.0f - (dist / 1.5f);
            uint8_t sparkleCount = (uint8_t)(intensity * 25.0f);
            for (int s = 0; s < sparkleCount; s++) {
                uint16_t rndPix = esp_random() % FRONT_LEDS;
                leds[rndPix] = (random8(100) < 60) ? CRGB(255, 255, 255) : blend(baseCol, CRGB(255, 215, 0), 160);
            }
        }
    }
    else if (elapsedMs < 21500) {
        // Block 8: Baton Leapfrog Chase (18.5s - 21.5s)
        uint8_t activeRunner = ((elapsedMs - 18500) / 428) % 7;
        if (floatIdx == activeRunner) {
            fill_solid(leds, FRONT_LEDS, CRGB(255, 245, 220));
        } else {
            CRGB dimBase = FLEET_ROSTER_INFO[floatIdx].color;
            dimBase.nscale8_video(40);
            fill_solid(leds, FRONT_LEDS, dimBase);
        }
    }
    else if (elapsedMs < 24500) {
        // Block 9: Synchronized Cosmic Breath (21.5s - 24.5s)
        uint8_t breath = beatsin8(36, 70, 255, fleetRoutineStartTime + 21500);
        CRGB col = routineColor;
        col.nscale8_video(breath);
        if (breath > 240) {
            col = blend(col, CRGB(255, 255, 230), map(breath, 240, 255, 0, 180));
        }
        fill_solid(leds, FRONT_LEDS, col);
    }
    else if (elapsedMs < 29500) {
        // Block 10: Grand Finale Carnival Crescendo (24.5s - 29.5s)
        float p = (float)(elapsedMs - 24500) / 5000.0f;
        uint8_t hue = (uint8_t)(elapsedMs * 3 / 10 + floatIdx * 36);
        fill_solid(leds, FRONT_LEDS, CHSV(hue, 220, 255));
        if (p >= 0.65f && ((elapsedMs / 70) % 2 == 0)) {
            fill_solid(leds, FRONT_LEDS, CRGB(255, 255, 255));
        }
    }
    else if (elapsedMs < 30000) {
        // Block 11: Curtain Blackout & Return (29.5s - 30.0s)
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }
    else {
        // Routine completed: blackout curtain
        fill_solid(leds, FRONT_LEDS, CRGB::Black);
    }

    // Duplicate front LEDs to back LEDs (or scatter active LEDs across 16x16 matrix)
    duplicateFrontToBack();

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

    // 1. Initialize Wi-Fi in Station Mode & Lock ESP-NOW Channel
    WiFi.persistent(false);
    WiFi.setAutoReconnect(false);
    WiFi.mode(WIFI_STA);
    WiFi.disconnect(true, true); // Erase any cached NVS STA credentials & stop background scanning
    delay(50);

    // Optional: Connect to Home Wi-Fi ONLY if credentials are explicitly configured (Fast 1.5s check)
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
        if (WiFi.status() != WL_CONNECTED) {
            // CRITICAL: Cancel STA connection attempt immediately so ESP32 never hops channels in background!
            WiFi.disconnect(true, true);
        }
    }
#endif

    if (WiFi.status() == WL_CONNECTED) {
        esp_wifi_set_ps(WIFI_PS_NONE);
        digitalWrite(STATUS_LED_PIN, HIGH); // Solid blue LED = Connected to Home Wi-Fi!
        Serial.print("[WIFI] Connected! IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        digitalWrite(STATUS_LED_PIN, LOW); // LED OFF = Direct Offline / Battery Mode
#if defined(ENABLE_WIFI_LIVE_STREAM) && defined(AP_SSID)
        // Enable SoftAP only when flashed specifically as a Wi-Fi Live Stream Receiver
        WiFi.mode(WIFI_AP_STA);
        WiFi.softAP(AP_SSID, AP_PASSWORD, ESPNOW_WIFI_CHANNEL);
        Serial.printf("[WIFI] Standalone Hotspot Active: '%s' on Ch %d (IP: %s)\n",
                      AP_SSID, ESPNOW_WIFI_CHANNEL, WiFi.softAPIP().toString().c_str());
#else
        WiFi.mode(WIFI_STA);
#endif
        // Lock 2.4GHz radio strictly to ESP-NOW Channel 1 with zero modem sleep latency
        esp_wifi_set_promiscuous(true);
        esp_wifi_set_channel(ESPNOW_WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
        esp_wifi_set_promiscuous(false);
        esp_wifi_set_ps(WIFI_PS_NONE);
        Serial.printf("[WIFI] Offline Walkie-Talkie Mode: Locked to Channel %d (WIFI_PS_NONE, zero background scanning).\n",
                      ESPNOW_WIFI_CHANNEL);
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
    uint8_t effectiveBrightness = MAX_BRIGHTNESS;
#if defined(COSTUME_BRIGHTNESS)
    effectiveBrightness = COSTUME_BRIGHTNESS;
#endif
    if (isCurrentFloatMatrix16x16() && effectiveBrightness > 35) {
        effectiveBrightness = max((uint8_t)15, (uint8_t)(effectiveBrightness / 2));
    }
    FastLED.setBrightness(effectiveBrightness);
    // Start at 350mA for the first 5 seconds after boot so laptop 500mA USB ports never brown out on plug-in
    FastLED.setMaxPowerInVoltsAndMilliamps(5, 350);

    Serial.println("[INFO] Setup complete! Starting default parade loop...\n");
}

// ============================================================================
// MAIN LOOP: AUTO-SWITCHES BETWEEN SIMULATOR STREAM & ESP-NOW PARADE FLEET
// ============================================================================
void loop() {
    uint32_t now = millis();
    static bool fullPowerUnlocked = false;
    if (!fullPowerUnlocked && now > 5000) {
        fullPowerUnlocked = true;
        FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_MILLIAMPS);
    }

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

        if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY || currentStandaloneMode == SHOW_MODE_PHOTO_STATIC || currentStandaloneMode == SHOW_MODE_WARM_WHITE_SPARKLE) {
            if (isLeader) {
                // Leader: Wake ENTIRE FLEET into Solo Show Mode (parade baseline, does NOT start 30s fleet routine)
                if (currentStandaloneMode == SHOW_MODE_WARM_WHITE_SPARKLE) {
                    broadcastWarmWhitePacket(0x49);
                } else if (currentStandaloneMode == SHOW_MODE_PHOTO_STATIC) {
                    broadcastPhotoModePacket(0x47);
                } else {
                    broadcastStandbyPacket(0x51);   // Wake entire fleet into solo show mode
                }
                previousStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                autonomousShowStartTime = now;

                uint8_t wakeFloatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                CRGB wakeColor = FLEET_ROSTER_INFO[wakeFloatIdx].color;

                fillActiveCostumeSolid(wakeColor); // Float signature color flash
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, HIGH);
                delay(150);
                fillActiveCostumeSolid(CRGB::Black);
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, LOW);

                Serial.println("[LEADER] ☀️ Button 1 Tap -> Woke ENTIRE FLEET into Solo Show Mode! (Tap again while awake to start 30s Fleet Show)");
            } else {
                // Follower: Wake LOCALLY to baseline solo show animation (do NOT start theatrical fleet routine)
                previousStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                autonomousShowStartTime = now;

                uint8_t wakeFloatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                CRGB wakeColor = FLEET_ROSTER_INFO[wakeFloatIdx].color;

                fillActiveCostumeSolid(wakeColor); // Float signature color flash
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, HIGH);
                delay(150);
                fillActiveCostumeSolid(CRGB::Black);
                FastLED.show();
                digitalWrite(STATUS_LED_PIN, LOW);

                Serial.printf("[FOLLOWER] Float %d Single Tap -> Woke locally into Solo Show Mode.\n", myFloatNumber);
            }
        } else if (isLeader) {
            // Leader active toggle
            if (currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE || currentStandaloneMode == SHOW_MODE_RAPID_ROLL_CALL) {
                currentStandaloneMode = SHOW_MODE_AUTONOMOUS_SEQUENCE;
                broadcastFleetRoutinePacket(0x00, 0);
                Serial.println("[LEADER] Early stop triggered via Button 1 -> returning to baseline.");

                for (int f = 0; f < 2; f++) {
                    fillActiveCostumeSolid(CRGB(255, 140, 0));
                    FastLED.show();
                    digitalWrite(STATUS_LED_PIN, HIGH);
                    delay(120);
                    fillActiveCostumeSolid(CRGB::Black);
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
            // Follower active: Button 1 is ignored while awake (only wake-up from Standby and 5s Hold Config are processed)
            Serial.printf("[FOLLOWER] Float %d Button 1 tap ignored while awake (wake-up only; fleet show reserved for Leader).\n", myFloatNumber);
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
    static uint8_t b2PendingTaps = 0;
    static uint32_t b2FirstTapReleaseTime = 0;

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
                currentStandaloneMode = SHOW_MODE_CORRAL_STANDBY;

                if (isLeader) {
                    broadcastStandbyPacket(0x50);
                    Serial.println("[LEADER] 🌙 Button 2 Held 3s -> Dropped ENTIRE FLEET into Corral Standby Mode!");
                } else {
                    Serial.printf("[FOLLOWER] Float %d Button 2 Held 3s -> Dropped locally into Corral Standby Mode.\n", myFloatNumber);
                }

                for (int f = 0; f < 3; f++) {
                    fillActiveCostumeSolid(CRGB(30, 60, 255)); // 3 Soft Indigo pulses
                    FastLED.show();
                    digitalWrite(STATUS_LED_PIN, HIGH);
                    delay(80);
                    fillActiveCostumeSolid(CRGB::Black);
                    FastLED.show();
                    digitalWrite(STATUS_LED_PIN, LOW);
                    delay(60);
                }
                // Wait until Button 2 is physically released so extended holds (>3s) never latch a false tap into Photo Mode
                while (isButton2Down()) {
                    delay(10);
                }
                b2WasPressed = false;
                b2HoldHandled = false;
                Serial.println("[BUTTON 2] Physically released after 3s sleep hold -> staying firmly in Corral Standby Mode.");
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

        if (b2HoldHandled) {
            b2HoldHandled = false;
            Serial.println("[BUTTON 2] Released after hold completed -> staying in current mode.");
            return;
        }

        if (pressDuration >= 1000) {
            Serial.printf("[BUTTON 2] Sleep hold aborted after %u ms -> returning to baseline with zero changes.\n", pressDuration);
            return;
        }

        // Button 2 Tap & Double-Tap detection (< 400ms double-tap window)
        if (!b2HoldHandled && pressDuration >= 50 && pressDuration < 600) {
            if (b2PendingTaps == 1 && (now - b2FirstTapReleaseTime <= 400)) {
                // DOUBLE TAP DETECTED on Button 2: Toggle 3% Warm White Starlight Mode!
                b2PendingTaps = 0;
                if (currentStandaloneMode == SHOW_MODE_WARM_WHITE_SPARKLE) {
                    // Turn OFF Warm White Mode -> return to Solo Show
                    currentStandaloneMode = previousStandaloneMode;
                    if (isLeader) {
                        broadcastWarmWhitePacket(0x49);
                        Serial.println("[LEADER] ✨ Button 2 Double-Tap -> Warm White Mode turned OFF for ENTIRE FLEET!");
                    } else {
                        Serial.printf("[FOLLOWER] Float %d Button 2 Double-Tap -> Warm White Mode turned OFF (local only).\n", myFloatNumber);
                    }
                    uint8_t wakeFloatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
                    fillActiveCostumeSolid(FLEET_ROSTER_INFO[wakeFloatIdx].color);
                    duplicateFrontToBack();
                    FastLED.show();
                    delay(100);
                } else {
                    // Turn ON Warm White Mode!
                    previousStandaloneMode = currentStandaloneMode;
                    if (isLeader) {
                        broadcastWarmWhitePacket(0x48);
                        Serial.println("[LEADER] ✨ Button 2 Double-Tap -> 3% Warm White Starlight Mode engaged for ENTIRE FLEET!");
                    } else {
                        Serial.printf("[FOLLOWER] Float %d Button 2 Double-Tap -> 3% Warm White Starlight Mode engaged (local only).\n", myFloatNumber);
                    }
                    // Visible confirmation: 2 distinct warm white pulses (150ms ON, 100ms OFF)
                    for (int f = 0; f < 2; f++) {
                        fillActiveCostumeSolid(CRGB(255, 185, 110));
                        FastLED.show();
                        delay(150);
                        fillActiveCostumeSolid(CRGB::Black);
                        FastLED.show();
                        delay(100);
                    }
                    currentStandaloneMode = SHOW_MODE_WARM_WHITE_SPARKLE;
                }
            } else {
                b2PendingTaps = 1;
                b2FirstTapReleaseTime = now;
            }
        }
    }

    // Evaluate Button 2 single tap once double-tap window expires (400ms)
    if (b2PendingTaps > 0 && !b2Pressed && (now - b2FirstTapReleaseTime > 400)) {
        b2PendingTaps = 0;
        if (currentStandaloneMode == SHOW_MODE_WARM_WHITE_SPARKLE) {
            // Single tap while in Warm White Mode exits back to Solo Show
            currentStandaloneMode = previousStandaloneMode;
            if (isLeader) {
                broadcastWarmWhitePacket(0x49);
                Serial.println("[LEADER] ☀️ Button 2 Tap -> Exited Warm White Mode for ENTIRE FLEET into Solo Show!");
            } else {
                Serial.printf("[FOLLOWER] Float %d Button 2 Tap -> Exited Warm White Mode locally into Solo Show.\n", myFloatNumber);
            }
            uint8_t wakeFloatIdx = (myFloatNumber >= 1 && myFloatNumber <= 7) ? (myFloatNumber - 1) : 0;
            fillActiveCostumeSolid(FLEET_ROSTER_INFO[wakeFloatIdx].color);
            duplicateFrontToBack();
            FastLED.show();
            delay(100);
        } else if (isLeader) {
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

                // Duplicate front LEDs to back LEDs (or scatter active LEDs across 16x16 matrix)
                duplicateFrontToBack();
                
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
        } else if (currentStandaloneMode == SHOW_MODE_WARM_WHITE_SPARKLE) {
            renderWarmWhiteSparkle(now);
            FastLED.show();
            digitalWrite(STATUS_LED_PIN, HIGH);
            delay(20);
        } else if (currentStandaloneMode == SHOW_MODE_CORRAL_STANDBY) {
            renderCorralStandby(now);
            if (!isCurrentFloatMatrix16x16()) {
                duplicateFrontToBack();
            }
            FastLED.show();
            delay(20);
        } else if (currentStandaloneMode == SHOW_MODE_RAPID_ROLL_CALL) {
            uint32_t elapsedMs = now - rapidRollCallStartTime;
            if (elapsedMs < RAPID_ROLL_CALL_TOTAL_MS) {
                static uint32_t lastRollCallSyncTx = 0;
                if (isLeader && (now - lastRollCallSyncTx >= 150)) {
                    lastRollCallSyncTx = now;
                    broadcastRapidRollCallPacket(elapsedMs, false);
                }
                renderRapidRollCall(elapsedMs);
            } else {
                currentStandaloneMode = previousStandaloneMode;
                fillActiveCostumeSolid(CRGB::Black);
                FastLED.show();
                Serial.println("[ROLL CALL] ⚡ Rapid Attendance Roll Call complete -> returned to baseline.");
            }
        } else if (currentStandaloneMode == SHOW_MODE_FLEET_30S_ROUTINE) {
            uint32_t elapsedMs = now - fleetRoutineStartTime;
            if (elapsedMs < FLEET_ROUTINE_TOTAL_MS) {
                static uint32_t lastRoutineSyncTx = 0;
                if (isLeader && (now - lastRoutineSyncTx >= 250)) {
                    lastRoutineSyncTx = now;
                    broadcastFleetRoutinePacket(0x30, elapsedMs, false);
                }
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
