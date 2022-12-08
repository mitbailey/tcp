# @file 
# @author Mit Bailey (mitbailey@outlook.com)
# @brief 
# @version See Git tags for version information.
# @date 2022.12.05
# 
# @copyright Copyright (c) 2022
# 
#

import tcpnet
import time
import random

def test_instantiation(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    pts = 0
    net = tcpnet.TCPNet('A %d'%(id), 52040, 'localhost', 52041)
    net.set_corruption_probability(corr_prob)
    net.set_corruption_type(corr_type)
    # net.set_corruption_which(corr_which)
    # print('ID #%d'%(id))
    if net is not None:
        pts += 1

    net.all_stop = True
    del net

    pts += 1
    return pts == 2

def test_single_byte_tx_rx(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    net1.set_corruption_probability(corr_prob)
    net1.set_corruption_type(corr_type)
    net2.set_corruption_probability(corr_prob)
    net2.set_corruption_type(corr_type)
    net1.set_corruption_which(corr_which)
    net2.set_corruption_which(corr_which)
    # print('ID #%d'%(id))

    sendable = b'a'
    net1.send(sendable)

    # print('Waiting for data...')
    if net2 is None:
        print('net2 is none')
    data, _ = net2.pop_data()
    
    # print(data)

    net1.all_stop = True
    net2.all_stop = True
    del net1
    del net2

    return data == sendable

def test_multi_byte_tx_rx(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    net1.set_corruption_probability(corr_prob)
    net1.set_corruption_type(corr_type)
    net2.set_corruption_probability(corr_prob)
    net2.set_corruption_type(corr_type)
    net1.set_corruption_which(corr_which)
    net2.set_corruption_which(corr_which)
    # print('ID #%d'%(id))

    sendable = b'abcdefg'
    net1.send(sendable)

    # print('Waiting for data...')
    data, _ = net2.pop_data()
    
    # print(data)

    net1.all_stop = True
    net2.all_stop = True
    del net1
    del net2

    return data == sendable

def test_multi_byte_delay_tx_rx(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    net1.set_corruption_probability(corr_prob)
    net1.set_corruption_type(corr_type)
    net2.set_corruption_probability(corr_prob)
    net2.set_corruption_type(corr_type)
    net1.set_corruption_which(corr_which)
    net2.set_corruption_which(corr_which)
    # print('ID #%d'%(id))

    sendable = b'abcdefg'
    time.sleep(1)
    net1.send(sendable)

    # print('Waiting for data...')
    data, _ = net2.pop_data()
    
    # print(data)

    net1.all_stop = True
    net2.all_stop = True
    del net1
    del net2

    return data == sendable

def test_single_packet_tx_rx(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    net1.set_corruption_probability(corr_prob)
    net1.set_corruption_type(corr_type)
    net2.set_corruption_probability(corr_prob)
    net2.set_corruption_type(corr_type)
    net1.set_corruption_which(corr_which)
    net2.set_corruption_which(corr_which)
    # print('ID #%d'%(id))

    sendable: bytearray = b''
    # for i in range(tcpnet.TCPNet.MAX_DATA_SIZE * 2):
    #     sendable += random.randint(65, 90).to_bytes(1, 'big')
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'A'
    # for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
    #     sendable += b'Z'
    # print(sendable)

    net1.send(sendable)

    # print('Waiting for data...')
    data, _ = net2.pop_data()

    # print(data)

    net1.all_stop = True
    net2.all_stop = True
    del net1
    del net2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    return data == sendable

def test_multi_packet_tx_rx(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    net1.set_corruption_probability(corr_prob)
    net1.set_corruption_type(corr_type)
    net2.set_corruption_probability(corr_prob)
    net2.set_corruption_type(corr_type)
    net1.set_corruption_which(corr_which)
    net2.set_corruption_which(corr_which)
    # print('ID #%d'%(id))

    sendable: bytearray = b''
    # for i in range(tcpnet.TCPNet.MAX_DATA_SIZE * 2):
        # sendable += random.randint(65, 90).to_bytes(1, 'big')
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'Y'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'Z'
    # print(sendable)

    net1.send(sendable)

    # print('Waiting for data...')
    data, _ = net2.pop_data()
    d, _ = net2.pop_data()
    data += d

    # print(data)

    net1.all_stop = True
    net2.all_stop = True
    del net1
    del net2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    return data == sendable

def test_many_packet_tx_rx(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    net1.set_corruption_probability(corr_prob)
    net1.set_corruption_type(corr_type)
    net2.set_corruption_probability(corr_prob)
    net2.set_corruption_type(corr_type)
    net1.set_corruption_which(corr_which)
    net2.set_corruption_which(corr_which)
    # print('ID #%d'%(id))

    sendable: bytearray = b''
    # for i in range(tcpnet.TCPNet.MAX_DATA_SIZE * 2):
    #     sendable += random.randint(65, 90).to_bytes(1, 'big')
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'D'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'E'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'F'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'G'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'H'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'I'
    # print(sendable)

    net1.send(sendable)

    # print('Waiting for data...')
    data, to = net2.pop_data()
    to = False
    while to is False:
        d, to = net2.pop_data(timeout=2.5)
        if d is not None:
            data += d

    # print(data)

    net1.all_stop = True
    net2.all_stop = True
    del net1
    del net2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    # print(data)
    # print(sendable)

    return data == sendable

def test_many_packet_multi_send_tx_rx(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    net1.set_corruption_probability(corr_prob)
    net1.set_corruption_type(corr_type)
    net2.set_corruption_probability(corr_prob)
    net2.set_corruption_type(corr_type)
    net1.set_corruption_which(corr_which)
    net2.set_corruption_which(corr_which)
    # print('ID #%d'%(id))

    sendable: bytearray = b''
    # for i in range(tcpnet.TCPNet.MAX_DATA_SIZE * 2):
    #     sendable += random.randint(65, 90).to_bytes(1, 'big')
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'D'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'E'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'F'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'G'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'H'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'I'
    # print(sendable)

    net1.send(sendable)

    # print('Waiting for data...')
    data, to = net2.pop_data()
    to = False
    while to is False:
        d, to = net2.pop_data(timeout=2.5)
        if d is not None:
            data += d

    sendableB: bytearray = b''
    # for i in range(tcpnet.TCPNet.MAX_DATA_SIZE * 2):
    #     sendable += random.randint(65, 90).to_bytes(1, 'big')
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendableB += b'J'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendableB += b'K'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendableB += b'L'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendableB += b'M'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendableB += b'N'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendableB += b'O'
    # print(sendable)

    net2.listen(52043, 'localhost', 52042)
    net1.send(sendableB)

    # print('Waiting for data...')
    dataB, to = net2.pop_data()
    to = False
    while to is False:
        d, to = net2.pop_data(timeout=2.5)
        if d is not None:
            dataB += d

    # print(data)

    net1.all_stop = True
    net2.all_stop = True
    del net1
    del net2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    return data == sendable and dataB == sendableB

def test_file_tx_rx(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    fnet1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    fnet2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    fnet1.set_corruption_probability(corr_prob)
    fnet1.set_corruption_type(corr_type)
    fnet2.set_corruption_probability(corr_prob)
    fnet2.set_corruption_type(corr_type)
    fnet1.set_corruption_which(corr_which)
    fnet2.set_corruption_which(corr_which)
    # print('ID #%d'%(id))

    file = open('smpte.bmp', 'rb')
    sendable = file.read()

    fnet1.send(sendable)

    # print('Waiting for data...')
    data, to = fnet2.pop_data()
    to = False
    while to is False:
        d, to = fnet2.pop_data(timeout=2.5)
        if d is not None:
            data += d
        # print(d)

    # print(data)

    fnet1.all_stop = True
    fnet2.all_stop = True
    del fnet1
    del fnet2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    file.close()

    return data == sendable

def test_big_file_tx_rx(corr_prob: float, corr_type: str, corr_which: str):
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    net1.set_corruption_probability(corr_prob)
    net1.set_corruption_type(corr_type)
    net2.set_corruption_probability(corr_prob)
    net2.set_corruption_type(corr_type)
    net1.set_corruption_which(corr_which)
    net2.set_corruption_which(corr_which)
    # print('ID #%d'%(id))

    file = open('card.bmp', 'rb')
    sendable = file.read()

    net1.send(sendable)

    # print('Waiting for data...')
    data, to = net2.pop_data()
    to = False
    while to is False:
        d, to = net2.pop_data(timeout=2.5)
        if d is not None:
            data += d
        # print(d)

    # print(data)

    print(net1.done)
    print(net2.done)

    net1.all_stop = True
    net2.all_stop = True
    del net1
    del net2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    file.close()

    # file = open('rx.bmp', 'wb')
    # file.write(data)
    # file.close()

    return data == sendable

if __name__ == '__main__':
    successes = 0
    failures = 0

    which_list = ['send', 'recv', 'both']
    for w in range(len(which_list)):
        corr_list = ['error', 'loss']
        for i in range(len(corr_list)):
            for ii in range(0, 50, 20): # Corruption Amounts
                corruption_prob = ii/100
                corruption_type = corr_list[i]
                which = which_list[w]

    # corruption_prob = 0.2
    # corruption_type = 'loss'
    # which = 'send'

                max_data_size = 5
                while max_data_size < 992:
                    max_data_size *= 2
                    if max_data_size > 992:
                        max_data_size = 992

                tcpnet.TCPNet.MAX_DATA_SIZE = max_data_size

                print('/////////////////////////////////////////////////')
                print('Max Packet Data, Corruption Prob, Corruption Type')
                print('%4d bytes,      %02.02f%%,          %s'%(max_data_size, corruption_prob*100, corruption_type))
                print('')

                print('Instantiation:')
                if test_instantiation(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

                print('Single Byte:')
                if test_single_byte_tx_rx(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1 
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

                print('Multi-Byte:')
                if test_multi_byte_tx_rx(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1 
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

                print('Multi-Byte Delay:')
                if test_multi_byte_delay_tx_rx(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1 
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

                print('Single-Packet:')
                if test_single_packet_tx_rx(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1 
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

                print('Multi-Packet:')
                if test_multi_packet_tx_rx(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1 
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

                print('Many Packet:')
                if test_many_packet_tx_rx(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1 
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

                print('Many Packet Multi-Send:')
                if test_many_packet_multi_send_tx_rx(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1 
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

                print('File:')
                if test_file_tx_rx(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1 
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

                print('Big File:')
                if test_big_file_tx_rx(corruption_prob, corruption_type, which):
                    print('SUCCESS')
                    successes += 1 
                else:
                    print('FAILURE')
                    failures += 1 
                    input('Press ENTER to continue...')
                print('')

    print('Tests complete (%d passes, %d fails).'%(successes, failures))