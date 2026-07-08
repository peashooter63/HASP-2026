from gpsPacket import NMEA_PACKET
import simplekml

class Live_GPS_Coordinates:

    @staticmethod
    def GET_POSITION_LIVE(NMEA_SENTENCE): 

        NMEA_FIELDS = NMEA_SENTENCE.split(",")
        print(NMEA_FIELDS)
        Latitude = float(NMEA_FIELDS[2])
        Longitude = float(NMEA_FIELDS[4])
        #Altitude = float(NMEA_FIELDS[5])

        # Format Latitude 
        DEG_WHOLE = int(Latitude/100)
        DEG_DEC = (Latitude - DEG_WHOLE*100)/60 
        if NMEA_FIELDS[1] == "N":
            DEG_LAT = DEG_WHOLE + DEG_DEC
        elif NMEA_FIELDS[1] == "S":
            DEG_LAT =   (DEG_WHOLE + DEG_DEC)


        # Format Latitude 
        DEG_WHOLE = int(Longitude/100)
        DEG_DEC = (Longitude - DEG_WHOLE*100)/60 
        if NMEA_FIELDS[3] == "E":
            DEG_LONG = DEG_WHOLE + DEG_DEC
        elif NMEA_FIELDS[3] == "W":
            DEG_LONG =  (DEG_WHOLE + DEG_DEC)
        
        print("Longitude")
        print(DEG_LONG)

        print("Latitude")
        print(DEG_LAT)
        # Write to a kml file 
        kml = simplekml.Kml()
        kml.newpoint(name="HASP GPS Test Point", coords=[(DEG_LONG,DEG_LAT)])
        kml.save("/home/hasp/Desktop/HASP_KML_TEST.kml")
    

#NMEA_TEST_SENTENCE = '$GPGGA,202212.00,3024.7205,N,09110.7264,W,1,06,1.69,00061,M,-025,M,,*51,'
#GET_POSITION_LIVE(NMEA_TEST_SENTENCE)