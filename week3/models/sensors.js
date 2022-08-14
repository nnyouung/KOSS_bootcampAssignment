const mongoose = require("mongoose"); //mongoose 모듈 불러오기

//데이터들의 Schema 설정
//Schema: 데이터들의 속성, 속성들의 집합인 개체, 개체 사이의 관계에 대한 정의와 이들이 유지해야 할 제약 조건들을 기술
const SensorsSchema = mongoose.Schema({
  tmp: { //온도
    type: String,
    required: true,
  },
  hum: { //습도
    type: String,
    required: true,
  },
  pm1: { //pm1
    type: String,
    require: true,
  },
  pm2: { //pm2
    type: String,
    require: true,
  },
  pm10: { //pm10
    type: String,
    require: true,
  },
  created_at: { //데이터 생성 시간
    type: Date,
    default: Date.now,
  },
});

//Schema를 사용하는 model 만든 후, export로 내보내기
module.exports = mongoose.model("Sensors", SensorsSchema);
