import adafruit_scd30
import adafruit_sgp30
import time

class SCD30_I2C_DEVICE:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.scd30 = None
        self.init = False  


    def INIT_SCD30(self):
        try:
            self.scd30 = adafruit_scd30.SCD30(self.i2c,address=self.address)
            self.scd30.temperature_offset = 10 
            self.scd30.measurement_interval = 4
            self.scd30.self_calibration_enabled = True 
            self.scd30.forced_recalibration_reference = 409  # Adjust later  
            self.scd30.ambient_pressure = 1100               # Adjust later
            self.scd30.altitude = 100                        # Adjust the meters above sea level LATER
            self.init = True
            print("SCD30_INITIALIZED")

        except (ValueError, OSError,RuntimeError) as e:
            print(f"Error: {e}")
            self.init = False
            print("Error setting up SCD30")




    def READ_SCD30_DATA(self):
        if self.init:
            if self.scd30.data_available:
                data = f"{self.scd30.CO2:.2f}" + ":" + f"{self.scd30.temperature:.2f}" + ":" + f"{self.scd30.relative_humidity:2f}"
                return data
    
                
        else:
            print("No SCD30 data yet!")
            return None
        
        time.sleep(2)


        
    @property
    def SCD30_INITIALIZED(self):
        return self.init



class PI_SGP30_I2C_DEVICE:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.sgp30 = None
        self.init = False  
        self.sgp30_calibration_ready = False 

    def INIT_SGP30(self):
        try:
            self.sgp30 = adafruit_sgp30.Adafruit_SGP30(self.i2c,address=self.address)
            if self.sgp30_calibration_ready:
                self.sgp30.set_iaq_baseline()
                self.init = True
                print("SGP30 INITIALIZED")
            else:
                print("Calibrate SGP30 baselines first")
                self.init = False

        except (ValueError, OSError,RuntimeError) as e:
            print(f"Error: {e}")
            self.init = False
            print("Error setting up SGP30")
    
    def READ_SGP30_IAQ_DATA(self):
        if self.init:
            eCO2, TVOC = self.sgp30.iaq_measure()
            data = f"{eCO2:.2f}" + ":" + f"{TVOC}" 
            return data
        else:
            print("SGP30 Data is not ready yet")
            return None
        
    def SET_BASELINE_SGP30(self,):
        if self.sgp30_calibration_ready:
            eCO2_baseline,TVOC_baseline = PI_SGP30_I2C_DEVICE.SGP30_CALIBRATION()
            self.sgp30.set_iaq_baseline(eCO2_baseline,TVOC_baseline)
        else:
            print("Unable to setup baseline values")


    def SGP30_CALIBRATION(self):
    
        try:
            eCO2_baseline = self.sgp30.baseline_eCO2
            TVOC_baseline = self.sgp30.baseline_TVOC
            self.sgp30_calibration_ready = True 
            return (eCO2_baseline,TVOC_baseline)

        except (ValueError, OSError,RuntimeError) as e:
            print(f"Error: {e}")
            self.init = False
            print("Error calibrating the SGP30.")
            self.sgp30_calibration_ready = False 

        # Notes:
        # At startup values will be 0 
        # Run the sensor for 12 hours to establish a baseline if current values in memory are a week old. 
        # Recommended to prevent drift, update baselines every ~1 hour 