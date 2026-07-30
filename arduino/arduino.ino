// Array of 40 pins to monitor (e.g., for Arduino Mega)
const int PINS[40] = {
  3, 5, 7, 9, 11, 43, 15, 17, 19, 21,
  23, 25, 27, 29, 31, 30, 28, 26, 24, 22,
  46, 44, 42, 40, 38, 36, 34, 32, 33, 35,
  20, 18, 16, 14, 12, 10, 8, 6, 4, 2
};
/*
    R1 : S-3 , G-5
    R2 : S-7 , G-9
    R3 : S-11, G-13
    R4 : S-15, G-17
    R5 : S-19, G-21
    R6 : S-23, G-25
    R7 : S-27, G-29
    R8 : S-31, G-30
    R9 : S-28, G-26
    R10: S-24, G-22
    R11: S-46, G-44
    R12: S-42, G-40
    R13: S-38, G-36
    R14: S-34, G-32
    R15: S-33, G-35
    R16: S-20, G-18
    R17: S-16, G-14
    R18: S-12, G-10
    R19: S-8 , G-6
    R20: S-4 , G-2
*/

const int NUM_PINS = 40;
uint8_t pinData[7];  // 5 bytes * 8 bits = 40 pins
unsigned long stt_time = 0;
unsigned long time;
const unsigned long WAIT_TIME = 100;  // Wait time between readings, in milliseconds
int idx_min = 0;
int idx_max = NUM_PINS;

void setup() {
  Serial.begin(115200);  // 115200 baud is much faster than 9600
  for (int i = 0; i < NUM_PINS; i++) {
    pinMode(PINS[i], INPUT_PULLUP);
  }
}

void loop() {
  time = millis();
  if (time >= stt_time + WAIT_TIME) {
    stt_time = stt_time + WAIT_TIME;  // Adds 100ms to the start_time
    // Clear buffer
    pinData[0] = 0xAA;  // Header

    for (int i = 1; i <= 5; i++) {
      pinData[i] = 0;
    }

    //for (int i = 0; i < NUM_PINS; i++) {
    for (int i = idx_min; i < idx_max; i++) {
      // LOW means pin is active/pressed (True)
      if (digitalRead(PINS[i]) == LOW) {
        int byteIdx = i / 8;
        int bitIdx = i % 8;
        pinData[1 + byteIdx] |= (1 << bitIdx);  // Set bit to 1
        // Serial.println(String(i/2+1)+"/"+String(i%2) + " - " + String(PINS[i]) + ": low");
      } else {
        // Serial.println(String(i/2+1)+"/"+String(i%2) + " - " + String(PINS[i]) + ": high");
      }
    }

    // Calculate XOR checksum over the payload bytes
    uint8_t checksum = 0;
    for (int i = 0; i <= 5; i++) {
      checksum ^= pinData[i];
    }
    pinData[6] = checksum;  // Trailer

    Serial.write(pinData, 7);
  }
}