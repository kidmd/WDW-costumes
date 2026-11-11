/**
 * 🏰 Main Street Electrical Parade (WDW 10K) - Universal Panel & Bench Test Firmware
 * 
 * Purpose:
 * Immediately sets all connected LEDs (up to 562 LEDs: Dual 16x16 Matrices [512] + 50 Fairy Lights)
 * into the authentic 3% Incandescent Warm White (~2500K vintage filament glow) with calm starlight sparkles
 * on boot — with ZERO button clicking, zero pairing, and zero graphic masking required!
 * 
 * Hardware Specs:
 * - Microcontroller: ESP32 DevKit (GPIO 16 Data Out, GPIO 4 Button 1, GPIO 33 Button 2, GPIO 0 BOOT)
 * - LED Standard: WS2812B / WS2811 (5V, 2.0A FastLED power limit enforced)
 * - Capacity: 562 LEDs (covers Front 16x16 [256] + 50 Fairy Lights + Back 16x16 [256])
 * - Default Mode: 2500K Warm White Base (~3.1% duty cycle) + Calm Starlight Bloom & Fade (~200ms decay)
 * 
 * Interactive Controls (Optional Bench Testing):
 * - BOOT (GPIO 0) / Button 1 (GPIO 4): Tap to cycle Sparkle Rate (Calm -> Ultra-Subtle -> Parade -> Solid Warm)
 * - Button 2 (GPIO 33): Tap to toggle Color Order (GRB for 16x16 BTF matrix <-> RGB for pebble strings)
 * - Button 2 (GPIO 33): Hold (>1s) for Subpixel RGB Inspection Cycle (Red -> Green -> Blue -> White)
 */

#include <Arduino.h>
#include <FastLED.h>

#define DATA_PIN            16      // GPIO 16 - Main LED Data Out
#define STATUS_LED_PIN      2       // Onboard Blue LED indicator
#define BUTTON_1_PIN        4       // External Button 1 (Show Director)
#define BUTTON_2_PIN        33      // External Button 2 (Photo / Sleep)
#define BUTTON_BOOT_PIN     0       // Onboard BOOT button (GPIO 0)

#define NUM_LEDS            562     // Full buffer driving 562 LEDs (Front 16x16 [256] + Fairy [50] + Back 16x16 [256])
#define LED_TYPE            WS2812B // Standard 5V addressable LED protocol
#define MAX_BRIGHTNESS      60      // Bench-safe brightness matching MSEP costume baseline
#define MAX_POWER_MILLIAMPS 2000    // 5V, 2.0A safety limit for USB power banks and bench supplies

CRGB leds[NUM_LEDS];
static uint8_t sparkleLevel[NUM_LEDS] = {0}; // Per-LED sparkle intensity (0 = base, 255 = peak sparkle)
static uint8_t sparkleDecay[NUM_LEDS] = {24}; // Per-LED decay rate for organic non-uniform fade

// Sparkle Rate Presets (calibrated for 562-LED full costume & 50 FPS)
// Uses ESP32 hardware True Random Number Generator (esp_random()) to eliminate PRNG cycle resonance
static const uint16_t SPARKLE_PROB_PER_1000[4] = { 100, 30, 300, 0 }; // Probability per 20ms frame (Calm ~5/s, Subtle ~1.5/s, Parade ~15/s, Solid 0)
static const uint8_t  SPARKLE_MAX_PER_FRAME[4]  = { 1,   1,  2,   0 }; // Max sparkles that can spawn in one frame
static const char* SPARKLE_NAMES[4] = {
    "1: Calm Starlight (~4-6 twinkles/sec across 562 LEDs, soft ~200ms bloom & fade)",
    "2: Ultra-Subtle (~1-2 twinkles/sec, gentle starlight)",
    "3: Parade Sparkle (~12-15 twinkles/sec, lively theatrical sparkle)",
    "4: Solid Warm White (0% sparkles / Steady Photo Mode)"
};
static uint8_t currentSparklePreset = 0; // Starts at Preset 0: Calm Starlight

// Fairy Light Layout Presets (Mixed Color Order on single GPIO 16 line)
// WS2812B 16x16 Panels are native GRB. WS2812B/WS2811 Fairy Lights are native RGB.
enum FairyLayoutMode : uint8_t {
    FAIRY_LAYOUT_COSTUME_25_25  = 0, // Panel 1 (0..255) -> Fairy 1 (256..280, 25 LEDs) -> Panel 2 (281..536) -> Fairy 2 (537..561, 25 LEDs) [Default]
    FAIRY_LAYOUT_BENCH_END      = 1, // Panels (0..511) -> Fairy 50 (512..561)
    FAIRY_LAYOUT_COSTUME_13_37  = 2, // Panel 1 (0..255) -> Fairy 1 (256..268, 13 LEDs) -> Panel 2 (269..524) -> Fairy 2 (525..561, 37 LEDs)
    FAIRY_LAYOUT_BENCH_MIDDLE   = 3, // Panel 1 (0..255) -> Fairy 50 (256..305) -> Panel 2 (306..561)
    FAIRY_LAYOUT_ALL_RGB        = 4  // All LEDs RGB (Full strip swap for standalone pebble strands)
};

static uint8_t currentFairyLayout = FAIRY_LAYOUT_COSTUME_25_25; // Default: 25 front fairy + 25 back fairy (matches user physical wiring)
static const char* FAIRY_LAYOUT_NAMES[5] = {
    "1: Costume 25/25 Split (Fairy 1 at 256..280 [25], Panel 2 at 281..536, Fairy 2 at 537..561 [25]) [DEFAULT]",
    "2: Bench End (Panels at 0..511, Fairy 50 at 512..561)",
    "3: Costume 13/37 Split (Fairy 1 at 256..268 [13], Panel 2 at 269..524, Fairy 2 at 525..561 [37])",
    "4: Bench Middle (Fairy 50 at 256..305, Panels at 0..255 & 306..561)",
    "5: All RGB (Full strip swap for standalone pebble strands)"
};

inline bool isFairyPixel(uint16_t i) {
    switch (currentFairyLayout) {
        case FAIRY_LAYOUT_COSTUME_25_25:
            // 25 bulbs on front harness (256..280) + 25 bulbs on back harness/tail (537..561)
            return ((i >= 256 && i <= 280) || (i >= 537 && i <= 561));
        case FAIRY_LAYOUT_BENCH_END:
            return (i >= 512 && i < 562);
        case FAIRY_LAYOUT_COSTUME_13_37:
            return ((i >= 256 && i <= 268) || (i >= 525 && i <= 561));
        case FAIRY_LAYOUT_BENCH_MIDDLE:
            return (i >= 256 && i < 306);
        case FAIRY_LAYOUT_ALL_RGB:
            return true;
        default:
            return false;
    }
}

static bool isRgbInspectionMode = false; // True when running Red/Green/Blue/White subpixel check

// Button Debounce & Timing State
static uint32_t lastB1PressTime = 0;
static uint32_t lastB2PressTime = 0;
static uint32_t b2PressStartTime = 0;
static bool b1PrevDown = false;
static bool b2PrevDown = false;

inline bool isButton1Down() {
    return (digitalRead(BUTTON_1_PIN) == LOW) || (digitalRead(BUTTON_BOOT_PIN) == LOW);
}

inline bool isButton2Down() {
    return (digitalRead(BUTTON_2_PIN) == LOW);
}

void setup() {
    Serial.begin(115200);
    delay(200);

    Serial.println();
    Serial.println("================================================================");
    Serial.println(" 🏰 MSEP UNIVERSAL PANEL & BENCH TEST FIRMWARE");
    Serial.println("================================================================");
    Serial.println(" * Mode: 2500K Incandescent Warm White + Calm Starlight Twinkle");
    Serial.println(" * Sparkle Decay: Smooth 200ms bloom & fade (zero strobe noise)");
    Serial.println(" * Target: GPIO 16 driving 562 LEDs (Dual 16x16 Matrices + 50 Fairy Lights)");
    Serial.println(" * FastLED Safety: 5V 2000mA Max Current Limit Active");
    Serial.println(" * Default Color Order: GRB (BTF-LIGHTING 16x16 Matrix Standard)");
    Serial.println("----------------------------------------------------------------");
    Serial.println(" Controls:");
    Serial.println("  - BOOT / Button 1 (GPIO 4/0): Tap to cycle Sparkle Rate (Calm -> Subtle -> Parade -> Solid)");
    Serial.println("  - Button 2 (GPIO 33): Tap to cycle Fairy Layout (Bench Middle -> Bench End -> Costume -> GRB -> RGB)");
    Serial.println("  - Button 2 (GPIO 33): Hold (>1s) for Subpixel RGB Inspection Cycle (Red -> Green -> Blue -> White)");
    Serial.println("================================================================");

    pinMode(STATUS_LED_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, HIGH); // Solid ON indicating active test firmware

    pinMode(BUTTON_1_PIN, INPUT_PULLUP);
    pinMode(BUTTON_2_PIN, INPUT_PULLUP);
    pinMode(BUTTON_BOOT_PIN, INPUT_PULLUP);

    // Initialize FastLED with GRB order by default (WS2812B 16x16 matrix standard)
    FastLED.addLeds<LED_TYPE, DATA_PIN, GRB>(leds, NUM_LEDS)
           .setCorrection(TypicalLEDStrip);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_POWER_MILLIAMPS);
    FastLED.setBrightness(MAX_BRIGHTNESS);

    // Initial Warm White illumination across entire panel
    fill_solid(leds, NUM_LEDS, CRGB(64, 46, 28));
    FastLED.show();
}

void renderWarmWhiteSparkles() {
    // Balanced Warm Incandescent / ~2500K Vintage Filament Glow
    // Base color: CRGB(255, 185, 110) scaled by 64 (~3.1% duty cycle)
    const CRGB baseCol = CRGB(64, 46, 28);
    // Starlight sparkle color: pure bright starlight pop scaled by 192 (~3x pop over base)
    const CRGB sparklePeak = CRGB(192, 192, 192);

    // 1. Smoothly decay active sparkles
    for (int i = 0; i < NUM_LEDS; i++) {
        if (sparkleLevel[i] > 0) {
            sparkleLevel[i] = qsub8(sparkleLevel[i], sparkleDecay[i]);
        }
    }

    // 2. Spawn new sparkles using ESP32 True Hardware RNG (esp_random())
    // This completely eliminates the 16-bit LCG harmonic resonance that caused sparkles to repeat on the same few LEDs!
    uint16_t prob = SPARKLE_PROB_PER_1000[currentSparklePreset];
    uint8_t maxSp = SPARKLE_MAX_PER_FRAME[currentSparklePreset];
    for (uint8_t s = 0; s < maxSp; s++) {
        if (prob > 0 && ((esp_random() % 1000) < prob)) {
            uint16_t target = esp_random() % NUM_LEDS;
            if (sparkleLevel[target] == 0) {
                // Organic variance: slight peak brightness variance (210..255) and decay duration (~160ms - 280ms)
                sparkleLevel[target] = 210 + (esp_random() % 46);
                sparkleDecay[target] = 18 + (esp_random() % 14);
            }
        }
    }

    // 3. Render base warm white and interpolate sparkles
    for (int i = 0; i < NUM_LEDS; i++) {
        CRGB col;
        if (sparkleLevel[i] == 0) {
            col = baseCol;
        } else {
            uint8_t sp = sparkleLevel[i];
            col = CRGB(
                lerp8by8(baseCol.r, sparklePeak.r, sp),
                lerp8by8(baseCol.g, sparklePeak.g, sp),
                lerp8by8(baseCol.b, sparklePeak.b, sp)
            );
        }

        // Color order correction:
        // WS2812B 16x16 Panels are native GRB. Fairy lights are RGB chips on a GRB data stream.
        // Swapping Red and Green on fairy lights eliminates the green tint so they match the warm white!
        if (isFairyPixel(i)) {
            leds[i] = CRGB(col.g, col.r, col.b);
        } else {
            leds[i] = col;
        }
    }
}

void renderSubpixelRgbTest(uint32_t now) {
    // 8-second cycle: 2s Red -> 2s Green -> 2s Blue -> 2s Pure White
    uint8_t phase = (now / 2000) % 4;
    CRGB testCol;
    switch (phase) {
        case 0: testCol = CRGB(180, 0, 0); break;   // Red inspection
        case 1: testCol = CRGB(0, 180, 0); break;   // Green inspection
        case 2: testCol = CRGB(0, 0, 180); break;   // Blue inspection
        default: testCol = CRGB(120, 120, 120); break; // Full white inspection
    }
    CRGB fairyTestCol = CRGB(testCol.g, testCol.r, testCol.b);
    for (int i = 0; i < NUM_LEDS; i++) {
        leds[i] = isFairyPixel(i) ? fairyTestCol : testCol;
    }
}

void loop() {
    uint32_t now = millis();

    // 1. Button 1 / BOOT button: Cycle Sparkle Presets (Calm -> Ultra-Subtle -> Parade -> Solid Warm)
    bool b1Down = isButton1Down();
    if (b1Down && !b1PrevDown && (now - lastB1PressTime > 300)) {
        lastB1PressTime = now;
        currentSparklePreset = (currentSparklePreset + 1) % 4;
        isRgbInspectionMode = false; // Return to sparkle mode
        Serial.printf("[SPARKLE PRESET] %s\n", SPARKLE_NAMES[currentSparklePreset]);

        // Blink status LED (1 to 4 blinks corresponding to preset)
        for (int k = 0; k <= currentSparklePreset; k++) {
            digitalWrite(STATUS_LED_PIN, LOW);
            delay(50);
            digitalWrite(STATUS_LED_PIN, HIGH);
            delay(50);
        }
    }
    b1PrevDown = b1Down;

    // 2. Button 2: Tap cycles Fairy Layout Mode, Hold (>1s) toggles Subpixel RGB Test
    bool b2Down = isButton2Down();
    if (b2Down && !b2PrevDown) {
        b2PressStartTime = now;
    }
    if (!b2Down && b2PrevDown && (now - lastB2PressTime > 300)) {
        lastB2PressTime = now;
        uint32_t holdDuration = now - b2PressStartTime;
        if (holdDuration >= 1000) {
            // Long Hold: Toggle Subpixel RGB Test
            isRgbInspectionMode = !isRgbInspectionMode;
            Serial.printf("[RGB INSPECTION] %s\n", isRgbInspectionMode ? "ACTIVE (Red->Green->Blue->White)" : "OFF (Warm White)");
        } else {
            // Short Tap: Cycle Fairy Layout Mode
            currentFairyLayout = (currentFairyLayout + 1) % 5;
            isRgbInspectionMode = false;
            Serial.printf("[FAIRY LAYOUT] %s\n", FAIRY_LAYOUT_NAMES[currentFairyLayout]);
            for (int k = 0; k <= currentFairyLayout; k++) {
                digitalWrite(STATUS_LED_PIN, LOW);
                delay(40);
                digitalWrite(STATUS_LED_PIN, HIGH);
                delay(40);
            }
        }
    }
    b2PrevDown = b2Down;

    // 3. Render Active Pattern
    if (isRgbInspectionMode) {
        renderSubpixelRgbTest(now);
    } else {
        renderWarmWhiteSparkles();
    }

    FastLED.show();
    delay(20); // ~50 FPS update rate matching parade firmware
}
