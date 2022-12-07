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
    print('Single Byte TX & RX:', end='\n')
    
    net1 = tcpnet.TCPNet('Sender', 52042, 'localhost', 52043)
    net2 = tcpnet.TCPNet('Receiver', 52043, 'localhost', 52042)

    net1.send(b'c')

    print('Waiting for data...')
    data = net2.pop_data()
    print(data)


if __name__ == '__main__':
    print('Instantiation:', end=' ')
    if test_instantiation():
        print('SUCCESS')
    else:
        print('FAILURE')
        exit(1)
    time.sleep(2)
    print('\n\n\n')

    test_single_byte_tx_rx()

    print('Complete.')