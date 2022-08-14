# 3주차 과제: 미세먼지 데이터 웹 페이지로 조회하기
## 1. 소스코드 및 코드 설명
### 1-1. app.js
```js
const express = require("express"); //express 모듈 불러오기
const app = express();
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

## 2. 구현 영상
