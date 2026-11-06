/**
 * 🏰 Main Street Electrical Parade (WDW 10K) - Universal Panel & Bench Test Firmware
 * Arduino IDE Sketch Version
 * 
 * Purpose:
 * Immediately sets all connected LEDs (up to 512 LEDs / full 16x16 matrices / 200-LED pebble strands)
 * into the authentic 3% Incandescent Warm White (~2500K vintage filament glow) with calm starlight sparkles
 * on boot — with ZERO button clicking, zero pairing, and zero graphic masking required!
 * 
 * Hardware Specs:
 * - Microcontroller: ESP32 DevKit (GPIO 16 Data Out, GPIO 4 Button 1, GPIO 33 Button 2, GPIO 0 BOOT)
 * - LED Standard: WS2812B / WS2811 (5V, 2.0A FastLED power limit enforced)
 * - Capacity: 512 LEDs (covers 256-LED 16x16 BTF matrix panels and 200-LED costume shirts)
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

#define NUM_LEDS            512     // Full buffer driving any panel up to 512 LEDs (16x16 = 256, dual = 512)
#define LED_TYPE            WS2812B // Standard 5V addressable LED protocol
#define MAX_BRIGHTNESS      60      // Bench-safe brightness matching MSEP costume baseline
#define MAX_POWER_MILLIAMPS 2000    // 5V, 2.0A safety limit for USB power banks and bench supplies

CRGB leds[NUM_LEDS];
static uint8_t sparkleLevel[NUM_LEDS] = {0}; // Per-LED sparkle intensity (0 = base, 255 = peak sparkle)

// Sparkle Rate Presets (calibrated for 256-LED 16x16 panels & 50 FPS)
// With 200ms smooth bloom & decay, lower thresholds yield calm, authentic starlight rather than rapid strobes
static const uint16_t SPARKLE_THRESHOLDS[4] = { 5, 2, 15, 0 }; // 0.05% (Calm), 0.02% (Ultra-Subtle), 0.15% (Parade), 0.0% (Solid)
static const char* SPARKLE_NAMES[4] = {
    "1: Calm Starlight (0.05% / ~4-6 twinkles/sec, soft 200ms fade)",
    "2: Ultra-Subtle (0.02% / ~1-2 twinkles/sec, gentle starlight)",
    "3: Parade Sparkle (0.15% / ~12-15 twinkles/sec)",
    "4: Solid Warm White (0% sparkles / Steady Photo Mode)"
};
static uint8_t currentSparklePreset = 0; // Starts at Preset 0: Calm Starlight

static bool isGrbOrder = true;          // True = GRB (16x16 BTF matrix default), False = RGB (pebble strings)
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
    Serial.println(" * Target: GPIO 16 driving up to 512 LEDs (16x16 Panels & Strands)");
    Serial.println(" * FastLED Safety: 5V 2000mA Max Current Limit Active");
    Serial.println(" * Default Color Order: GRB (BTF-LIGHTING 16x16 Matrix Standard)");
    Serial.println("----------------------------------------------------------------");
    Serial.println(" Controls:");
    Serial.println("  - BOOT / Button 1 (GPIO 4/0): Tap to cycle Sparkle Rate (Calm -> Subtle -> Parade -> Solid)");
    Serial.println("  - Button 2 (GPIO 33): Tap to toggle Color Order (GRB <-> RGB)");
    Serial.println("  - Button 2 (GPIO 33): Hold (>1s) for Subpixel RGB Inspection Cycle");
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

    uint16_t threshold = SPARKLE_THRESHOLDS[currentSparklePreset];

    for (int i = 0; i < NUM_LEDS; i++) {
        // 1. Decay active sparkle smoothly over ~200ms (10 frames at 20ms per frame)
        if (sparkleLevel[i] > 0) {
            sparkleLevel[i] = qsub8(sparkleLevel[i], 24);
        }

        // 2. Trigger new sparkle at calm rate
        if (threshold > 0 && random16(10000) < threshold) {
            sparkleLevel[i] = 255;
        }

        // 3. Smooth linear interpolation between warm base and starlight white
        if (sparkleLevel[i] == 0) {
            leds[i] = baseCol;
        } else {
            uint8_t sp = sparkleLevel[i];
            leds[i] = CRGB(
                lerp8by8(baseCol.r, sparklePeak.r, sp),
                lerp8by8(baseCol.g, sparklePeak.g, sp),
                lerp8by8(baseCol.b, sparklePeak.b, sp)
            );
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
    fill_solid(leds, NUM_LEDS, testCol);
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

    // 2. Button 2: Tap toggles Color Order (GRB <-> RGB), Hold (>1s) toggles Subpixel RGB Test
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
            // Short Tap: Toggle Color Order
            isGrbOrder = !isGrbOrder;
            Serial.printf("[COLOR ORDER] Toggled to: %s\n", isGrbOrder ? "GRB (16x16 Matrix)" : "RGB (Pebble String)");
            for (int k = 0; k < 2; k++) {
                digitalWrite(STATUS_LED_PIN, LOW);
                delay(60);
                digitalWrite(STATUS_LED_PIN, HIGH);
                delay(60);
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

    // 4. Dynamic Color Order Correction if RGB mode selected
    if (!isGrbOrder) {
        // Swap Red and Green bytes dynamically for RGB seed pebble strands
        for (int i = 0; i < NUM_LEDS; i++) {
            uint8_t tempR = leds[i].r;
            leds[i].r = leds[i].g;
            leds[i].g = tempR;
        }
    }

    FastLED.show();
    delay(20); // ~50 FPS update rate matching parade firmware
}
