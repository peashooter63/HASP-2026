class NMEA_PACKET:

    def Parse_NMEA(NMEA_Sentence):
            
            NMEA_FIELDS = NMEA_Sentence.split(",")
            NMEA_FIX = NMEA_FIELDS.index("$GPGGA")
            
            #NMEA_Sentence.strip("$GPGGA")
        # Check the type of NMEA sentence 
            if NMEA_Sentence.startswith("$GPGGA") or NMEA_Sentence.startswith("GNGGA"):   #Got to fix this, GNGGA may have difference in structure
                
                UTC = NMEA_FIELDS[1]
                if "S" in NMEA_FIELDS:
                    SOUTH_INDEX = NMEA_FIELDS.index("S")
                    Latitude = "-" + f"{NMEA_FIELDS[SOUTH_INDEX-1]}"
                    LATITUDE_DIR = NMEA_FIELDS[SOUTH_INDEX]
                elif "N" in NMEA_FIELDS:
                    NORTH_INDEX = NMEA_FIELDS.index("N")
                    Latitude = f"{NMEA_FIELDS[NORTH_INDEX-1]}"
                    LATITUDE_DIR = NMEA_FIELDS[NORTH_INDEX]

                if "W" in NMEA_FIELDS:
                    WEST_INDEX = NMEA_FIELDS.index("W")
                    Longitude = "-" + f"{NMEA_FIELDS[WEST_INDEX-1]}"
                    LONGITUDE_DIR = NMEA_FIELDS[WEST_INDEX]
                else:
                    EAST_INDEX = NMEA_FIELDS.index("E")
                    Longitude = f"{NMEA_FIELDS[EAST_INDEX-1]}"
                    LONGITUDE_DIR = NMEA_FIELDS[EAST_INDEX]

                Altitude = NMEA_FIELDS[8]
            

            NMEA_STRING = f"{UTC}" + "," + f"{LATITUDE_DIR}" + "," + f"{Latitude}" + "," + f"{LONGITUDE_DIR}" + "," + f"{Longitude}" + "," + f"{Altitude}" 
            print("NMEA_STRING")
            print(NMEA_STRING)
            return NMEA_STRING


    def Calculate_Checksum(NMEA_SENTENCE):
        x = 0
        NMEA_FIX = NMEA_SENTENCE.find('$')
        checksum_index = NMEA_SENTENCE.find('*')
        received_checksum = NMEA_SENTENCE[checksum_index+1:checksum_index+3]
        print("RECEIVED CHECKSUM")
        print(received_checksum)
        # XOR between $ and *
        print("Test my checksum prints for the XOR") 
        print(NMEA_SENTENCE[NMEA_FIX+1:checksum_index])
        for i, char in enumerate(NMEA_SENTENCE[NMEA_FIX+1:checksum_index]):
            #print(char, hex(ord(char))) 
            x ^= ord(char)
            
        Calculated_Checksum = f"{x:02X}"                             

        Nibble_1 = (x & 0XF0 ) >> 4
        Nibble_2 = (x & 0X0F)

        Hex_Nibble1 = (hex(Nibble_1))[2:]
        Hex_Nibble2 = (hex(Nibble_2))[2:]
        hex_XOR = "".join(Hex_Nibble1+Hex_Nibble2)
        print("Calculated Checksum XOR")
        print(hex_XOR)

        if hex_XOR == received_checksum:
            print("Checksum matches")
        else:
            print("NMEA Data is corrupted")
   


# Test sentence  (WIll USE A .STRIP ON THIS.)
NMEA_TEST_SENTENCE = '$GPGGA,202212.00,3024.7205,N,09110.7264,W,1,06,1.69,00061,M,-025,M,,*51,'



