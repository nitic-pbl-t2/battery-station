// serial portを MEGAにするが必要あります
#include <ArduinoJson.h>
#include <Servo.h>

// 使用するピンの定義
const int VOL_PIN = A0; // ポートの電流を流すピン
const int SWITCH_PIN = A1; // バッテリーが繋がってるかのピン
const int SWITCH_PIN2 = A2; // サーボモータのスイッチ
const int SV_PIN = A3; // サーボモータを動かすピン

// LED3色は以下に対応
const int LED_PIN_GREEN = 5; // Available
const int LED_PIN_YELLOW = 6; // Charging
const int LED_PIN_RED = 7; // Reserved


void setup() {
    pinMode(SWITCH_PIN, INPUT);
    pinMode(SWITCH_PIN2,INPUT);
    pinMode(LED_PIN_GREEN, OUTPUT);
    pinMode(LED_PIN_YELLOW, OUTPUT);
    pinMode(LED_PIN_RED, OUTPUT);
    servo.attach(SV_PIN, 500, 2400);
    Serial.begin(9600);
}

Servo servo; // サーボを動かすときに使う変数
bool isOpen=false; // 蓋を開けるかの処理
bool isCharging= false;  // バッテリーが充電されているかのフラグ
bool isConnected=false;　// バッテリーが接続されているかのフラグ
float volt=0.0; // 計測された電圧が入る
int const sampleTimes=50; // 計測回数

void loop() {
 if (Serial.available() > 0) {
    // ラズベリーパイからのデータを読み取る
    String jsonData = Serial.readStringUntil('\n');

    // 受信したJSONデータをパース
    StaticJsonDocument<200> jsonDocument;
    DeserializationError error = deserializeJson(jsonDocument, jsonData);
    
    if (error) {
      Serial.print("Error decoding JSON: ");
      Serial.println(error.c_str());
    } else {
      // データを分解
      const char* sensor = jsonDocument["sensor"];
      int value = jsonDocument["value"];
      
      // ここで受け取ったデータを使った処理を行う
      Serial.print("Received Sensor: ");
      Serial.println(sensor);
      Serial.print("Received Value: ");
      Serial.println(value);

      // データを加工してラズベリーパイに送信
      int processedValue = value * 2;
      sendToRaspberryPi(sensor, processedValue);
    }
  }


    // 蓋の動作
    if(isOpen){
      servo.write(78);  // サーボモーターを90度の位置まで動かす -> 開いてる状態
    }else{
      servo.write(180);  // サーボモーターを0度の位置まで動かす -> 閉じてる状態
    }


    // バッテリーに電流が流れているかの判定
    // バッテリーの状態を表現する変数 -> strcmpで初期化できてなかったら怖いので、ローカルスコープで定義する
    char state[10];
    int floatCount=0; // 浮遊している判定の回数
    int chargeCount=0;

    // 浮遊しているしている多数決をとる
    for(int i=0;i< sampleTimes ;i++){
        // 電圧の計測
      volt = analogRead(VOL_PIN);
      volt = 2 * volt * 5.0 / 1023.0;

      if(volt <= 0.03){  // 0.03v 以下だったら浮遊していると見做す（実験の結果）
        floatCount++;
      }else{
        chargeCount++;
      }
      delay(100); // 0.1秒後にまた計測
    }

    // 多数決の結果の表示
    Serial.println("Is battery charging now?");
    Serial.print("no : ");
    Serial.println(floatCount);
    Serial.print("yes: ");
    Serial.println(chargeCount);
    
    if(chargeCount > 0.9 * sampleTimes){ // 充電している判定が、計測回数の9割を超えたら
      isCharging=true;
    }else{
      isCharging =false;
    }

    // 計測したデータからバッテリーの状態を求める
    isConnected = !digitalRead(SWITCH_PIN);
    if(!isConnected){
      strcpy(state,"Reserved"); // そもそも、バッテリーが繋がってない場合
    }else if(isCharging){
      strcpy(state,"Charging"); // バッテリーが繋がってる -> 充電完了していない場合
    }else{
      strcpy(state,"Available"); // バッテリーが繋がってる、かつ、充電終わってる場合
    }
    Serial.println(state);

    // LEDを制御
     if (strcmp(state, "Available") == 0) {
         digitalWrite(LED_PIN_GREEN, HIGH);
         digitalWrite(LED_PIN_YELLOW, LOW);
         digitalWrite(LED_PIN_RED, LOW);
     } else if (strcmp(state, "Charging") == 0) {
         digitalWrite(LED_PIN_GREEN, LOW);
         digitalWrite(LED_PIN_YELLOW, HIGH);
         digitalWrite(LED_PIN_RED, LOW);
     } else if (strcmp(state, "Reserved") == 0) {
         digitalWrite(LED_PIN_GREEN, LOW);
         digitalWrite(LED_PIN_YELLOW, LOW);
         digitalWrite(LED_PIN_RED, HIGH);
     } else {
         digitalWrite(LED_PIN_GREEN, LOW);
         digitalWrite(LED_PIN_YELLOW, LOW);
         digitalWrite(LED_PIN_RED, LOW);
     }
}
