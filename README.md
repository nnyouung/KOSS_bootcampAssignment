# 👩‍💻 3주차 과제: 미세먼지 데이터 웹 페이지로 조회하기
## 1. 소스코드 및 코드 설명
### 1-1. app.js
```js
const express = require("express"); //express 모듈 불러오기
const app = express(); //
const path = require("path"); //path 모듈 불러오기
const bodyParser = require("body-parser"); //body-parser 모듈 불러오기
const mqtt = require("mqtt"); //mqtt 모듈 불러오기
const http = require("http"); //http 모듈 불러오기
const mongoose = require("mongoose"); //mongoose 모듈 불러오기
const Sensors = require("./models/sensors"); //sensors 불러오기
const devicesRouter = require("./routes/devices"); //devices 불러오기
require("dotenv/config"); //.env 파일 불러오기

app.use(express.static(__dirname + "/public")); //public 폴더를 static으로
app.use(bodyParser.json()); //body-parser 사용
app.use(bodyParser.urlencoded({ extended: false })); //body-parser 사용
app.use("/devices", devicesRouter); //라우터 사용

//MQTT접속 하기
const client = mqtt.connect("mqtt://172.20.10.12"); //mqtt와 라즈베리파이와 연결(라즈베리파이 url 입력)
client.on("connect", () => {
  console.log("mqtt connect"); //콘솔에 메세지 출력
  client.subscribe("sensors"); //클라이언트가 센서 정보 구독
});

client.on("message", async (topic, message) => {
  var obj = JSON.parse(message);
  var date = new Date(); //현재 시간(locale 시간) 불러오기
  var year = date.getFullYear(); //현재 연도 불러오기
  var month = date.getMonth(); //현재 월 불러오기
  var today = date.getDate(); //현재 일 불러오기
  var hours = date.getHours(); //현재 시간 불러오기
  var minutes = date.getMinutes(); //현재 분 불러오기
  var seconds = date.getSeconds(); //현재 초 불러오기
  // 앞서 불러온 정보들을 이용해 Date 객체 생성
  obj.created_at = new Date(
    Date.UTC(year, month, today, hours, minutes, seconds)
  );
  // console.log(obj);

  const sensors = new Sensors({ 
    tmp: obj.tmp, //센서에 온도 정보 추가
    pm1: obj.pm1, //센서에 pm1 정보 추가
    pm2: obj.pm25, //센서에 pm25 정보 추가
    pm10: obj.pm10, //센서에 pm10 정보 추가
    created_at: obj.created_at, //센서에 시간 정보 추가
  });

  try {
    const saveSensors = await sensors.save(); //센서 정보 저장
    console.log("insert OK"); //콘솔에 정보 저장 성공 시, 메세지 출력
  } catch (err) {
    console.log({ message: err }); //콘솔에 정보 저장 실패 시, 메세지 출력
  }
});
app.set("port", "3000"); //포트 설정
var server = http.createServer(app); //서버 생성
var io = require("socket.io")(server); //소켓 서버 생성
io.on("connection", (socket) => {
  //웹에서 소켓을 이용한 sensors 센서데이터 모니터링
  socket.on("socket_evt_mqtt", function (data) {
    Sensors.find({}) //sensors의 정보 찾기
      .sort({ _id: -1 }) //나중에 들어온 정보(최근 정보)부터 조회
      .limit(1) //최근 정보 1개 조회
      .then((data) => {
        //console.log(JSON.stringify(data[0]));
        socket.emit("socket_evt_mqtt", JSON.stringify(data[0]));
      });
  });
  //웹에서 소켓을 이용한 LED ON/OFF 제어하기
  socket.on("socket_evt_led", (data) => {
    var obj = JSON.parse(data);
    client.publish("led", obj.led + "");
  });
});

//웹서버 구동 및 DATABASE 구동
server.listen(3000, (err) => {
  if (err) {
    return console.log(err); //웹서버 구동 실패 시, 메세지 출력
  } else {
    console.log("server ready"); //웹서버 구동 성공 시, 메세지 출력
    //DB 연결
    mongoose.connect(
      process.env.MONGODB_URL, //DB 연결 주소
      { useNewUrlParser: true, useUnifiedTopology: true }, //DB 옵션
      () => console.log("connected to DB!") //DB 연결 성공 시, 메세지 출력
    );
  }
});
```
### 1-2. devices.js
```js
var express = require("express"); //express 모듈 불러오기
var router = express.Router(); //express의 router 불러오기(router: 페이지들을 연결하는 중계 역할)
const mqtt = require("mqtt"); //mqtt 모듈 불러오기
const Sensors = require("../models/sensors"); //sensors 불러오기
// MQTT Server 접속
const client = mqtt.connect("mqtt://172.20.10.12"); //mqtt와 라즈베리파이와 연결(라즈베리파이 url 입력)
//웹에서 rest-full 요청받는 부분(POST 방식)
router.post("/led", function (req, res, next) {
  res.set("Content-Type", "text/json");
  //MQTT에서 LED로 전송, 1일 때 on
  if (req.body.flag == "on") {
    client.publish("led", "1");
    res.send(JSON.stringify({ led: "on" })); //웹에서 받은 데이터를 LED로 전송
  //MQTT에서 LED로 전송, 2일 때 off
  } else {
    client.publish("led", "2");
    res.send(JSON.stringify({ led: "off" })); //웹에서 받은 데이터를 LED로 전송
  }
});
module.exports = router; //export로 router 내보내기
```
### 1-3. MQTT.html
```html
<!DOCTYPE html> <!--html 선언-->
<html> <!--html 시작-->
  <head> <!--head 시작-->
    <meta charset="utf-8" /> <!--유니코드 사용-->
    <title>IOT</title> <!--웹페이지 타이틀 설정-->

    <!--자바 스크립트 시작-->
    <script type="text/javascript" src="/socket.io/socket.io.js"></script>
    <script src="http://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script type="text/javascript">
      var socket = null; //socket 선언 및 초기화
      $; //jquery
      var timer = null; //timer 선언 및 초기화
      $(document).ready(function () {
        socket = io.connect(); // 3000port
        // Node.js보낸 데이터를 수신하는 부분
        socket.on("socket_evt_mqtt", function (data) {
          data = JSON.parse(data);
          console.log(data);
          $(".mqttlist").html(
            "<li>" +
              " tmp: " +
              data.tmp +
              "°C" + //온도 출력
              " hum: " +
              data.hum +
              "%" + //습도 출력
              " pm1: " +
              data.pm1 + //pm1 값 출력
              " pm2.5: " +
              data.pm2 + //pm2.5 값 출력
              " pm10: " +
              data.pm10 + //pm10 값 출력
              "</li>"
          );
        });

        //timer가 null이면 1초(1000)마다 time1 함수 실행
        if (timer == null) {
          timer = window.setInterval("timer1()", 1000);
        }
      });
      function timer1() { //time1 함수 시작
        socket.emit("socket_evt_mqtt", JSON.stringify({}));
        console.log("---------"); //콘솔에 메세지 출력
      }
      function ledOnOff(value) { //ledOnOff 함수 시작
        // {"led":1}, {"led":2}
        socket.emit("socket_evt_led", JSON.stringify({ led: Number(value) }));
      }
      function ajaxledOnOff(value) { //ajaxledOnOff 함수 시작
        if (value == "1") var value = "on"; //value가 1이면 on
        else if (value == "2") var value = "off"; //value가 2이면 off
        $.ajax({ //jquery 객체인 ajax 함수 시작
          url: "http://localhost:3000/devices/led", //local url
          type: "post", //post 방식으로
          data: { flag: value },
          success: ledStatus, //성공 시, ledStatus 함수 실행
          error: function () { //실패 시, 에러 알림 출력
            alert("error");
          },
        });
      }
      function ledStatus(obj) { //ledStatus 함수 시작
        $("#led").html("<font color='red'>" + obj.led + "</font> 되었습니다."); //led 출력
      }
    </script>
    <!--자바 스크립트 종료-->
  </head> <!--head 종료-->
  <body> <!--body 시작(웹페이지에 보여지는 부분)-->
    <h2>socket 이용한 센서 모니터링 서비스</h2>
    <div id="msg">
      <div id="mqtt_logs">
        <ul class="mqttlist"></ul>
      </div>
      <h2>socket 통신 방식(LED제어)</h2>
      <button onclick="ledOnOff(1)">LED_ON</button>
      <button onclick="ledOnOff(2)">LED_OFF</button>
      <h2>RESTfull Service 통신 방식(LED제어)</h2>
      <button onclick="ajaxledOnOff(1)">LED_ON</button>
      <button onclick="ajaxledOnOff(2)">LED_OFF</button>
      <div id="led">LED STATUS</div>
    </div>
  </body> <!--body 종료-->
</html> <!--html 종료-->
```

<br/>

## 2. 구현영상
https://user-images.githubusercontent.com/104901660/185309141-69fbd3a5-7343-4978-bfef-5ec7e09119a2.mp4

<br/><br/>

- - -

<br/><br/>

# 👩‍💻 4주차 과제: PyQT5를 이용해 실내 미세먼지 데이터 시각화하기
## 1. 소스코드 및 코드 설명
```python
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
client = MongoClient("mongodb+srv://DB명:비밀번호@cluster0.98cftdx.mongodb.net/DB명?retryWrites=true&w=majority")
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
      for d, cnt in zip(db['sensors'].find().sort('created_at', -1), range(10, 0, -1)):
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
  ```
