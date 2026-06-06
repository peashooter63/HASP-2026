import busio
import board
import struct
i2c = busio.I2C(board.SCL, board.SDA)
from robohat_mpu9250.mpu9250 import MPU9250
from robohat_mpu9250.mpu6500 import MPU6500
from robohat_mpu9250.ak8963 import AK8963

ADDRESS_1 = 0X2C
REGISTER_4 = 0X04
REGISTER_5 = 0X05

class MPU9250_DATA: # Later add a data parameter
   
    @staticmethod
    def READ_MPU9250_1():
        if i2c.try_lock():
            try:
                # Write to the slave
                i2c.writeto(ADDRESS_1, bytes([REGISTER_4]))
                buffer = bytearray(24)
                i2c.readfrom_into(ADDRESS_1,buffer)

            except Exception as e:
                print(f"An error occured {e}")

            finally:
            # Always unlock the bus after
                i2c.unlock()

        return MPU9250_DATA.DECODE_MPU9250_1(buffer)

    @staticmethod
    def READ_MPU9250_2():
        if i2c.try_lock():
            try:
                # Write to the slave
                i2c.writeto(ADDRESS_1, bytes([REGISTER_5]))
                buffer = bytearray(20)
                i2c.readfrom_into(ADDRESS_1,buffer)

            except Exception as e:
                print(f"An error occured {e}")

            finally:
            # Always unlock the bus after
                i2c.unlock()

        return MPU9250_DATA.DECODE_MPU9250_2(buffer)



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

    def INIT_MPU9250(self):
        try:
            
            self.mpu6500 = MPU6500(self.i2c, self.address)
            self.ak = AK8963(self.i2c)
            self.mpu9250 = MPU9250(self.mpu6500,self.ak)
            self.mpu9250.read_whoami()
            self.init = True
            print("MPU9250 Device initialized!")

        except (ValueError, OSError) as e:
            print(f"Error: {e}")
            self.init = False


    def READ_MPU9250_DEVICE(self):
        if self.init:
            try:
                acceleration_x, acceleration_y, acceleration_z = self.mpu9250.read_acceleration()
                magnetometer_x,magnetometer_y,magnetometer_z = self.mpu9250.read_magnetic()
                gyroscope_x,gyroscope_y,gyroscope_z = self.mpu9250.read_gyro()


                return (f"{acceleration_x:.2f}" + ":" + f"{acceleration_y:.2f}" + ":" + f"{acceleration_z:.2f}"
                + ":" + f"{gyroscope_x:.2f}" + ":" + f"{gyroscope_y:.2f}" + ":" + f"{gyroscope_z:.2f}"
                + ":" + f"{magnetometer_x:.2f}" + ":" + f"{magnetometer_y:.2f}" + ":" + f"{magnetometer_z:.2f}")
            
            except (ValueError, OSError) as e:
                print(f"Error: {e}")
        else:
            print("Device not ready")
            return None
        