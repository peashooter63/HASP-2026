class PICO_TIME:
    def __init__(self, i2c, address, register):
        self.i2c = i2c
        self.address = address
        self.register = register
        self.bme280 = None
        self.init = False  

    def READ_PICO_TIME(self):
        if self.i2c.try_lock():
            try:
                # Write to the slave
                self.i2c.writeto(self.address, bytes([self.register]))
                buffer = bytearray(4)
                self.i2c.readfrom_into(self.address,buffer)
                return int.from_bytes(buffer[0:4], byteorder='little')

            except Exception as e:
                print(f"An error occured {e}")
                return None

            finally:
            # Always unlock the bus after
                self.i2c.unlock()

