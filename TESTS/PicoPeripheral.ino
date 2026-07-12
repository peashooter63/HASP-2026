#include <Wire.h>

constexpr uint8_t I2C_ADDR = 0x2C;
constexpr int POT_PIN = 1;


volatile uint8_t potByte = 0;

volatile uint8_t registerNumber = 0;

uint8_t readPotByte() {
  return 0x31;
}

void onI2CRequest() {
  //uint8_t value = potByte;
  //Wire.write(&value, 1);
  String sensorData = "";
  if (registerNumber == 1)
  {
    sensorData = "S1&T1:70&T2:90&T3:200&T4:300";
  }
  else if (registerNumber ==2)
  {
    sensorData = "S1&C1:170&C2:290&C3:200&C4:350";
  }
  else
  {
    sensorData = "S1&M1:7&M2:9&M3:20&M4:8";
  }
  //int bufferLength = sensorData.length() + 1;
  int bufferLength = sensorData.length();

  for (int i = 0; i < 32 - bufferLength; i++)
  {
    sensorData.concat(" ");
  }
  char charArray[32];
  sensorData.toCharArray(charArray, 32);
  Wire.write(charArray, 32);
}

void onI2CReceive(int numBytes) {
  while (Wire.available())
    //(void)Wire.read();
    registerNumber = Wire.read();
}

void setup() {
  Serial.begin(115200);

  Wire.begin(I2C_ADDR);
  Wire.onRequest(onI2CRequest);
  Wire.onReceive(onI2CReceive);

  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  potByte = readPotByte();
  
  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  delay(1000);                      // wait for a second
  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
  delay(1000);                      // wait for a second
}
