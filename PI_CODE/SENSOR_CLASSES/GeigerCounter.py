# IMPORTS 
import busio
import board
import struct
from datetime import datetime

# Initialize I2C (using default SCL and SDA pins)
i2c = busio.I2C(board.SCL, board.SDA)

# PICO Addresses:
ADDRESS_1 = 0X2C
#ADDRESS_2 = ??? 

# GEIGER COUNTER Registers 
REGISTER_1 = 0X01     # GEIGER_1_COUNT_REGISTER 1
REGISTER_2 = 0X02     # GEIGER_1_DATA_REGISTER  2
REGISTER_3 = 0X03     # GEIGER_2_COUNT_REGISTER 3
REGISTER_4 = 0X04     # GEIGER_2_DATA_REGISTER  4


REGISTER_10 = 0X0A    # GEIGER_3_COUNT_REGISTER 10
REGISTER_11 = 0X0B    # GEIGER_3_DATA_REGISTER  11
REGISTER_12 = 0X0C    # GEIGER_4_COUNT_REGISTER 12
REGISTER_13 = 0X0D    # GEIGER_4_DATA_REGISTER  13
REGISTER_14 = 0X0E    # GEIGER_5_COUNT_REGISTER 14
REGISTER_15 = 0X0F    # GEIGER_5_DATA_REGISTER  15


class GeigerClass:
    counts = 0

    @staticmethod
    def DECODE_COUNTS(dataCount):
        decodeCounts = int.from_bytes((dataCount),'little')
        
        return decodeCounts

    @staticmethod
    def DECODE_QUEUE_AMOUNT(dataCount):
        queueCounts = int.from_bytes((dataCount),'little')
        return queueCounts

    @staticmethod
    def READ_QUEUE_1():
        if i2c.try_lock():
            try:
                # Write to REGISTER_2 and obtain how many counts there are by reading data
                i2c.writeto(ADDRESS_1, bytes([REGISTER_1]))  
                BUFFER = bytearray(4)      
                i2c.readfrom_into(ADDRESS_1,BUFFER)  
                DECODE_QUEUE_AMOUNT = GeigerClass.DECODE_QUEUE_AMOUNT(BUFFER)
                return DECODE_QUEUE_AMOUNT

            except Exception as e:
                print(f"An error occured {e}")
                return None

            finally:
            # Always unlock the bus after
                i2c.unlock()

            


    def READ_GEIGER_1(QUEUE_ITEM_COUNT):
        #decodeQueueCountNum = GeigerClass.READ_QUEUE_1()
        print(f"Received Number of items in Queue: {QUEUE_ITEM_COUNT}")   
        COUNT_ARRAY = [0] * QUEUE_ITEM_COUNT


        if i2c.try_lock():
            try:
                for i in range(QUEUE_ITEM_COUNT):   # Loop through the number of counts and read from REGISTER_2 for each count 
                
                    i2c.writeto(ADDRESS_1, bytes([REGISTER_2]))
                    buffer2 = bytearray(4)
                    i2c.readfrom_into(ADDRESS_1,buffer2)
                    Geiger_1_Count = GeigerClass.DECODE_COUNTS(buffer2)
                    print(f"Geiger Counter 1: iteration {i}   Count: {Geiger_1_Count}")
                    COUNT_ARRAY[i] = Geiger_1_Count
                    
                s = str(COUNT_ARRAY)
                return s
                    

            except Exception as e:
                print(f"An error occured reading GEIGER_1  {e}")
                return None 

            finally:
            # Always unlock the bus after
                i2c.unlock()

# ----------------------- New Geiger Class 

class GeigerClass_New:

    def __init__(self,i2c,address,queue_register,data_register):
        self.i2c = i2c 
        self.address = address 
        self.queue_register = queue_register
        self.data_register = data_register  
        self.counts = 0


    @staticmethod
    def DECODE_COUNTS(dataCount):
        decodeCounts = int.from_bytes((dataCount),'little')
        
        return decodeCounts

    @staticmethod
    def DECODE_QUEUE_AMOUNT(dataCount):
        queueCounts = int.from_bytes((dataCount),'little')
        return queueCounts

    def READ_QUEUE(self):
        if self.i2c.try_lock():
            try:
                # Write to REGISTER_2 and obtain how many counts there are by reading data
                self.i2c.writeto(self.address, bytes([self.queue_register]))  
                BUFFER = bytearray(4)      
                self.i2c.readfrom_into(self.address,BUFFER)  
                DECODE_QUEUE_AMOUNT = GeigerClass.DECODE_QUEUE_AMOUNT(BUFFER)
                return DECODE_QUEUE_AMOUNT

            except Exception as e:
                print(f"An error occured {e}")
                return None

            finally:
            # Always unlock the bus after
                self.i2c.unlock()
        else:
            return None


    def READ_GEIGER(self,QUEUE_ITEM_COUNT):
        #decodeQueueCountNum = GeigerClass.READ_QUEUE_1()
        print(f"Received Number of items in Queue: {QUEUE_ITEM_COUNT}")   
        COUNT_ARRAY = [0] * QUEUE_ITEM_COUNT


        if self.i2c.try_lock():
            try:
                for i in range(QUEUE_ITEM_COUNT):   # Loop through the number of counts and read from REGISTER_2 for each count 
                
                    self.i2c.writeto(self.address, bytes([self.data_register]))
                    buffer2 = bytearray(4)
                    self.i2c.readfrom_into(self.address,buffer2)
                    Geiger_Count_Event = GeigerClass.DECODE_COUNTS(buffer2)
                    print(f"Geiger Counter 1: iteration {i}   Count: {Geiger_Count_Event}")
                    COUNT_ARRAY[i] = Geiger_Count_Event
                    
                s = str(COUNT_ARRAY)
                return s
                    

            except Exception as e:
                print(f"An error occured reading the Geiger {e}")
                return None 

            finally:
            # Always unlock the bus after
                self.i2c.unlock()
        else:
            return None
 
         
