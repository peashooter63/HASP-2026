
#include <Wire.h>
#include <cmath>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <string.h>
#include <cstring>``````````````````````````


#define LED_BUILTIN 25
#define SEALEVELPRESSURE_HPA (1013.25)

const byte addr1 = 0x66;
//const byte addr2 = 0x70;
  // Pico ID 
int8_t tempID = 0X08;

// Global char buffer
uint8_t buffer[32];

volatile uint8_t registerValue = 1; // modified in onReceive event

 
struct __attribute__((packed)) sensorData {
  // Size of struct is 8 bytes (without) padding
  int16_t temperature; // 2 bytes
  int16_t humidity;   // 2 bytes
  int32_t pressure;   // 4 bytes
  //int16_t altitude;   // 2 bytes
  //uint32_t myTime;    // 4 bytes. Not unsigned long.

  
};

sensorData data;

// BME280 object
Adafruit_BME280 bme;



void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  bme.begin(0x77);
 
  Wire1.setSDA(2);
  Wire1.setSCL(3);
  Wire1.begin(addr1);
  //Wire1.begin(addr2);
   
   // Pi talking to specific registers
  Wire1.onReceive(I2C_RECEIVE);
  // Slave responding to master with data
  Wire1.onRequest(I2C_REQUEST);


}

void loop() {

  // Build packet again because sensor data updates per run
  buildPacket();

  // Turn LED on and off & show pico power on
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);

}

// Build Packet Function
void buildPacket() {

  // Check packet size just for my testing :-)
  Serial.println(sizeof(sensorData));
  // Read sensor values
  float temp = bme.readTemperature();
  float hum  = bme.readHumidity();
  float pres = bme.readPressure();
  // float alt = bme.readAltitude(SEALEVELPRESSURE_HPA);

  // Convert to an integer each time built
  data.temperature = (int16_t)std::round(temp * 100.0f);
  data.humidity    = (int16_t)std::round(hum * 100.0f);
  data.pressure    = (int32_t)std::round(pres * 100.0f);

  // Copy struct data to buffer for transmission 
  memcpy(buffer,&data, sizeof(sensorData));      // Later fix, not very good practice.
  
  
  // Will integrate little endian protocol to simplify endianess unpacking on Pi (Swap from copying raw struct to buffer)
  // Manually serialize & shift 
  // Write into buffer and pi unpack little endian 

}


// I2C Request Handler
void I2C_REQUEST() {
// Send data back to pi requests 
// Acts as an handler on the slave to respond to calls from the master.
Serial.println("Sending sensor data back...");

  if ( registerValue == 1) {
    //Wire1.write(tempID, 1); 
    Wire1.write(buffer, 8);   //Adjust this value for testing for buffer


  Serial.println("Sent packet to Pi");  // Will remove this later. Prints should never be in handlers.
  }
}

// I2C Receive Handler 
void I2C_RECEIVE(int bytesReceived) {
  // Master requests data from a specific register
  // Handler allows the volatile register var to change 
  while (Wire1.available()) {
    registerValue = Wire1.read();
    Serial.print("Master requested data from the register: ");
    Serial.println(registerValue);
  }
}
