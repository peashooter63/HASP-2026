from smbus2 import SMBus
import struct
import sqlite3 as sql

bus = SMBus(1)

# I2C address of Pico 1 (BME)
address1 = 0x66
# I2C address of Pico 2 (GEIGER)
address2 = 0x70

# Registers
reg1 = 1    # Sensor reg
reg2 = 2    # Geiger reg1
reg2 = 3    # Geiger reg2
reg2 = 4    # Geiger reg3
reg2 = 5    # Geiger reg4
reg2 = 6    # Geiger reg5

# ID BME example
sensorID = 0xAB

# Treat writing to register as writing data to a handler
bus.write_byte(address1,reg1)
bus.write_byte(address2, reg2)

# Writing data to different registers and pico
data = bus.read_i2c_block_data(address1,1,8)    #Adjust value here for current sensor packet. Using 8 to test packet
data2 = bus.read_i2c_block_data(address2,2,1)   # Read from geiger module

# Create a bytes object for the unpacking sensor function:
sensorBuffer = bytes(data)

print(f"Raw sensor module bytes: {data}")
print(f"Geiger Window counts {data2}")
print(f"the window counts from Pico 2 are {data2}")


class sensorData:

    @staticmethod
    def unpackSensor(data):
        temp = struct.unpack_from('<H',data,0)[0]      #Unpack in an order following the struct (low endian) on Pico.
        hum = struct.unpack_from('<H',data,2)[0]
        pres = struct.unpack_from('<I',data,4)[0]
        
        # Display data   
        print(f"Temperature: {temp/100.0} Degrees Celsius")
        print(f"Humidity: {hum/100.0}")
        print(f"Pressure: {pres/100.0}")

        return temp, hum, pres


# Unpack data
#sensorData.unpackSensor(sensorBuffer)

# Tuple of objects
temp, hum, pres = sensorData.unpackSensor(sensorBuffer)

# Rounded sensor parameters for DB
roundTemp = (temp)/100.0
roundHum = (hum)/100.0
roundPres = (pres)/100.0


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

#connection.commit()







#BME DATA for Pi. Will move this into a new module
#calibration_params = bme28+
#print(data.temperature)
#print(data.pressure)
#print(data.humidity)