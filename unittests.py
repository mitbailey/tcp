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

def test_instantiation():
    id = random.randint(10000, 99999)
    pts = 0
    net = tcpnet.TCPNet('A %d'%(id), 52040, 'localhost', 52041)
    print('ID #%d'%(id))
    if net is not None:
        pts += 1

    net.done = True
    del net

    pts += 1
    return pts == 2

def test_single_byte_tx_rx():
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    print('ID #%d'%(id))

    sendable = b'a'
    net1.send(sendable)

    # print('Waiting for data...')
    data, _ = net2.pop_data()
    
    print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    return data == sendable

def test_multi_byte_tx_rx():
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    print('ID #%d'%(id))

    sendable = b'abcdefg'
    net1.send(sendable)

    # print('Waiting for data...')
    data, _ = net2.pop_data()
    
    print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    return data == sendable

def test_multi_byte_delay_tx_rx():
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    print('ID #%d'%(id))

    sendable = b'abcdefg'
    time.sleep(1)
    net1.send(sendable)

    # print('Waiting for data...')
    data, _ = net2.pop_data()
    
    # print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    return data == sendable

def test_single_packet_tx_rx():
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    print('ID #%d'%(id))

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

    net1.done = True
    net2.done = True
    del net1
    del net2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    return data == sendable

def test_multi_packet_tx_rx():
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    print('ID #%d'%(id))

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

    net1.done = True
    net2.done = True
    del net1
    del net2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    return data == sendable

def test_many_packet_tx_rx():
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    print('ID #%d'%(id))

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
        d, to = net2.pop_data()
        if d is not None:
            data += d

    # print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    return data == sendable

def test_file_tx_rx():
    id = random.randint(10000, 99999)
    fnet1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    fnet2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    print('ID #%d'%(id))

    file = open('smpte.bmp', 'rb')
    sendable = file.read()

    fnet1.send(sendable)

    # print('Waiting for data...')
    data, to = fnet2.pop_data()
    to = False
    while to is False:
        d, to = fnet2.pop_data()
        if d is not None:
            data += d
        # print(d)

    # print(data)

    fnet1.done = True
    fnet2.done = True
    del fnet1
    del fnet2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    file.close()

    return data == sendable

def test_big_file_tx_rx():
    id = random.randint(10000, 99999)
    net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
    print('ID #%d'%(id))

    file = open('card.bmp', 'rb')
    sendable = file.read()

    net1.send(sendable)

    # print('Waiting for data...')
    data, to = net2.pop_data()
    to = False
    while to is False:
        d, to = net2.pop_data()
        if d is not None:
            data += d
        # print(d)

    # print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    # print('\n\n\nDATA')
    # print(data)
    # print('\n\n\nSENDABLE')
    # print(sendable)

    file.close()

    return data == sendable

if __name__ == '__main__':
    successes = 0
    failures = 0
    max_data_size = 5
    while max_data_size < 1000:
        max_data_size *= 2
        if max_data_size > 1000:
            max_data_size = 1000

        tcpnet.TCPNet.MAX_DATA_SIZE = max_data_size

        print('Maximum Data Size =', max_data_size, 'bytes\n')

        print('Instantiation:')
        if test_instantiation():
            print('SUCCESS')
            successes += 1
        else:
            print('FAILURE')
            failures += 1 
        print('')

        print('Single Byte:')
        if test_single_byte_tx_rx():
            print('SUCCESS')
            successes += 1 
        else:
            print('FAILURE')
            failures += 1 
        print('')

        print('Multi-Byte:')
        if test_multi_byte_tx_rx():
            print('SUCCESS')
            successes += 1 
        else:
            print('FAILURE')
            failures += 1 
        print('')

        print('Multi-Byte Delay:')
        if test_multi_byte_delay_tx_rx():
            print('SUCCESS')
            successes += 1 
        else:
            print('FAILURE')
            failures += 1 
        print('')

        print('Single-Packet:')
        if test_single_packet_tx_rx():
            print('SUCCESS')
            successes += 1 
        else:
            print('FAILURE')
            failures += 1 
        print('')

        print('Multi-Packet:')
        if test_multi_packet_tx_rx():
            print('SUCCESS')
            successes += 1 
        else:
            print('FAILURE')
            failures += 1 
        print('')

        print('Many Packet:')
        if test_many_packet_tx_rx():
            print('SUCCESS')
            successes += 1 
        else:
            print('FAILURE')
            failures += 1 
        print('')

        print('File:')
        if test_file_tx_rx():
            print('SUCCESS')
            successes += 1 
        else:
            print('FAILURE')
            failures += 1 
        print('')

    print('Big File:')
    if test_big_file_tx_rx():
        print('SUCCESS')
        successes += 1 
    else:
        print('FAILURE')
        failures += 1 
    print('')

    print('Tests complete (%d passes, %d fails).'%(successes, failures))