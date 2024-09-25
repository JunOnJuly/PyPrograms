import cv2
import sys, os
from PIL import Image

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


# 메인 윈도우
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.filename = ''
        self.curFrame = 0
        self.startFrame = 0
        self.endFrame = 0
        self.initUI()
    

    def initUI(self):
        # 메타 데이터
        version = '0.0.1'

        # 시퀀스 구성
        self.initWindow(version)
        self.initLayout()
        self.initWidget()
        self.initStyle()
        self.showLayout()

        # 실행
        self.show()


    # 윈도우 구성 시퀀스
    def initWindow(self, version):
        # 타이틀
        self.setWindowTitle("비디오 gif 변환기 - v " + version)
        # 크기 및 위치
        self.setGeometry(100, 100, 1200, 800)


    # 레이아웃 구성 시퀀스
    def initLayout(self):
        # 이미지 섹션과 조작 섹션을 구분하기 위한 QV
        self.mainQH = QHBoxLayout()
        # 이미지 섹션
        self.imageQV = QVBoxLayout()
        # 조작 섹션
        self.operQV = QVBoxLayout()


    # 위젯 구성 시퀀스
    def initWidget(self):
        # 비디오 선택을 위한 버튼 위젯
        self.videoSelectBtn = QPushButton('동영상을 선택해주세요', self)
        self.videoSelectBtn.setCheckable(True)
        self.videoSelectBtn.clicked.connect(self.videoSelectDialog)

        # 이미지 섹션 위젯
        # self.pixmap = QPixmap('sample.jpeg')
        self.lbl_img = QLabel()
        # self.lbl_img.setPixmap(self.pixmap)

        # 이미지 선택 슬라이더 위젯
        self.imageSlider = QSlider(Qt.Horizontal, self)
        self.imageSlider.setEnabled(False)
        self.imageSlider.valueChanged.connect(self.setImage)

        # 시작 프레임 선택을 위한 버튼 위젯
        self.startFrameBtn = QPushButton('시작 위치를 선택해주세요', self)
        self.startFrameBtn.setEnabled(False)
        self.startFrameBtn.clicked.connect(self.startFrameSelect)
        # 시작 프레임 기록 텍스트
        self.startFrameLbl = QLabel('-')

        # 종료 프레임 선택을 위한 버튼 위젯
        self.endFrameBtn = QPushButton('종료 위치를 선택해주세요', self)
        self.endFrameBtn.setEnabled(False)
        self.endFrameBtn.clicked.connect(self.endFrameSelect)
        # 종료 프레임 기록 텍스트
        self.endFrameLbl = QLabel('-')

        # 동영상 변환 버튼 위젯
        self.convertBtn = QPushButton('gif 변환', self)
        self.convertBtn.setEnabled(False)
        self.convertBtn.clicked.connect(self.convert)

        # 설명 텍스트 위젯
        guide_text = '버전 0.0.1\n1. 동영상을 선택 및 대기\n2. 시작 밑 종료 프레임 선택\n3. gif 변환'
        self.guideLbl = QLabel(guide_text)
        
        # 마진
        self.marginLbl = QLabel()


    # 다이얼로그 구성 시퀀스
    def videoSelectDialog(self):
        # 이미지 다이얼로그
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        self.videoSelectBtn.setText("동영상을 읽어오는 중")
        if fname[0]:
            video = cv2.VideoCapture(fname[0])
            self.filename = f"{fname[0].split('/')[-1].split('.')[0]}_converted_gif"
            frame_cnt = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = int(video.get(cv2.CAP_PROP_FPS))
            self.all_frame = frame_cnt
            try:
                if not os.path.exists(self.filename):
                    os.makedirs(self.filename)
            except OSError:
                print ('Error: Creating directory. ' +  self.filename)

            for i in range(frame_cnt):
                ret, frame = video.read()
                if ret:
                    save_path = f"{self.filename}/{i}.jpg"
                    cv2.imwrite(save_path, frame)

            video.release()

            self.videoSelectBtn.setEnabled(False)
            self.imageSlider.setRange(0, len(os.listdir(self.filename))-1)
            
            self.endFrame = len(os.listdir(self.filename))-1
            self.endFrameLbl.setText(str(self.endFrame) + '/' + str(self.all_frame-1))
            self.startFrameLbl.setText(str(self.startFrame) + '/' + str(self.all_frame-1))
            self.startFrameBtn.setEnabled(True)
            self.endFrameBtn.setEnabled(True)

            self.imageSlider.setSingleStep(1)
            self.imageSlider.setEnabled(True)

            self.pixmap = QPixmap(self.filename + f'/0')
            self.lbl_img.setPixmap(self.pixmap)

            self.convertBtn.setEnabled(True)
        self.videoSelectBtn.setText("동영상을 읽어오기 완료")


    # 스타일 구성 시퀀스
    def initStyle(self):
        # 임시
        self.lbl_img.setStyleSheet(
            "color : #6E6F71;"
            "background-color : #FFFFFF;"
            "border-style: solid;"
            "border-width: 2px;"
            "border-color: #595959;"
        )


    # 레이아웃 출력 시퀀스
    def showLayout(self):
        # 메인 QV 에 이미지 섹션 삽입
        self.mainQH.addLayout(self.imageQV, 20)
        # 이미지 섹션에 이미지 위젯 삽입
        self.imageQV.addWidget(self.lbl_img)
        # 이미지 섹션 에 슬라이더 위젯 삽입
        self.imageQV.addWidget(self.imageSlider, 1)

        # 메인 QV 에 조작 섹션 삽입
        self.mainQH.addLayout(self.operQV, 8)
        # 조작 섹션에 가이드 위젯 삽입
        self.operQV.addWidget(self.marginLbl, 20)
        self.operQV.addWidget(self.guideLbl, 5)
        # 프레임 선택 버튼 / 텍스트 섹션에 버튼 / 텍스트 삽입
        self.operQV.addWidget(self.startFrameBtn, 1)
        self.operQV.addWidget(self.startFrameLbl, 1)
        self.startFrameLbl.setAlignment(Qt.AlignHCenter)
        self.operQV.addWidget(self.endFrameBtn, 1)
        self.operQV.addWidget(self.endFrameLbl, 1)
        self.endFrameLbl.setAlignment(Qt.AlignHCenter)
        # 조작 섹션에 비디오 선택 위젯 삽입
        self.operQV.addWidget(self.videoSelectBtn, 1)
        # 조작 섹션에 변환 버튼 위젯 삽입
        self.operQV.addWidget(self.convertBtn, 1)

        # 레이아웃 출력
        self.setLayout(self.mainQH)


    # 슬라이더에 따라 프레임 출력
    def setImage(self, value):
        self.curFrame = value
        self.pixmap = QPixmap(self.filename + f'/{value}')
        self.lbl_img.setPixmap(self.pixmap)


    # 시작 프레임 선택
    def startFrameSelect(self):
        self.startFrame = self.curFrame
        self.startFrameLbl.setText(str(self.curFrame) + '/' + str(self.all_frame-1))


    # 종료 프레임 선택
    def endFrameSelect(self):
        self.endFrame = self.curFrame
        self.endFrameLbl.setText(str(self.curFrame) + '/' + str(self.all_frame-1))

    
    # gif 변환
    def convert(self):
        self.convertBtn.setText("동영상 변환 중")
        self.convertBtn.setEnabled(False)
        imgs = os.listdir(self.filename)
        imgs.sort(key=lambda x: int(x.split('.')[0]))
        imgs = [self.filename + '/' + x for x in imgs]
        imgs = [Image.open(x) for x in imgs]

        im = imgs[self.startFrame]
        im.save(f'{self.filename}.gif', save_all=True, append_images=imgs[self.startFrame+1:self.endFrame+1], loop=0, duration=(1/self.fps)*1000)
        self.convertBtn.setText("동영상 변환 완료")


    # 구역 선택
    def setSection(self, e):
        pass

    # 종료이벤트
    # 종료시 임시 이미지파일 삭제
    def closeEvent(self, QCloseEvent):
        if self.filename and os.path.exists(self.filename):
            for file in os.listdir(self.filename):
                os.remove(self.filename + '/' + file)
            os.rmdir(self.filename)


if __name__ == "__main__":
    # 앱 지정
    app = QApplication(sys.argv)

    #실행
    window = MainWindow()
    app.exec_()