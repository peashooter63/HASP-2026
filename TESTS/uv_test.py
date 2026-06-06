from smbus2 import SMBus, i2c_msg
import struct
import sqlite3 as sql
import time





# Defining variables and objects

totalCounts = 0
bus = SMBus(1)
# Registers
reg1 = 1    # Sensor reg
reg2 = 2    # Geiger1 Count reg
reg3 = 3    # Geiger1 Time  reg
reg4 = 4    # Geiger2 Count reg
reg5 = 5    # Geiger2 Time  reg
reg6 = 6    # Geiger3 Count reg
reg7 = 7    # Geiger3 Time  reg
# I2C address of Pico 1 (address 1:BME) & Pico 2 (adress 2: Geiger)
address1 = 0x66
address2 = 0x70

# Instances of i2c_msg (Test for Geigers)
#readTrans1 = i2c_msg.read(address2,reg2)
#readTrans2 = i2c_msg.read(address2,reg2,4)  

# ID BME example
sensorID = 0xAB

# Write to register (handler)
bus.write_byte(address1,reg1)   
bus.write_byte(address2, reg2) 
#bus.write_byte(address2, reg3)

# Writing data to different registers and pico
data = bus.read_i2c_block_data(address1,1,28)    #Adjust value here for current sensor packet. Using 8 to test packet   
#data2 = bus.read_i2c_block_data(address2,2,4)   # Read from geiger module (Counts)                                      
#data3 = bus.read_i2c_block_data(address2,3,4)   # Read from geiger module (Time)

#Test Poll Loop
for i in range(5):
    #bus.write_byte(address1,reg1)
    #data = bus.read_i2c_block_data(address1,1,28) 
    #bus.write_byte(address2, reg2)
    data2 = bus.read_i2c_block_data(address2,2,4) 
    print(data2)
    time.sleep(0.1)


# Create a bytes object for the unpacking and decoding:
sensorBuffer = bytes(data)
geigerBuffer = bytearray(data2)

print(f"Raw sensor module bytes: {data}")


class sensorData:

    @staticmethod
    def unpackSensor(data):
        temp = struct.unpack_from('<H',data,0)[0]      #Unpack in an order following the struct (low endian) on Pico.
        hum = struct.unpack_from('<H',data,2)[0]
        pres = struct.unpack_from('<I',data,4)[0]

        ax = struct.unpack_from('<H',data,8)[0]      #Unpack in an order following the struct (low endian) on Pico.
        ay = struct.unpack_from('<H',data,10)[0]
        az = struct.unpack_from('<H',data,12)[0]

        gx = struct.unpack_from('<H',data,14)[0]      #Unpack in an order following the struct (low endian) on Pico.
        gy = struct.unpack_from('<H',data,16)[0]
        gz = struct.unpack_from('<H',data,18)[0]

        mx = struct.unpack_from('<I',data,20)[0]      #Unpack in an order following the struct (low endian) on Pico.
        my = struct.unpack_from('<H',data,24)[0]
        mz = struct.unpack_from('<H',data,26)[0]
        
        
        # Display data   
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

        return temp, hum, pres

class countData:

    #@staticmethod
    def decodeCount(dataCount):
        decodeCounts = int.from_bytes((data2),'little')
        return decodeCounts



# Sensor Data
temp, hum, pres = sensorData.unpackSensor(sensorBuffer)


# Rounded sensor parameters for DB
roundTemp = (temp)/100.0
roundHum = (hum)/100.0
roundPres = (pres)/100.0


# Geiger Data
#counts = countData.decodeCount(data2)
counts = int.from_bytes(geigerBuffer, 'little')
totalCounts += 1
print(f"Counts: {counts}")
print(f"The window counts from Pico 2 are {counts}")  # OH SH.. ITS NOT DECODING IT. PUT DATA2 BACK IN RLLY QUICK
#print(f"The corresponding Boot time from Pico 2 are {data3}")
print(f"The total counts are {totalCounts}")

# Complete multiple rdwr I2C transactions for Geiger
#bus.i2c_rdwr(readTrans1,readTrans2)

# HASP mini Database 

# Connect to the database & create a relational database
with sql.connect("HaspLogger.db") as HaspLogger: 
    cursor = HaspLogger.cursor()
    sql = "DROP TABLE IF EXISTS sensorTable"
    cursor.execute(sql)
    sql = "CREATE TABLE IF NOT EXISTS sensorTable (SensorID BLOB, Temperature REAL, Humidity REAL, Pressure REAL)"
    cursor.execute(sql)


# Add data to the database
sql = "INSERT INTO sensorTable (SensorID, Temperature,Humidity,Pressure) VALUES (?, ?,?,?)"
cursor.execute(sql,(sensorID,roundTemp,roundHum,roundPres))
HaspLogger.commit()


#BME DATA for Pi. Will move this into a new module
#calibration_params = bme28+
#print(data.temperature)
#print(data.pressure)
#print(data.humidity) 
