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
    MAX_DATA_SIZE = 10
    DEFAULT_TIMEOUT = 0.001

    def __init__(self, ID: str, source_port: int, dest_ip: str, dest_port: int):
        self.whois = ID

        self.sent_syn = False
        self.sent_syn_ack = False
        self.sent_ack = False
        self.got_syn = False
        self.got_syn_ack = False
        self.got_ack = False

        self.done = False
        self.rx_buffer = collections.deque()
        self.rx_tid = threading.Thread(target=self._tcp_rx_thread)

        self.rx_tid_active = False
        self.send_tid_active = False
        self.sent_pkts = 0
        self.send_data = None

        self._setup(source_port, dest_ip, dest_port)

        self.zero_index = 0

        self.dynamic_winsize = True
        self.last_sent_packet = None

    def __del__(self):
        self.done = True
        if self.rx_tid_active:
            self.rx_tid.join()

        # print(self.whois, 'destructor finished.')

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

        self.rx_tid_active = True
        self.rx_tid.start()

        self.ack_required = False

    def send(self, send_data: bytes):
        if self.handshake_complete:
            print(self.whois, 'Cannot begin a new stream while another is active.')
            return False
        self.send_data = send_data
        # self._handshake(0)

    def _handshake(self, flags = 0):
        if self.handshake_complete:
            return

        if flags == 0b0 and not self.handshake_begun:
            self._handshake_syn()
        elif flags == 0b000010: # SYN
            self.handshake_begun = True
            print(self.whois, 'Got SYN.', self.last_rxed_seq_num, self.last_rxed_ack_num)
            self._handshake_syn_ack()
        elif flags == 0b010010: # SYN-ACK
            self.handshake_begun = True
            print(self.whois, 'Got SYN-ACK.', self.last_rxed_seq_num, self.last_rxed_ack_num)
            self._handshake_ack()
        elif flags == 0b010000:
            print(self.whois, 'Got ACK.', self.last_rxed_seq_num, self.last_rxed_ack_num)
            if self.sent_syn_ack:
                self.handshake_complete = True 
                print(self.whois, 'HANDSHAKE COMPLETED', self.last_rxed_seq_num, self.last_rxed_ack_num)

    # CLIENT STEP 1 (Part 1)
    def _handshake_syn(self):
        print(self.whois, 'Sending SYN')
        self.sent_syn = True
        self.curr_seq_num = 1
        self.curr_ack_num = 0
        syn_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b000010)) # 2
        self._udt_send(syn_pkt)

    # SERVER STEP 1 (Part 2)
    def _handshake_syn_ack(self):
        print(self.whois, 'Sending SYN-ACK')
        self.sent_syn_ack = True
        self.curr_seq_num = 2
        self.curr_ack_num = self.last_rxed_seq_num + 1
        self.zero_index = self.curr_ack_num 
        syn_ack_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b010010)) # 18
        self._udt_send(syn_ack_pkt)

    # CLIENT STEP 2 (Part 3)
    def _handshake_ack(self):
        print(self.whois, 'Sending ACK')
        self.sent_ack = True
        self.curr_seq_num = self.last_rxed_ack_num
        self.curr_ack_num = self.last_rxed_seq_num + 1
        self.zero_index = self.curr_seq_num 
        ack_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b010000)) # 16
        self.handshake_complete = True
        # print(self.whois, 'HANDSHAKE COMPLETE')
        self._udt_send(ack_pkt)

    def _teardown(self):
        # 4-way handshake
        print(self.whois, 'TEARDOWN HAS BEEN CALLED!')
        self.udp_sock.shutdown(socket.SHUT_RDWR)
        self.udp_sock.close()
        self.done = True
        pass

    def set_timeout(self, duration):
        self.udp_sock.settimeout(duration)

    def set_winsize(self, size: int):
        self.rx_win_size = size

    def set_dynamic_winsize(self, on: bool = True):
        self.dynamic_winsize = True

    def make_pkt(self, seq_num: int, ack_num: int, data: bytes):
        print(self.whois, 'Making packet with data:', data)
        pkt: bytearray = bytearray(self.make_hdr(seq_num, int.from_bytes(self.bit16sum(data), 'big')) + data)
        return pkt

    def make_hdr(self, seq_num: int, ack_num: int, checksum: bytes = 0x0, flags: int = 0b00000000):
        hdr_len = 0 # Header length = Header length field value x 4 bytes
        urg_ptr = 0

        # print('dest ip', type(self.DEST_IP), self.DEST_IP)
        # print('source port', type(self.SOURCE_PORT), self.SOURCE_PORT)
        # print('dest port', type(self.DEST_PORT), self.DEST_PORT)
        # print('seq num', type(seq_num), seq_num)
        # print('ack num', type(ack_num), ack_num)
        # print('hdr len', type(hdr_len), hdr_len)
        # print('flags', type(flags), flags)
        # print('rx win size', type(self.rx_win_size), self.rx_win_size)
        # print('checksum', type(checksum), checksum)
        # print('urg ptr', type(urg_ptr), urg_ptr)

        header: bytearray = bytearray(self.SOURCE_PORT.to_bytes(2, 'big') + self.DEST_PORT.to_bytes(2, 'big') + seq_num.to_bytes(4, 'big') + ack_num.to_bytes(4, 'big') + hdr_len.to_bytes(1, 'big') + flags.to_bytes(1, 'big') + self.rx_win_size.to_bytes(2, 'big') + checksum.to_bytes(2, 'big') + urg_ptr.to_bytes(2, 'big'))

        return header

    def _udt_send(self, packet):
        self.last_sent_packet = packet
        # print(self.whois, 'UDT_SEND: ', packet)
        self.udp_sock.sendto(packet, (self.DEST_IP, self.DEST_PORT)) #Send the packet (either corrupted or as-intended) to the defined IP/port number 
        return 1

    def _tcp_send_thread(self):
        data = self.send_data        
        sent_pkts = 0
        window = self.rx_win_size
        ack = self.last_rxed_ack_num # Basically the next requested byte.

        if not self.handshake_complete:
            return

        if self.ack_required:
            a_seq = 69696
            a_ack = self.curr_ack_num
            a_pkt = self.make_hdr(a_seq, a_ack, flags=0b010000)
            sent_pkts += self._udt_send(a_pkt)

        if self.send_data is not None:
            # Check for the case where all the bytes of this data have been acknowledged.
            # print('if ack - self.zero_index == len(data)')
            # print('if %d - %d == %d'%(ack, self.zero_index, len(data)))
            if ack - self.zero_index >= len(data):
                self.send_data = None
                # self._teardown()
            else:
                print('\nNEW WINDOW')
                for i in range(window):
                    # TODO: Something here is messed up.
                    seq = ack + (i * TCPNet.MAX_DATA_SIZE)
                    adj_ack = ack - self.zero_index
                    # Create packet
                    print('Making packet from data[%d:%d]:'%(adj_ack + (i * TCPNet.MAX_DATA_SIZE), adj_ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)))
                    print(data[adj_ack + (i * TCPNet.MAX_DATA_SIZE) : adj_ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)])
                    print('\n')
                    pkt = self.make_pkt(seq, ack, data[adj_ack + (i * TCPNet.MAX_DATA_SIZE) : adj_ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)])
                    # Send packet
                    sent_pkts += self._udt_send(pkt)

                    # We've read to the end of the data and its time to stop.
                    if (adj_ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)) >= len(data):
                        break

        self.send_tid_active = False
        self.sent_pkts += sent_pkts

    def _retransmit(self):
        self._udt_send(self.last_sent_packet)

    #Define rdt_rcv() function: Receive packets 
    def _tcp_rx_thread(self):
        while not self.done:
            force_close = False
            timedout = False

            # The main receiving function.
            src_port, dest_port, seq_num, ack_num, hdr_len, flags, rx_win_size, checksum, urg_ptr, data, force_close, timedout = self._tcp_recv()
            
            if not timedout:
                pass
                # print(self.whois, 'just got:', src_port, dest_port, seq_num, ack_num, hdr_len, flags, rx_win_size, checksum, urg_ptr, data)
            
            # Ensures that the program exits when told to.
            if timedout and self.done:
                break
            
            # Accounts for accidental direct loopback (highly unlikely).
            if dest_port == self.DEST_PORT:
                # print(self.whois, 'Ignored!')
                continue
            
            # Deals with timeouts via retransmission.
            if timedout:
                if self.last_sent_packet is not None:
                    self._retransmit()

            if seq_num is not None and ack_num is not None:
                self.last_rxed_seq_num = seq_num
                self.last_rxed_ack_num = ack_num
                if flags == 0: 
                    self.ack_required = True

            # There's data and the sequence number is what we are looking for.
            if data is not None and data != b'':
                if seq_num == self.curr_ack_num:
                    print('APPENDING')
                    print('data:', data)
                    print('TO THE DEQUE')
                    self.rx_buffer.appendleft(data)
                    # print('CURR_ACK_NUM += LEN(DATA) + 1', self.curr_ack_num, len(data))
                    self.curr_ack_num += len(data)

            if not self.handshake_complete: # Handshake is incomplete.
                if self.send_data is not None: # We are the sender.
                    if flags is None: # We listened but heard nothing and are the sender.
                        self._handshake(0) # Fire the initial handshake.
                    else:
                        self._handshake(flags)
                elif flags is not None and flags > 0: # We are the receiver (or not ready to send) and got a flag.
                    self._handshake(flags)

                # if flags is None:
                #     flags = 0
                # self._handshake(flags)

            elif not self.send_tid_active:
                self.send_tid_active = True
                self.send_tid = threading.Thread(target=self._tcp_send_thread)
                self.send_tid.start()


            # TODO: Handle TCP things

        self.rx_tid_active = False

    def pop_data(self, block: bool = True, timeout: int = 0):
        start = time.time_ns()
        to = False

        print('rx_buffer:', self.rx_buffer)
        if self.rx_buffer:
            print('rx_buffer:', self.rx_buffer)
            return self.rx_buffer.pop(), to
        elif not block:
            print('rx_buffer:', self.rx_buffer)
            return None, to

        while not self.done:
            if (timeout > 0) and (time.time_ns() - start >= 1e9 * timeout):
                print('TIMED OUT!')
                to = True
                return None, to
            if self.rx_buffer:
                print('rx_buffer:', self.rx_buffer)
                return self.rx_buffer.pop(), to
            time.sleep(0.0001)

    def data_empty(self):
        if len(self.rx_buffer) == 0:
            return True
        return False

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
            # print(data)
            # print(rcv_pkt[20:])
            # print(rcv_pkt[15:])

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
