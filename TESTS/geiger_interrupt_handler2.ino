import busio
import board
import struct
import sqlite3 as sql
import time


 # https://www.digikey.com/en/maker/projects/circuitpython-basics-i2c-and-spi/9799e0554de14af3850975dfb0174ae3 GOOD TUTORIAL 
 #data_to_send = bytes([0x01, 0xFF])  # Data must be sent as a byte-like object (bytes or bytearray) list

# Initialize I2C (using default SCL and SDA pins)
i2c = busio.I2C(board.SCL, board.SDA)

# Define I2C address and regs
addr1 = 0x66
addr2 = 0x70

reg1 = 0x01
reg2 = 0x02
reg3 = 0x03
reg4 = 0x04
reg5 = 0x05
reg6 = 0x06



# Create an array to hold the register values for each device
regArr = [bytes([reg1]), bytes([reg2])]




# Lock the bus for no conflicts with other devices on one bus line  (OLD TEST RUN w/ RAW data)
if i2c.try_lock():
    try:
        

        # Write to reg1 on the peripheral device at addr1 
        i2c.writeto(addr1, bytes([reg1]))
        buffer = bytearray(28)
        i2c.readfrom_into(addr1, buffer)
        print(buffer)

    except Exception as e:
        print(f"An error occured {e}")

    finally:
        # Always unlock the bus after
        i2c.unlock()




   # Declare classes and functions here

class sensorData:
    
    @staticmethod
    def readSensor():
        if i2c.try_lock():
            try:
                # Write to the slave
                i2c.writeto(addr1, bytes([reg1]))
                buffer = bytearray(28)
                i2c.readfrom_into(addr1,buffer)

            except Exception as e:
                print(f"An error occured {e}")

            finally:
            # Always unlock the bus after
                i2c.unlock()

        sensorData.unpackSensor(buffer)   # ERror: saying cannot access local variable buffer wheh it doesnt have a value   

    @staticmethod
    def unpackSensor(data):
        temp = struct.unpack_from('<H',data,0)[0]      #Unpack in an order following the struct (low endian) on Pico.
        hum = struct.unpack_from('<H',data,2)[0]
        pres = struct.unpack_from('<I',data,4)[0]

        ax = struct.unpack_from('<H',data,8)[0]        #Unpack in an order following the struct (low endian) on Pico.
        ay = struct.unpack_from('<H',data,10)[0]
        az = struct.unpack_from('<H',data,12)[0]

        gx = struct.unpack_from('<H',data,14)[0]       #Unpack in an order following the struct (low endian) on Pico.
        gy = struct.unpack_from('<H',data,16)[0]
        gz = struct.unpack_from('<H',data,18)[0]

        mx = struct.unpack_from('<I',data,20)[0]       #Unpack in an order following the struct (low endian) on Pico.
        my = struct.unpack_from('<H',data,24)[0]
        mz = struct.unpack_from('<H',data,26)[0]

        # Print the unpacked values (testing only)
        print(f"Temperature: {temp/100.0} Degrees Celsius")
        print(f"Humidity: {hum/100.0}")
        print(f"Pressure: {pres/100.0}")

        print(f"Acceleration x: {ax/1000.0} m/s^2")
        print(f"Acceleration y: {ay/1000.0} m/s^2")
        print(f"Acceleration z: {az/1000.0} m/s^2")

        print(f"Gyroscope x: {gx/1000.0} degrees/s")
        print(f"Gyroscope y: {gy/1000.0} degrees/s")
        print(f"Gyroscope z: {gz/1000.0} degrees/s")

        print(f"Magnetometer x: {mx/1000.0} gauss ")
        print(f"Magnetometer y: {my/1000.0} gauss ")
        print(f"Magnetometer z: {mz/1000.0} gauss ")

class countData:
    counts = 0

    @staticmethod
    def decodeCount(dataCount):
        decodeCounts = int.from_bytes((dataCount),'little')
        print(f"Counts: {decodeCounts}")
        return decodeCounts

    @staticmethod
    def decodeQueueCount(dataCount):
        queueCounts = int.from_bytes((dataCount),'little')
        print(f"Number of items in queue: {queueCounts}")   #SEems to be working whne I PRINT RATHER THAN RETURN these values for both prints..
        return queueCounts


    def readQueue1():
        if i2c.try_lock():
            try:
                # Write to reg2 and obtain how many counts there are by reading data
                i2c.writeto(addr2, bytes([reg2]))  # NEW
                bufferCountNum = bytearray(4)      # NEW
                i2c.readfrom_into(addr2,bufferCountNum)  # New
                decodeQueueCountNum = countData.decodeQueueCount(bufferCountNum)   # new

            except Exception as e:
                print(f"An error occured {e}")

            finally:
            # Always unlock the bus after
                i2c.unlock()
                return decodeQueueCountNum

    

    def readGeiger1():
        decodeQueueCountNum = countData.readQueue1()

        if i2c.try_lock():
            try:
                for i in range(1,decodeQueueCountNum+1):   # Loop through the number of counts and read from reg2 for each count # NEW 
                #i2c.writeto(addr2, bytes([reg2]))
                    buffer2 = bytearray(4)
                    i2c.readfrom_into(addr2,buffer2)
                    geiger1Count = countData.decodeCount(buffer2)   # New 
                    #print(f"Geiger Counter 1 Count: {}") # New 
                    

            except Exception as e:
                print(f"An error occured {e}")

            finally:
            # Always unlock the bus after
                i2c.unlock()

            # Decode geiger counter binary data 
            #geiger1Count = countData.decodeCount(buffer2)
            

        
        
# Create an instance of the sensorData class and call the readSensor function to read and unpack data (Bad Practice)
sensor = sensorData()
geiger1 = countData()

 # Initialize a dictionary mapping to map registers to their corresponding data values

switcher = {
    reg1: sensorData.readSensor,
    reg2: countData.readQueue1,
    reg3: countData.readGeiger1
}

#switcher.get(reg1, lambda: "Invalid Register")() # Call the function associated with reg1



# Polling loop to continiously read data from each peripheral

try:
    while True:
        for reg in range(1,3): #Loop through the registers to read from each device (currently only up to 2 reg for testing)
            switcher.get(reg, lambda: "Invalid Register")() # Call the function associated with reg1    
        time.sleep(5)

            # Log data to the database here
            

            # Connect to the database & create a relational database


except KeyboardInterrupt:
    print("\nScript interrupted")
    exit(0)

