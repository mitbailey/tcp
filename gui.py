# @file 
# @author Mit Bailey (mitbailey@outlook.com)
# @brief 
# @version See Git tags for version information.
# @date 2022.12.05
# 
# @copyright Copyright (c) 2022
# 
#

import os
import sys

try:
    exeDir = sys._MEIPASS
except Exception:
    exeDir = os.getcwd()

if getattr(sys, 'frozen', False):
    appDir = os.path.dirname(sys.executable)
elif __file__:
    appDir = os.path.dirname(__file__)

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

#%% More Standard Imports
import configparser as confp
from email.charset import QP
from time import sleep
import weakref
from io import TextIOWrapper
import math as m
import numpy as np
import datetime as dt
from functools import partial

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# %% Custom Imports
import webbrowser
import tcptest

# %%

class GUI_Main(QMainWindow):
    def __init__(self, application, uiresource=None):
        self.application: QApplication = application
        self._startup_args = self.application.arguments()
        super(GUI_Main, self).__init__()
        uic.loadUi(uiresource, self)

        self.test = tcptest.TCPTest(self.application)
        self.test.filename = self.transfer_file_line_edit.text()
        self.test.SIGNAL_complete.connect(self.complete)
        self.test.SIGNAL_update.connect(self.update)
        self.test.SIGNAL_begun.connect(self.begun)

        self.make_connections()
        self.update_s4()
        self.show()
        self.set_transfer_file()

    def make_connections(self):
        self.transfer_file_line_edit.textChanged.connect(self.set_transfer_file)
        self.begin_button.clicked.connect(self.begin_transfer)
        self.start_spinbox.valueChanged.connect(self.update_s4)
        self.stop_spinbox.valueChanged.connect(self.update_s4)
        self.step_spinbox.valueChanged.connect(self.update_s4)
        self.samples_spinbox.valueChanged.connect(self.update_s4)

    def update_s4(self):
        self.test.c_start = self.start_spinbox.value()
        self.test.c_stop = self.stop_spinbox.value()
        self.test.c_step = self.step_spinbox.value()
        self.test.c_samples = self.samples_spinbox.value()

    def set_transfer_file(self):
        self.filename = self.transfer_file_line_edit.text()
        self.test.filename = self.filename
        if os.path.exists(self.filename):
            self.filesize = os.path.getsize(self.filename)
            # self.subsubprogress_progress_bar.setMaximum(filesize)

    def begin_transfer(self):
        self.test.tests_bools = [self.data_error_checkbox.isChecked(), self.data_loss_checkbox.isChecked(), self.ack_error_checkbox.isChecked(), self.ack_loss_checkbox.isChecked()]
        self.test.start()
   
    def complete(self, transfer_numbers, corr_probs, corr_types, corr_which, total_packets_sent_tx, total_packets_sent_rx, total_packets_recvd_tx, total_packets_recvd_rx, total_packets_corrupted_tx, total_packets_corrupted_rx, total_packets_lost_tx, total_packets_lost_rx, logged_timeouts_tx, logged_timeouts_rx, logged_winsizes_tx, logged_winsizes_rx, logged_times_tx, logged_times_rx):
        self.state_label.setText('N/A')
        self.file_progress_bar.setValue(0)
        self.process_progress_bar.setValue(0)
        self.produce_graphs(transfer_numbers, corr_probs, corr_types, corr_which, total_packets_sent_tx, total_packets_sent_rx, total_packets_recvd_tx, total_packets_recvd_rx, total_packets_corrupted_tx, total_packets_corrupted_rx, total_packets_lost_tx, total_packets_lost_rx, logged_timeouts_tx, logged_timeouts_rx, logged_winsizes_tx, logged_winsizes_rx, logged_times_tx, logged_times_rx)

    def begun(self, trials):
        self.trials = trials

    def update(self, handshake_complete, teardown_initiated, done, trial, byte):
        # print('byte, filesize:', byte, self.filesize)
        # print('prog:', int((byte/self.filesize)*100))
        # print('prog:', byte/self.filesize)

        if done:
            self.state_label.setText('IDLE')
        elif teardown_initiated:
            self.state_label.setText('TEARDOWN')
        elif not handshake_complete:
            self.state_label.setText('HANDSHAKE')
        elif handshake_complete:
            self.state_label.setText('DATA TRANSFER')
        else:
            self.state_label.setText('UNKNOWN')

        self.file_progress_bar.setValue(int((byte/self.filesize)*100))
        self.process_progress_bar.setValue(int( ((trial/self.trials) + ((byte/self.filesize)/self.trials))   *100))

    def produce_graphs(self, transfer_numbers, corr_probs, corr_types, corr_which, total_packets_sent_tx, total_packets_sent_rx, total_packets_recvd_tx, total_packets_recvd_rx, total_packets_corrupted_tx, total_packets_corrupted_rx, total_packets_lost_tx, total_packets_lost_rx, logged_timeouts_tx, logged_timeouts_rx, logged_winsizes_tx, logged_winsizes_rx, logged_times_tx, logged_times_rx):
        # Total Packets Sent, Total Packets Recvd vs Corruption   
        # axA2 = axA1.twinx()

        # axA2.set_ylabel('Line Corruption (%)', color='r')

        # Data Error - de
        # Data Loss  - dl
        # Ack Error  - ae
        # Ack Loss   - al
        
        # RECEIVER PLOTS
        figA = plt.figure()
        axA1 = plt.axes()

        axA1.axes.set_title('Packets Sent and Received with Data Packet Bit Error')
        axA1.set_xlabel('Corruption')
        axA1.set_ylabel('Total Packets')
        de_corr_probs = [x for i, x in enumerate(corr_probs) if corr_types[i] == 'error' and corr_which[i] == 'send']
        de_total_packets_sent = [x for i, x in enumerate(total_packets_sent_tx) if corr_types[i] == 'error' and corr_which[i] == 'send']
        de_total_packets_recv = [x for i, x in enumerate(total_packets_recvd_tx) if corr_types[i] == 'error' and corr_which[i] == 'send']
        ae_corr_probs = [x for i, x in enumerate(corr_probs) if corr_types[i] == 'error' and corr_which[i] == 'recv']
        ae_total_packets_sent = [x for i, x in enumerate(total_packets_sent_rx) if corr_types[i] == 'error' and corr_which[i] == 'recv']
        ae_total_packets_recv = [x for i, x in enumerate(total_packets_recvd_rx) if corr_types[i] == 'error' and corr_which[i] == 'recv']

        axA1.scatter(de_corr_probs, de_total_packets_sent, marker='>', linestyle='solid', label='Packets Sent by Sender')
        axA1.scatter(de_corr_probs, de_total_packets_recv, marker='<', linestyle='solid', label='Packets Received by Sender')
        axA1.scatter(ae_corr_probs, ae_total_packets_sent, marker='>', linestyle='solid', label='Packets Sent by Receiver')
        axA1.scatter(ae_corr_probs, ae_total_packets_recv, marker='<', linestyle='solid', label='Packets Received by Receiver')
        axA1.axes.legend()
        
        figB = plt.figure()
        axB1 = plt.axes()

        axB1.axes.set_title('Packets Sent and Received with Data Packet Loss')
        axB1.set_xlabel('Corruption')
        axB1.set_ylabel('Total Packets')
        de_corr_probs = [x for i, x in enumerate(corr_probs) if corr_types[i] == 'loss' and corr_which[i] == 'send']
        de_total_packets_sent = [x for i, x in enumerate(total_packets_sent_tx) if corr_types[i] == 'loss' and corr_which[i] == 'send']
        de_total_packets_recv = [x for i, x in enumerate(total_packets_recvd_tx) if corr_types[i] == 'loss' and corr_which[i] == 'send']
        ae_corr_probs = [x for i, x in enumerate(corr_probs) if corr_types[i] == 'loss' and corr_which[i] == 'recv']
        ae_total_packets_sent = [x for i, x in enumerate(total_packets_sent_rx) if corr_types[i] == 'loss' and corr_which[i] == 'recv']
        ae_total_packets_recv = [x for i, x in enumerate(total_packets_recvd_rx) if corr_types[i] == 'loss' and corr_which[i] == 'recv']

        axB1.scatter(de_corr_probs, de_total_packets_sent, marker='>', linestyle='solid', label='Packets Sent by Sender')
        axB1.scatter(de_corr_probs, de_total_packets_recv, marker='<', linestyle='solid', label='Packets Received by Sender')
        axB1.scatter(ae_corr_probs, ae_total_packets_sent, marker='>', linestyle='solid', label='Packets Sent by Receiver')
        axB1.scatter(ae_corr_probs, ae_total_packets_recv, marker='<', linestyle='solid', label='Packets Received by Receiver')
        axB1.axes.legend()

        for llist in logged_winsizes_rx:
            fig = plt.figure()
            ax = plt.axes()
            ax.plot(range(len(llist)), llist, marker='.', linestyle='solid', label='Window Size')

        for llist in logged_timeouts_tx:
            fig = plt.figure()
            ax = plt.axes()
            ax.plot(range(len(llist)), llist, marker='.', linestyle='solid', label='Timeouts')

        figC = plt.figure()
        axC1 = plt.axes()

        completion_times = [(x[-1]/1e9) for x in logged_times_rx]
        # de_corr_probs = [x for i, x in enumerate(corr_probs) if corr_types[i] == 'loss' and corr_which[i] == 'send']
        de_completion_times = [x for i, x in enumerate(completion_times) if corr_types[i] == 'loss' and corr_which[i] == 'send']

        axC1.scatter(de_corr_probs, de_completion_times, marker='o', linestyle='solid', label='Completion Times')

        plt.show()
        
        pass

if __name__ == '__main__':
    application = QApplication(sys.argv)
    ui_file_name = 'untitled.ui'
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)
    mainWindow = GUI_Main(application, ui_file)
    exit_code = application.exec_()
    del mainWindow
    sys.exit(exit_code)
