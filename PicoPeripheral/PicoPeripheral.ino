#include <Wire.h>
#include <ArduinoQueue.h>
#include "Geiger.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_LSM6DSOX.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <cfloat>
#include "MPU9250.h"

constexpr uint8_t I2C_ADDR = 0x2C;

//#define DEBUG_MODE    // Comment this line out for production code, uncomment it for testing

//#define LED_PIN 22

#define GEIGER_1_INTERRUPT_PIN 21
#define GEIGER_2_INTERRUPT_PIN 22
#define GEIGER_3_INTERRUPT_PIN 26
#define GEIGER_4_INTERRUPT_PIN 27
#define GEIGER_5_INTERRUPT_PIN 28

#define GEIGER_QUEUE_SIZE 100

#define WIRE0_SDA_PIN 0
#define WIRE0_SCL_PIN 1

#define WIRE1_SDA_PIN 2
#define WIRE1_SCL_PIN 3

#define GEIGER_1_COUNT_REGISTER 1
#define GEIGER_1_DATA_REGISTER  2

#define GEIGER_2_COUNT_REGISTER 3
#define GEIGER_2_DATA_REGISTER  4

#define GEIGER_3_COUNT_REGISTER 10
#define GEIGER_3_DATA_REGISTER  11

#define GEIGER_4_COUNT_REGISTER 12
#define GEIGER_4_DATA_REGISTER  13

#define GEIGER_5_COUNT_REGISTER 14
#define GEIGER_5_DATA_REGISTER  15

#define BME_280_DATA 5
#define RMU_DATA     6
#define DS18_TEMPERATURE_DATA 7
#define MPU9250_YPR_MAG_DATA 8
#define MPU9250_ACC_GYRO_DATA 9

#define ONE_WIRE_BUS 6

volatile uint8_t registerNumber = 0;

Geiger geiger_1(GEIGER_1_INTERRUPT_PIN, GEIGER_QUEUE_SIZE);
Geiger geiger_2(GEIGER_2_INTERRUPT_PIN, GEIGER_QUEUE_SIZE);
Geiger geiger_3(GEIGER_3_INTERRUPT_PIN, GEIGER_QUEUE_SIZE);
Geiger geiger_4(GEIGER_4_INTERRUPT_PIN, GEIGER_QUEUE_SIZE);
Geiger geiger_5(GEIGER_5_INTERRUPT_PIN, GEIGER_QUEUE_SIZE);

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

typedef struct __attribute__((packed)) {
    float data1;          // 4 bytes
    float data2;          // 4 bytes
    float data3;          // 4 bytes
    float data4;          // 4 bytes
    float data5;          // 4 bytes
    float data6;          // 4 bytes
    float data7;          // 4 bytes
    unsigned long time;   // 4 bytes
} mpuData;

Adafruit_BME280 bme;
MPU9250 mpu;
MPU9250Setting mpu_setting;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

sensorData data;
rmuData rmu;
ds18Data ds18;
mpuData mpudata1;
mpuData mpudata2;

//Adafruit_LSM6DSOX sox;
//const MPU9250Setting mpu_setting = MPU9250Setting();

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

  if (!(sio_hw->gpio_in & (1 << GEIGER_3_INTERRUPT_PIN)))   // If the pin is low, we have an interrupt on that pin
  {
    if (geiger_3.enqueueItem(m) == false)
    {
      Serial.println("Guiger 3 Queue is full.");
    }
  }

  if (!(sio_hw->gpio_in & (1 << GEIGER_4_INTERRUPT_PIN)))   // If the pin is low, we have an interrupt on that pin
  {
    if (geiger_4.enqueueItem(m) == false)
    {
      Serial.println("Guiger 4 Queue is full.");
    }
  }

  if (!(sio_hw->gpio_in & (1 << GEIGER_5_INTERRUPT_PIN)))   // If the pin is low, we have an interrupt on that pin
  {
    if (geiger_5.enqueueItem(m) == false)
    {
      Serial.println("Guiger 5 Queue is full.");
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

    case GEIGER_3_COUNT_REGISTER:
      {
        unsigned short s = geiger_3.getQueueCount();
        byte byteArray[sizeof(unsigned short)];
        memcpy(byteArray, &s, sizeof(unsigned short));
        Wire.write(byteArray, 2);
      }
      break;

    case GEIGER_3_DATA_REGISTER:
      {
        unsigned long l = geiger_3.dequeueItem();
        byte byteArray[sizeof(unsigned long)];
        memcpy(byteArray, &l, sizeof(unsigned long));
        Wire.write(byteArray, 4);
      }
      break;

    case GEIGER_4_COUNT_REGISTER:
      {
        unsigned short s = geiger_4.getQueueCount();
        byte byteArray[sizeof(unsigned short)];
        memcpy(byteArray, &s, sizeof(unsigned short));
        Wire.write(byteArray, 2);
      }
      break;

    case GEIGER_4_DATA_REGISTER:
      {
        unsigned long l = geiger_4.dequeueItem();
        byte byteArray[sizeof(unsigned long)];
        memcpy(byteArray, &l, sizeof(unsigned long));
        Wire.write(byteArray, 4);
      }
      break;

    case GEIGER_5_COUNT_REGISTER:
      {
        unsigned short s = geiger_5.getQueueCount();
        byte byteArray[sizeof(unsigned short)];
        memcpy(byteArray, &s, sizeof(unsigned short));
        Wire.write(byteArray, 2);
      }
      break;

    case GEIGER_5_DATA_REGISTER:
      {
        unsigned long l = geiger_5.dequeueItem();
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
        //sensors_event_t accel;
        //sensors_event_t gyro;
        //sensors_event_t temp;
        //sox.getEvent(&accel, &gyro, &temp);
        //rmu.temperatue = temp.temperature;            // temperature deg C
        //rmu.acceleration_x = accel.acceleration.x;    // acceleration m/s^2
        //rmu.acceleration_y = accel.acceleration.y;    // acceleration m/s^2
        //rmu.acceleration_z = accel.acceleration.z;    // acceleration m/s^2
        //rmu.rotation_x = gyro.gyro.x;                 // rotation rad/s
        //rmu.rotation_y = gyro.gyro.y;                 // rotation rad/s
        //rmu.rotation_z = gyro.gyro.z;                 // rotation rad/s
        //rmu.time = millis();
        char buffer[sizeof(rmuData)];
        memcpy(buffer, &rmu, sizeof(rmu));
        Wire.write(buffer, 32);
      }
      break;

    case DS18_TEMPERATURE_DATA:
      {
        ds18.temperature1 = DEVICE_DISCONNECTED_C;
        ds18.temperature2 = DEVICE_DISCONNECTED_C;
        ds18.temperature3 = DEVICE_DISCONNECTED_C;
        ds18.temperature4 = DEVICE_DISCONNECTED_C;
        ds18.temperature5 = DEVICE_DISCONNECTED_C;
        ds18.temperature6 = DEVICE_DISCONNECTED_C;
        ds18.temperature7 = DEVICE_DISCONNECTED_C;
        ds18.time = millis();

        int n = sensors.getDS18Count();
        if (n > 0)
        {
          sensors.requestTemperatures();
          for (int i=0; i<n; i++)
          {
            float tempC = sensors.getTempCByIndex(i);
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
        }
        print_ds18_data();
        
        char buffer[sizeof(ds18Data)];
        memcpy(buffer, &ds18, sizeof(ds18));
        Wire.write(buffer, 32);
      }
      break;

    case MPU9250_YPR_MAG_DATA:
      {
        char buffer[sizeof(mpudata1)];
        memcpy(buffer, &mpudata1, sizeof(mpudata1));
        Wire.write(buffer, 32);
      }
      break;

    case MPU9250_ACC_GYRO_DATA:
      {
        char buffer[sizeof(mpudata2)];
        memcpy(buffer, &mpudata2, sizeof(mpudata2));
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

  Wire.setSDA(WIRE0_SDA_PIN);
  Wire.setSCL(WIRE0_SCL_PIN);
  Wire.begin(I2C_ADDR);
  Wire.onRequest(onI2CRequest);
  Wire.onReceive(onI2CReceive);

  Wire1.setSDA(WIRE1_SDA_PIN);
  Wire1.setSCL(WIRE1_SCL_PIN);
  Wire1.begin();

  bme.begin(0x77, &Wire1);
  //sox.begin_I2C(0x6A, &Wire1);

  mpu_setting.accel_fs_sel = ACCEL_FS_SEL::A16G;
  mpu_setting.gyro_fs_sel = GYRO_FS_SEL::G2000DPS; 
  mpu_setting.mag_output_bits = MAG_OUTPUT_BITS::M16BITS; 
  mpu_setting.fifo_sample_rate = FIFO_SAMPLE_RATE::SMPL_200HZ;
  mpu_setting.gyro_dlpf_cfg = GYRO_DLPF_CFG::DLPF_41HZ;
  mpu_setting.accel_dlpf_cfg = ACCEL_DLPF_CFG::DLPF_45HZ;
  mpu_setting.accel_fchoice = 0x01;
  mpu_setting.gyro_fchoice = 0x03;

  if (!mpu.setup(0x68, mpu_setting, Wire1))
  {
    Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
  }

  //mpu.verbose(true);
  //delay(5000);
  //mpu.calibrateAccelGyro();
  //Serial.println("Mag calibration will start in 5sec.");
  //Serial.println("Please Wave device in a figure eight until done.");
  //delay(5000);
  //mpu.calibrateMag();
  //print_mpu_calibration();
  //mpu.verbose(false);
  //mpu.setMagneticDeclination(11.29);

  pinMode(LED_BUILTIN, OUTPUT);
  //pinMode(LED_PIN, OUTPUT);

  pinMode(GEIGER_1_INTERRUPT_PIN, INPUT_PULLUP);
  pinMode(GEIGER_2_INTERRUPT_PIN, INPUT_PULLUP);
  pinMode(GEIGER_3_INTERRUPT_PIN, INPUT_PULLUP);
  pinMode(GEIGER_4_INTERRUPT_PIN, INPUT_PULLUP);
  pinMode(GEIGER_5_INTERRUPT_PIN, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(GEIGER_1_INTERRUPT_PIN), handleInterrupt, FALLING);
  attachInterrupt(digitalPinToInterrupt(GEIGER_2_INTERRUPT_PIN), handleInterrupt, FALLING);

  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW

  //digitalWrite(LED_PIN, LOW);
  
  //sox_settings();

  sensors.begin();
}

void loop() {
  //digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  //delay(500);                      // wait for a second
  //digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
  //delay(500);                      // wait for a second

  //if ((geiger_1.getQueueCount() > 0) || (geiger_2.dequeueItem() > 0))
  //{
  //  digitalWrite(LED_PIN, HIGH);
  //}
  //else
  //{
  //  digitalWrite(LED_PIN, LOW);
  //}

  //noInterrupts();

  if (mpu.update())
  {
    static uint32_t prev_ms = millis();
    if (millis() > prev_ms + 2500)
    {
      mpudata1.data1 = mpu.getYaw();
      mpudata1.data2 = mpu.getPitch();
      mpudata1.data3 = mpu.getRoll();
      mpudata1.data4 = mpu.getMagX();
      mpudata1.data5 = mpu.getMagY();
      mpudata1.data6 = mpu.getMagZ();
      mpudata1.data7 = mpu.getTemperature();
      mpudata1.time = millis();

      mpudata2.data1 = mpu.getAccX();
      mpudata2.data2 = mpu.getAccY();
      mpudata2.data3 = mpu.getAccZ();
      mpudata2.data4 = mpu.getGyroX();
      mpudata2.data5 = mpu.getGyroX();
      mpudata2.data6 = mpu.getGyroX();
      mpudata2.data7 = mpu.getTemperature();
      mpudata2.time = millis();

      print_mpu_data();

      prev_ms = millis();
    }
  }

  // ds18.temperature1 = DEVICE_DISCONNECTED_C;
  // ds18.temperature2 = DEVICE_DISCONNECTED_C;
  // ds18.temperature3 = DEVICE_DISCONNECTED_C;
  // ds18.temperature4 = DEVICE_DISCONNECTED_C;
  // ds18.temperature5 = DEVICE_DISCONNECTED_C;
  // ds18.temperature6 = DEVICE_DISCONNECTED_C;
  // ds18.temperature7 = DEVICE_DISCONNECTED_C;
  // ds18.time = millis();

  // int n = sensors.getDS18Count();
  // if (n > 0)
  // {
  //   static uint32_t prev_ms_2 = millis();
  //   if (millis() > prev_ms_2 + 2500)
  //   {
  //     sensors.requestTemperatures();
  //     for (int i=0; i<n; i++)
  //     {
  //       float tempC = sensors.getTempCByIndex(i);
  //       if(tempC != DEVICE_DISCONNECTED_C)
  //       {
  //         switch (i)
  //         {
  //           case 0:
  //             ds18.temperature1 = tempC;
  //             break;

  //           case 1:
  //             ds18.temperature2 = tempC;
  //             break;
               
  //           case 2:
  //             ds18.temperature3 = tempC;
  //             break;
              
  //           case 3:
  //             ds18.temperature4 = tempC;
  //             break;
          
  //           case 4:
  //             ds18.temperature5 = tempC;
  //             break;
             
  //           case 5:
  //             ds18.temperature6 = tempC;
  //             break;
           
  //           case 6:
  //             ds18.temperature7 = tempC;
  //             break;
  //         }
  //       }
  //     }

  //     print_ds18_data();
  //     prev_ms_2 = millis();
  //   }
  // }

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
    Serial.println("Geiger 1 Queue is empty.");
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
    Serial.println("Geiger 2 Queue is empty.");
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

  //sox_data();

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
  //for (int i = 0; i<32; i++)
  //{
  //  Serial.println(buffer[i], HEX);
  //}
#endif

}

void sox_settings()
{
  Serial.println("SOX Setting:");

  //sox.setAccelRange(LSM6DS_ACCEL_RANGE_2_G);
  Serial.print("Accelerometer range set to: ");
  //switch (sox.getAccelRange()) {
  //case LSM6DS_ACCEL_RANGE_2_G:
  //  Serial.println("+-2G");
  //  break;
  //case LSM6DS_ACCEL_RANGE_4_G:
  //  Serial.println("+-4G");
  //  break;
  //case LSM6DS_ACCEL_RANGE_8_G:
  //  Serial.println("+-8G");
  //  break;
  //case LSM6DS_ACCEL_RANGE_16_G:
  //  Serial.println("+-16G");
  //  break;
  //}

  //sox.setGyroRange(LSM6DS_GYRO_RANGE_250_DPS );
  Serial.print("Gyro range set to: ");
  //switch (sox.getGyroRange()) {
  //case LSM6DS_GYRO_RANGE_125_DPS:
  //  Serial.println("125 degrees/s");
  //  break;
  //case LSM6DS_GYRO_RANGE_250_DPS:
  //  Serial.println("250 degrees/s");
  //  break;
  //case LSM6DS_GYRO_RANGE_500_DPS:
  //  Serial.println("500 degrees/s");
  //  break;
  //case LSM6DS_GYRO_RANGE_1000_DPS:
  //  Serial.println("1000 degrees/s");
  //  break;
  //case LSM6DS_GYRO_RANGE_2000_DPS:
  //  Serial.println("2000 degrees/s");
  //  break;
  //case ISM330DHCX_GYRO_RANGE_4000_DPS:
  //  break; // unsupported range for the DSOX
  //}

  //sox.setAccelDataRate(LSM6DS_RATE_12_5_HZ);
  Serial.print("Accelerometer data rate set to: ");
  //switch (sox.getAccelDataRate()) {
  //case LSM6DS_RATE_SHUTDOWN:
  //  Serial.println("0 Hz");
  //  break;
  //case LSM6DS_RATE_12_5_HZ:
  //  Serial.println("12.5 Hz");
  //  break;
  //case LSM6DS_RATE_26_HZ:
  //  Serial.println("26 Hz");
  //  break;
  //case LSM6DS_RATE_52_HZ:
  //  Serial.println("52 Hz");
  //  break;
  //case LSM6DS_RATE_104_HZ:
  //  Serial.println("104 Hz");
  //  break;
  //case LSM6DS_RATE_208_HZ:
  //  Serial.println("208 Hz");
  //  break;
  //case LSM6DS_RATE_416_HZ:
  //  Serial.println("416 Hz");
  //  break;
  //case LSM6DS_RATE_833_HZ:
  //  Serial.println("833 Hz");
  //  break;
  //case LSM6DS_RATE_1_66K_HZ:
  //  Serial.println("1.66 KHz");
  //  break;
  //case LSM6DS_RATE_3_33K_HZ:
  //  Serial.println("3.33 KHz");
  //  break;
  //case LSM6DS_RATE_6_66K_HZ:
  //  Serial.println("6.66 KHz");
  //  break;
  //}

  //sox.setGyroDataRate(LSM6DS_RATE_12_5_HZ);
  Serial.print("Gyro data rate set to: ");
  //switch (sox.getGyroDataRate()) {
  //case LSM6DS_RATE_SHUTDOWN:
  //  Serial.println("0 Hz");
  //  break;
  //case LSM6DS_RATE_12_5_HZ:
  //  Serial.println("12.5 Hz");
  //  break;
  //case LSM6DS_RATE_26_HZ:
  //  Serial.println("26 Hz");
  //  break;
  //case LSM6DS_RATE_52_HZ:
  //  Serial.println("52 Hz");
  //  break;
  //case LSM6DS_RATE_104_HZ:
  //  Serial.println("104 Hz");
  //  break;
  //case LSM6DS_RATE_208_HZ:
  //  Serial.println("208 Hz");
  //  break;
  //case LSM6DS_RATE_416_HZ:
  //  Serial.println("416 Hz");
  //  break;
  //case LSM6DS_RATE_833_HZ:
  //  Serial.println("833 Hz");
  //  break;
  //case LSM6DS_RATE_1_66K_HZ:
  //  Serial.println("1.66 KHz");
  //  break;
  //case LSM6DS_RATE_3_33K_HZ:
  //  Serial.println("3.33 KHz");
  //  break;
  //case LSM6DS_RATE_6_66K_HZ:
  //  Serial.println("6.66 KHz");
  //  break;
  //}
}

void sox_data()
{
  //  /* Get a new normalized sensor event */
  sensors_event_t accel;
  sensors_event_t gyro;
  sensors_event_t temp;
  //sox.getEvent(&accel, &gyro, &temp);

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

void print_mpu_data()
{
  Serial.println("First Read of MPU Data:");
  Serial.print("Yaw, Pitch, Roll: ");
  Serial.print(mpudata1.data1, 2);
  Serial.print(", ");
  Serial.print(mpudata1.data2, 2);
  Serial.print(", ");
  Serial.println(mpudata1.data3, 2);

  Serial.print("MagX, MagY, MagZ: ");
  Serial.print(mpudata1.data4, 2);
  Serial.print(", ");
  Serial.print(mpudata1.data5, 2);
  Serial.print(", ");
  Serial.println(mpudata1.data6, 2);

  Serial.print("Temp: ");
  Serial.println(mpudata1.data7, 2);

  Serial.print("Time: ");
  Serial.println(mpudata1.time);

  Serial.println("Second Read of MPU Data Read:");
  Serial.print("AccX, AccY, AccZ: ");
  Serial.print(mpudata2.data1, 2);
  Serial.print(", ");
  Serial.print(mpudata2.data2, 2);
  Serial.print(", ");
  Serial.println(mpudata2.data3, 2);

  Serial.print("GyroX, GyroY, GyroZ: ");
  Serial.print(mpudata2.data4, 2);
  Serial.print(", ");
  Serial.print(mpudata2.data5, 2);
  Serial.print(", ");
  Serial.println(mpudata2.data6, 2);

  Serial.print("Temp: ");
  Serial.println(mpudata2.data7, 2);

  Serial.print("Time: ");
  Serial.println(mpudata2.time);
}

void print_ds18_data()
{
  Serial.println("DS18 Temperature Data:");
  Serial.print("Temp1, Temp2, Temp3, Temp4, Temp5, Temp6, Temp7:");
  Serial.print(ds18.temperature1, 2);
  Serial.print(", ");
  Serial.print(ds18.temperature2, 2);
  Serial.print(", ");
  Serial.print(ds18.temperature3, 2);
  Serial.print(", ");
  Serial.print(ds18.temperature4, 2);
  Serial.print(", ");
  Serial.print(ds18.temperature5, 2);
  Serial.print(", ");
  Serial.print(ds18.temperature6, 2);
  Serial.print(", ");
  Serial.println(ds18.temperature7, 2);

  Serial.print("Time: ");
  Serial.println(ds18.time);
}


void print_mpu_calibration() {
    Serial.println("< calibration parameters >");
    Serial.println("accel bias [g]: ");
    Serial.print(mpu.getAccBiasX() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getAccBiasY() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getAccBiasZ() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY);
    Serial.println();
    Serial.println("gyro bias [deg/s]: ");
    Serial.print(mpu.getGyroBiasX() / (float)MPU9250::CALIB_GYRO_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getGyroBiasY() / (float)MPU9250::CALIB_GYRO_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getGyroBiasZ() / (float)MPU9250::CALIB_GYRO_SENSITIVITY);
    Serial.println();
    Serial.println("mag bias [mG]: ");
    Serial.print(mpu.getMagBiasX());
    Serial.print(", ");
    Serial.print(mpu.getMagBiasY());
    Serial.print(", ");
    Serial.print(mpu.getMagBiasZ());
    Serial.println();
    Serial.println("mag scale []: ");
    Serial.print(mpu.getMagScaleX());
    Serial.print(", ");
    Serial.print(mpu.getMagScaleY());
    Serial.print(", ");
    Serial.print(mpu.getMagScaleZ());
    Serial.println();
}
