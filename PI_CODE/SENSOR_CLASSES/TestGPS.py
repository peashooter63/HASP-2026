import adafruit_ublox

import board
import busio
import adafruit_ublox
from adafruit_extended_bus import ExtendedI2C as I2C 

i2c_pi_bus = I2C(3)

def read_ublox_gps(address=0x42, i2c=i2c_pi_bus):
    if i2c is None:
        i2c = busio.I2C(board.SCL, board.SDA)

    ddc = adafruit_ublox.UBloxDDC(i2c, address=address)
    gps = adafruit_ublox.GPS_UBloxI2C(ddc)
    gps.update()

    if not gps.has_fix:
        return None

    return {
        "latitude": gps.latitude,
        "longitude": gps.longitude,
        "altitude_m": gps.altitude_m,
        "satellites": gps.satellites,
        "speed_knots": gps.speed_knots,
        "speed_kmh": gps.speed_kmh,
        "track_angle_deg": gps.track_angle_deg,
        "horizontal_dilution": gps.horizontal_dilution,
        "height_geoid": gps.height_geoid,
    }

# Example
data = read_ublox_gps()
if data is None:
    print("No GPS fix yet")
else:
    print(data)
