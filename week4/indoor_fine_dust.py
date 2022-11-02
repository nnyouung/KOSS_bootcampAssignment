import sys #python interpreter와 관련된 정보 및 기능 제공
#PyQt5.QtWidgets, PyQt5.QtGui, PyQt5.QtCore 패키지에서 여러 기능의 모듈 불러오기
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
#matplotlib.backends.backend_qt5agg 패키지에서 여러 기능의 모듈 불러오기
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#matplotlib.figure패키지에서 Figure 모듈 불러오기
from matplotlib.figure import Figure
#python에서 mongoDB를 이용하기 위해 라이브러리 불러오기
from pymongo import MongoClient

#MongoClient의 값으로 MongoDB 서버 URI를 입력
client = MongoClient("mongodb+srv://DB명:비밀번호!!!@cluster0.98cftdx.mongodb.net/DB명?retryWrites=true&w=majority")
db = client['DB명'] #DB에 접근하기 위해 'DB명'을 변수에 지정

class MyApp(QMainWindow):
  def __init__(self): #python의 생성자명은 __init__ 고정이며, 반드시 첫 번째 인수로 self를 지정
      
      #다른 클래스의 속성 및 메소드를 자동으로 불러와 해당 클래스에서 사용 가능하게 함
      super().__init__()

      self.main_widget = QWidget() #메인 위젯
      self.setCentralWidget(self.main_widget) #메인 위젯의 가운데 정렬

      #그래프의 크기를 가로 4인치, 세로 3인치로 설정
      dynamic_canvas = FigureCanvas(Figure(figsize=(4, 3)))

      #레이아웃 변수 지정
      self.vbox = QVBoxLayout(self.main_widget)
      self.vbox1 = QVBoxLayout()
      self.vbox2 = QVBoxLayout()
      self.hbox1 = QHBoxLayout()

      #라벨 변수 지정
      #label1 = 현재 실내 미세먼지 농도는 ~예요
      #label2 = 현재 상태(좋음/보통/나쁨/매우나쁨)
      #label2_img = 현재 상태 이미지
      self.label1 = QLabel()
      self.label2 = QLabel()
      self.label2_img = QLabel()

      #label1과 label2_img를 각각 가운데 정렬 및 오른쪽 정렬
      self.label1.setAlignment(Qt.AlignCenter)
      self.label2_img.setAlignment(Qt.AlignRight)

      #순서 중요
      self.vbox1.addWidget(self.label1) #vbox1 레이아웃에 label1 라벨 추가

      self.hbox1.addWidget(self.label2_img) #hbox1 레이아웃에 label2_img 라벨 추가
      self.hbox1.addWidget(self.label2) #hbox1 레이아웃에 label2 라벨 추가
      self.vbox2.addLayout(self.hbox1) #vbox2 레이아웃에 hbox1 레이아웃 추가

      self.vbox.addLayout(self.vbox1) #vbox 레이아웃에 vbox1 레이아웃 추가
      self.vbox.addLayout(self.vbox2) #vbox 레이아웃에 vbox2 레이아웃 추가
      self.vbox.addWidget(dynamic_canvas) #vbox 레이아웃에 그래프(=dynamic_canvas) 추가

      #그래프
      self.dynamic_ax = dynamic_canvas.figure.subplots()  #좌표축 준비
      self.timer = dynamic_canvas.new_timer( #그래프가 변하는 주기 (0.1초(=100ms), 실행되는 함수)
      100, [(self.update_canvas, (), {})])
      self.timer.start()  #타이머 시작

      #윈도우(=위젯이 배치되는 가장 기본이 되는 위젯) 옵션
      self.setWindowTitle('실내 미세먼지 농도 측정기') #타이틀바
      self.setGeometry(300, 100, 600, 400) #위치 설정 (x축 위치, y축 위치, 너비, 높이)
      self.show() #윈도우 띄우기

  def update_canvas(self): #업데이트되는 그래프의 함수
      self.dynamic_ax.clear() #그래프 초기화

      li = []
      ti = []
      #DB의 sensors에서 정보를 찾아 뒤에서부터 10개의 정보(최근 정보) 가져오기
      for d, cnt in zip(db['sensors'].find(), range(10, 0, -1)):
        li.append(int(d['pm1'])) #li 리스트에 미세먼지 정보 저장
        ti2 = str(d['created_at']) #시간 정보를 가져와 string 형태로 저장
        #ti2 변수를 11번째 문자부터(=날짜를 제외한 시간 정보만 가져오기 위해) ti 리스트에 저장
        ti.append(ti2[11:])

      self.dynamic_ax.plot(ti, li, color='deeppink') #점 찍기(x좌표, y좌표, 색깔)
      self.dynamic_ax.figure.canvas.draw() #그래프에 그리기

      #label1 자리에 텍스트 출력
      self.label1.setText(f'현재 실내 미세먼지 농도는 {li[-1]}예요')

      #조건에 따라 label2에는 텍스트, label2_img에는 이미지 출력
      if 0 <= li[-1] <= 30 or 0 <= li[-1] <= 15:
          self.label2.setText('좋음')
          self.label2_img.setPixmap(QPixmap('./좋음.png'))
      elif 31 <= li[-1] <= 50 or 16 <= li[-1] <= 25:
          self.label2.setText('보통')
          self.label2_img.setPixmap(QPixmap('./보통.png'))
      elif 51 <= li[-1] <= 100 or 26 <= li[-1] <= 50:
          self.label2.setText('나쁨')
          self.label2_img.setPixmap(QPixmap('./나쁨.png'))
      elif 101 <= li[-1] or 51 <= li[-1]:
          self.label2.setText('매우 나쁨')
          self.label2_img.setPixmap(QPixmap('./매우나쁨.png'))

#py파일은 하나의 모듈 형태로 만들어지기 때문에 누가 import하냐에 따라 __name__ 값이 달라짐
if __name__ == '__main__':
  app = QApplication(sys.argv) #QApplication 객체 생성(sys.argv: 현재 작업중인 .py파일의 절대 경로)
  ex = MyApp() #생성자의 self는 ex를 전달받음
  #무한루프되고 있는 app 상태에서, system의 x버튼을 누르면 실행되고 있는 app을 종료
  sys.exit(app.exec_())
