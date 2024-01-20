import serial
import time

# Arduinoのシリアルポートを適切なものに変更
ser = serial.Serial('/dev/ttyACM1',9600, timeout=1)

try:
    while True:
        if ser.in_waiting > 0:
            # Arduinoからデータを読み取り
            line = ser.readline().decode('utf-8').rstrip()
            
            # 読み取ったデータを表示
            # print("Received data from Arduino:", line)
            status = line
            
            print("status: ", status) 
            
            # sousin
            data_to_send = "Hello Arduino from raspberrypi!\n"
            ser.write(data_to_send.encode('utf-8'))
            
            
        time.sleep(1)  # 1秒ごとにデータを確認

except KeyboardInterrupt:
    ser.close()
    print("シリアル通信を閉じました")
