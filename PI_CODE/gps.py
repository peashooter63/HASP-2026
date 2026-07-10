import threading
import time
import adafruit_ublox
from adafruit_extended_bus import ExtendedI2C as I2C

class GPS_UBLOX:
    def __init__(self, i2c_bus, debug_ubx=False):
        self.i2c = i2c_bus
        self.debug_ubx = debug_ubx
        self.ddc = adafruit_ublox.UBloxDDC(self.i2c)
        self.ubx = adafruit_ublox.UBloxUBX(self.ddc, debug=self.debug_ubx)
        self.gps = adafruit_ublox.GPS_UBloxI2C(self.ddc)

        self.latitude = None
        self.longitude = None
        self.altitude_m = None

        #print("Attempting to configure NMEA output (GGA and RMC only)...")
        self.ubx.set_nmea_output({adafruit_ublox.NMEA_GGA, adafruit_ublox.NMEA_RMC})

        #print("Attempting to set 1 Hz update rate...")
        self.ubx.set_update_rate(1)
        
        self.stop_gps_thread = False
        self.gps_thread = threading.Thread(target=self.gps_worker_thread)

    def gps_worker_thread(self):
        global stop_gps_thread
        last_print = time.monotonic()

        while True:
            if self.stop_gps_thread:
                break

            try:
                current = time.monotonic()
                if current - last_print >= 1.0:
                    self.gps.update()
                    last_print = current
                    if not self.gps.has_fix:
                        # Try again if we don't have a fix yet.
                        #print("Waiting for fix...")
                        self.latitude = None
                        self.longitude = None
                        self.altitude_m = None
                        continue

                    self.latitude = self.gps.latitude
                    self.longitude = self.gps.longitude
                    self.altitude_m = self.gps.altitude_m

                    # if self.gps.satellites is not None:
                    #     print(f"# satellites: {self.gps.satellites}")
                    # if self.gps.altitude_m is not None:
                    #     print(f"Altitude: {self.gps.altitude_m} meters")
                    # if self.gps.speed_knots is not None:
                    #     print(f"Speed: {self.gps.speed_knots} knots")
                    # if self.gps.speed_kmh is not None:
                    #     print(f"Speed: {self.gps.speed_kmh} km/h")
                    # if self.gps.track_angle_deg is not None:
                    #     print(f"Track angle: {self.gps.track_angle_deg} degrees")
                    # if self.gps.horizontal_dilution is not None:
                    #     print(f"Horizontal dilution: {self.gps.horizontal_dilution}")
                    # if self.gps.height_geoid is not None:
                    #     print(f"Height geoid: {self.gps.height_geoid} meters")
                    # if self.gps.datetime is not None:
                    #     print(f"Timestamp: {self.gps.datetime}")
                else:
                    pass
            except Exception as e:
                print(f"Error occurred: {e}")
                continue

    def start_gps_thread(self):
        self.gps_thread.start()

    def stop_gps_thread(self):
        self.stop_gps_thread = True
        self.gps_thread.join()
        print("Exiting...")

    def get_gps_data(self):
        return self.latitude, self.longitude, self.altitude_m

i2c_bus = I2C(3)
GPS_UBLOX_instance = GPS_UBLOX(i2c_bus, debug_ubx=False)

while True:
    try:
        GPS_UBLOX_instance.start_gps_thread()
        while True:
            time.sleep(1)
            latitude, longitude, altitude = GPS_UBLOX_instance.get_gps_data()
            print(f"Lat: {latitude}, Lon: {longitude}, Alt: {altitude}")
            print("=" * 40)
    except KeyboardInterrupt:
        GPS_UBLOX_instance.stop_gps_thread()
        print("Exiting...")
        break
    except Exception as e:
        print(f"Error occurred: {e}")
        continue
