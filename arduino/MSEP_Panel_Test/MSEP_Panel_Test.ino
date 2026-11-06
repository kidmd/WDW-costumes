/**
 * 🏰 Main Street Electrical Parade (WDW 10K) - Universal Panel & Bench Test Firmware
 * Arduino IDE Sketch Version
 * 
 * Purpose:
 * Immediately sets all connected LEDs (up to 512 LEDs / full 16x16 matrices / 200-LED pebble strands)
 * into the authentic 3% Incandescent Warm White (~2500K vintage filament glow) with starlight sparkles
 * on boot — with ZERO button clicking, zero pairing, and zero graphic masking required!
 * 
 * Hardware Specs:
 * - Microcontroller: ESP32 DevKit (GPIO 16 Data Out, GPIO 4 Button 1, GPIO 33 Button 2, GPIO 0 BOOT)
 * - LED Standard: WS2812B / WS2811 (5V, 2.0A FastLED power limit enforced)
 * - Capacity: 512 LEDs (covers 256-LED 16x16 BTF matrix panels and 200-LED costume shirts)
 * - Default Mode: 2500K Warm White Base (~3.1% physical duty cycle) + 0.5% Starlight Sparkles (~3x pop)
 * 
 * Interactive Controls (Optional Bench Testing):
 * - BOOT (GPIO 0) / Button 1 (GPIO 4): Tap to toggle Color Order (GRB for 16x16 BTF matrix <-> RGB for pebble strings)
 * - Button 2 (GPIO 33): Tap to cycle (Warm White + Sparkle -> Solid Warm White -> RGB Subpixel Inspection)
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

#define SPARKLE_RATE        0.5     // 0.5% probability per LED per frame (calm, subtle starlight twinkle)

CRGB leds[NUM_LEDS];

// Operational Test Modes
enum PanelTestMode {
    TEST_MODE_WARM_WHITE_SPARKLE = 0, // Default: 3% Warm White + Starlight Sparkles
    TEST_MODE_WARM_WHITE_SOLID   = 1, // Solid Warm White (no sparkles, 100% steady for photo inspection)
    TEST_MODE_SUBPIXEL_RGB       = 2  // RGB Subpixel Cycle (Red -> Green -> Blue -> White check)
};

static PanelTestMode currentTestMode = TEST_MODE_WARM_WHITE_SPARKLE;
static bool isGrbOrder = true; // True = GRB (16x16 BTF matrix default), False = RGB (pebble strings)

// Button Debounce State
static uint32_t lastB1PressTime = 0;
static uint32_t lastB2PressTime = 0;
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
    Serial.println(" * Mode: 2500K Incandescent Warm White + 0.5% Starlight Sparkles");
    Serial.println(" * Target: GPIO 16 driving up to 512 LEDs (16x16 Panels & Strands)");
    Serial.println(" * FastLED Safety: 5V 2000mA Max Current Limit Active");
    Serial.println(" * Default Color Order: GRB (BTF-LIGHTING 16x16 Matrix Standard)");
    Serial.println("----------------------------------------------------------------");
    Serial.println(" Controls:");
    Serial.println("  - BOOT / Button 1 (GPIO 4/0): Toggle Color Order (GRB <-> RGB)");
    Serial.println("  - Button 2 (GPIO 33): Cycle (Sparkle -> Solid Warm -> RGB Test)");
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
    CRGB baseCol = CRGB(255, 185, 110);
    baseCol.nscale8_video(64);

    // Starlight sparkle color: pure bright starlight pop scaled by 192 (~3x pop over base)
    CRGB sparkleCol = CRGB(255, 255, 255);
    sparkleCol.nscale8_video(192);

    for (int i = 0; i < NUM_LEDS; i++) {
        if (random16(10000) < (uint16_t)(SPARKLE_RATE * 100)) {
            leds[i] = sparkleCol;
        } else {
            leds[i] = baseCol;
        }
    }
}

void renderSolidWarmWhite() {
    CRGB baseCol = CRGB(255, 185, 110);
    baseCol.nscale8_video(64);
    fill_solid(leds, NUM_LEDS, baseCol);
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

    // 1. Button 1 / BOOT button: Toggle Color Order (GRB <-> RGB)
    bool b1Down = isButton1Down();
    if (b1Down && !b1PrevDown && (now - lastB1PressTime > 300)) {
        lastB1PressTime = now;
        isGrbOrder = !isGrbOrder;
        Serial.printf("[COLOR ORDER] Toggled to: %s\n", isGrbOrder ? "GRB (16x16 Matrix)" : "RGB (Pebble String)");

        // 2 Quick blinks of onboard status LED to confirm toggle
        for (int k = 0; k < 2; k++) {
            digitalWrite(STATUS_LED_PIN, LOW);
            delay(60);
            digitalWrite(STATUS_LED_PIN, HIGH);
            delay(60);
        }
    }
    b1PrevDown = b1Down;

    // 2. Button 2: Cycle Test Mode
    bool b2Down = isButton2Down();
    if (b2Down && !b2PrevDown && (now - lastB2PressTime > 300)) {
        lastB2PressTime = now;
        currentTestMode = (PanelTestMode)(((int)currentTestMode + 1) % 3);
        const char* modeName = "Warm White + Sparkles";
        if (currentTestMode == TEST_MODE_WARM_WHITE_SOLID) modeName = "Solid Warm White (No Sparkles)";
        else if (currentTestMode == TEST_MODE_SUBPIXEL_RGB) modeName = "Subpixel RGB Inspection";
        Serial.printf("[TEST MODE] Switched to: %s\n", modeName);
    }
    b2PrevDown = b2Down;

    // 3. Render Active Pattern
    switch (currentTestMode) {
        case TEST_MODE_WARM_WHITE_SPARKLE:
            renderWarmWhiteSparkles();
            break;
        case TEST_MODE_WARM_WHITE_SOLID:
            renderSolidWarmWhite();
            break;
        case TEST_MODE_SUBPIXEL_RGB:
            renderSubpixelRgbTest(now);
            break;
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
