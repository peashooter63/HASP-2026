import busio
import serial
import board
import threading
import queue
import time
import sqlite3 as sql
from datetime import datetime, timezone
import digitalio

# Adafruit Libraries 
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_ads1x15 import ADS1115
from adafruit_ina228 import INA228 

# Class imports 
from BME280_Class import BME280_DATA
from GeigerCounter import GeigerClass
from MPU9250_Class import MPU9250_DATA

DATA_QUEUE = queue.Queue(maxsize=50)
SENSOR_REGISTER_ARRAY = bytes([0x01, 0x03, 0x04, 0x05])
timer_event = threading.Event()
stop_sensor_data_thread = False
stop_timer_thread = False
stop_serial_thread = False
stop_processing_thread = False
i2c = busio.I2C(board.SCL, board.SDA)


class SerialComms:

    def __init__(self):
        self.__port = serial.Serial(
            port="/dev/ttyUSB0",
            baudrate=9600,
            timeout=1
        )

    def isOpen(self):
        return self.__port.is_open

    def readPort(self):
        return self.__port.readline()   # RAW BYTES

    def writePort(self, data):
        self.__port.write(data)


class LatestData:

    def __init__(self):
        self._lock = threading.Lock()
        self.bme = 0
        self.mpu1 = 0
        self.mpu2 = 0
        self.geiger1 = 0

    def update_sensor_data(self, sensor_ID, current_data):
        with self._lock:
            if sensor_ID == "BME280_1":
                self.bme = current_data
            elif sensor_ID == "MPU9250_1":
                self.mpu1 = current_data
            elif sensor_ID == "MPU9250_2":
                self.mpu2 = current_data
            elif sensor_ID == "GEIGER_1":
                self.geiger1 = current_data

    def get_current_data(self):
        with self._lock:
            return f"{self.bme},{self.mpu1},{self.mpu2},{self.geiger1}"


class HASP_STATES:

    def __init__(self):
        self.current_state = "INIT"

    def transition(self, state):
        if state in ["INIT", "RUNNING"]:
            self.current_state = state
            return self.current_state
        else:
            print(f"Invalid State {state}")

def sensor_worker_thread(SENSOR_REGISTER_ARRAY):

    global stop_sensor_data_thread

    while True:

        if stop_sensor_data_thread:
            break

        for REGISTER in SENSOR_REGISTER_ARRAY:
            print(f"CURRENT REGISTER: {REGISTER}")

            match REGISTER:

                case 0x01:
                    queue_count_number = GeigerClass.READ_QUEUE_1()
                    data = GeigerClass.READ_GEIGER_1(queue_count_number)
                    DATA_QUEUE.put(f"GEIGER_1_COUNTS,{datetime.now(timezone.utc)},{data}")
                   

                case 0x03:
                    data = BME280_DATA.READ_BME280()
                    DATA_QUEUE.put(f"BME280_1,{datetime.now(timezone.utc)},{data}")
                    

                case 0x04:
                    data = MPU9250_DATA.READ_MPU9250_1()
                    DATA_QUEUE.put(f"MPU9250_1,{datetime.now(timezone.utc)},{data}")
                    time.sleep(5)

                case 0x05:
                    data = MPU9250_DATA.READ_MPU9250_2()
                    DATA_QUEUE.put(f"MPU9250_2,{datetime.now(timezone.utc)},{data}")
                    
                


                #case 0x20:  # Need to replace this with the I2C sparkfun GPS, not nmea. Nmea belongs in serial comm thread.
                #    data = GPSPacket.READ_NMEA()
                #    DATA_QUEUE.put(f"NMEA,{datetime.now(timezone.utc)},{data}")

        


def geiger_worker_thread():
    pass

def processing_thread():

    global stop_processing_thread

    data_object = LatestData()


    while True:
        if stop_processing_thread:
            break
        
        while not DATA_QUEUE.empty():
            data_string = DATA_QUEUE.get()
            parts = data_string.split(",")

            sensor_ID = parts[0]
            timestamp = parts[1]
            current_data = ",".join(parts[2:])

            data_object.update_sensor_data(sensor_ID, current_data)

            with sql.connect("HaspLogger.db") as HaspLogger:
                cursor = HaspLogger.cursor()
                cursor.execute(
                    "INSERT INTO HASP_Table (SensorID, DATA, TIME) VALUES (?, ?, ?)",
                    (sensor_ID, current_data, timestamp)
                )

            if timer_event.is_set():

                packet = data_object.get_current_data()
                cesars_packet = (f"C,E,{packet},END")
                uart_buffer = bytearray(cesars_packet, "utf-8")

                #if serial_comm.isOpen():
                #    serial_comm.writePort(uart_buffer)

                with sql.connect("Hasp_Packet.db") as Hasp_Packet:
                    cursor = Hasp_Packet.cursor()
                    cursor.execute(
                        "INSERT INTO HASP_Table_PACKET (SensorID, PACKET, TIME) VALUES (?, ?, ?)",
                        ("DOWNLINK", cesars_packet, str(datetime.now(timezone.utc)))
                        )

                timer_event.clear()
                #HaspLogger.commit()
                #Hasp_Packet.commit()



            DATA_QUEUE.task_done()




def downlink_timer():

    global stop_timer_thread

    while True:

        if stop_timer_thread:
            break

        time.sleep(600)
        timer_event.set()



def receive_serial_data():
    global stop_serial_thread
    command_byte_join = None


    while True:

        if stop_serial_thread:
            break

        if serial_comm.isOpen():

            RAW_DATA = serial_comm.readPort()
            print(RAW_DATA)

            #if not RAW_DATA:
            #    print("No valid data incoming")

            if b'$GPGGA' in RAW_DATA:
                decoded_GPS_DATA = RAW_DATA.decode("utf-8", errors="ignore").strip()
                print("GPS DATA INCOMING!")
                # GPS handler here

            elif RAW_DATA.endswith(b'\r\n') and len(RAW_DATA) >= 4:
                print("COMMAND INCOMING!")
                command_byte_1 = RAW_DATA[2]
                command_byte_2 = RAW_DATA[3]

                    # Build command
                if (command_byte_1 + command_byte_2) == 256:
                    command_byte_join = (command_byte_1 << 8) | command_byte_2
                    print("Match commands")
                    match command_byte_join:
                    

                        case 0x9070:
                                DATA_QUEUE.put(f"COMMAND 0X9070,{datetime.now(timezone.utc)},{str(command_byte_join)}")
                
                        case 0x9769:
                            pass
                        case 0x916F:
                            pass
                        case 0x926E:
                            pass
                    
                        case 0x936D:
                            pass
                #       case 0x946C:
                #                pass
                #            case 0x956B:
                #                pass
                #            case 0x966A:
                #                pass
                #            case 0x9868:
                #                pass
                        case _:
                            print("Command not recognized")
        else:
            print("Serial Port not available")




# Define Threads
sensor_data_thread = threading.Thread(target=sensor_worker_thread, args=(SENSOR_REGISTER_ARRAY,))
data_process_thread = threading.Thread(target=processing_thread)
timer_thread = threading.Thread(target=downlink_timer)
serial_thread = threading.Thread(target=receive_serial_data)
geiger_thread = threading.Thread(target=geiger_worker_thread)


# Initialize System 
i2c = busio.I2C(board.SCL, board.SDA)

# Mapped to GPIO pins
#JPL_arm = digitalio.DigitalInOut(board.GP23)
#JPL_arm.direction = digitalio.Direction.OUTPUT
#JPL_disarm = digitalio.DigitalInOut(board.GP16)
#JPL_disarm.direction = digitalio.Direction.OUTPUT
#JPL_On = digitalio.DigitalInOut(board.GP24)
#JPL_On.direction = digitalio.Direction.OUTPUT
#JPL_Off = digitalio.DigitalInOut(board.GP25)
#JPL_Off.direction = digitalio.Direction.OUTPUT

# JPL FLAGS 

JPL_ARM_FLAG = 0
JPL_DISARM_FLAG = 0
JPL_ON_FLAG = 0 
JPL_OFF_FLAG = 0

# JPL designs in progress on laptop not uploaded yet



state_machine = HASP_STATES()
serial_comm = SerialComms()
stop_sensor_data_thread = False
stop_timer_thread = False
stop_serial_thread = False
stop_processing_thread = False



# Place Adafruit I2C object instances here LATER 

# Database Logger
with sql.connect("HaspLogger.db") as HaspLogger:
    cursor = HaspLogger.cursor()
    cursor.execute("DROP TABLE IF EXISTS HASP_Table")

cursor.execute(
    "CREATE TABLE IF NOT EXISTS HASP_Table (SensorID TEXT, DATA TEXT, TIME TEXT,PACKET)"
)

HaspLogger.commit()

# Downlink Logger
with sql.connect("Hasp_Packet.db") as Hasp_Packet:
    cursor = Hasp_Packet.cursor()
    cursor.execute("DROP TABLE IF EXISTS HASP_Table_PACKET")

cursor.execute(
    "CREATE TABLE IF NOT EXISTS HASP_Table_PACKET (SensorID TEXT, PACKET TEXT, TIME TEXT)"
)

Hasp_Packet.commit()

sensor_data_thread.start()
data_process_thread.start()
timer_thread.start()
serial_thread.start()
