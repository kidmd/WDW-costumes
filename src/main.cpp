#include <Arduino.h>
#include <FastLED.h>
#include <WiFi.h>
#include <esp_wifi.h>

// ============================================================================
// HARDWARE CONFIGURATION
// ============================================================================
#define DATA_PIN    16          // ESP32 GPIO connected to LED Data wire (via 220-470 ohm resistor)
#define LED_TYPE    WS2812B     // Standard for seed/pebble pixel strings
#define COLOR_ORDER GRB         // Most WS2812B strings use GRB order
#define NUM_LEDS    50          // Adjust to match your test strand length

// Safety & Brightness Caps for Bench Testing
#define MAX_BRIGHTNESS 40       // 0-255 (~15% brightness - comfortable indoors, safe current)
#define MAX_POWER_MILLIAMPS 800 // FastLED hardware safety limiter (5V @ 800mA)

CRGB leds[NUM_LEDS];

// ============================================================================
// ANIMATION HELPERS (Main Street Electrical Parade Theme)
// ============================================================================

// Mode 1: Classic Golden Marquee Bulb Chase
// Simulates the classic incandescent chasing bulbs of the MSEP floats
void patternMarqueeChase() {
    static uint8_t offset = 0;
    
    for (int i = 0; i < NUM_LEDS; i++) {
        // Every 3rd bulb is lit, and the pattern steps along the wire
        if ((i + offset) % 3 == 0) {
            leds[i] = CRGB(255, 147, 41); // Warm incandescent amber/gold
        } else {
            leds[i] = CRGB::Black;
        }
    }
    FastLED.show();
    offset++;
    delay(120);
}

// Mode 2: Multi-Color Float Sparkle
// Classic parade palette: Gold, Emerald Green (Elliott), Cyan, Ruby Red, Warm White
void patternParadePalette() {
    static const CRGB paradeColors[] = {
        CRGB(255, 160, 20),  // Marquee Gold
        CRGB(0, 255, 50),    // Pete's Dragon Green
        CRGB(255, 30, 0),    // Casey Jr. Caboose Red
        CRGB(0, 180, 255),   // Cinderella Carriage Cyan
        CRGB(255, 230, 180)  // Warm White Incandescent
    };
    const uint8_t numColors = sizeof(paradeColors) / sizeof(paradeColors[0]);

    for (int i = 0; i < NUM_LEDS; i++) {
        leds[i] = paradeColors[(i + (millis() / 200)) % numColors];
    }
    FastLED.show();
    delay(50);
}

// Mode 3: Gentle Twinkle / Starlight
void patternTwinkle() {
    fadeToBlackBy(leds, NUM_LEDS, 20);
    if (random8() < 60) {
        int pos = random16(NUM_LEDS);
        leds[pos] = CRGB(255, 220, 150); // Warm starlight flash
    }
    FastLED.show();
    delay(30);
}

// ============================================================================
// SETUP & LOOP
// ============================================================================
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n========================================================");
    Serial.println("  MAIN STREET ELECTRICAL PARADE - LED BENCH TEST (NODE 1)");
    Serial.println("========================================================");

    // Initialize Wi-Fi in Station mode to retrieve the ESP32 MAC address
    // (This MAC address will be used to identify boards in ESP-NOW)
    WiFi.mode(WIFI_STA);
    Serial.print("[INFO] Board MAC Address: ");
    Serial.println(WiFi.macAddress());

    // Configure FastLED with conservative power management
    FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS)
           .setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(MAX_BRIGHTNESS);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_POWER_MILLIAMPS);

    Serial.printf("[INFO] LEDs Initialized: %d pixels on GPIO %d\n", NUM_LEDS, DATA_PIN);
    Serial.printf("[INFO] Power Limit: 5V @ %d mA | Max Brightness: %d/255\n", 
                  MAX_POWER_MILLIAMPS, MAX_BRIGHTNESS);
    Serial.println("[INFO] Starting Animation Loop...\n");
}

void loop() {
    // Cycle between MSEP animations every 10 seconds
    uint32_t currentSec = (millis() / 10000) % 3;

    switch (currentSec) {
        case 0:
            patternMarqueeChase();
            break;
        case 1:
            patternParadePalette();
            break;
        case 2:
            patternTwinkle();
            break;
    }
}
