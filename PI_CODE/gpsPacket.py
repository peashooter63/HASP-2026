nmeaSentence = '$GPGGA,202212.00,3024.7205,N,09110.7264,W,1,06,1.69,00061,M,-025,M,,*51,'
sentenceSize = len(nmeaSentence)

# Get all strings between $ and *
fixData = nmeaSentence[0]
newSentence = (nmeaSentence.strip(fixData)).split("*")[-3:-1]
nmeaFields = (nmeaSentence.strip(fixData)).split("*")[-3:-1]
nmeaParsing = ("".join(nmeaFields)).split(",")

def parseNmea(nmeaSentence):
    # Check the type of NMEA sentence and make a new string to write to buffer for UART port
    if nmeaParsing[0] == "GPGGA" or nmeaParsing[0] == "GNGGA":   #Got to fix this, GNGGA may have difference in structure
        getUTC = nmeaParsing[1]
        getLatitude = nmeaParsing[2]
        getHemisphere1 = nmeaParsing[3]
        getLongitude = nmeaParsing[4]
        getHemisphere2 = nmeaParsing[5]
        mslAltitude = nmeaParsing[9]
        
        nmeaSentenceFinal = getUTC + "," + getLatitude + "," + getHemisphere1 + "," + getLongitude + "," + getHemisphere2 + "," + mslAltitude
        print(f" Here is the new sentence: {nmeaSentenceFinal}")


# Join strings to make list of chars between $ and * for checksum calculation
newString = "".join(newSentence)
nmeaChars = list(newString)
print(nmeaChars)

def calculateChecksum(nmeaChars):

    x = ord(nmeaChars[0])
    charSize = len(nmeaChars)
    # XOR between $ and *
    for i, char in enumerate(nmeaChars[1:charSize],start=1):
        y = ord(nmeaChars[i])
        x ^= y
    
    #Calculated NMEA checksum
    packetChecksum = hex(x)

    nibble1 = (x & 0XF0 ) >> 4
    nibble2 = (x & 0X0F)
    hexNibble1 = (hex(nibble1))[2:]
    hexNibble2 = (hex(nibble2))[2:]

    # Join a hex strings
    hexCalculated = "".join(hexNibble1+hexNibble2)
    print("Calculated Hex Checksum",hexCalculated )

    # Computed ASCII Checksum
    #asciiChecksum = bytes.fromhex(hexNibble1 + hexNibble2).decode("utf-8")  
    #print(f"Computed Ascii Checksum: {asciiChecksum}")

    # Received NMEA checksum

    nmeaSentence = '$GPGGA,202212.00,3024.7205,N,09110.7264,W,1,06,1.69,00061,M,-025,M,,*51,'
    nmeaSize = len(nmeaSentence)
    checksumString = nmeaSentence[nmeaSize-3:nmeaSize-1]  #can change to -4
    hexPayloadChecksum = hex(int(checksumString,16))[2:]

    print("Received Hex Checksum",hexPayloadChecksum )

    # Received ASCII Checksum
    #receivedChecksum = bytes.fromhex(hexPayloadChecksum).decode("utf-8")
    #print(f"Received Ascii Checksum: {receivedChecksum}")

    if hexPayloadChecksum == hexCalculated:
        print("Checksum matches")
    else:
        print("Data is corrupted")
   
def parseNmea(nmeaSentence):
    #After byte array written to serial port and decode
    print("")



    # Call method to assign data to fields 
parseNmea(nmeaParsing)

    # Call method to calculate checksums 
calculateChecksum(nmeaChars)