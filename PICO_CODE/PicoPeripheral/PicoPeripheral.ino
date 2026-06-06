#include <Wire.h>
#include <ArduinoQueue.h>
#include "Geiger.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_LSM6DSOX.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <cfloat>

constexpr uint8_t I2C_ADDR = 0x2C;

//#define DEBUG_MODE    // Comment this line out for production code, uncomment it for testing

#define LED_PIN 22
#define GEIGER_1_INTERRUPT_PIN 21
#define GEIGER_2_INTERRUPT_PIN 20
#define GEIGER_QUEUE_SIZE 100
#define WIRE1_SDA_PIN 2
#define WIRE1_SCL_PIN 3

#define GEIGER_1_COUNT_REGISTER 1
#define GEIGER_1_DATA_REGISTER  2

#define GEIGER_2_COUNT_REGISTER 3
#define GEIGER_2_DATA_REGISTER  4

#define BME_280_DATA 5
#define RMU_DATA     6
#define DS18_TEMPERATURE_DATA 7

#define ONE_WIRE_BUS 15

volatile uint8_t registerNumber = 0;

Geiger geiger_1(GEIGER_1_INTERRUPT_PIN, GEIGER_QUEUE_SIZE);
Geiger geiger_2(GEIGER_2_INTERRUPT_PIN, GEIGER_QUEUE_SIZE);

typedef struct __attribute__((packed)) {
  float temperature;    // 4 bytes
  float humidity;       // 4 bytes
  float pressure;       // 4 bytes
  float altitude;       // 4 bytes
  unsigned long time;   // 4 bytes
} sensorData;

typedef struct __attribute__((packed)) {
    float temperatue;       // 4 bytes
    float acceleration_x;   // 4 bytes
    float acceleration_y;   // 4 bytes
    float acceleration_z;   // 4 bytes
    float rotation_x;       // 4 bytes
    float rotation_y;       // 4 bytes
    float rotation_z;       // 4 bytes
    unsigned long time;     // 4 bytes
} rmuData;

typedef struct __attribute__((packed)) {
    float temperature1;   // 4 bytes
    float temperature2;   // 4 bytes
    float temperature3;   // 4 bytes
    float temperature4;   // 4 bytes
    float temperature5;   // 4 bytes
    float temperature6;   // 4 bytes
    float temperature7;   // 4 bytes
    unsigned long time;   // 4 bytes
} ds18Data;

Adafruit_BME280 bme;
Adafruit_LSM6DSOX sox;

sensorData data;
rmuData rmu;
ds18Data ds18;

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void handleInterrupt() {
  unsigned long m;
  m = millis();

  if (!(sio_hw->gpio_in & (1 << GEIGER_1_INTERRUPT_PIN)))   // If the pin is low, we have an interrupt on that pin
  {
    if (geiger_1.enqueueItem(m) == false)
    {
      Serial.println("Guiger 1 Queue is full.");
    }
  }

  if (!(sio_hw->gpio_in & (1 << GEIGER_2_INTERRUPT_PIN)))   // If the pin is low, we have an interrupt on that pin
  {
    if (geiger_2.enqueueItem(m) == false)
    {
      Serial.println("Guiger 2 Queue is full.");
    }
  }
}

void onI2CRequest() {
  switch (registerNumber)
  {
    case GEIGER_1_COUNT_REGISTER:
      {
        unsigned short s = geiger_1.getQueueCount();
        byte byteArray[sizeof(unsigned short)];
        memcpy(byteArray, &s, sizeof(unsigned short));
        Wire.write(byteArray, 2);
      }
      break;

    case GEIGER_1_DATA_REGISTER:
      {
        unsigned long l = geiger_1.dequeueItem();
        byte byteArray[sizeof(unsigned long)];
        memcpy(byteArray, &l, sizeof(unsigned long));
        Wire.write(byteArray, 4);
      }
      break;

    case GEIGER_2_COUNT_REGISTER:
      {
        unsigned short s = geiger_2.getQueueCount();
        byte byteArray[sizeof(unsigned short)];
        memcpy(byteArray, &s, sizeof(unsigned short));
        Wire.write(byteArray, 2);
      }
      break;

    case GEIGER_2_DATA_REGISTER:
      {
        unsigned long l = geiger_2.dequeueItem();
        byte byteArray[sizeof(unsigned long)];
        memcpy(byteArray, &l, sizeof(unsigned long));
        Wire.write(byteArray, 4);
      }
      break;

    case BME_280_DATA:
      {
        data.temperature = bme.readTemperature();           // Celsius
        data.humidity = bme.readHumidity();                 // %RH
        data.pressure = bme.readPressure();                 // mbar
        float seaLevelPressure = 1013.25;
        data.altitude = bme.readAltitude(seaLevelPressure); // meters
        data.time = millis();
        char buffer[sizeof(sensorData)];
        memcpy(buffer, &data, sizeof(data));
        //sprintf(buffer, "%4d,%6d,%5d,%3d,%10d", (int)temp, (int)press, (int)alt, (int)hum, millis());
        //Wire.write(buffer, 32);
        Wire.write(buffer, 20);
      }
      break;

    case RMU_DATA:
      {
        sensors_event_t accel;
        sensors_event_t gyro;
        sensors_event_t temp;
        sox.getEvent(&accel, &gyro, &temp);
        rmu.temperatue = temp.temperature;            // temperature deg C
        rmu.acceleration_x = accel.acceleration.x;    // acceleration m/s^2
        rmu.acceleration_y = accel.acceleration.y;    // acceleration m/s^2
        rmu.acceleration_z = accel.acceleration.z;    // acceleration m/s^2
        rmu.rotation_x = gyro.gyro.x;                 // rotation rad/s
        rmu.rotation_y = gyro.gyro.y;                 // rotation rad/s
        rmu.rotation_z = gyro.gyro.z;                 // rotation rad/s
        rmu.time = millis();
        char buffer[sizeof(rmuData)];
        memcpy(buffer, &rmu, sizeof(rmu));
        Wire.write(buffer, 32);
      }
      break;

    case DS18_TEMPERATURE_DATA:
      {
        char buffer[sizeof(ds18Data)];
        memcpy(buffer, &ds18, sizeof(ds18));
        Wire.write(buffer, 32);
      }
      break;
  }
}

void onI2CReceive(int numBytes) {
  while (Wire.available())
    registerNumber = Wire.read();
}

void setup() {
  Serial.begin(115200);

  Wire.begin(I2C_ADDR);
  Wire.onRequest(onI2CRequest);
  Wire.onReceive(onI2CReceive);

  Wire1.setSDA(WIRE1_SDA_PIN);
  Wire1.setSCL(WIRE1_SCL_PIN);
  Wire1.begin();

  bme.begin(0x77, &Wire1);
  sox.begin_I2C(0x6A, &Wire1);

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  pinMode(GEIGER_1_INTERRUPT_PIN, INPUT_PULLUP);
  pinMode(GEIGER_2_INTERRUPT_PIN, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(GEIGER_1_INTERRUPT_PIN), handleInterrupt, FALLING);
  attachInterrupt(digitalPinToInterrupt(GEIGER_2_INTERRUPT_PIN), handleInterrupt, FALLING);

  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW

  digitalWrite(LED_PIN, LOW);
  
  sox_settings();

  sensors.begin();
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  delay(500);                      // wait for a second
  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
  delay(500);                      // wait for a second

  if ((geiger_1.getQueueCount() > 0) || (geiger_2.dequeueItem() > 0))
  {
    digitalWrite(LED_PIN, HIGH);
  }
  else
  {
    digitalWrite(LED_PIN, LOW);
  }

  //noInterrupts();

  ds18.temperature1 = DEVICE_DISCONNECTED_C;
  ds18.temperature2 = DEVICE_DISCONNECTED_C;
  ds18.temperature3 = DEVICE_DISCONNECTED_C;
  ds18.temperature4 = DEVICE_DISCONNECTED_C;
  ds18.temperature5 = DEVICE_DISCONNECTED_C;
  ds18.temperature6 = DEVICE_DISCONNECTED_C;
  ds18.temperature7 = DEVICE_DISCONNECTED_C;
  ds18.time = millis();

  int n = sensors.getDS18Count();
  Serial.println(n);

  sensors.requestTemperatures();

  for (int i=0; i<n; i++)
  {
    float tempC = sensors.getTempCByIndex(i);
    Serial.println(tempC);
    if(tempC != DEVICE_DISCONNECTED_C)
    {
      switch (i)
      {
        case 0:
          ds18.temperature1 = tempC;
          break;

        case 1:
          ds18.temperature2 = tempC;
          break;
               
        case 2:
          ds18.temperature3 = tempC;
          break;
              
        case 3:
          ds18.temperature4 = tempC;
          break;
            
        case 4:
          ds18.temperature5 = tempC;
          break;
             
        case 5:
          ds18.temperature6 = tempC;
          break;
           
        case 6:
          ds18.temperature7 = tempC;
          break;
      }
    }
  }

  //interrupts();

#ifdef DEBUG_MODE
  int n1 = geiger_1.getQueueCount();
  if (n1 != 0)
  {
    Serial.println("Geiger 1 Queue Data: ");

    for (int i=0; i<n1; i++)
    {
      unsigned long l = geiger_1.dequeueItem();
      Serial.println(l);
      byte byteArray[sizeof(unsigned long)];
      memcpy(byteArray, &l, sizeof(unsigned long));
      for (size_t j = 0; j < sizeof(unsigned long); j++)
      {
        Serial.println("byte[" + String(j) + "]: 0x" + String(byteArray[j], HEX));
      }
    }
  }
  else
  {
    //Serial.println("Geiger 1 Queue is empty.");
  }

  int n2 = geiger_2.getQueueCount();
  if (n2 != 0)
  {
    Serial.println("Geiger 2 Queue Data: ");

    for (int i=0; i<n2; i++)
    {
      unsigned long l = geiger_2.dequeueItem();
      Serial.println(l);
      byte byteArray[sizeof(unsigned long)];
      memcpy(byteArray, &l, sizeof(unsigned long));
      for (size_t j = 0; j < sizeof(unsigned long); j++)
      {
        Serial.println("byte[" + String(j) + "]: 0x" + String(byteArray[j], HEX));
      }
    }
  }
  else
  {
    //Serial.println("Geiger 2 Queue is empty.");
  }

  float temp = bme.readTemperature(); // Celsius
  Serial.print("Temperature: ");
  Serial.print(temp);
  Serial.println(" *C");

  float press = bme.readPressure();
  Serial.print("Pressure: ");
  Serial.print(press);
  Serial.println(" mbar");

  float seaLevelPressure = 1013.25;
  float alt = bme.readAltitude(seaLevelPressure);
  Serial.print("Altitude: ");
  Serial.print(alt);
  Serial.println(" m");

  float hum = bme.readHumidity();
  Serial.print("Humidity: ");
  Serial.print(hum);
  Serial.println(" %RH");

  char buffer[32];
  sprintf(buffer, "%4d,%6d,%5d,%3d,%10d", (int)temp, (int)press, (int)alt, (int)hum, millis());
  Serial.println(buffer);

  sox_data();

  Serial.print("Requesting temperatures...");
  sensors.requestTemperatures();
  Serial.println("DONE");

  Serial.println(ds18.temperature1);
  Serial.println(ds18.temperature2);
  Serial.println(ds18.temperature3);
  Serial.println(ds18.temperature4);
  Serial.println(ds18.temperature5);
  Serial.println(ds18.temperature6);
  Serial.println(ds18.temperature7);
  ds18.time = millis();
  //char buffer[sizeof(ds18Data)];
  memcpy(buffer, &ds18, sizeof(ds18));
  for (int i = 0; i<32; i++)
  {
    Serial.println(buffer[i], HEX);
  }
#endif
}

void sox_settings()
{
  Serial.println("SOX Setting:");

  sox.setAccelRange(LSM6DS_ACCEL_RANGE_2_G);
  Serial.print("Accelerometer range set to: ");
  switch (sox.getAccelRange()) {
  case LSM6DS_ACCEL_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case LSM6DS_ACCEL_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case LSM6DS_ACCEL_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case LSM6DS_ACCEL_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }

  sox.setGyroRange(LSM6DS_GYRO_RANGE_250_DPS );
  Serial.print("Gyro range set to: ");
  switch (sox.getGyroRange()) {
  case LSM6DS_GYRO_RANGE_125_DPS:
    Serial.println("125 degrees/s");
    break;
  case LSM6DS_GYRO_RANGE_250_DPS:
    Serial.println("250 degrees/s");
    break;
  case LSM6DS_GYRO_RANGE_500_DPS:
    Serial.println("500 degrees/s");
    break;
  case LSM6DS_GYRO_RANGE_1000_DPS:
    Serial.println("1000 degrees/s");
    break;
  case LSM6DS_GYRO_RANGE_2000_DPS:
    Serial.println("2000 degrees/s");
    break;
  case ISM330DHCX_GYRO_RANGE_4000_DPS:
    break; // unsupported range for the DSOX
  }

  sox.setAccelDataRate(LSM6DS_RATE_12_5_HZ);
  Serial.print("Accelerometer data rate set to: ");
  switch (sox.getAccelDataRate()) {
  case LSM6DS_RATE_SHUTDOWN:
    Serial.println("0 Hz");
    break;
  case LSM6DS_RATE_12_5_HZ:
    Serial.println("12.5 Hz");
    break;
  case LSM6DS_RATE_26_HZ:
    Serial.println("26 Hz");
    break;
  case LSM6DS_RATE_52_HZ:
    Serial.println("52 Hz");
    break;
  case LSM6DS_RATE_104_HZ:
    Serial.println("104 Hz");
    break;
  case LSM6DS_RATE_208_HZ:
    Serial.println("208 Hz");
    break;
  case LSM6DS_RATE_416_HZ:
    Serial.println("416 Hz");
    break;
  case LSM6DS_RATE_833_HZ:
    Serial.println("833 Hz");
    break;
  case LSM6DS_RATE_1_66K_HZ:
    Serial.println("1.66 KHz");
    break;
  case LSM6DS_RATE_3_33K_HZ:
    Serial.println("3.33 KHz");
    break;
  case LSM6DS_RATE_6_66K_HZ:
    Serial.println("6.66 KHz");
    break;
  }

  sox.setGyroDataRate(LSM6DS_RATE_12_5_HZ);
  Serial.print("Gyro data rate set to: ");
  switch (sox.getGyroDataRate()) {
  case LSM6DS_RATE_SHUTDOWN:
    Serial.println("0 Hz");
    break;
  case LSM6DS_RATE_12_5_HZ:
    Serial.println("12.5 Hz");
    break;
  case LSM6DS_RATE_26_HZ:
    Serial.println("26 Hz");
    break;
  case LSM6DS_RATE_52_HZ:
    Serial.println("52 Hz");
    break;
  case LSM6DS_RATE_104_HZ:
    Serial.println("104 Hz");
    break;
  case LSM6DS_RATE_208_HZ:
    Serial.println("208 Hz");
    break;
  case LSM6DS_RATE_416_HZ:
    Serial.println("416 Hz");
    break;
  case LSM6DS_RATE_833_HZ:
    Serial.println("833 Hz");
    break;
  case LSM6DS_RATE_1_66K_HZ:
    Serial.println("1.66 KHz");
    break;
  case LSM6DS_RATE_3_33K_HZ:
    Serial.println("3.33 KHz");
    break;
  case LSM6DS_RATE_6_66K_HZ:
    Serial.println("6.66 KHz");
    break;
  }
}

void sox_data()
{
  //  /* Get a new normalized sensor event */
  sensors_event_t accel;
  sensors_event_t gyro;
  sensors_event_t temp;
  sox.getEvent(&accel, &gyro, &temp);

  Serial.print("\t\tTemperature ");
  Serial.print(temp.temperature);
  Serial.println(" deg C");

  /* Display the results (acceleration is measured in m/s^2) */
  Serial.print("\t\tAccel X: ");
  Serial.print(accel.acceleration.x);
  Serial.print(" \tY: ");
  Serial.print(accel.acceleration.y);
  Serial.print(" \tZ: ");
  Serial.print(accel.acceleration.z);
  Serial.println(" m/s^2 ");

  /* Display the results (rotation is measured in rad/s) */
  Serial.print("\t\tGyro X: ");
  Serial.print(gyro.gyro.x);
  Serial.print(" \tY: ");
  Serial.print(gyro.gyro.y);
  Serial.print(" \tZ: ");
  Serial.print(gyro.gyro.z);
  Serial.println(" radians/s ");
  Serial.println();

  delay(100);

  //  // serial plotter friendly format

  //  Serial.print(temp.temperature);
  //  Serial.print(",");

  //  Serial.print(accel.acceleration.x);
  //  Serial.print(","); Serial.print(accel.acceleration.y);
  //  Serial.print(","); Serial.print(accel.acceleration.z);
  //  Serial.print(",");

  // Serial.print(gyro.gyro.x);
  // Serial.print(","); Serial.print(gyro.gyro.y);
  // Serial.print(","); Serial.print(gyro.gyro.z);
  // Serial.println();
  //  delayMicroseconds(10000);
}