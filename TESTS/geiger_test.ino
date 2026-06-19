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

int count = 0;

// Global char buffer
//uint8_t bufferCount[1];
//uint32_t bufferTime[4];

const uint8_t i2cAddr2 = 0x70;
volatile int geigerCount = 1;        // modified in each ISR
volatile uint8_t registerNumber = 0; // modified in onReceive event
int copyCount = 0;
volatile unsigned long geigerTime;
volatile bool countFlag = false;
volatile bool timeFlag = false;

// Define Queues  
ArduinoQueue<int> countQueue1(100);
ArduinoQueue<unsigned long> timeQueue1(100);

ArduinoQueue<int> countQueue2(100);
ArduinoQueue<unsigned long> timeQueue2(100);


void setup() {

  // Testing whether queue full:
  //unsigned int n = countQueue1.itemCount();    // Returns the number of items currently on the queue
  //unsigned int n = timeQueue1.itemSize();    // Returns the size of the item being stored (bytes)

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
  // FOUND OUT ITS NOT ENQUEUEING. 


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
  //geigerCount = 1;
  geigerTime = millis();

  // Test if ISR ran:
  Serial.println("Geiger1 ISR running.");

  // Check if Queues is not full 

  if (!countQueue1.isFull()) {
    countQueue1.enqueue(geigerCount);
    Serial.println(geigerCount);
     Serial.println("Enqueueing geiger Data");
      
  }
  else { 
    Serial.println("Not Enqueueing Geiger1 Data");
    // Set a Flag 
  }

 if (!timeQueue1.isFull() ) {       // Will fix this
  timeQueue1.enqueue(geigerTime);
  Serial.println("Enqueueing Time1 Data");
  
  }
  else {
    Serial.println("Not Enqueueing Time1 Data");
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
    Serial.println("Not Enqueueing Geiger2 Data");
  }
}

void I2CRequest() {

    // Disable Interrupts
    

  if (registerNumber == 2) {

    // Pi asks for how many itemsin the queue: 
    // Checking Item Amount in Queues   (TEST)
      unsigned long timeCountNum = timeQueue1.item_count();
      unsigned int queueCountNum = countQueue1.itemCount();
      Serial.println("Count Queue Items:");
      Serial.println(queueCountNum);
      Serial.println("Count Time Items:");
      Serial.println(queueCountNum);

    // State the amount of counts to Pi
      Wire1.write((uint8_t*)(&queueCountNum),4);
  }

    
  else if (registerNumber == 3) {
      
    // Send all counts to pi

    if (!countQueue1.isEmpty()) {
        int count = countQueue1.dequeue();
        Wire1.write((uint8_t*)(&count),4);   ///4 bytes per int
               
      }
    else {
      Serial.println("Count Queue full");
      uint32_t zero = 0;
      Wire1.write((uint8_t*)(&zero), 4);         // Note: This line was added to stop crashing when master does not get an ACK byte from slave. 
      }
    }
    
      /* Checking Item Anount in Queues if working (TEST)
      unsigned long timeCountNum = timeQueue1.item_count();
      unsigned int queueCountNum = countQueue1.itemCount();
      Serial.println("Count Queue Items:");
      Serial.println(queueCountNum);
      Serial.println("Count Time Items:");
      Serial.println(timeCountNum);*/

     // Enable interrupts
    

}

void onReceive(int numBytes) {
  while (Wire1.available()) {
    registerNumber = Wire1.read();
    // Pi Continues to request for data until pico sends empty flag 
  }
}
