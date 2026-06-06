#pragma pack(push, 1)
struct CesarsPacket {
    char ID_1; 
    char ID_2;
    uint8_t Packet_ID;
    uint8_t Length;
    uint16_t Checksum;
    uint32_t Timestamp;
    uint8_t Data[64];

};
#pragma pack(pop)

