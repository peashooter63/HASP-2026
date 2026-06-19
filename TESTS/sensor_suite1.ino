// Gennifer Chiu & Karenna Chiu
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#define LED_BUILTIN 25
#define SEALEVELPRESSURE_HPA (1013.25)

const byte addr1 = 0x66;

byte sendData = 2;
int data_send = 4;

//bme280 start
/*Adafruit_BME280 bme; // Pico default gpio pins SDA (GP4) and SCL (GP5)
float temp = bme.readTemperature();
int pressure = bme.readPressure() / 100.0F;
float altitude = bme.readAltitude(SEALEVELPRESSURE_HPA);
float humidity = bme.readHumidity(); */

void setup() {

// initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(115200);

  Wire1.setSDA(2);
  Wire1.setSCL(3);
  //Wire1.begin(addr1);
  Wire1.begin(addr2);
// Slave receiving data from master
  Wire1.onReceive(I2C_RECEIVE);
  Wire1.onRequest(I2C_REQUEST);

  //bme.begin(0x77);
  //Serial.println("BME280 is online!");

//look for bme280



}

void loop() {
// Have slave device keep listening
Wire1.onReceive(I2C_RECEIVE);
Wire1.onRequest(I2C_REQUEST);
// LED on and off
digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
delay(1000);                       // wait for a second
digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
delay(1000);

/*Serial.print("Temperature = ");
Serial.print(bme.readTemperature());
Serial.println(" °C");

Serial.print("Pressure = ");

Serial.print(bme.readPressure() / 100.0F);
Serial.println(" hPa");

Serial.print("Approx. Altitude = ");
Serial.print(bme.readAltitude(SEALEVELPRESSURE_HPA));
Serial.println(" m");

Serial.print("Humidity = ");
Serial.print(bme.readHumidity());
Serial.println(" %");

Serial.println();
*/

} 


void I2C_RECEIVE(int bytesReceived) {

while (Wire1.available()) {
  int i = Wire1.read();  // Receiving an integer byte
  Serial.println("Received byte from master:");
  Serial.println(i);
}

}

void I2C_REQUEST() {
// SEND DATA BACK TO CONTROLLER
  Serial.println("Sending data to master...");
  Wire1.write(data_send);
  //Wire1.write(temp);
  //Wire1.write(pressure);
  //Wire1.write(altitude);
  //Wire1.write(humidity);

}