seq_num: int = 4294967295
ack_num: int = 0
checksum: bytes = 0x0
flags: bytes = 0b11001100
hdr_len = 240 # Header length = Header length field value x 4 bytes
urg_ptr = 0
SOURCE_PORT = 65535
DEST_PORT = 0
rx_win_size = 65535

header: bytearray = bytearray(SOURCE_PORT.to_bytes(2, 'big') + DEST_PORT.to_bytes(2, 'big') + seq_num.to_bytes(4, 'big') + ack_num.to_bytes(4, 'big') + hdr_len.to_bytes(1, 'big') + flags.to_bytes(1, 'big') + rx_win_size.to_bytes(2, 'big') + checksum.to_bytes(2, 'big') + urg_ptr.to_bytes(2, 'big'))

print(header[0:])
print(header[0:2])
print(header[2:4])
print(header[4:8])
print(header[8:12])
print(header[12:13])
print(header[13:14])
print(header[14:16])
print(header[16:18])
print(header[18:20])