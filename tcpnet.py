# @file 
# @author Mit Bailey (mitbailey@outlook.com)
# @brief 
# @version See Git tags for version information.
# @date 2022.12.05
# 
# @copyright Copyright (c) 2022
# 
#

# Imports
import socket
import random
import time
import collections
import threading

class TCPNet:
    MAX_DATA_SIZE = 1000
    DEFAULT_TIMEOUT = 2

    def __init__(self, source_port: int, dest_ip: str, dest_port: int):
        self.whois = 'RECV'

        self.done = False
        self.rx_buffer = collections.deque()
        self.rx_tid = threading.Thread(target=self._tcp_rx_thread)
        self.send_tid = threading.Thread(target=self._tcp_send_thread)
        self.rx_tid_started = False
        self.send_tid_active = False
        self.sent_pkts = 0
        self.send_data = None

        self._setup(source_port, dest_ip, dest_port)

    def __del__(self):
        self.done = True
        if self.rx_tid_started:
            self.rx_tid.join()


    def _setup(self, source_port: int, dest_ip: str, dest_port: int):
        self.sent_pkts = 0

        self.DEST_IP = dest_ip #Set socket IP based on provided IP arguement (i.e., 'localhost')
        self.DEST_PORT = dest_port #Set outbound port based on provided arguement 
        self.SOURCE_PORT = source_port

        self.udp_sock = None #Declare UDP socket, set to None
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Define UDP socket with socket library
        self.udp_sock.settimeout(TCPNet.DEFAULT_TIMEOUT) #Set UDP socket timeout to 1 ms 
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.udp_sock.bind((self.DEST_IP, self.SOURCE_PORT)) #Bind to UDP socket/listen on inbound port

        self.rx_win_size = 1
        self.curr_ack_num = 0
        self.curr_seq_num = 0
        self.last_rxed_ack_num = 0
        self.last_rxed_seq_num = 0
        self.handshake_begun = False
        self.handshake_complete = False

        self.rx_tid_started = True
        self.rx_tid.start()

    def send(self, send_data: bytes):
        self.whois = 'SEND'
        if self.handshake_complete:
            print('Cannot begin a new stream while another is active.')
            return False
        self.send_data = send_data

    def _handshake(self):
        self.handshake_begun = True
        self._handshake_syn()

    # CLIENT STEP 1 (Part 1)
    def _handshake_syn(self):
        print(self.whois, '_handshake_syn')
        self.curr_seq_num = 1
        self.curr_ack_num = 0
        syn_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b000010)) # 2
        self._udt_send(syn_pkt)

    # SERVER STEP 1 (Part 2)
    def _handshake_syn_ack(self):
        print(self.whois, '_handshake_syn_ack')
        self.curr_seq_num = 2
        self.curr_ack_num = self.last_rxed_seq_num + 1
        syn_ack_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b010010)) # 18
        self._udt_send(syn_ack_pkt)

    # CLIENT STEP 2 (Part 3)
    def _handshake_ack(self):
        print(self.whois, '_handshake_ack')
        self.curr_seq_num = self.last_rxed_ack_num
        self.curr_ack_num = self.last_rxed_seq_num + 1
        ack_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b010000)) # 16
        self.handshake_begun = False
        self.handshake_complete = True
        self._udt_send(ack_pkt)

    def _teardown(self):
        # 4-way handshake

        self.udp_sock.shutdown(socket.SHUT_RDWR)
        self.udp_sock.close()

        pass

    def set_timeout(self, duration):
        self.udp_sock.settimeout(duration)

    def make_pkt(self, seq_num: int, ack_num: int, data: bytes):
        pkt: bytearray = bytearray(self.make_hdr(seq_num, self.bit16sum(data)) + data)
        return pkt

    def make_hdr(self, seq_num: int, ack_num: int, checksum: bytes = 0x0, flags: int = 0b00000000):
        hdr_len = 0 # Header length = Header length field value x 4 bytes
        urg_ptr = 0

        # print(type(self.DEST_IP))
        # print(type(self.SOURCE_PORT))
        # print(type(self.DEST_PORT))
        # print(type(seq_num))
        # print(type(ack_num))
        # print(type(hdr_len))
        # print(type(flags))
        # print(type(self.rx_win_size))
        # print(type(checksum))
        # print(type(urg_ptr))

        header: bytearray = bytearray(self.SOURCE_PORT.to_bytes(2, 'big') + self.DEST_PORT.to_bytes(2, 'big') + seq_num.to_bytes(4, 'big') + ack_num.to_bytes(4, 'big') + hdr_len.to_bytes(1, 'big') + flags.to_bytes(1, 'big') + self.rx_win_size.to_bytes(2, 'big') + checksum.to_bytes(2, 'big') + urg_ptr.to_bytes(2, 'big'))

        return header

    def _udt_send(self, packet):
        self.udp_sock.sendto(packet, (self.DEST_IP, self.DEST_PORT)) #Send the packet (either corrupted or as-intended) to the defined IP/port number 
        return 1

    def _tcp_send_thread(self):
        data = self.send_data        
        sent_pkts = 0
        window = self.rx_win_size
        ack = self.last_rxed_ack_num # Basically the next requested byte.

        if not self.handshake_complete:
            return

        # Check for the case where all the bytes of this data have been acknowledged.
        if ack == len(data):
            self._teardown()
        else:
            for i in range(window):
                seq = ack + (i * TCPNet.MAX_DATA_SIZE)
                # Create packet
                pkt = self.make_pkt(seq, ack, data[ack + (i * TCPNet.MAX_DATA_SIZE) : ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)])
                # Send packet
                sent_pkts += self._udt_send(pkt)

                # We've read to the end of the data and its time to stop.
                if (ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)) >= len(data):
                    break

        self.send_tid_active = False
        self.sent_pkts += sent_pkts

    #Define rdt_rcv() function: Receive packets 
    def _tcp_rx_thread(self):
        while not self.done:
            force_close = False
            timedout = False

            src_port, dest_port, seq_num, ack_num, hdr_len, flags, rx_win_size, checksum, urg_ptr, data, force_close, timedout = self._tcp_recv()
            if dest_port == self.DEST_PORT:
                print(self.whois, 'Ignored!')
                continue
            print(self.whois, src_port, dest_port, seq_num, ack_num, flags, self.handshake_complete)

            if seq_num is not None:
                self.last_rxed_seq_num = seq_num
            if ack_num is not None:
                self.last_rxed_ack_num = ack_num

            if not self.handshake_complete:
                if not self.handshake_begun:
                    self._handshake()
                elif flags == 0b000010: # SYN
                    print(self.whois, 'Got SYN.')
                    self._handshake_syn_ack()
                elif flags == 0b010010: # SYN-ACK
                    print(self.whois, 'Got SYN-ACK.')
                    self._handshake_ack()
                elif flags == 0b010000:
                    print(self.whois, 'Got ACK.')
                    self.handshake_begun = False
                    self.handshake_complete = True 

            elif not self.send_tid_active and self.send_data is not None:
                self.send_tid_active = True
                self.send_tid.start()

            # There's data and the sequence number is what we are looking for.
            if data is not None:
                if seq_num == self.curr_ack_num:
                    self.rx_buffer.appendleft(data)

            # TODO: Handle TCP things

    def pop_data(self, block: bool = True):
        if self.rx_buffer:
            return self.rx_buffer.pop()
        elif not block:
            return None

        while not self.done:
            if self.rx_buffer:
                return self.rx_buffer.pop()
            time.sleep(0.0001)

    def _tcp_recv(self):
        src_port = None
        dest_port = None
        seq_num = None
        ack_num = None
        hdr_len = None
        flags = None
        rx_win_size = None
        checksum = None
        urg_ptr = None
        data = None

        force_close = False
        timedout = False
        
        try:
            rcv_pkt, ret_addr = self.udp_sock.recvfrom(1024)
        except socket.error as e:
            if str(e) == '[WinError 10054] An existing connection was forcibly closed by the remote host':
                force_close = True
                pass
            elif str(e) == 'timed out':
                timedout = True
                pass
            else:
                raise e

        if not force_close and not timedout:
            src_port = int.from_bytes(rcv_pkt[0:2], 'big')
            dest_port = int.from_bytes(rcv_pkt[2:4], 'big')
            seq_num = int.from_bytes(rcv_pkt[4:8], 'big')
            ack_num = int.from_bytes(rcv_pkt[8:12], 'big')
            hdr_len = int.from_bytes(rcv_pkt[12:13], 'big')
            flags = int.from_bytes(rcv_pkt[13:14], 'big')
            rx_win_size = int.from_bytes(rcv_pkt[14:16], 'big')
            checksum = int.from_bytes(rcv_pkt[16:18], 'big')
            urg_ptr = int.from_bytes(rcv_pkt[18:20], 'big')
            data = rcv_pkt[20:]

        return src_port, dest_port, seq_num, ack_num, hdr_len, flags, rx_win_size, checksum, urg_ptr, data, force_close, timedout

    #Define is_valid() function: Checks to ensure checksum/data is valid. If checksum/data is valid, returns a True flag. If checksum/data is invalid, returns a False flag. 
    def is_valid(self, packet):
        if packet == None or packet == '': #If packet is empty, return False flag
            return False

        if packet[3:5] != self.bit16sum(packet[6:]): #If checksums between sender/receiver do not match, return False flag
            return False

        # if int.from_bytes(packet[0:2], 'big') != 0 and int.from_bytes(packet[0:2], 'big') != 1: #If packet data betwen sender/receiver does not match, return a False flag
        #     return False

        return True  #Otherwise, if the packet is valid return a True flag

    #Define get_seq_num() function: Extracts the sequence number from the packet and returns that value 
    def get_seq_num(self, packet):
        return int.from_bytes(packet[0:2], 'big')

    #Define get_data() function: Extracts the data from a packet and returns that value (i.e., the data in bytes)
    def get_data(self, packet):
        return packet[6:]

    #Define bit16sum() function: Computes the packet checksum based on the checksum algorithm learned in class. 
    def bit16sum(self, data)->bytearray:
        checksum = 0 #Initialize checksum variable, set equal to zero 
        for i, byte in enumerate(data): #For pyte in data
            if (i % 2 == 0): #If i modulus 2 == 0, then sll data by eight bits 
                bit16 = data[i] << 8
                if (i+1 < len(data)): #If the next byte is less than the length of the data, then compute addition w/ carryover 
                    bit16 = (data[i] << 8) | (data[i+1]) 
            checksum = (checksum + bit16) & 0xFFFF #Compute 1s complement (addition result AND'd with 0xFFFF mask) to yield final checksum 
        return checksum.to_bytes(2, 'big')
