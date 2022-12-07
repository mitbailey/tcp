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
    pts = 0
    net = tcpnet.TCPNet('A', 52040, 'localhost', 52041)
    if net is not None:
        pts += 1

    net.done = True
    del net

    pts += 1
    return pts == 2

def test_single_byte_tx_rx():
    net1 = tcpnet.TCPNet('Sender', 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver', 52043, 'localhost', 52042)

    sendable = b'a'
    net1.send(sendable)

    print('Waiting for data...')
    data = net2.pop_data()
    
    print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    return data == sendable

def test_multi_byte_tx_rx():
    net1 = tcpnet.TCPNet('Sender', 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver', 52043, 'localhost', 52042)

    sendable = b'abcdefg'
    net1.send(sendable)

    print('Waiting for data...')
    data = net2.pop_data()
    
    print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    return data == sendable

def test_single_packet_tx_rx():
    net1 = tcpnet.TCPNet('Sender', 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver', 52043, 'localhost', 52042)

    sendable: bytearray = b''
    # for i in range(tcpnet.TCPNet.MAX_DATA_SIZE * 2):
    #     sendable += random.randint(65, 90).to_bytes(1, 'big')
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'A'
    # for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
    #     sendable += b'Z'
    print(sendable)

    net1.send(sendable)

    print('Waiting for data...')
    data = net2.pop_data()
    # data += net2.pop_data()
    # data += net2.pop_data()

    print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    print('\n\n\nDATA')
    print(data)
    print('\n\n\nSENDABLE')
    print(sendable)

    return data == sendable

def test_multi_packet_tx_rx():
    net1 = tcpnet.TCPNet('Sender', 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver', 52043, 'localhost', 52042)

    sendable: bytearray = b''
    # for i in range(tcpnet.TCPNet.MAX_DATA_SIZE * 2):
    #     sendable += random.randint(65, 90).to_bytes(1, 'big')
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'Y'
    for i in range(tcpnet.TCPNet.MAX_DATA_SIZE):
        sendable += b'Z'
    print(sendable)

    net1.send(sendable)

    print('Waiting for data...')
    data = net2.pop_data()
    data += net2.pop_data()
    # data += net2.pop_data()

    print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    print('\n\n\nDATA')
    print(data)
    print('\n\n\nSENDABLE')
    print(sendable)

    return data == sendable

def test_many_packet_tx_rx():
    net1 = tcpnet.TCPNet('Sender', 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver', 52043, 'localhost', 52042)

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
    print(sendable)

    net1.send(sendable)

    print('Waiting for data...')
    data = net2.pop_data()
    data += net2.pop_data()
    data += net2.pop_data()
    data += net2.pop_data()
    data += net2.pop_data()
    # data += net2.pop_data()

    print(data)

    net1.done = True
    net2.done = True
    del net1
    del net2

    print('\n\n\nDATA')
    print(data)
    print('\n\n\nSENDABLE')
    print(sendable)

    return data == sendable

if __name__ == '__main__':
    print('Instantiation:', end=' ')
    if test_instantiation():
        print('SUCCESS')
    else:
        print('FAILURE')
        exit(1)
    print('\n\n')

    print('Single Byte:', end=' ')
    if test_single_byte_tx_rx():
        print('SUCCESS')
    else:
        print('FAILURE')

    print('Multi-Byte:', end=' ')
    if test_multi_byte_tx_rx():
        print('SUCCESS')
    else:
        print('FAILURE')

    print('Single-Packet:', end=' ')
    if test_single_packet_tx_rx():
        print('SUCCESS')
    else:
        print('FAILURE')

    print('Multi-Packet:', end=' ')
    if test_multi_packet_tx_rx():
        print('SUCCESS')
    else:
        print('FAILURE')

    print('Many Packet:', end=' ')
    if test_many_packet_tx_rx():
        print('SUCCESS')
    else:
        print('FAILURE')

    print('Tests complete.')