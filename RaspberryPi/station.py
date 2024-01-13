import serial
import json

ser = serial.Serial('/dev/ttyUSB0', 9600)  # シリアルポートの設定に注意
ser.flush()

# Arduinoからのデータを受信
def receive_from_arduino():
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        print("Received from Arduino:", line)

        # 受信したJSONデータをパース
        try:
            data = json.loads(line)
            print("Sensor:", data["sensor"])
            print("Value:", data["value"])
            return data
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
    return None

# データを加工してArduinoに送信
def send_to_arduino(sensor, processed_value):
    # JSONデータを作成
    data_to_send = {"sensor": sensor, "processedValue": processed_value}

    # JSONデータを文字列に変換してシリアルポート経由で送信
    json_data_str = json.dumps(data_to_send) + '\n'
    ser.write(json_data_str.encode())
    print("Sent to Arduino:", json_data_str)

# メインの処理
while True:
    received_data = receive_from_arduino()
    
    if received_data is not None:
        # データを加工してArduinoに送信
        sensor_value = received_data["value"]
        processed_value = sensor_value * 2
        send_to_arduino(received_data["sensor"], processed_value)
