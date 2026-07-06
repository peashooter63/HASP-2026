import struct

class DS18_DATA(): 
    @staticmethod
    def DECODE_DS18(data):
        temperature1 = struct.unpack_from('<f',data,0)[0]  
        temperature2 = struct.unpack_from('<f',data,4)[0]  
        temperature3 = struct.unpack_from('<f',data,8)[0]  
        temperature4 = struct.unpack_from('<f',data,12)[0]  
        temperature5 = struct.unpack_from('<f',data,16)[0]  
        temperature6 = struct.unpack_from('<f',data,20)[0]  
        temperature7 = struct.unpack_from('<f',data,24)[0]  
        time     = int.from_bytes(data[28:32], byteorder='little')
        return f"{temperature1:.2f}" + ":" + f"{temperature2:.2f}" + ":" + f"{temperature3:.2f}" + ":" + f"{temperature4:.2f}:" + f"{temperature5:.2f}:" + f"{temperature6:.2f}:" + f"{temperature7:.2f}:" + f"{time}"

class PICO_DS18_I2C_DEVICE:
    def __init__(self, i2c, address, register):
        self.i2c = i2c
        self.address = address
        self.register = register

    def READ_DS18(self):
        if self.i2c.try_lock():
            try:
                self.i2c.writeto(self.address, bytes([self.register]))
                buffer = bytearray(32)
                self.i2c.readfrom_into(self.address,buffer)
                return DS18_DATA.DECODE_DS18(buffer)

            except Exception as e:
                print(f"An error occured {e}")
                return None

            finally:
                self.i2c.unlock()

