#include <Arduino.h>
#include <FastLED.h>
#include <WiFi.h>

// ============================================================================
// HARDWARE CONFIGURATION
// ============================================================================
#define DATA_PIN        16      // 8th pin on the right on your ESP-32D
#define LED_TYPE        WS2812B // Seed / Pebble pixels
#define COLOR_ORDER     GRB
#define NUM_LEDS        50      // Test strand count (change if you have more)
#define STATUS_LED_PIN  2       // Onboard blue heartbeat LED

// Safety & Brightness Caps for USB Power
#define MAX_BRIGHTNESS  45      // Warm, distinct incandescent look without blinding
#define MAX_MILLIAMPS   800     // 5V FastLED current limiter

CRGB leds[NUM_LEDS];

// ============================================================================
// MAIN STREET ELECTRICAL PARADE ANIMATIONS
// ============================================================================

// 1. Classic Golden Marquee Chasing Bulbs
// Simulates the vintage incandescent chase around the float frames
void patternMarqueeChase() {
    static uint8_t offset = 0;
    for (int i = 0; i < NUM_LEDS; i++) {
        if ((i + offset) % 3 == 0) {
            leds[i] = CRGB(255, 147, 41); // Warm incandescent amber/gold
        } else {
            leds[i] = CRGB::Black;
        }
    }
    FastLED.show();
    offset++;
    delay(110);
}

// 2. Parade Multi-Color Float Sparkle
// Elliott Green, Casey Jr. Red, Cinderella Cyan, Marquee Gold, Warm White
void patternParadePalette() {
    static const CRGB paradeColors[] = {
        CRGB(255, 160, 20),  // Marquee Gold
        CRGB(0, 255, 50),    // Pete's Dragon (Elliott) Green
        CRGB(255, 25, 0),    // Casey Jr. Caboose Red
        CRGB(0, 190, 255),   // Cinderella Carriage Cyan
        CRGB(255, 230, 180)  // Incandescent Warm White
    };
    const uint8_t numColors = sizeof(paradeColors) / sizeof(paradeColors[0]);

    for (int i = 0; i < NUM_LEDS; i++) {
        leds[i] = paradeColors[(i + (millis() / 200)) % numColors];
    }
    FastLED.show();
    delay(50);
}

// 3. Starlight / Fairy Dust Twinkle
// Cinderella fairy dust and clock tower shimmer
void patternTwinkle() {
    fadeToBlackBy(leds, NUM_LEDS, 25);
    if (random8() < 70) {
        int pos = random16(NUM_LEDS);
        leds[pos] = CRGB(255, 220, 160); // Warm sparkle
    }
    FastLED.show();
    delay(30);
}

// 4. Traveling Float Wave (Preview of ESP-NOW sync pulse)
// A wave of brilliant light that sweeps down the float
void patternTravelingPulse() {
    static int head = 0;
    static int direction = 1;

    fadeToBlackBy(leds, NUM_LEDS, 40);
    leds[head] = CRGB(255, 200, 100);
    if (head > 0) leds[head - 1] = CRGB(200, 100, 20);
    if (head < NUM_LEDS - 1) leds[head + 1] = CRGB(200, 100, 20);

    FastLED.show();
    head += direction;
    if (head >= NUM_LEDS - 1 || head <= 0) {
        direction = -direction;
    }
    delay(40);
}

// ============================================================================
// SETUP & LOOP
// ============================================================================
void setup() {
    Serial.begin(115200);
    pinMode(STATUS_LED_PIN, OUTPUT);
    delay(500);

    Serial.println("\n========================================================");
    Serial.println("  MAIN STREET ELECTRICAL PARADE - FULL ANIMATION SUITE");
    Serial.println("========================================================");

    WiFi.mode(WIFI_STA);
    Serial.print("[INFO] Board MAC Address: ");
    Serial.println(WiFi.macAddress());

    FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS)
           .setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(MAX_BRIGHTNESS);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_MILLIAMPS);

    Serial.printf("[INFO] LEDs Initialized on GPIO %d (8th pin on the right)\n", DATA_PIN);
    Serial.println("[INFO] Cycling through 4 MSEP animations every 10 seconds...\n");
}

void loop() {
    // Heartbeat blink on the onboard blue LED
    digitalWrite(STATUS_LED_PIN, (millis() / 500) % 2);

    // Cycle through 4 parade modes (10 seconds each)
    uint32_t mode = (millis() / 10000) % 4;

    switch (mode) {
        case 0:
            patternMarqueeChase();
            break;
        case 1:
            patternParadePalette();
            break;
        case 2:
            patternTwinkle();
            break;
        case 3:
            patternTravelingPulse();
            break;
    }
}
