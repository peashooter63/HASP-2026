#IMPORTS 

import busio
import serial
import board
import threading
import queue
from collections import deque 
import os 
import time
import sqlite3 as sql
from datetime import datetime, timezone
from adafruit_extended_bus import ExtendedI2C as I2C 
import digitalio

# Adafruit Libraries 
import adafruit_ublox
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15
import adafruit_ina228
import adafruit_scd30
import adafruit_sgp30

# Custom Class Imports 
from SENSOR_CLASSES.BME280_Class import BME280_DATA, BME280_I2C_DEVICE, PICO_BME280_I2C_DEVICE
from SENSOR_CLASSES.GeigerCounter import GeigerClass, GeigerClass_New
from SENSOR_CLASSES.MPU9250_Class import MPU9250_DATA, MPU9250_I2C_DEVICE, PICO_MPU9250_I2C_DEVICE
from SENSOR_CLASSES.ADS1115_Class import ADS1115_DEVICE
from SENSOR_CLASSES.INA228_Class import INA228_I2C_DEVICE
from gpsPacket import NMEA_PACKET
from GPS_COORDINATES_LIVE import Live_GPS_Coordinates
from SENSOR_CLASSES.GPS_UBLOX_Class import I2C_GPS_UBLOX
from SENSOR_CLASSES.Environment_Sensors_Class import SCD30_I2C_DEVICE
from SENSOR_CLASSES.DS18_Class import PICO_DS18_I2C_DEVICE
from SENSOR_CLASSES.PICO_Time_Class import PICO_TIME
#from gps2 import GPS_UBLOX

DATA_QUEUE = queue.Queue(maxsize=50)
circular_buffer = deque(maxlen=10)

# For Geiger counters, this arraay only contains the register number of the each Geiger counter count register.
# In the case statement in the sensor_worker_thread, the register number is used to determine which Geiger counter to read from.
# The class instance for each Geiger counter contains the data count and the data register numbers.
# Since we have two PICOs, then for each Geiger counter we read from each PICO
#                              G1    G2    G3    G4    G5    BME   DS18  MPU1  MPU2  PI_BME PI_MPU PI_GPS JPL_A0 JPL_A1 JPL_A2 JPL_A3 MICS  SCD30 INA228
SENSOR_REGISTER_ARRAY = bytes([0x01, 0x03, 0x0A, 0X0C, 0X0E, 0x05, 0X07, 0x08, 0x09, 0x10,  0X11,  0x12,  0x13,  0x14,  0x15,  0x16, 0x17])
#SENSOR_REGISTER_ARRAY = bytes([0x01, 0x03, 0x0A])

PACKET_COUNTER = 0 
#i2c_lock = threading.Lock()

class SerialComms:

    def __init__(self):
        self.__port = serial.Serial(
            #port="/dev/ttyUSB0",
            port="/dev/ttyAMA0",
            baudrate=4800,
            timeout=1
        )

    def isOpen(self):
        return self.__port.is_open

    def readPort(self):
        return self.__port.readline()   # RAW BYTES

    def writePort(self, data):
        self.__port.write(data)


class Latest_Data:

    def __init__(self):
        self._lock = threading.Lock()
        self.bme = 0
        self.mpu1 = 0
        self.mpu2 = 0

        self.JPL_ON = 0 
        self.JPL_ARM = 0

        self.INA228_1 = 0 
        self.INA228_2 = 0
        self.INA228_3 = 0 
        self.INA228_4 = 0 
    
        self.JPL_A0 = 0
        self.JPL_A1 = 0
        self.JPL_A2 = 0
        self.JPL_A3 = 0

        self.GEIGER_1 = 0
        self.GEIGER_2 = 0
        self.GEIGER_3 = 0
        self.GEIGER_4 = 0
        self.GEIGER_5 = 0
        self.GEIGER_6 = 0
        self.GEIGER_7 = 0
        self.GEIGER_8 = 0
        self.GEIGER_9 = 0
        self.GEIGER_10 = 0 

        self.PI_BME280 = 0
        self.PI_MPU9250 = 0 
        self.PI_UBLOX_GPS = 0

    def update_sensor_data(self, sensor_ID, current_data):
        sensor_id_list = (["JPL_ON","JPL_ARM","INA228_1","INA228_2","INA228_3","INA228_4",
                          "JPL_ARM_STATUS","JPL_A0","JPL_A1","JPL_A2","JPL_A3",
                          "PI_BME280", "PI_MPU9250","GEIGER_1","GEIGER_1","GEIGER_2","GEIGER_3"
                          "GEIGER_4","GEIGER_5","GEIGER_6","GEIGER_7","GEIGER_8","GEIGER_9","GEIGER_10","PI_UBLOX_GPS"
                          ])
        
        with self._lock:
            if sensor_ID in sensor_id_list:
                setattr(self,sensor_ID,current_data)

# Build CESARS Packet -----------------------------

    def get_packet_data(self):
        #with self._lock:
            global PACKET_COUNTER 
            PACKET_COUNTER += 1
            timestamp = datetime.now(timezone.utc)
            ending_character = "\r\n"
            packet_checksum = 0 

            cpu_temperature = os.popen("vcgencmd measure_temp").readline().rstrip("\r\n").strip("'C").strip()
            system_input_voltage = os.popen("vcgencmd pmic_read_adc EXT5V_V").readline().rstrip("\r\n").strip("'").strip()
            cpu_ram_voltage = os.popen("vcgencmd measure_volts core").readline().rstrip("\r\n").strip("'").strip()
            rtc_battery_voltage = os.popen("vcgencmd pmic_read_adc BATT_V").readline().rstrip("\r\n").strip("'").strip()

            BUILD_PACKET =( "C" + "," + "E" + "," + f"{PACKET_COUNTER}"  + ","+ f"{timestamp}" +  
                           "," f"{JPL_ON_FLAG}" + ":" + f"{JPL_ARM_FLAG}" + ":" + f"{JPL_DATA_CHANNEL_0}" + ":"
                + f"{JPL_DATA_CHANNEL_1}"+ ":" + f"{JPL_DATA_CHANNEL_2}" + ":" + f"{JPL_DATA_CHANNEL_3}" + ":"
                + f"{self.PI_BME280}" + ":" + f"{self.PI_MPU9250}" + ":"
                + f"{GEIGER_01_COUNT}" + ":" + f"{GEIGER_02_COUNT}" + ":" + f"{GEIGER_03_COUNT}" + ":" + f"{GEIGER_04_COUNT}" + ":" + f"{GEIGER_05_COUNT}" + ":"
                + f"{GEIGER_06_COUNT}" + ":" + f"{GEIGER_07_COUNT}" + ":" + f"{GEIGER_08_COUNT}" + ":" + f"{GEIGER_09_COUNT}" + ":" + f"{GEIGER_10_COUNT}" + ":"
                + f"{self.PI_UBLOX_GPS}"
                + f"," + f"{cpu_temperature}" + "," + f"{system_input_voltage}" + "," + f"{cpu_ram_voltage}" + "," + f"{rtc_battery_voltage}"  
                + "," + f"{packet_checksum}" + "," + f"{ending_character}"
            )

            packet_payload_bytes = BUILD_PACKET.encode("utf-8")
            packet_payload_length = len(packet_payload_bytes)
            #CESARS_Packet = (f"C,E,{packet_payload_length},{BUILD_PACKET},CHECKSUM,{ending_character}")   

            CESARS_PACKET =( "C" + "," + "E" + "," + f"{PACKET_COUNTER}" + "," + f"{packet_payload_length}" + ","+ f"{timestamp}" +  
                           "," f"{JPL_ON_FLAG}" + ":" + f"{JPL_ARM_FLAG}" + ":" + f"{JPL_DATA_CHANNEL_0}" + ":"
                + f"{JPL_DATA_CHANNEL_1}"+ ":" + f"{JPL_DATA_CHANNEL_2}" + ":" + f"{JPL_DATA_CHANNEL_3}" + ":" 
                + f"{self.PI_BME280}" + ":" + f"{self.PI_MPU9250}" + ":"
                + f"{GEIGER_01_COUNT}" + ":" + f"{GEIGER_02_COUNT}" + ":" + f"{GEIGER_03_COUNT}" + ":" + f"{GEIGER_04_COUNT}" + ":" + f"{GEIGER_05_COUNT}" + ":"
                + f"{GEIGER_06_COUNT}" + ":" + f"{GEIGER_07_COUNT}" + ":" + f"{GEIGER_08_COUNT}" + ":" + f"{GEIGER_09_COUNT}" + ":" + f"{GEIGER_10_COUNT}" + ":"
                + f"{self.PI_UBLOX_GPS}"
                + f"," + f"{cpu_temperature}" + "," + f"{system_input_voltage}" + "," + f"{cpu_ram_voltage}" + "," + f"{rtc_battery_voltage}"  
                + "," + f"{packet_checksum}" + "," + f"{ending_character}"
            )

            #update_latest_packets()    This line causes exception
            return CESARS_PACKET
        

class latest_command:   

    def __init__(self):
        self.current_command = None
        self.command_list = ([0x9070, 0x916F, 0x926E, 0x936D, 0x946C,
                              0x956B, 0x966A, 0x9769, 0x9967, 0x9A66,
                              0x9B65, 0x9C64, 0x9D63, 0x9E62, 0x9F61
                            ])
        
    def set_latest_command(self,command): 
        if int(command) in self.command_list:
                self.current_command = command
        else:
            print("Command not in list")
            
    def get_latest_command(self,command):
        return self.current_command

#:::::::VAHID::::::: Added the following line to get the latest command
VAHID_LAST_COMMAND = latest_command()
#:::::::VAHID:::::::

# Utility Method   -----------------------------
 
def update_latest_packets():
        latest_data = Recent_Data.get_packet_data()
        circular_buffer.append(latest_data)

# HASP Phases -----------------------------

class HASP_STATES:

    def __init__(self):
        self.current_state = "INIT"

    def transition(self, state):
        if state in ["INTEGRATION","INIT", "RUNNING"]:
            self.current_state = state
            return self.current_state
        else:
            print(f"Invalid State {state}")

# Thread methods -----------------------------

#:::::::VAHID:::::::
#def sensor_worker_thread(SENSOR_REGISTER_ARRAY):
#:::::::VAHID:::::::
def sensor_worker_thread():
    global stop_sensor_data_thread
    global SENSOR_REGISTER_ARRAY
    global JPL_DATA_CHANNEL_0
    global JPL_DATA_CHANNEL_1
    global JPL_DATA_CHANNEL_2
    global JPL_DATA_CHANNEL_3
    global GEIGER_01_COUNT
    global GEIGER_02_COUNT
    global GEIGER_03_COUNT
    global GEIGER_04_COUNT
    global GEIGER_05_COUNT
    global GEIGER_06_COUNT
    global GEIGER_07_COUNT
    global GEIGER_08_COUNT
    global GEIGER_09_COUNT
    global GEIGER_10_COUNT

    print("sensor thread running")
    print(f"stop sensor data thread status: {stop_sensor_data_thread}")

    while True:
        try: 
            for REGISTER in SENSOR_REGISTER_ARRAY:
                print(f"CURRENT REGISTER: {REGISTER}")
                
                match REGISTER:
                    case 0x01:
                        #pass
                        queue_count_number = pico1_geiger_1.READ_QUEUE()
                        GEIGER_01_COUNT = queue_count_number
                        data = pico1_geiger_1.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_1,{datetime.now(timezone.utc)},{item}")
                        queue_count_number = pico2_geiger_1.READ_QUEUE()
                        GEIGER_06_COUNT = queue_count_number
                        data = pico2_geiger_1.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_6,{datetime.now(timezone.utc)},{item}")

                    case 0x03:
                        #pass
                        queue_count_number = pico1_geiger_2.READ_QUEUE()
                        GEIGER_02_COUNT = queue_count_number
                        data = pico1_geiger_2.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_2,{datetime.now(timezone.utc)},{item}")
                        queue_count_number = pico2_geiger_2.READ_QUEUE()
                        GEIGER_07_COUNT = queue_count_number
                        data = pico2_geiger_2.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_7,{datetime.now(timezone.utc)},{item}")

                    case 0x0A:
                        #pass
                        queue_count_number = pico1_geiger_3.READ_QUEUE()
                        GEIGER_03_COUNT = queue_count_number
                        data = pico1_geiger_3.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_3,{datetime.now(timezone.utc)},{item}")
                        queue_count_number = pico2_geiger_3.READ_QUEUE()
                        GEIGER_08_COUNT = queue_count_number
                        data = pico2_geiger_3.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_8,{datetime.now(timezone.utc)},{item}")

                    case 0X0C:
                        #pass
                        queue_count_number = pico1_geiger_4.READ_QUEUE()
                        GEIGER_04_COUNT = queue_count_number
                        data = pico1_geiger_4.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_4,{datetime.now(timezone.utc)},{item}")
                        queue_count_number = pico2_geiger_4.READ_QUEUE()
                        GEIGER_09_COUNT = queue_count_number
                        data = pico2_geiger_4.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_9,{datetime.now(timezone.utc)},{item}")

                    case 0x0E:
                        #pass
                        queue_count_number = pico1_geiger_5.READ_QUEUE()
                        GEIGER_05_COUNT = queue_count_number
                        data = pico1_geiger_5.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_5,{datetime.now(timezone.utc)},{item}")
                        queue_count_number = pico2_geiger_5.READ_QUEUE()
                        GEIGER_10_COUNT = queue_count_number
                        data = pico2_geiger_5.READ_GEIGER(queue_count_number)
                        for item in data:
                            DATA_QUEUE.put(f"GEIGER_10,{datetime.now(timezone.utc)},{item}")

                    case 0x05:
                        #pass
                        data = pico1_BME280.READ_BME280()
                        DATA_QUEUE.put(f"BME280_1,{datetime.now(timezone.utc)},{data}")
                        data = pico2_BME280.READ_BME280()
                        DATA_QUEUE.put(f"BME280_2,{datetime.now(timezone.utc)},{data}")

                    case 0x07:
                        #pass
                        data = pico1_DS18.READ_DS18()
                        DATA_QUEUE.put(f"DS18_1,{datetime.now(timezone.utc)},{data}")
                        data = pico2_DS18.READ_DS18()
                        DATA_QUEUE.put(f"DS18_2,{datetime.now(timezone.utc)},{data}")

                    case 0x08:
                        #pass
                        data = pico1_MPU9250.READ_MPU9250_DEVICE_1()
                        DATA_QUEUE.put(f"MPU9250_1_1,{datetime.now(timezone.utc)},{data}")
                        data = pico2_MPU9250.READ_MPU9250_DEVICE_1()
                        DATA_QUEUE.put(f"MPU9250_2_1,{datetime.now(timezone.utc)},{data}")

                    case 0x09:
                        pass
                        data = pico1_MPU9250.READ_MPU9250_DEVICE_2()
                        DATA_QUEUE.put(f"MPU9250_1_2,{datetime.now(timezone.utc)},{data}")
                        data = pico2_MPU9250.READ_MPU9250_DEVICE_2()
                        DATA_QUEUE.put(f"MPU9250_2_2,{datetime.now(timezone.utc)},{data}")

                    # PI DEVICE READS -------------------------

                    case 0x10:
                        #pass
                        data = PI_BME280_Class.READ_BME280_DEVICE()                         
                        DATA_QUEUE.put(f"PI_BME280,{datetime.now(timezone.utc)},{data}")

                    case 0x11:
                        #pass                                                              
                        data = PI_MPU9250_Class.READ_MPU9250_DEVICE()
                        DATA_QUEUE.put(f"PI_MPU9250,{datetime.now(timezone.utc)},{data}")

                    case 0x12:
                        pass
                        #gps_data = _gps.get_gps_data()
                        #DATA_QUEUE.put(f"PI_UBLOX_GPS,{datetime.now(timezone.utc)},{gps_data}")
                        GPS_UBLOX_DATA = PI_UBLOX_GPS_Class.GET_GPS_DATA()                  
                        DATA_QUEUE.put(f"PI_UBLOX_GPS,{datetime.now(timezone.utc)},{GPS_UBLOX_DATA}")

                    case 0x13:
                        #pass
                        channel_timestamp = datetime.now(timezone.utc)
                        data_channel_1 = PI_ADS1115_JPL_1.READ_ADS1115_CHANNELS(0)
                        data_channel_2 = PI_ADS1115_JPL_1.READ_ADS1115_CHANNELS(1)
                        data_channel_3 = PI_ADS1115_JPL_1.READ_ADS1115_CHANNELS(2)
                        data_channel_4 = PI_ADS1115_JPL_1.READ_ADS1115_CHANNELS(3)

                        JPL_DATA_CHANNEL_0 = data_channel_1
                        JPL_DATA_CHANNEL_1 = data_channel_2
                        JPL_DATA_CHANNEL_2 = data_channel_3
                        JPL_DATA_CHANNEL_3 = data_channel_4

                        DATA_QUEUE.put(f"JPL_A0,{channel_timestamp},{data_channel_1}")
                        DATA_QUEUE.put(f"JPL_A1,{channel_timestamp},{data_channel_2}")
                        DATA_QUEUE.put(f"JPL_A2,{channel_timestamp},{data_channel_3}")
                        DATA_QUEUE.put(f"JPL_A3,{channel_timestamp},{data_channel_4}")
                         
                    case 0x14:
                        #pass
                        channel_timestamp = datetime.now(timezone.utc)
                        data_channel_1 = PI_ADS1115_MICS5524.READ_ADS1115_CHANNELS(0)
                        DATA_QUEUE.put(f"MICS5524_A0,{channel_timestamp},{data_channel_1}")

                    case 0x15:
                        #pass
                        data = PI_SCD30_Class.READ_SCD30_DATA()
                        DATA_QUEUE.put(f"SCD30,{datetime.now(timezone.utc)},{data}")

                    case 0x16:
                        #pass
                        data = INA228_1.READ_INA228()
                        DATA_QUEUE.put(f"INA228_1,{datetime.now(timezone.utc)},{data}")
                        data = INA228_2.READ_INA228()
                        DATA_QUEUE.put(f"INA228_2,{datetime.now(timezone.utc)},{data}")
                        data = INA228_3.READ_INA228()
                        DATA_QUEUE.put(f"INA228_3,{datetime.now(timezone.utc)},{data}")
                        data = INA228_4.READ_INA228()
                        DATA_QUEUE.put(f"INA228_4,{datetime.now(timezone.utc)},{data}")

                    case 0x17:
                        # PICO Time
                        #pass
                        data = pico1_TIME.READ_PICO_TIME()
                        DATA_QUEUE.put(f"PICO_1_TIME,{datetime.now(timezone.utc)},{data}")
                        data = pico2_TIME.READ_PICO_TIME()
                        DATA_QUEUE.put(f"PICO_2_TIME,{datetime.now(timezone.utc)},{data}")

                if stop_sensor_data_thread:
                    break

            time.sleep(5)

        except Exception as e:  
            print(f"Reading Devices failed. Error: {e}")


def processing_thread():
    global stop_processing_thread
    global HaspLogger
    global Hasp_Packet

    while True:
        if stop_processing_thread:
            break
        
        while not DATA_QUEUE.empty():
            #print("Sensor thread Loop running")
            data_string = DATA_QUEUE.get()
            parts = data_string.split(",")
            if len(parts) >= 3:
                sensor_ID = parts[0]
                timestamp = parts[1]
                current_data = ",".join(parts[2:])
                Recent_Data.update_sensor_data(sensor_ID, current_data)
                #update_latest_packets()

            with sql.connect(_HaspLoggerDatabase_Name) as HaspLogger:
                cursor = HaspLogger.cursor()
                cursor.execute(
                    "INSERT INTO HASP_Table (SensorID, DATA, TIME) VALUES (?, ?, ?)",
                    (sensor_ID, current_data, timestamp)
                )

            HaspLogger.commit()

            if database_timer_event.is_set():

                source_con = sql.connect(_HaspLoggerDatabase_Name)

                database_backup_con = sql.connect("HASP_BACKUP.db")

                with database_backup_con:
                    source_con.backup(database_backup_con)

                source_con.close()
                database_backup_con.close()
                database_timer_event.clear()


            if timer_event.is_set():

                cesars_packet = Recent_Data.get_packet_data()
                uart_buffer = bytearray(cesars_packet, "utf-8")

                if serial_comm.isOpen():
                    serial_comm.writePort(uart_buffer)

                with sql.connect(_HaspPacketDatabase_Name) as Hasp_Packet:
                    cursor = Hasp_Packet.cursor()
                    cursor.execute(
                        "INSERT INTO HASP_Table_PACKET (SensorID, PACKET, TIME) VALUES (?, ?, ?)",
                        ("DOWNLINK", cesars_packet, str(datetime.now(timezone.utc)))
                        )

                timer_event.clear()
                Hasp_Packet.commit()

            DATA_QUEUE.task_done()

        time.sleep(1)

def downlink_timer():

    global stop_timer_thread

    while True:

        if stop_timer_thread:
            break

        timer_event.set()
        time.sleep(30)

def backup_data_timer():

    global stop_database_backup_thread

    while True:

        if stop_database_backup_thread:
            break

        # This time is subject to change
        time.sleep(30)

        database_timer_event.set()

def receive_serial_data():
    global stop_serial_thread
    global INTEGRATION_END_FLAG
    command_byte_join = None
    global JPL_ARM_FLAG
    global JPL_ON_FLAG

    while True:
        if stop_serial_thread:
            break

        if serial_comm.isOpen():
            RAW_DATA = serial_comm.readPort()
            #print(RAW_DATA)
            if (len(RAW_DATA) > 0):
                print("Serial Data Received:", end=" ")
                print(' '.join(f'{b:02X}' for b in RAW_DATA))

            #if not RAW_DATA:
            #    print("No valid data incoming")

            if b'$GPGGA' in RAW_DATA:
                decoded_GPS_DATA = RAW_DATA.decode("utf-8", errors="replace").strip()
                if "$GPGGA" in decoded_GPS_DATA and "*" in decoded_GPS_DATA:
                    NMEA_fix_index = decoded_GPS_DATA.find("$GPGGA")
                    checksum_index = decoded_GPS_DATA.find('*')
                    formatted_GPS_DATA = decoded_GPS_DATA[NMEA_fix_index:checksum_index+3]
                    print("RAW GPS DATA")
                    print(formatted_GPS_DATA)
                    print("GPS DATA INCOMING!")
                    NMEA_PACKET.Calculate_Checksum(formatted_GPS_DATA)
                    NMEA_STRING = NMEA_PACKET.Parse_NMEA(formatted_GPS_DATA)
                    DATA_QUEUE.put(f"NMEA GPS DATA,{datetime.now(timezone.utc)},{NMEA_STRING}")
                    #Coordinate Display attempt:
                    Live_GPS_Coordinates.GET_POSITION_LIVE(NMEA_STRING)
                else:
                    print("BAD GPS DATA")

            elif RAW_DATA.endswith(b'\r\n') and len(RAW_DATA) >= 4:
                print("COMMAND INCOMING!")
                command_byte_1 = RAW_DATA[2]
                command_byte_2 = RAW_DATA[3]

                # Build command
                if (command_byte_1 + command_byte_2) == 256:
                    command_byte_join = (command_byte_1 << 8) | command_byte_2
                    print("Match commands")
                    #:::::::VAHID::::::: Added the following line to get the latest command
                    #latest_command.set_latest_command(f"{command_byte_join}") 
                    VAHID_LAST_COMMAND.set_latest_command(f"{command_byte_join}") 
                    #:::::::VAHID:::::::
                    match command_byte_join:
                        case 0x9070:
                            for i in reversed(range(len((circular_buffer)))):
                                buffer = bytearray(circular_buffer[i], "utf-8")
                                print(buffer)
                                serial_comm.writePort(buffer)
                                DATA_QUEUE.put(f"COMMAND 0X9070,{datetime.now(timezone.utc)},{str(command_byte_join)}")
                    
                        case 0x9769:
                            pass

                        # Recalibration command. Recalibrate MPU9250 and SGP30?
                        case 0x916F:
                            pass
                        
                        case 0x926E:
                            if JPL_ARM_FLAG == 1 and JPL_ON_FLAG == 0:
                                JPL_ON.value = True
                                time.sleep(0.5)
                                JPL_ON.value = False
                                DATA_QUEUE.put(f"JPL ON,{datetime.now(timezone.utc)},{' '.join(f'{b:02X}' for b in command_byte_join.to_bytes(2, 'big'))}")
                                JPL_ON_FLAG = 1
                            else:
                                pass

                        case 0x936D:
                            if JPL_ON_FLAG == 1:
                                JPL_OFF.value = True
                                time.sleep(0.5)
                                JPL_OFF.value = False
                                DATA_QUEUE.put(f"JPL OFF,{datetime.now(timezone.utc)},{' '.join(f'{b:02X}' for b in command_byte_join.to_bytes(2, 'big'))}")
                                JPL_ON_FLAG = 0
                            else:
                                pass

                        case 0x946C:
                            if JPL_ARM_FLAG == 0:
                                JPL_ARM.value = True
                                time.sleep(0.5)
                                JPL_ARM.value = False
                                DATA_QUEUE.put(f"JPL Armed,{datetime.now(timezone.utc)},{' '.join(f'{b:02X}' for b in command_byte_join.to_bytes(2, 'big'))}")
                                JPL_ARM_FLAG = 1
                            else:
                                pass
                               
                        case 0x956B:
                            if JPL_ARM_FLAG == 1:
                                JPL_DISARM.value = True
                                time.sleep(0.5)
                                JPL_DISARM.value = False
                                DATA_QUEUE.put(f"JPL Disarmed,{datetime.now(timezone.utc)},{' '.join(f'{b:02X}' for b in command_byte_join.to_bytes(2, 'big'))}")
                                JPL_ARM_FLAG = 0
                            else:
                                pass

                        case 0x966A:
                            # pass
                            JPL_OFF.value = True
                            time.sleep(0.5)
                            JPL_OFF.value = False
                            os.system("sudo shutdown -h now")

                        case 0x9868:
                            buffer = bytearray(latest_command.get_latest_command().encode("utf-8"))
                            serial_comm.writePort(buffer)
                            DATA_QUEUE.put(f"COMMAND 0X9868,{datetime.now(timezone.utc)},{str(command_byte_join)}")

                        case 0X9967:
                            INTEGRATION_END_FLAG = 1 

                        case _:
                            print("Command not recognized")
        else:
            print("Serial Port not available")

        time.sleep(1)

# MAIN THREAD-------------------------------------------------------------------------------

#def main_thread():

# Define Threads
#:::::::VAHID:::::::
#sensor_data_thread = threading.Thread(target=sensor_worker_thread, args=(SENSOR_REGISTER_ARRAY,))
#:::::::VAHID:::::::
sensor_data_thread = threading.Thread(target=sensor_worker_thread, args=())
data_process_thread = threading.Thread(target=processing_thread, args=())
timer_thread = threading.Thread(target=downlink_timer, args=())
database_backup_timer_thread = threading.Thread(target=backup_data_timer, args=())
serial_thread = threading.Thread(target=receive_serial_data, args=())


# Mapped to GPIO pins
#JPL_arm = digitalio.DigitalInOut(board.GPIO23)
#JPL_arm.direction = digitalio.Direction.OUTPUT
#JPL_disarm = digitalio.DigitalInOut(board.GP16)
#JPL_disarm.direction = digitalio.Direction.OUTPUT
#JPL_On = digitalio.DigitalInOut(board.GP24)
#JPL_On.direction = digitalio.Direction.OUTPUT
#JPL_Off = digitalio.DigitalInOut(board.GP25)
#JPL_Off.direction = digitalio.Direction.OUTPUT


# ADC ADDRESSES 
ADS1115_ADDRESS_1 = 0X48   
ADS1115_ADDRESS_2_MICS = 0X49    

# POWER MONITOR ADDRESSES 
INA228_ADDRESS_1 = 0X40      
INA228_ADDRESS_2 = 0X41
INA228_ADDRESS_3 = 0X45         # This can conflict with the PI_UBLOX_GPS Address. Please place on another line. 
INA228_ADDRESS_4 = 0X44 

# SENSOR I2C ADDRESSES 
PI_BME280_ADDRESS = 0X76
PI_MPU9250_ADDRESS = 0X68
PI_UBLOX_GPS_ADDRESS = 0X42
PI_SCD30_ADDRESS = 0X61     # NDIR CO2 Temperature and Humidity 
PI_SGP30 = 0X58             # Air Quality Sensor (Monitor Air QUality)

# GEIGER COUNTER REGISTERS On THE PICO
REGISTER_1 = 0X01     # GEIGER_1_COUNT_REGISTER 1
REGISTER_2 = 0X02     # GEIGER_1_DATA_REGISTER  2
REGISTER_3 = 0X03     # GEIGER_2_COUNT_REGISTER 3
REGISTER_4 = 0X04     # GEIGER_2_DATA_REGISTER  41
REGISTER_10 = 0X0A    # GEIGER_3_COUNT_REGISTER 10
REGISTER_11 = 0X0B    # GEIGER_3_DATA_REGISTER  11
REGISTER_12 = 0X0C    # GEIGER_4_COUNT_REGISTER 12
REGISTER_13 = 0X0D    # GEIGER_4_DATA_REGISTER  13
REGISTER_14 = 0X0E    # GEIGER_5_COUNT_REGISTER 14
REGISTER_15 = 0X0F    # GEIGER_5_DATA_REGISTER  15
REGISTER_16 = 0X10    # PICO TIME_REGISTER      16

#BME280 REGISTER ON THE PICO
REGISTER_5 = 0X05     # BME280_REGISTER 5

#DS18 REGISTER ON THE PICO
REGISTER_7 = 0X07     # DS18_REGISTER 7

#MPU9250 REGISTER ON THE PICO
REGISTER_8 = 0X08     # MPU9250_REGISTER 8
REGISTER_9 = 0X09     # MPU9250_REGISTER 9

# PICO ADDRESSES 
PICO_1_ADDR = 0X2B
PICO_2_ADDR = 0X2C

# I2C BUS 
i2c = busio.I2C(board.SCL, board.SDA)
i2c_pi_bus = I2C(3)

# JPL FLAGS 
JPL_ARM_FLAG = 0        # 0 = Disarmed, 1 = Armed
JPL_ON_FLAG = 0         # 0 = OFF, 1 = ON
JPL_DATA_CHANNEL_0 = "0: 0"
JPL_DATA_CHANNEL_1 = "0: 0"
JPL_DATA_CHANNEL_2 = "0: 0"
JPL_DATA_CHANNEL_3 = "0: 0"
GEIGER_01_COUNT = 0
GEIGER_02_COUNT = 0
GEIGER_03_COUNT = 0
GEIGER_04_COUNT = 0
GEIGER_05_COUNT = 0
GEIGER_06_COUNT = 0
GEIGER_07_COUNT = 0
GEIGER_08_COUNT = 0
GEIGER_09_COUNT = 0
GEIGER_10_COUNT = 0

# Thread class instances 
state_machine = HASP_STATES()
serial_comm = SerialComms()
Recent_Data = Latest_Data()

stop_sensor_data_thread = False
stop_timer_thread = False
stop_database_backup_thread = False
stop_serial_thread = False
stop_processing_thread = False
timer_event = threading.Event()
database_timer_event = threading.Event()
INTEGRATION_END_FLAG = 0

#:::::::VAHID:::::::
#SET_STATE = state_machine.transition("INTEGRATION")
#:::::::VAHID:::::::
SET_STATE = state_machine.transition("INIT")

#:::::::VAHID:::::::
serial_thread.start() 
#:::::::VAHID:::::::

# CLASS INSTANCES 

# SENSORS I2C 
PI_BME280_Class = BME280_I2C_DEVICE(i2c_pi_bus,PI_BME280_ADDRESS)
PI_MPU9250_Class = MPU9250_I2C_DEVICE(i2c_pi_bus,PI_MPU9250_ADDRESS)
PI_UBLOX_GPS_Class = I2C_GPS_UBLOX(i2c_pi_bus,PI_UBLOX_GPS_ADDRESS)     
PI_SCD30_Class = SCD30_I2C_DEVICE(i2c_pi_bus,PI_SCD30_ADDRESS)
#PI_SGP30_Class = 

# ANALOG 
PI_ADS1115_JPL_1 = ADS1115_DEVICE(i2c_pi_bus,ADS1115_ADDRESS_1)              
PI_ADS1115_MICS5524 = ADS1115_DEVICE(i2c_pi_bus,ADS1115_ADDRESS_2_MICS)

# POWER MONITORS 
INA228_1 = INA228_I2C_DEVICE(i2c_pi_bus,INA228_ADDRESS_1)
INA228_2 = INA228_I2C_DEVICE(i2c_pi_bus,INA228_ADDRESS_2)
INA228_3 = INA228_I2C_DEVICE(i2c_pi_bus,INA228_ADDRESS_3)
INA228_4 = INA228_I2C_DEVICE(i2c_pi_bus,INA228_ADDRESS_4)

# GEIGER COUNTERS 
pico1_geiger_1 = GeigerClass_New(i2c, PICO_1_ADDR, REGISTER_1,  REGISTER_2)
pico1_geiger_2 = GeigerClass_New(i2c, PICO_1_ADDR, REGISTER_3,  REGISTER_4)
pico1_geiger_3 = GeigerClass_New(i2c, PICO_1_ADDR, REGISTER_10, REGISTER_11)
pico1_geiger_4 = GeigerClass_New(i2c, PICO_1_ADDR, REGISTER_12, REGISTER_13)
pico1_geiger_5 = GeigerClass_New(i2c, PICO_1_ADDR, REGISTER_14, REGISTER_15)

pico2_geiger_1 = GeigerClass_New(i2c, PICO_2_ADDR, REGISTER_1,  REGISTER_2)
pico2_geiger_2 = GeigerClass_New(i2c, PICO_2_ADDR, REGISTER_3,  REGISTER_4)
pico2_geiger_3 = GeigerClass_New(i2c, PICO_2_ADDR, REGISTER_10, REGISTER_11)
pico2_geiger_4 = GeigerClass_New(i2c, PICO_2_ADDR, REGISTER_12, REGISTER_13)
pico2_geiger_5 = GeigerClass_New(i2c, PICO_2_ADDR, REGISTER_14, REGISTER_15)

pico1_BME280 = PICO_BME280_I2C_DEVICE(i2c, PICO_1_ADDR, REGISTER_5)
pico2_BME280 = PICO_BME280_I2C_DEVICE(i2c, PICO_2_ADDR, REGISTER_5)

pico1_DS18 = PICO_DS18_I2C_DEVICE(i2c, PICO_1_ADDR, REGISTER_7)
pico2_DS18 = PICO_DS18_I2C_DEVICE(i2c, PICO_2_ADDR, REGISTER_7)

pico1_MPU9250 = PICO_MPU9250_I2C_DEVICE(i2c, PICO_1_ADDR, REGISTER_8, REGISTER_9)
pico2_MPU9250 = PICO_MPU9250_I2C_DEVICE(i2c, PICO_2_ADDR, REGISTER_8, REGISTER_9)

pico1_TIME = PICO_TIME(i2c, PICO_1_ADDR, REGISTER_16)
pico2_TIME = PICO_TIME(i2c, PICO_2_ADDR, REGISTER_16)

timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
_HaspLoggerDatabase_Name = f"HaspLogger_{timestamp}.db"
_HaspPacketDatabase_Name = f"HaspPacket_{timestamp}.db"

#_gps = GPS_UBLOX(i2c_pi_bus)

while True:
    
    CURRENT_STATE = state_machine.current_state 

    match CURRENT_STATE:
        case "INTEGRATION":
            if INTEGRATION_END_FLAG == 1:
                SET_STATE = state_machine.transition("INIT")

        case "INIT":                         
            #print(CURRENT_STATE)
            INTEGRATION_END_FLAG = 0

            # Initialize devices 
            PI_MPU9250_Class.SETUP_MPU9250()
            PI_BME280_Class.INIT_BME280()
            PI_UBLOX_GPS_Class.INIT_GPS()  
            PI_SCD30_Class.INIT_SCD30()

            # Initialize Channels 
            PI_ADS1115_JPL_1.INIT_ADS1115_CHANNELS()        
            PI_ADS1115_MICS5524.INIT_ADS1115_CHANNELS()

            # Initialize Power monitors
            INA228_1.INIT_INA228()            
            INA228_2.INIT_INA228()      
            INA228_3.INIT_INA228() 
            INA228_4.INIT_INA228()            

            # Check if initialization work 
            if (PI_BME280_Class.BME280_INITIALIZED and PI_MPU9250_Class.MPU9250_INITIALIZED 
            and PI_UBLOX_GPS_Class.GPS_INITIALIZED 
            and PI_ADS1115_JPL_1.CHANNELS_INITIALIZED
            and PI_SCD30_Class.SCD30_INITIALIZED and INA228_1.INA228_INITIALIZED):   # Will change this to a wrapper that loops and initializes all devices together. 
                print("All Devices INITIALIZED")

                # Database Logger
                with sql.connect(_HaspLoggerDatabase_Name) as HaspLogger:
                    cursor = HaspLogger.cursor()
                    cursor.execute("DROP TABLE IF EXISTS HASP_Table")

                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS HASP_Table (SensorID TEXT, DATA TEXT, TIME TEXT,PACKET)"
                )

                HaspLogger.commit()

                with sql.connect(_HaspLoggerDatabase_Name) as HaspLogger:
                    cursor = HaspLogger.cursor()
                    cursor.execute(
                        "INSERT INTO HASP_Table (SensorID, DATA, TIME) VALUES (?, ?, ?)",
                        ("STARTUP", datetime.now(timezone.utc), datetime.now(timezone.utc))
                    )

                HaspLogger.commit()

                # Downlink Logger
                with sql.connect(_HaspPacketDatabase_Name) as Hasp_Packet:
                    cursor = Hasp_Packet.cursor()
                    cursor.execute("DROP TABLE IF EXISTS HASP_Table_PACKET")

                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS HASP_Table_PACKET (SensorID TEXT, PACKET TEXT, TIME TEXT)"
                )

                Hasp_Packet.commit()

                sensor_data_thread.start()
                #:::::::VAHID:::::::
                data_process_thread.start()
                #:::::::VAHID:::::::
                timer_thread.start()
                #:::::::VAHID:::::::
                #database_backup_timer_thread.start()
                #:::::::VAHID:::::::

                #_gps.start_gps_thread()  # Start GPS thread to read GPS data

                # Initialize GPIO pins using digitalio
                JPL_ARM              = digitalio.DigitalInOut(board.D16)
                JPL_ARM.direction    = digitalio.Direction.OUTPUT
                JPL_DISARM           = digitalio.DigitalInOut(board.D23)
                JPL_DISARM.direction = digitalio.Direction.OUTPUT
                JPL_ON               = digitalio.DigitalInOut(board.D25)
                JPL_ON.direction     = digitalio.Direction.OUTPUT
                JPL_OFF              = digitalio.DigitalInOut(board.D24)
                JPL_OFF.direction    = digitalio.Direction.OUTPUT
                JPL_ARM.value    = False  # Set LOW
                JPL_DISARM.value = False  # Set LOW
                JPL_ON.value     = False  # Set LOW
                JPL_OFF.value    = False  # Set LOW
                JPL_ARM_FLAG = 0
                JPL_ON_FLAG  = 0

                SET_STATE = state_machine.transition("RUNNING")
    
            else:
                print("REINITIALIZE SYSTEM AGAIN")

        case "RUNNING":
            #print(CURRENT_STATE)
            stop_sensor_data_thread = False
            stop_processing_thread = False
            stop_timer_thread = False 
            stop_database_backup_thread = False 

#if __name__ == "__main__": 
#   main_thread()