# @file 
# @author Mit Bailey (mitbailey@outlook.com)
# @brief 
# @version See Git tags for version information.
# @date 2022.12.05
# 
# @copyright Copyright (c) 2022
# 
#

import random
import tcpnet
import time
import threading
import os

# %% PyQt Imports
from PyQt5 import uic
from PyQt5.Qt import QTextOption
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, Q_ARG, QAbstractItemModel,
                          QFileInfo, qFuzzyCompare, QMetaObject, QModelIndex, QObject, Qt,
                          QThread, QTime, QUrl, QSize, QEvent, QCoreApplication, QFile, QIODevice, QMutex, QWaitCondition)
from PyQt5.QtGui import QColor, qGray, QImage, QPainter, QPalette, QIcon, QKeyEvent, QMouseEvent, QFontDatabase, QFont
from PyQt5.QtMultimedia import (QAbstractVideoBuffer, QMediaContent,
                                QMediaMetaData, QMediaPlayer, QMediaPlaylist, QVideoFrame, QVideoProbe)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QMainWindow, QDoubleSpinBox, QApplication, QComboBox, QDialog, QFileDialog,
                             QFormLayout, QHBoxLayout, QLabel, QListView, QMessageBox, QPushButton,
                             QSizePolicy, QSlider, QStyle, QToolButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPlainTextEdit,
                             QTableWidget, QTableWidgetItem, QSplitter, QAbstractItemView, QStyledItemDelegate, QHeaderView, QFrame, QProgressBar, QCheckBox, QToolTip, QGridLayout, QSpinBox,
                             QLCDNumber, QAbstractSpinBox, QStatusBar, QAction, QScrollArea, QSpacerItem)
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore, QtWidgets

# %%
class TCPTest(QThread):
    SIGNAL_begun = pyqtSignal(int)
    SIGNAL_complete = pyqtSignal(list, list, list, list, list, list, list, list, list, list, list, list, list, list, list, list, list, list)
    SIGNAL_update = pyqtSignal(bool, bool, bool, int, int)

    def __init__(self, parent: QMainWindow):
        super(TCPTest, self).__init__()

        self.net_tx = None
        self.net_rx = None

        self.tests_bools = []
        # self.is_sender = True
        self.filename = 'none'
        # self.tester = RDTFSM()
        self.c_start = 0
        self.c_stop = 61
        self.c_step = 30
        self.c_samples = 1
        self.updater_done = False
        self.running = False
        self.trial = 0

        self.transfer_number = 0
        self.transfer_numbers = []
        self.corr_probs = []
        self.corr_types = []
        self.corr_whichs = []
        self.total_packets_sent_tx = []
        self.total_packets_sent_rx = []
        self.total_packets_recvd_tx = []
        self.total_packets_recvd_rx = []
        self.total_packets_corrupted_tx = []
        self.total_packets_corrupted_rx = []
        self.total_packets_lost_tx = []
        self.total_packets_lost_rx = []
        self.logged_timeouts_tx = []
        self.logged_timeouts_rx = []
        self.logged_winsizes_tx = []
        self.logged_winsizes_rx = []
        self.logged_times_tx = []
        self.logged_times_rx = []

    def __del__(self):
        self.done = True

    def updater(self):
        while not self.updater_done:
            time.sleep(0.01)
            if self.running:
                self.SIGNAL_update.emit(self.net_tx.handshake_complete, self.net_rx.teardown_initiated, self.net_rx.done, self.trial, self.net_rx.curr_ack_num)
                # print(self.net_rx.rx_win_size, self.net_tx.rx_win_size)
                # print(self.net_rx.curr_ack_num)
                # print('Updater running.')

    def run(self):
        # First, delete all of the previous files.
        file_list = os.listdir('.')
        for filename in file_list:
            if '_TCPRX_' in filename:
                if os.path.exists(filename):
                    os.remove(filename)

        self.updater_done = False
        self.updater_tid = threading.Thread(target=self.updater)
        self.updater_tid.start()
        self.trial = 0

        corr_types = ['error', 'loss']
        corr_which = ['send', 'recv']

        print('Transferring %s %d times.'%(self.filename, len(range(self.c_start, self.c_stop, self.c_step)) * self.c_samples * len(corr_types) * len(corr_which)))
        self.SIGNAL_begun.emit(len(range(self.c_start, self.c_stop, self.c_step)) * self.c_samples * len(corr_types) * len(corr_which))

        for i in range(self.c_start, self.c_stop, self.c_step):
            for c_type in corr_types:
                for which in corr_which:
                    for ii in range(self.c_samples):
                        print('Transferring...')
                        # print(i, c_type, which)
                        self.transfer_file(self.filename, i/100, c_type, which)
                        self.trial += 1
        print('Complete.')
        self.updater_done = True
        self.SIGNAL_complete.emit(self.transfer_numbers, self.corr_probs, self.corr_types, self.corr_whichs, self.total_packets_sent_tx, self.total_packets_sent_rx, self.total_packets_recvd_tx, self.total_packets_recvd_rx, self.total_packets_corrupted_tx, self.total_packets_corrupted_rx, self.total_packets_lost_tx, self.total_packets_lost_rx, self.logged_timeouts_tx, self.logged_timeouts_rx, self.logged_winsizes_tx, self.logged_winsizes_rx, self.logged_times_tx, self.logged_times_rx)

        self.transfer_number = 0
        self.transfer_numbers = []
        self.corr_probs = []
        self.corr_types = []
        self.corr_whichs = []
        self.total_packets_sent_tx = []
        self.total_packets_sent_rx = []
        self.total_packets_recvd_tx = []
        self.total_packets_recvd_rx = []
        self.total_packets_corrupted_tx = []
        self.total_packets_corrupted_rx = []
        self.total_packets_lost_tx = []
        self.total_packets_lost_rx = []
        self.logged_timeouts_tx = []
        self.logged_timeouts_rx = []
        self.logged_winsizes_tx = []
        self.logged_winsizes_rx = []
        self.logged_times_tx = []
        self.logged_times_rx = []

    def transfer_file(self, filename: str, corr_prob: float, corr_type: str, corr_which: str):
        id = random.randint(10000, 99999)
        net1 = tcpnet.TCPNet('Sender %d'%(id), 52042, 'localhost', 52043)
        net2 = tcpnet.TCPNet('Receiver %d'%(id), 52043, 'localhost', 52042)
        net1.set_corruption_probability(corr_prob)
        net1.set_corruption_type(corr_type)
        net2.set_corruption_probability(corr_prob)
        net2.set_corruption_type(corr_type)
        net1.set_corruption_which(corr_which)
        net2.set_corruption_which(corr_which)
        self.net_tx = net1
        self.net_rx = net2
        # print('ID #%d'%(id))

        file = open(filename, 'rb')
        sendable = file.read()

        self.running = True
        net1.send(sendable)

        # print('Waiting for data...')
        data, to = net2.pop_data()
        to = False
        tov = 2.5
        while to is False:
            d, to = net2.pop_data(timeout=tov)
            if d is not None:
                data += d
                if data == sendable:
                    tov = 0.25
            # print(d)
        self.running = False

        # Collect the profiling data.
        # print(net1.logged_time)

        self.transfer_number += 1
        self.transfer_numbers.append(self.transfer_number)
        print('corr_prob', corr_prob, corr_prob * 100)
        self.corr_probs.append(corr_prob*100)
        self.corr_types.append(corr_type)
        self.corr_whichs.append(corr_which)
        self.total_packets_sent_tx.append(net1.logged_packets_sent[-1])
        self.total_packets_sent_rx.append(net2.logged_packets_sent[-1])
        self.total_packets_recvd_tx.append(net1.logged_packets_recvd[-1])
        self.total_packets_recvd_rx.append(net2.logged_packets_recvd[-1])
        self.total_packets_corrupted_tx.append(net1.logged_packets_corrupted[-1])
        self.total_packets_corrupted_rx.append(net2.logged_packets_corrupted[-1])
        self.total_packets_lost_tx.append(net1.logged_packets_lost[-1])
        self.total_packets_lost_rx.append(net2.logged_packets_lost[-1])
        self.logged_timeouts_tx.append(net1.logged_timeout)
        self.logged_timeouts_rx.append(net2.logged_timeout)
        self.logged_winsizes_tx.append(net1.logged_winsize)
        self.logged_winsizes_rx.append(net2.logged_winsize)
        self.logged_times_tx.append(net1.logged_time)
        self.logged_times_rx.append(net2.logged_time)

        # print(data)

        # print(net1.done)
        # print(net2.done)

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

        self.net_tx = None
        self.net_rx = None

        # This is where the received data is written to files.
        file = open(filename + '_TCPRX_' + str(time.time_ns()) + '.bmp', 'wb')
        file.write(data)
        file.close()

        return data == sendable