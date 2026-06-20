import adafruit_ina228
import time

class INA228_I2C_DEVICE:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.ina228 = None
        self.init = False  


    def INIT_INA228(self):
        try:
            self.ina228 = adafruit_ina228.INA228(self.i2c,address=self.address)
            self.init = True
            print("INA228 INITIALIZED")

        except (ValueError, OSError,RuntimeError) as e:
            print(f"Error: {e}")
            self.init = False
            print("Error setting up ina228")

    def READ_INA228(self):
        try:
            print("\nCurrent Measurements:")
            print(f"Current: {self.ina228.current:.2f} mA")
            print(f"Bus Voltage: {self.ina228.bus_voltage:.2f} V")
            print(f"Shunt Voltage: {self.ina228.shunt_voltage*1000:.2f} mV")
            print(f"Power: {self.ina228.power:.2f} mW")
            print(f"Energy: {self.ina228.energy:.2f} J")
            print(f"Temperature: {self.ina228.die_temperature:.2f} °C")
            
            current = self.ina228.current
            shunt_voltage = self.ina228.shunt_voltage*1000
            power = self.ina228.power
            power_temperature = self.ina228.die_temperature
            bus_voltage = self.ina228.bus_voltage

            s =( ":" + f"{current:.2f}" + ":" + f"{shunt_voltage:.2f}" + ":" + f"{self.ina228.power}" + ":" 
                + f"{ power_temperature:.2f}"+ ":" + f"{ bus_voltage:.2f}" + ":" )
            
            return s 

        except (ValueError, OSError,RuntimeError) as e:
            print(f"Error: {e}")
            self.init = False
            print("Error setting up ina228")

            return None
        
    @property
    def INA228_INITIALIZED(self):
        return self.init


