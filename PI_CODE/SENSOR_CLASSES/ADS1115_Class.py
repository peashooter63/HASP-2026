# IMPORTS 
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15
from adafruit_ads1x15.ads1x15 import Mode 

class ADS1115_DEVICE:
    def __init__(self, i2c,address):
        self.i2c = i2c
        self.address = address      #Works but may need to check current address for addr 0x48
        self.ads1115 = None
        self.mode    = None
        self.channels_list = []
        self.chan_1  = None
        self.chan_2  = None
        self.chan_3  = None
        self.chan_4  = None
        self.init    = False 

    def INIT_ADS1115_CHANNELS(self): #May throw error for gas sensor addr since pins other than A0 not used. Separate obj?
        try:
            self.mode = Mode.SINGLE
            self.ads1115 = ADS1115(self.i2c,address=self.address,mode=self.mode)
            self.chan_1 = AnalogIn(self.ads1115,ads1x15.Pin.A0)
            self.chan_2 = AnalogIn(self.ads1115,ads1x15.Pin.A1)
            self.chan_3 = AnalogIn(self.ads1115,ads1x15.Pin.A2)
            self.chan_4 = AnalogIn(self.ads1115,ads1x15.Pin.A3)
            self.channels_list = [self.chan_1, self.chan_2, self.chan_3, self.chan_4]
            self.init = True
            print("Channels initialized!")

        except Exception as e:
            print(f"Error initializing channel: {e}")
            self.init = False 
        
    def READ_ADS1115_CHANNELS(self,channel_number): 
        if self.init:
            if channel_number in range(len(self.channels_list)):
                
                try:
                    voltage = self.channels_list[channel_number].voltage
                    value = self.channels_list[channel_number].value

                    # For testing only i put-----
                    print(f"Voltage: {voltage:.2f} ")
                    print(f"Value: {value:.2f} ")

                    return  f"{voltage:.2f}" + ":" + f"{value:.2f}" 
            
                except Exception as e:
                    print(f"Error {e}")
                    return None
                
            else:
                print("Channel data not ready or invalid channel")
                return None
        

    @property
    def CHANNELS_INITIALIZED(self):
        return self.init
