import sys, os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from scapy.all import *
import binascii

from datetime import datetime


class GetPacket(QThread):
    got_packet = pyqtSignal(int)
    got_packet_text = pyqtSignal(str)


    def __init__(self):
        super().__init__()
        self.packet_length = self.packetLength()
        self.packet_string = ''


    def find_ip(self, text_data, filter_list, src):
        if '<ALL_CHANNELS>' in text_data:
            filter_list.append('host')
            filter_list.append(src)


    def showPacket(self, packet):
        raw_data = raw(packet)
        hex_data = raw_data.hex()
        
        if (packet.getlayer(IP)):
            src = packet.getlayer(IP).src
        else: src = ''
        
        text_data = ''
        
        for idx in range(0, len(hex_data), 2):
            try:
                text_data += binascii.unhexlify(hex_data[idx:idx+2]).decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text_data += binascii.unhexlify(hex_data[idx:idx+6]).decode('utf-8')
                except UnicodeDecodeError:
                    continue
        
        if len(filter_list) == 1:
            self.find_ip(text_data, filter_list, src)
        
        if '<ALL_CHANNELS>' in text_data:
            text_data = '<ALL_CHANNELS>' + ' ' + text_data.split('<ALL_CHANNELS>')[1][4:]
            text_data = text_data[:-11]
            
            with open('log.txt', 'a', encoding='utf-8') as f:
                f.write(datetime.now().strftime('%Y-%m-%d/%H:%M:%S ' + text_data + "\n"))

            self.packet_length += 1
            self.packet_string = text_data
            self.got_packet.emit(self.packet_length)
            self.got_packet_text.emit(self.packet_string)

        
    def packetLength(self):
        num = 0

        with open('log.txt', 'r', encoding='utf-8') as f:
            while f.readline():
                num += 1

        self.packet_length = num

        return num


    def run(self):
        global filter_list
        filter_list = ['tcp']
        sniff(filter=' '.join(filter_list), prn=self.showPacket, count=0)


class MabiPacket(QWidget):
    def __init__(self):
        super().__init__()

        self.getPacket = GetPacket()
        self.getPacket.start()
        self.getPacket.got_packet.connect(self.got_packet)
        self.getPacket.got_packet_text.connect(self.got_packet_text)

        self.initUI()


    def initUI(self):
        self.setWindowTitle('MabiPacket')
        self.setWindowIcon(QIcon('icon.png'))
        self.center()
        self.resize(1200, 500)

        log_size = self.sizingLog()

        self.curText = QLabel('', self)
        self.curText.setAlignment(Qt.AlignCenter)
        
        self.curFont = self.curText.font()
        self.curFont.setPointSize(12)
        self.curFont.setBold(True)
        self.curText.setFont(self.curFont)

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(log_size)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        with open('log.txt', 'r', encoding='utf-8') as f:
            for i in range(log_size):
                line = f.readline().split()
                self.tableWidget.setItem(i, 0, QTableWidgetItem(line[0]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(line[1]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(line[2]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(' '.join(line[4:])))

        layout_H = QHBoxLayout()
        layout_V = QVBoxLayout()

        layout_H.addStretch(1)
        layout_H.addLayout(layout_V, 10)
        layout_H.addStretch(1)

        layout_V.addStretch(1)
        layout_V.addWidget(self.curText, 1)
        layout_V.addWidget(self.tableWidget, 6)
        layout_V.addStretch(1)

        self.setLayout(layout_H)
        self.show()

    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def sizingLog(self):
        num = 0

        with open('log.txt', 'r', encoding='utf-8') as f:
            while f.readline():
                num += 1
        
        return num


    @pyqtSlot(int)
    def got_packet(self, num):
        self.tableWidget.setRowCount(num)

        with open('log.txt', 'r', encoding='utf-8') as f:
            for i in range(num):
                line = f.readline().split()
                self.tableWidget.setItem(i, 0, QTableWidgetItem(line[0]))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(line[1]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(line[2]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(' '.join(line[4:])))

        self.update()

    
    @pyqtSlot(str)
    def got_packet_text(self, text):
        self.curText.setText(text)

        self.update()


if __name__ == '__main__':
    if not os.path.exists('./log.txt'):
        with open('log.txt', 'a') as f:
            pass

    app = QApplication(sys.argv)
    ex = MabiPacket()
    sys.exit(app.exec_())