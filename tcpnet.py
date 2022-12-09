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

# %%

class TCPNet():
    MAX_DATA_SIZE = 992
    DEFAULT_TIMEOUT = 0.001
    TYPICAL_RTT = 0.125
    TYPICAL_BETA = 0.15

    def __init__(self, ID: str, source_port: int, dest_ip: str, dest_port: int):
        self.CORR_PROB = 0
        self.CORR_TYPE = 'none' # none, loss, error, both
        self.CORR_WHICH = 'none'

        self.whois = ID

        self._setup(source_port, dest_ip, dest_port)

    def __del__(self):
        self.done = True
        if self.rx_tid_active:
            self.rx_tid.join()

        # print(self.whois, 'destructor finished.')

    def _setup(self, source_port: int, dest_ip: str, dest_port: int):
        # self.log = None
        self.logged_time = []
        self.logged_packets_sent = []
        self.logged_packets_recvd = []
        self.logged_packets_corrupted = []
        self.logged_packets_lost = []
        self.logged_timeout = []
        self.logged_winsize = []

        self.packets_sent = 0
        self.packets_recvd = 0
        self.packets_corrupted = 0
        self.packets_lost = 0

        self.teardown_initiated = False
        self.consecutive_nacks = 0

        self.estimated_rtt = TCPNet.TYPICAL_RTT
        self.timeout_interval = TCPNet.DEFAULT_TIMEOUT
        self.dev_rtt = TCPNet.TYPICAL_BETA

        self.sent_syn = False
        self.sent_syn_ack = False
        self.sent_ack = False
        self.got_syn = False
        self.got_syn_ack = False
        self.got_ack = False

        self.done = False
        self.all_stop = False
        self.rx_buffer = collections.deque()

        self.rx_tid = None
        self.rx_tid_active = False
        self.send_tid_active = False
        self.sent_pkts = 0
        
        self.send_data = None
        
        self.zero_index = 0

        self.dynamic_winsize = True
        self.last_sent_packet = None

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

        self.rx_tid = threading.Thread(target=self._tcp_rx_thread)
        self.rx_tid_active = True
        self.rx_tid.start()

        self.ack_required = False

    def listen(self, source_port: int, dest_ip: str, dest_port: int):
        if self.done:
            self._setup(source_port, dest_ip, dest_port)
        else:
            print(self.whois, 'Already setup to listen!')

    def send(self, send_data: bytes):
        if self.handshake_complete:
            print(self.whois, 'Cannot begin a new stream while another is active.')
            return False

        # If done, then we already sent something and then finished. Things must be reset.
        if self.done:
            self._setup(self.SOURCE_PORT, self.DEST_IP, self.DEST_PORT)

        # self.log_initial()
        self.send_data = send_data

    def _handshake(self, flags = 0):
        if self.handshake_complete:
            return

        if flags == 0b0 and not self.handshake_begun:
            self._handshake_syn()
        elif flags == 0b000010: # SYN
            self.handshake_begun = True
            # print(self.whois, 'Got SYN.', self.last_rxed_seq_num, self.last_rxed_ack_num)
            self._handshake_syn_ack()
        elif flags == 0b010010: # SYN-ACK
            self.handshake_begun = True
            # print(self.whois, 'Got SYN-ACK.', self.last_rxed_seq_num, self.last_rxed_ack_num)
            self._handshake_ack()
        elif flags == 0b010000:
            # print(self.whois, 'Got ACK.', self.last_rxed_seq_num, self.last_rxed_ack_num)
            if self.sent_syn_ack:
                self.handshake_complete = True 
                # print(self.whois, 'HANDSHAKE COMPLETED', self.last_rxed_seq_num, self.last_rxed_ack_num)

    # CLIENT STEP 1 (Part 1)
    def _handshake_syn(self):
        # print(self.whois, 'Sending SYN')
        self.sent_syn = True
        self.curr_seq_num = 1
        self.curr_ack_num = 0
        syn_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b000010, checksum=0)) # 2
        self._udt_send(syn_pkt)

    # SERVER STEP 1 (Part 2)
    def _handshake_syn_ack(self):
        # print(self.whois, 'Sending SYN-ACK')
        self.sent_syn_ack = True
        self.curr_seq_num = 2
        self.curr_ack_num = self.last_rxed_seq_num + 1
        self.zero_index = self.curr_ack_num 
        syn_ack_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b010010, checksum=0)) # 18
        self._udt_send(syn_ack_pkt)

    # CLIENT STEP 2 (Part 3)
    def _handshake_ack(self):
        # print(self.whois, 'Sending ACK')
        self.sent_ack = True
        self.curr_seq_num = self.last_rxed_ack_num
        self.curr_ack_num = self.last_rxed_seq_num + 1
        self.zero_index = self.curr_seq_num 
        ack_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b010000, checksum=0)) # 16
        self.handshake_complete = True
        # print(self.whois, 'HANDSHAKE COMPLETE', self.curr_seq_num, self.curr_ack_num)
        self._udt_send(ack_pkt)

    def _teardown(self):
        self._teardown_fin()

    def _teardown_fin(self):
        # 4-way handshake
        # print(self.whois, 'TEARDOWN HAS BEEN CALLED!')
        self.teardown_initiated = True

        fin_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b000001, checksum=0))
        self._udt_send(fin_pkt)

        # self.done = True

    def _teardown_ack(self):
        # print(self.whois, 'TEARDOWN HAS BEEN REQUESTED!')

        ack_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b010000, checksum=0))
        
        self._udt_send(ack_pkt)

        if not self.teardown_initiated:
            # If teardown initiated, then we must be the initiator and have already sent a FIN.
            fin_pkt: bytearray = bytearray(self.make_hdr(seq_num=self.curr_seq_num, ack_num=self.curr_ack_num, flags=0b000001, checksum=0))
            
            self._udt_send(fin_pkt)

        self.teardown_initiated = True
        # self._shutdown()
        self.done = True
        # self.log_final()
        # print('self.done?', self.done)

    def _shutdown(self):
        # print(self.whois, 'SHUTTING DOWN')
        # self.done = True

    # def _terminate(self):
        self.udp_sock.shutdown(socket.SHUT_RDWR)
        self.udp_sock.close()

        self.handshake_begun = False
        self.handshake_complete = False


        # print(self.whois, 'CONNECTION TERMINATED')

    def set_corruption_type(self, c_type: str):
        self.CORR_TYPE = c_type

    def set_corruption_probability(self, c_prob: float):
        self.CORR_PROB = c_prob

    def set_corruption_which(self, which: str):
        self.CORR_WHICH = which

    def set_timeout(self, duration):
        self.udp_sock.settimeout(duration)

    def set_winsize(self, size: int):
        self.rx_win_size = size

    def set_dynamic_winsize(self, on: bool = True):
        self.dynamic_winsize = True

    def make_pkt(self, seq_num: int, ack_num: int, data: bytes):
        # print(self.whois, 'Making packet with data:', data)
        pkt: bytearray = bytearray(self.make_hdr(seq_num, ack_num, int.from_bytes(self.bit16sum(data), 'big')) + data)
        return pkt

    def make_hdr(self, seq_num: int, ack_num: int, checksum: int, flags: int = 0b00000000):
        hdr_len = 0 # Header length = Header length field value x 4 bytes
        urg_ptr = 0

        header: bytearray = bytearray(self.SOURCE_PORT.to_bytes(2, 'big') + self.DEST_PORT.to_bytes(2, 'big') + seq_num.to_bytes(4, 'big') + ack_num.to_bytes(4, 'big') + hdr_len.to_bytes(1, 'big') + flags.to_bytes(1, 'big') + self.rx_win_size.to_bytes(2, 'big') + checksum.to_bytes(2, 'big') + urg_ptr.to_bytes(2, 'big') + time.time_ns().to_bytes(8, 'big'))

        return header

    def _udt_send(self, packet):
        # self.log_update()

        if self.done:
            return 0

        self.last_sent_packet = packet

        if (len(packet) > 35) and (((self.CORR_WHICH == 'send') and (self.send_data is not None)) or ((self.CORR_WHICH == 'recv') and (self.send_data is None))):
            if random.random() < self.CORR_PROB:
                if self.CORR_TYPE == 'loss':
                    # print(self.whois, 'CORRUPTION: Packet lost!', self.last_rxed_seq_num, self.last_rxed_ack_num)
                    self.packets_lost += 1
                    self.packets_sent += 1
                    return 1
                if self.CORR_TYPE == 'error':
                    # print(self.whois, 'CORRUPTION: Packet error!', self.last_rxed_seq_num, self.last_rxed_ack_num, self.curr_seq_num, self.curr_ack_num)
                    self.packets_corrupted += 1
                    packet[35] = 42

        # print(self.whois, 'UDT_SEND: ', packet)
        # print(self.whois, self.last_rxed_seq_num, self.last_rxed_ack_num, self.curr_seq_num, self.curr_ack_num)
        # print(self.whois, 'SENDING:', packet[28:])

        try:
            self.udp_sock.sendto(packet, (self.DEST_IP, self.DEST_PORT)) #Send the packet (either corrupted or as-intended) to the defined IP/port number 
        except Exception as e:
            print(str(e))
            print('self.done', self.done)
            print('self.all_stop', self.all_stop)
            print('The socket is', self.udp_sock, 'and is type', type(self.udp_sock))
            input('Press ENTER to continue...')
        self.packets_sent += 1
        return 1

    def _handle_winsize(self, timedout):
        ack = self.last_rxed_ack_num
        seq = self.curr_seq_num

        # This is where we reset win_size to 1/2 due to packet loss.
        if ack != seq + self.MAX_DATA_SIZE:
            self.consecutive_nacks += 1
        else:
            self.consecutive_nacks = 0
        if timedout:
            self.consecutive_nacks = 0
            self.rx_win_size = 1
        elif self.consecutive_nacks > 3:
            self.consecutive_nacks = 0
            self.rx_win_size = int(self.rx_win_size / 2)
            if self.rx_win_size < 1:
                self.rx_win_size = 1
        else:
            self.rx_win_size += 1

    def _tcp_send_thread(self):
        data = self.send_data        
        sent_pkts = 0
        ack = self.last_rxed_ack_num # Basically the next requested byte.
        seq = self.curr_seq_num

        window = self.rx_win_size

        if not self.handshake_complete:
            return

        if self.ack_required and self.send_data is None:
            a_seq = 42424
            a_ack = self.curr_ack_num
            a_pkt = self.make_hdr(a_seq, a_ack, checksum=0, flags=0b010000)
            sent_pkts += self._udt_send(a_pkt)

        if self.send_data is not None:
            # Check for the case where all the bytes of this data have been acknowledged.
            # print('if ack - self.zero_index == len(data)')
            # print('if %d - %d == %d'%(ack, self.zero_index, len(data)))
            if ack - self.zero_index >= len(data):
                # print(self.whois, 'Calling teardown because %d >= %d.'%(ack-self.zero_index, len(data)))
                self.send_data = None
                self._teardown()
            else:
                # print('\nNEW WINDOW')
                for i in range(window):
                    seq = ack + (i * TCPNet.MAX_DATA_SIZE)
                    adj_ack = ack - self.zero_index
                    # Create packet
                    # print('Making packet from data[%d:%d]:'%(adj_ack + (i * TCPNet.MAX_DATA_SIZE), adj_ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)))
                    # print(data[adj_ack + (i * TCPNet.MAX_DATA_SIZE) : adj_ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)])
                    # print('\n')
                    pkt = self.make_pkt(seq, ack, data[adj_ack + (i * TCPNet.MAX_DATA_SIZE) : adj_ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)])
                    # Send packet
                    sent_pkts += self._udt_send(pkt)

                    # We've read to the end of the data and its time to stop.
                    if (adj_ack + TCPNet.MAX_DATA_SIZE + (i * TCPNet.MAX_DATA_SIZE)) >= len(data):
                        break

        self.curr_seq_num = seq
        self.send_tid_active = False
        self.sent_pkts += sent_pkts

    def _retransmit(self, timedout):
        ret_pkt = self.last_sent_packet

        # if timedout:
        #     self.rx_win_size = 1
        #     ret_pkt[14:16] = self.rx_win_size.to_bytes(2, 'big')
        self._udt_send(ret_pkt)


    #Define rdt_rcv() function: Receive packets 
    def _tcp_rx_thread(self):
        while not self.done and not self.all_stop:
            force_close = False
            timedout = False

            # Update our log lists.
            self.logged_time.append(time.time_ns())
            self.logged_packets_sent.append(self.packets_sent)
            self.logged_packets_recvd.append(self.packets_recvd)
            self.logged_packets_corrupted.append(self.packets_corrupted)
            self.logged_packets_lost.append(self.packets_lost)
            self.logged_timeout.append(self.timeout_interval)
            self.logged_winsize.append(self.rx_win_size)

            # The main receiving function.
            src_port, dest_port, seq_num, ack_num, hdr_len, flags, rx_win_size, checksum, urg_ptr, timestamp, data, force_close, timedout = self._tcp_recv()
            # print(self.whois, 'RECEIVED:', data)

            if not timedout:
                self.packets_recvd += 1
                pass
                # print(self.whois, 'just got:', src_port, dest_port, seq_num, ack_num, hdr_len, flags, rx_win_size, checksum, urg_ptr, data)
            
            # Ensures that the program exits when told to.
            # if self.done:
            if timedout and self.done:
                # print('Shutting down - recv')
                self._shutdown()
                break
            
            # Accounts for accidental direct loopback (highly unlikely).
            if dest_port == self.DEST_PORT: # Somehow not for us.
                # print(self.whois, 'Ignored!')
                continue
            
            # Calculates the updated timeout based on RTT.
            if timestamp is not None:
                sample_rtt = (time.time_ns() - timestamp) / 1e9
                self.estimated_rtt = (1 - TCPNet.TYPICAL_RTT) * self.estimated_rtt + TCPNet.TYPICAL_RTT * sample_rtt
                self.dev_rtt = (1 - TCPNet.TYPICAL_BETA) * self.dev_rtt + TCPNet.TYPICAL_BETA * abs(sample_rtt - self.estimated_rtt)
                self.timeout_interval = self.estimated_rtt + 4 * self.dev_rtt
                # print('sample_rtt:', sample_rtt)
                # print('TO: %f s'%(self.timeout_interval))
                self.set_timeout(self.timeout_interval)

            if rx_win_size is not None:
                self.rx_win_size = rx_win_size
            
            if (flags == 0):
                self._handle_winsize(timedout)

            # Deals with timeouts via retransmission.
            # if (flags == 0) and (data is not None):
                # print(checksum, int.from_bytes(self.bit16sum(data), 'big'))
            if (flags == 0) and (data is not None) and (timedout or checksum != int.from_bytes(self.bit16sum(data), 'big')):
                # print('bedfdfs')
                if self.last_sent_packet is not None:
                    self._retransmit(timedout)
                if checksum != self.bit16sum(data):
                    continue

            # TODO: Read the timestamp, compare to now, and adjust the timeout accordingly.

            if flags is not None and flags == 1:
                # Received FIN!
                self._teardown_ack()

            if seq_num is not None and ack_num is not None:
                self.last_rxed_seq_num = seq_num
                self.last_rxed_ack_num = ack_num
                if flags == 0: 
                    self.ack_required = True

            # There's data and the sequence number is what we are looking for.
            if data is not None and data != b'':
                if seq_num == self.curr_ack_num:
                    # print('APPENDING')
                    # print('data:', data)
                    # print('TO THE DEQUE')
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

            elif not self.send_tid_active:
                self.send_tid_active = True
                self.send_tid = threading.Thread(target=self._tcp_send_thread)
                self.send_tid.start()


            # TODO: Handle TCP things

        self.rx_tid_active = False
        self._shutdown()

    def pop_data(self, block: bool = True, timeout: int = 0):
        start = time.time_ns()
        to = False

        # print('rx_buffer:', self.rx_buffer)
        if self.rx_buffer:
            # print('rx_buffer:', self.rx_buffer)
            return self.rx_buffer.pop(), to
        elif not block:
            # print('rx_buffer:', self.rx_buffer)
            return None, to

        while not self.all_stop:
            if (timeout > 0) and (time.time_ns() - start >= 1e9 * timeout):
                # print('TIMED OUT!')
                to = True
                return None, to
            if self.rx_buffer:
                # print('rx_buffer:', self.rx_buffer)
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
        timestamp = None
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
            timestamp = int.from_bytes(rcv_pkt[20:28], 'big')
            data = rcv_pkt[28:]
            # print(data)
            # print(rcv_pkt[20:])
            # print(rcv_pkt[15:])

        return src_port, dest_port, seq_num, ack_num, hdr_len, flags, rx_win_size, checksum, urg_ptr, timestamp, data, force_close, timedout

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

    # def log_initial(self):
    #     whois = self.whois.replace(' ', '_')
    #     self.log = open('log_' + whois + '.txt', 'w')
    #     # self.log.write(self.whois, self.CORR_PROB, self.CORR_TYPE, self.CORR_WHICH)

    # def log_update(self):
    #     self.log.write(self.whois)
    #     self.log.write(', ')
    #     self.log.write(str(self.CORR_PROB))
    #     # + ', ' + self.CORR_TYPE + ', ' + self.CORR_WHICH + ', ' + self.packets_sent + ', ' + self.packets_recvd + ', ' + self.packets_corrupted + ', ' + self.packets_lost + ', ' + self.rx_win_size + ', ' + self.timeout_interval)

    # def log_final(self):
    #     self.log.close()
