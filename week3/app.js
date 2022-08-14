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
