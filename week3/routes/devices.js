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
