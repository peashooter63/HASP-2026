import busio
import board
import struct
from datetime import datetime


# Initialize I2C (using default SCL and SDA pins)
i2c = busio.I2C(board.SCL, board.SDA)

ADDRESS_1 = 0X2C
REGISTER_1 = 0X01
REGISTER_2 = 0X02


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
                i2c.writeto(ADDRESS_1, bytes([REGISTER_1]))  # NEW
                BUFFER = bytearray(4)      # NEW
                i2c.readfrom_into(ADDRESS_1,BUFFER)  # New
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

            