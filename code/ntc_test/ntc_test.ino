#include <Arduino.h>

// Each divider: 3.3V -> NTC -> GPIO junction -> fixed resistor -> GND.
// Heating the NTC increases the measured voltage.
constexpr uint8_t NTC_PINS[] = {2, 3, 4, 5, 6};
constexpr size_t NTC_COUNT = sizeof(NTC_PINS) / sizeof(NTC_PINS[0]);
constexpr int SAMPLES = 16;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);

  for (size_t i = 0; i < NTC_COUNT; ++i) {
    pinMode(NTC_PINS[i], INPUT);
    analogSetPinAttenuation(NTC_PINS[i], ADC_11db);
  }

  delay(500);
  Serial.println("Five NTC test: GPIO2-6");
}

void loop() {
  uint32_t sums[NTC_COUNT] = {};

  for (int sample = 0; sample < SAMPLES; ++sample) {
    for (size_t i = 0; i < NTC_COUNT; ++i) {
      sums[i] += analogReadMilliVolts(NTC_PINS[i]);
    }
    delay(2);
  }

  for (size_t i = 0; i < NTC_COUNT; ++i) {
    if (i > 0) {
      Serial.print(" | ");
    }
    Serial.printf(
      "NTC%u GPIO%u: %lu mV",
      static_cast<unsigned>(i + 1),
      static_cast<unsigned>(NTC_PINS[i]),
      static_cast<unsigned long>(sums[i] / SAMPLES)
    );
  }

  Serial.println();
  delay(1000);
}
