import busio
import board
import struct
from adafruit_bme280 import basic as adafruit_bme280

ADDRESS_1 = 0X2C
REGISTER_3 = 0X03


# Initialize I2C (using default SCL and SDA pins)
i2c = busio.I2C(board.SCL, board.SDA)

class BME280_DATA(): 
   
    @staticmethod
    def READ_BME280():
        if i2c.try_lock():
            try:
                # Write to the slave
                i2c.writeto(ADDRESS_1, bytes([REGISTER_3]))
                buffer = bytearray(20)
                i2c.readfrom_into(ADDRESS_1,buffer)

            except Exception as e:
                print(f"An error occured {e}")

            finally:
            # Always unlock the bus after
                i2c.unlock()
        return BME280_DATA.DECODE_BME280(buffer)
    

    @staticmethod
    def DECODE_BME280(data):
        temperature = struct.unpack_from('<f',data,0)[0]  
        humidity = struct.unpack_from('<f',data,4)[0]
        pressure = struct.unpack_from('<f',data,8)[0]
        altitude = struct.unpack_from('<f',data,12)[0]
        #time     = struct.unpack_from('<f',data,16)[0]
        return f"{temperature:.2f}" + ":" + f"{humidity:.2f}" + ":" + f"{pressure:.2f}" + ":" + f"{altitude:.2f}"
    

class BME280_I2C_DEVICE:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.bme280 = None
        #self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address)
        self.init = False  

    def INIT_BME280(self):
        try:
            self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, self.address) 
            self.init = True
            print("BME280 Device initialized!")
            return True
        except (ValueError, OSError) as e:
            print(f"Error: {e}")
            return False 
            

    def READ_BME280_DEVICE(self):
        if self.init:
            try:
                humidity = self.bme280.humidity
                temperature = self.bme280.temperature
                pressure = self.bme280.pressure
                altitude = self.bme280.altitude

                # For testing only 
                print("\nTemperature: %0.1f C" % self.bme280.temperature)
                print("Humidity: %0.1f %%" % self.bme280.humidity)
                print("Pressure: %0.1f hPa" % self.bme280.pressure)
                #------------------
                return f"{humidity},{temperature},{pressure},{altitude}"
        
            except (ValueError, OSError) as e:
                print(f"Error {e}")
                return None
            
        else:
            print("Device not ready")
            return None
