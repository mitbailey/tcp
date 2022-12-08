seq_num: int = 4294967295
ack_num: int = 1002
checksum: bytes = 0x0
flags: bytes = 0b11001100
hdr_len = 240 # Header length = Header length field value x 4 bytes
urg_ptr = 0
SOURCE_PORT = 65535
DEST_PORT = 0
rx_win_size = 65535

import time

header: bytearray = bytearray(SOURCE_PORT.to_bytes(2, 'big') + DEST_PORT.to_bytes(2, 'big') + seq_num.to_bytes(4, 'big') + ack_num.to_bytes(4, 'big') + hdr_len.to_bytes(1, 'big') + flags.to_bytes(1, 'big') + rx_win_size.to_bytes(2, 'big') + checksum.to_bytes(2, 'big') + urg_ptr.to_bytes(2, 'big') + time.time_ns().to_bytes(8, 'big'))

print(time.time_ns())

print(header[0:])
print(header[0:2])
print(header[2:4])
print(int.from_bytes(header[4:8], 'big'))
print(int.from_bytes(header[8:12], 'big'))
print(header[12:13])
print(header[13:14])
print(header[14:16])
print(header[16:18])
print(header[18:20])
print(int.from_bytes(header[20:28], 'big'))
# print(len(header))
# print(header[28])
print(time.perf_counter_ns())