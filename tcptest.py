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
    SIGNAL_complete = pyqtSignal()
    SIGNAL_update = pyqtSignal(bool, bool, int, int)

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

    def __del__(self):
        self.done = True

    def updater(self):
        while not self.updater_done:
            time.sleep(0.01)
            if self.running:
                self.SIGNAL_update.emit(self.net_tx.handshake_complete, self.net_rx.teardown_initiated, self.trial, self.net_rx.curr_ack_num)
                # print(self.net_rx.rx_win_size, self.net_tx.rx_win_size)
                # print(self.net_rx.curr_ack_num)
                # print('Updater running.')

    def run(self):
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
                        self.transfer_file(self.filename, i/100, c_type, which)
                        self.trial += 1
        print('Complete.')
        self.updater_done = True
        self.SIGNAL_complete.emit()

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
        while to is False:
            d, to = net2.pop_data(timeout=2.5)
            if d is not None:
                data += d
            # print(d)
        self.running = False

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

        return data == sendable