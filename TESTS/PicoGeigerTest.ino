#include <Wire.h>
#include <ArduinoQueue.h> 
#include <string.h>

// Com 4 (bme pico) Com 5 (geiger pico)

#define GEIGER_1_INTERRUPT_PIN 26
//#define GEIGER_2_INTERRUPT_PIN NUMBER
//#define GEIGER_3_INTERRUPT_PIN NUMBER
//#define GEIGER_4_INTERRUPT_PIN NUMBER
//#define GEIGER_5_INTERRUPT_PIN NUMBER

// Size
int countSize = 200;
int timeSize = 200;

// Global char buffer
uint8_t bufferCount[1];
uint32_t bufferTime[4];

const uint8_t i2cAddr2 = 0x70;
volatile int geigerCount = 0;        // modified in each ISR
volatile uint8_t registerNumber = 0; // modified in onReceive event
int copyCount = 0;
volatile unsigned long geigerTime;

// Define Queues  
ArduinoQueue<int> countQueue1(countSize);
ArduinoQueue<unsigned long> timeQueue1(timeSize);

ArduinoQueue<int> countQueue2(countSize);
ArduinoQueue<unsigned long> timeQueue2(timeSize);


void setup() {

  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);

  // Enable interrupts and associate a GPIO pin with a ISR
  pinMode(GEIGER_1_INTERRUPT_PIN, INPUT_PULLUP);
  //pinMode(GEIGER_2_INTERRUPT_PIN, INPUT_PULLUP);
  //pinMode(GEIGER_3_INTERRUPT_PIN, INPUT_PULLUP);
  //pinMode(GEIGER_4_INTERRUPT_PIN, INPUT_PULLUP);
  //pinMode(GEIGER_5_INTERRUPT_PIN, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(GEIGER_1_INTERRUPT_PIN),ISR_geiger1, FALLING);
  //attachInterrupt(digitalPinToInterrupt(GEIGER_2_INTERRUPT_PIN),ISR_geiger2, FALLING);
  //attachInterrupt(digitalPinToInterrupt(GEIGER_3_INTERRUPT_PIN),ISR_geiger3, FALLING);
  //attachInterrupt(digitalPinToInterrupt(GEIGER_4_INTERRUPT_PIN),ISR_geiger4, FALLING);
  //attachInterrupt(digitalPinToInterrupt(GEIGER_5_INTERRUPT_PIN),ISR_geiger5, FALLING);


  Wire1.setSDA(2);
  Wire1.setSCL(3);
  //Wire1.begin(i2cAddr1);
  Wire1.begin(i2cAddr2);

  Wire1.onReceive(onReceive);
  Wire1.onRequest(I2CRequest);
}

void loop() {

  // Turn LED on and off 
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}


void ISR_geiger1() {
  // Hardware disables interrupt per event
  geigerCount=1;
  geigerTime = millis();

  // Check if Queues is not full 

  if (!countQueue1.isFull()) {
    countQueue1.enqueue(geigerCount);
  }
  else { 
    // Set a Flag 
  }

 if (!timeQueue1.isFull() ) {       // Will fix this
  timeQueue1.enqueue(geigerTime);
  }
  else {
    // Set a flag
  }
}

void ISR_geiger2() {
  // Hardware disables interrupt per event
  geigerCount = 1;
  geigerTime = millis();
  
  // Check if Queue is not full 
  if (!countQueue2.isFull()) {
    countQueue2.enqueue(geigerCount);
  }
  else {
    // Set an overflow Flag 
  }
}

void I2CRequest() {

    // Disable Interrupts
    noInterrupts();

  if (registerNumber == 2) {

    // Clear Counts
    geigerCount = 0;

    if (!countQueue1.isEmpty()) {
      int count = countQueue1.dequeue();
      //uint8_t bufferCount[1]; 
      memcpy(bufferCount,&count,1);
      Wire1.write(bufferCount,1);
    }
    else {
      Wire1.write(0XEE);
    }
  }
    
    if (registerNumber == 3) {
      
      if (!timeQueue1.isEmpty()) {
        unsigned long time = timeQueue1.dequeue();  // may memcpy instead? 
        Wire1.write((uint8_t*)(&time),4);           // 4 byte per unsigned
      }
      else {
        Wire1.write(0XEE);
      }
    }
    
      // Checking Item Anount in Queues if working (TEST)
      unsigned long timeCountNum = timeQueue1.item_count();
      unsigned int queueCountNum = countQueue1.itemCount();
      Serial.println("Count Queue Items:");
      Serial.println(queueCountNum);
      Serial.println("Count Time Items:");
      Serial.println(timeCountNum);

     // Enable interrupts
    interrupts();
}

void onReceive(int numBytes) {
  while (Wire1.available()) {
    registerNumber = Wire1.read();
    // Pi Continues to request for data until pico sends empty flag 
  }
}