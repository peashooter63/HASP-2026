import adafruit_ublox

class I2C_GPS_UBLOX:

    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.ddc = None
        self.ubx = None
        self.gps = None
        self.init = False  


    def INIT_GPS(self):
        try:
            self.ddc = adafruit_ublox.UBloxDDC(self.i2c,address=self.address)
            self.gps = adafruit_ublox.GPS_UBloxI2C(self.ddc)
            self.gps.update()
            #self.gps.set_nmea_output({adafruit_ublox.NMEA_GGA, adafruit_ublox.NMEA_RMC})
            print("Try to set 1 Hz update rate..")
            #self.gps.set_update_rate(1)
            self.init = True
            print("UBLOX GPS INITIALIZED")

        except (ValueError, OSError,RuntimeError) as e:
            print(f"Error: {e}")
            self.init = False
            print("Error setting up UBLOX GPS")



    def GET_GPS_DATA(self):
        self.gps.update()
        if self.init:
            self.gps.update()
            if not self.gps.has_fix:
                print("Don't have fix yet")
                return None

            
            elif self.gps.has_fix:
                s = (f"Lat: {self.gps.latitude:.6f} degrees, "
                    f"Lon: {self.gps.longitude:.6f} degrees, "
                    f"Satellites: {self.gps.satellites}, "
                    f"Altitude: {self.gps.altitude_m} meters, "
                    f"Speed (knots): {self.gps.speed_knots}, "
                    f"Speed (km/h): {self.gps.speed_kmh}, "
                    f"Track angle: {self.gps.track_angle_deg} degrees, "
                    f"Horizontal dilution: {self.gps.horizontal_dilution}, "
                    f"Height geoid: {self.gps.height_geoid} meters")

                return s
        else:
            print("GPS is not ready")
            return None

    @property
    def GPS_INITIALIZED(self):
        return self.init