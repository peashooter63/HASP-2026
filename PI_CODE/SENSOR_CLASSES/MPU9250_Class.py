# IMPORTS 
import busio
import board
import struct
from robohat_mpu9250.mpu9250 import MPU9250
from robohat_mpu9250.mpu6500 import MPU6500
from robohat_mpu9250.ak8963 import AK8963
import os.path
from pathlib import Path
import json

# Initialize I2C (using default SCL and SDA pins)
i2c = busio.I2C(board.SCL, board.SDA)

# PICO ADDRESSES 
ADDRESS_1 = 0X2C
#ADDRESS_2 = ??? 

# MPU9250 REGISTERS 
REGISTER_8 = 0X08
REGISTER_9 = 0X09

class MPU9250_DATA: # Later add a data parameter
   
    @staticmethod
    def READ_MPU9250_1():
        if i2c.try_lock():
            try:
                # Write to the slave
                i2c.writeto(ADDRESS_1, bytes([REGISTER_8]))
                buffer = bytearray(24)
                i2c.readfrom_into(ADDRESS_1,buffer)
                return MPU9250_DATA.DECODE_MPU9250_1(buffer)

            except Exception as e:
                print(f"An error occured {e}")
                return None

            finally:
            # Always unlock the bus after
                i2c.unlock()


    @staticmethod
    def READ_MPU9250_2():
        if i2c.try_lock():
            try:
                # Write to the slave
                i2c.writeto(ADDRESS_1, bytes([REGISTER_9]))
                buffer = bytearray(20)
                i2c.readfrom_into(ADDRESS_1,buffer)
                return MPU9250_DATA.DECODE_MPU9250_2(buffer)

            except Exception as e:
                print(f"An error occured {e}")
                return None

            finally:
            # Always unlock the bus after
                i2c.unlock()


    @staticmethod
    def DECODE_MPU9250_1(data):
        acceleration_x = struct.unpack_from('<f',data,0)[0]
        acceleration_y = struct.unpack_from('<f',data,4)[0]
        acceleration_z = struct.unpack_from('<f',data,8)[0]
        gyroscope_x = struct.unpack_from('<f',data,12)[0]
        gyroscope_y = struct.unpack_from('<f',data,16)[0]
        gyroscope_z = struct.unpack_from('<f',data,20)[0]
        return (f"{acceleration_x:.2f}" + ":" + f"{acceleration_y:.2f}" + ":" + f"{acceleration_z:.2f}" + ":" + 
                f"{gyroscope_x:.2f}" + ":" + f"{gyroscope_y:.2f}" + ":" + f"{gyroscope_z:.2f}")

    @staticmethod
    def DECODE_MPU9250_2(data):
        rotation_x = struct.unpack_from('<f',data,0)[0]
        rotation_y = struct.unpack_from('<f',data,4)[0]
        rotation_z = struct.unpack_from('<f',data,8)[0]
        time       = struct.unpack_from('f',data,12)[0]
        return f"{rotation_x:.2f}" + ":" + f"{rotation_y:.2f}" + ":" + f"{rotation_z:.2f}" 
    

class MPU9250_I2C_DEVICE:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.mpu6500 = None
        self.ak = None
        self.mpu9250 = None
        self.init = False  
        self.mpu9250_calibration_ready = False 

    def SETUP_MPU9250(self):
        try:
            
            self.mpu6500 = MPU6500(self.i2c, self.address)
            self.ak = AK8963(self.i2c)
            self.mpu9250 = MPU9250(self.mpu6500,self.ak)
            self.mpu9250.read_whoami()
            self.init = True
            print("MPU9250 Device setup!")

        except Exception as e:
            print(f"Error: {e}")
            self.init = False
            print("MPU9250 Device setup failed!")


    def READ_MPU9250_DEVICE(self):
        if self.init:
            try:
                acceleration_x, acceleration_y, acceleration_z = self.mpu9250.read_acceleration()
                magnetometer_x,magnetometer_y,magnetometer_z = self.mpu9250.read_magnetic()
                gyroscope_x,gyroscope_y,gyroscope_z = self.mpu9250.read_gyro()


                return (f"{acceleration_x:.2f}" + ":" + f"{acceleration_y:.2f}" + ":" + f"{acceleration_z:.2f}"
                + ":" + f"{gyroscope_x:.2f}" + ":" + f"{gyroscope_y:.2f}" + ":" + f"{gyroscope_z:.2f}"
                + ":" + f"{magnetometer_x:.2f}" + ":" + f"{magnetometer_y:.2f}" + ":" + f"{magnetometer_z:.2f}")
            
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("MPU9250 data not ready")
            return None
    
    @property
    def MPU9250_INITIALIZED(self):
        return self.init
    
        
    def MPU9250_CALIBRATION(self):
        pass

        # #calibration_mpu9250_file = Path(calibration_mpu9250_file)
        # if not calibration_mpu9250_file.exists():
        #     offset, scale = self.ak.calibrate(count = 256, delay=200)      # Offsets for a 1 minute calibration. Change offset and scale with caution. 
        #     self.ak = AK8963(offset,scale)
        #     print("Begin Calibrating PI MPU9250 now!")
        #     mpu9250_calibration_data = {"offset": offset,"scale": scale}
        #     with open("mpu9250_calibration_data.json",'w') as calibration_mpu9250_file: 
        #         json.dump(mpu9250_calibration_data,calibration_mpu9250_file)   
        #         self.calibration_ready = True 
        # else:
        #     if calibration_mpu9250_file.exists(): 
        #         with open("mpu9250_calibration_data","r") as calibration_mpu9250_file:
        #             data = json.load(calibration_mpu9250_file)
        # calibration_mpu9250_file = Path("mpu9250_calibration_data.json")

        # try:

        #     # Existing calibration found
        #     if calibration_mpu9250_file.exists():

        #         with calibration_mpu9250_file.open("r") as f:
        #             data = json.load(f)

        #         offset = tuple(data["offset"])
        #         scale = tuple(data["scale"])
        #         self.ak = AK8963(self.i2c,offset=offset,scale=scale)
        #         self.calibration_ready = True
        #         print("Loading MPU9250 calibration")

        #     # If no existing calibration, begin calibration sequence 
        #     else:

        #         print("No MPU9250 calibration file found.")
        #         print("Start mpu9250 magnometer calibration...")
        #         self.ak = AK8963(self.i2c)
        #         offset, scale = self.ak.calibrate(count=256,delay=200)              # 1 Minute Calibration. Edit with caution. 
        #         calibration_data = {"offset": offset,"scale": scale}

        #         with calibration_mpu9250_file.open("w") as f:
        #             json.dump(calibration_data, f)
        #         self.ak = AK8963(self.i2c,offset=offset,scale=scale)
        #         self.calibration_ready = True

        #         print("Calibration complete and saved.")

        # except Exception as e:

        #     print(f"MPU9250 calibration error: {e}")
        #     self.calibration_ready = False
    
 
