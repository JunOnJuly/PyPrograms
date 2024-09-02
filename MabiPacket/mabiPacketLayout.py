import sys, os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from scapy.all import *
import binascii

from datetime import datetime


# 메인 윈도우
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 저장된 필터 불러오기
        self.filters = dict()
        if not os.path.exists('./filters.txt'):
            with open('./filters.txt', 'a', encoding='utf-8') as f:
                pass
        else:
            with open('./filters.txt', 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.split()[1] == 'F':
                        self.filters[line.split()[0]] = False
                    else:
                        self.filters[line.split()[0]] = True

        self.getPacket = GetPacket()
        self.getPacket.start()
        self.getPacket.got_packet.connect(self.got_packet)
        self.getPacket.got_filterd_packet.connect(self.got_filterd_packet)

        self.initUI()


    def initUI(self):
        # 데이터
        version = '0.0.1'

        # 윈도우 구성
        self.initWindow(version)
        self.initLayout()
        self.initWidget()
        self.initStyle()
        self.showLayout()

        # 실행
        self.show()


    # 윈도우 세팅
    def initWindow(self, version):
        # 타이틀
        self.setWindowTitle("마비노기 시스템 로거 - v " + version)
        # 크기 및 위치
        self.setGeometry(100, 100, 1200, 800)
        # 로고
        self.setWindowIcon(QIcon("icon.png"))
    
    
    def initLayout(self):
        # 양 옆 마진을 위한 QH
        self.marginQH = QHBoxLayout()
        # 안에 삽입할 QV
        self.mainQV = QVBoxLayout()
        # 라인 에디트를 담을 QH
        self.leQH = QHBoxLayout()
        # 필터 선택 유무를 확인하기 위한 체크박스를 담을 QV
        self.checkQH = QHBoxLayout()


    def initWidget(self):
        # mainQV 안에 삽입할 텍스트 구역
        self.lblCurTxt = QLabel('마비노기를 실행하고 기다려주세요')
        # 필터링 된 텍스트 리스트
        self.filteredTable = QTableWidget()
        self.filteredTable.setRowCount(0)
        self.filteredTable.setColumnCount(4)
        self.filteredTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.filteredTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # 필터 입력을 받을 라인에디트
        self.getFilter = QLineEdit("추가할 필터를 입력해주세요", self)
        # 라인에디트와 연결된 버튼
        self.getFilterBtn = QPushButton("추가", self)
        self.getFilterBtn.clicked.connect(self.filterBtnClickded)
        # 필터 체크박스 리스트
        self.checkList = []
        for key, value in self.filters.items():
            tempchk = QCheckBox(key, self)
            if value:
                tempchk.toggle()
            self.checkList.append(tempchk)
        for chk in self.checkList:
            chk.stateChanged.connect(self.filterCheck)
        # 전체 텍스트 리스트
        self.allTable = QTableWidget()
        self.allTable.setRowCount(0)
        self.allTable.setColumnCount(4)
        self.allTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.allTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


    def initStyle(self):
        # 라벨 스타일
        self.lblCurTxt.setStyleSheet(
            "color : #FF7B1B;"
            "background-color : #FFFFFF;"
            "border-style: solid;"
            "border-width: 2px;"
            "border-color: #FF7B1B;"
        )
        # 폰트 스타일
        self.curTxtFont = self.lblCurTxt.font()
        self.curTxtFont.setPointSize(10)
        self.curTxtFont.setBold(True)
        self.lblCurTxt.setFont(self.curTxtFont)
        # 필터링 된 텍스트 리스트 스타일
        self.filteredTable.setStyleSheet(
            "color : #FF7B1B;"
            "background-color : #FFFFFF;"
            "border-style: solid;"
            "border-width: 1px;"
            "border-color: #FF7B1B;"
        )
        # 라인에디트 스타일
        self.getFilter.setStyleSheet(
            "color : #FF7B1B;"
            "background-color : #FFFFFF;"
            "border-style: solid;"
            "border-width: 2px;"
            "border-color: #FF7B1B;"
        )
        # 버튼 스타일
        self.getFilterBtn.setStyleSheet(
            "color : #FF7B1B;"
            "background-color : #FFFFFF;"
            "border-style: solid;"
            "border-width: 2px;"
            "border-color: #FF7B1B;"
        )
        # 전체 텍스트 리스트 스타일
        self.allTable.setStyleSheet(
            "color : #000000;"
            "background-color : #FFFFFF;"
            "border-style: solid;"
            "border-width: 1px;"
            "border-color: #FF7B1B;"
        )

    
    def showLayout(self):
        ### 마진
        self.marginQH.addStretch(1)
        ### mainQV
        self.marginQH.addLayout(self.mainQV, 20)

        ## 마진
        self.mainQV.addStretch(1)
        ## 최신 텍스트 라벨
        self.mainQV.addWidget(self.lblCurTxt, 1)
        ## 필터링된 텍스트 리스트
        self.mainQV.addWidget(self.filteredTable, 8)
        
        # 라인 에디트
        self.leQH.addWidget(self.getFilter, 15)
        # 라인 에디트 버튼
        self.leQH.addWidget(self.getFilterBtn, 5)
        # 마진
        self.leQH.addStretch(60)

        ## 필터를 입력받을 라인 에디트 구역
        self.mainQV.addLayout(self.leQH, 1)

        # 필터
        for check in self.checkList:
            self.checkQH.addWidget(check, 5)
            self.checkQH.addStretch(1)

        ## 필터 리스트
        self.mainQV.addLayout(self.checkQH, 2)
        ## 전체 텍스트 리스트
        self.mainQV.addWidget(self.allTable, 8)
        ## 마진
        self.mainQV.addStretch(1)

        ### 마진
        self.marginQH.addStretch(1)

        # 창 띄우기
        self.setLayout(self.marginQH)

    
    # 필터 입력 버튼
    def filterBtnClickded(self):
        # 필터가 공백이 아닐 경우에만
        if self.getFilter.text().strip() == '':
            return
        if self.getFilter.text() in self.filters.keys():
            return
        # 쓰래드 멈추기
        self.getPacket.running = False
        self.getPacket.filter_updated = False
        # 리스트에 필터 추가
        self.filters[self.getFilter.text()] = True
        # 필터 기록
        with open('./filters.txt', 'a+', encoding='utf-8') as f:
            if f.readline():
                f.write('\n')
            f.write(f'{self.getFilter.text()} T\n')

        # 필터 최신화
        self.checkList.append(QCheckBox(self.getFilter.text()))
        self.checkList[-1].toggle()
        self.checkList[-1].stateChanged.connect(self.filterCheck)
        self.checkQH.addWidget(self.checkList[-1], 5)
        self.checkQH.addStretch(1)
        self.update()
        # 쓰래드 재시작
        self.getPacket.running = True
        self.getPacket.start()
        # 입력란 초기화
        self.getFilter.setText('')


    # 체크박스
    def filterCheck(self, state):
        # 쓰래드 멈추기
        self.getPacket.running = False
        self.getPacket.filter_updated = False
        # 현재 필터를 삭제
        os.remove('filters.txt')
        # 현재 상태를 기록 및 필터 최신화
        with open('filters.txt', 'a+', encoding='utf-8') as f:
            for chk in self.checkList:
                f.write(f"{chk.text()} {'T' if chk.isChecked() else 'F'}\n")
                self.filters[chk.text()] = chk.isChecked()
        # 쓰래드 재시작
        self.getPacket.running = True
        self.getPacket.start()


    # 패킷 리스트 개수 받기
    @pyqtSlot(int)
    def got_packet(self, num):
        self.allTable.setRowCount(num)

        with open('./logs/log.txt', 'r', encoding='utf-8') as f:
            for i, line in enumerate(f.readlines()[::-1]):
                line = line.split()
                self.allTable.setItem(i, 0, QTableWidgetItem(line[0]))
                self.allTable.setItem(i, 1, QTableWidgetItem(line[1]))
                self.allTable.setItem(i, 2, QTableWidgetItem(line[2]))
                self.allTable.setItem(i, 3, QTableWidgetItem(' '.join(line[4:])))

        self.update()


    # 필터링된 패킷 리스트 개수 받기
    @pyqtSlot(int)
    def got_filterd_packet(self, num):
        self.filteredTable.setRowCount(num)

        with open('./logs/filteredLog.txt', 'r', encoding='utf-8') as f:
            for i, line in enumerate(f.readlines()[::-1]):
                # 필터링된 최신 텍스트 업데이트
                if i == 0:
                    self.lblCurTxt.setText(' '.join(line.split()[1:]))
                    
                line = line.split()

                for key, value in self.filters.items():
                    if value and key in ' '.join(line[4:]):
                        self.filteredTable.setItem(i, 0, QTableWidgetItem(line[0]))
                        self.filteredTable.setItem(i, 1, QTableWidgetItem(line[1]))
                        self.filteredTable.setItem(i, 2, QTableWidgetItem(line[2]))
                        self.filteredTable.setItem(i, 3, QTableWidgetItem(' '.join(line[4:])))
                

        self.update()


    # 윈도우가 닫힐 때 로그 저장
    def closeEvent(self, event):
        allLogName = '[AllLog]'
        filteredLogName = '[FilteredLog]'
    

        with open('./logs/log.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            allLogName += '-'.join('-'.join(lines[0].split()[0].split('/')).split(':'))
            allLogName += '~~'
            allLogName += '-'.join('-'.join(lines[-1].split()[0].split('/')).split(':'))
            allLogName += '.txt'

            for line in lines:
                with open('./logs/' + allLogName, 'a+', encoding='utf-8') as f:
                    f.write(line)
        
        with open('./logs/filteredLog.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                filteredLogName += '-'.join('-'.join(lines[0].split()[0].split('/')).split(':'))
                filteredLogName += '~~'
                filteredLogName += '-'.join('-'.join(lines[-1].split()[0].split('/')).split(':'))
                filteredLogName += '.txt'
            else:
                filteredLogName += '~None'
            for line in lines:
                with open('./logs/' + filteredLogName, 'a+', encoding='utf-8') as f:
                    f.write(line)

        os.remove('./logs/log.txt')
        os.remove('./logs/filteredLog.txt')




# 패킷 가져오기
class GetPacket(QThread):
    # 리스트 수
    got_packet = pyqtSignal(int)
    # 필터링 된 리스트 수
    got_filterd_packet = pyqtSignal(int)


    def __init__(self):
        super().__init__()

        # 저장된 필터 불러오기
        self.filter_updated = False
        self.filters = dict()
        if not os.path.exists('./filters.txt'):
            with open('./filters.txt', 'a', encoding='utf-8') as f:
                pass
        else:
            with open('./filters.txt', 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.split()[1] == 'F':
                        self.filters[line.split()[0]] = False
                    else:
                        self.filters[line.split()[0]] = True

        # 패킷 탐색 필터
        self.packet_filter_list = ['tcp']
        # 패킷 리스트 수
        self.packet_length = self.packetLength()
        # 필터링된 리스트 수
        self.filtered_length = self.filterdPacketLength()
        # 반복 실행 여부
        self.running = True


    # 마비노기 ip 찾기
    def find_ip(self, text_data, src):
        if '<ALL_CHANNELS>' in text_data:
            self.packet_filter_list.append('and')
            self.packet_filter_list.append('host')
            self.packet_filter_list.append(src)


    # 패킷 복호
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
        
        if len(self.packet_filter_list) == 1:
            self.find_ip(text_data, src)
        
        if '<ALL_CHANNELS>' in text_data:
            text_data = '<ALL_CHANNELS>' + ' ' + text_data.split('<ALL_CHANNELS>')[1][4:]
            text_data = text_data[:-11]
            
            with open('./logs/log.txt', 'a', encoding='utf-8') as f:
                f.write(datetime.now().strftime('%Y-%m-%d/%H:%M:%S ' + text_data + "\n"))

            self.packet_length += 1
            for key, value in self.filters.items():
                if value and key in text_data:
                    with open('./logs/filteredLog.txt', 'a', encoding='utf-8') as f:
                        f.write(datetime.now().strftime('%Y-%m-%d/%H:%M:%S ' + text_data + "\n"))
                    self.filtered_length += 1
                    break

            self.got_packet.emit(self.packet_length)
            self.got_filterd_packet.emit(self.filtered_length)

    
    # 패킷 개수
    def packetLength(self):
        num = 0

        with open('./logs/log.txt', 'r', encoding='utf-8') as f:
            while f.readline():
                num += 1

        self.packet_length = num

        return num


    # 필터링 된 패킷 개수
    def filterdPacketLength(self):
        num = 0

        with open('./logs/filteredLog.txt', 'r', encoding='utf-8') as f:
            while f.readline():
                num += 1

        self.filtered_length = num

        return num
    

    # 실행
    def run(self):
        # 필터를 업데이트 했는지 여부
        while self.running:
            if not self.filter_updated:
                # 저장된 필터 불러오기
                with open('./filters.txt', 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        if line.split()[1] == 'F':
                            self.filters[line.split()[0]] = False
                        else:
                            self.filters[line.split()[0]] = True
                self.filter_updated = True
            sniff(filter=' '.join(self.packet_filter_list), prn=self.showPacket, count=1)


if __name__ == "__main__":
    # 로깅 파일 만들기
    if not os.path.exists('./logs'):
        os.mkdir('logs')
    if not os.path.exists('./logs/log.txt'):
        with open('./logs/log.txt', 'a') as f:
            pass
    if not os.path.exists('./logs/filteredLog.txt'):
        with open('./logs/filteredLog.txt', 'a') as f:
            pass

    # 앱 지정
    app = QApplication(sys.argv)

    # 앱 스타일
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 230, 212))
    app.setPalette(palette)

    #실행
    window = MainWindow()
    app.exec_()