# IMPORTS 
import busio
import board
import struct
from adafruit_bme280 import basic as adafruit_bme280

# Initialize I2C (using default SCL and SDA pins)
i2c = busio.I2C(board.SCL, board.SDA)

ADDRESS_1 = 0X2C
#ADDRESS_2 = ???? 

# Registers 
REGISTER_5 = 0X05

class BME280_DATA(): 
   
    @staticmethod
    def READ_BME280():
        if i2c.try_lock():
            try:
                # Write to the slave
                i2c.writeto(ADDRESS_1, bytes([REGISTER_5]))
                buffer = bytearray(20)
                i2c.readfrom_into(ADDRESS_1,buffer)
                return BME280_DATA.DECODE_BME280(buffer)
                

            except Exception as e:
                print(f"An error occured {e}")
                return None

            finally:
            # Always unlock the bus after
                i2c.unlock()
    

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
        #:::::::VAHID::::::: Commented the following line
        #self.bme280.sea_level_pressure = None       
        #:::::::VAHID:::::::
        self.init = False  

    def INIT_BME280(self):
        try:
            self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, self.address) 
            self.init = True
            self.bme280.sea_level_pressure = 1013.25    # Adjust this reference based on the weather station at Palestine integration (barometric)
            print("BME280 Device initialized!")
    
        except Exception as e:
            print(f"Error: {e}")
            self.init = False
            print("BME280 Device initialization failed!")
            

    def READ_BME280_DEVICE(self):
        if self.init:
            try:
                sea_level_pressure = self.bme280.sea_level_pressure
                humidity = self.bme280.humidity
                temperature = self.bme280.temperature
                pressure = self.bme280.pressure
                altitude = self.bme280.altitude

                # For testing only 
                print("\nTemperature: %0.1f C" % self.bme280.temperature)
                print("Humidity: %0.1f %%" % self.bme280.humidity)
                print("Pressure: %0.1f hPa" % self.bme280.pressure)
                print("Sea Level Pressure: %0.1f hPa" % self.bme280.sea_level_pressure)
                #------------------
                return ( f"{humidity:.2f}" + ":" + f"{temperature:.2f}" + ":" + f"{pressure:.2f}" + ":" + f"{altitude:.2f}" )
        
            except Exception as e:
                print(f"Error {e}")
                return None
            
        else:
            print("Device not ready")
            return None
        
    @property
    def BME280_INITIALIZED(self):
        return self.init

