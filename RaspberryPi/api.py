import requests
import time
import tkinter as tk
import serial
import time
import json

# Arduinoのシリアルポートを適切なものに変更
ser = serial.Serial('/dev/ttyACM0',9600, timeout=1)

if ser is None:
    print("serial port cannot be read")


#except KeyboardInterrupt:
 #   ser.close()
  #  print("シリアル通信を閉じました")


def update_display(value):
    display_var.set(value)

# GUIの設定
root = tk.Tk()
root.title("passcode")



# 5けたの数値を表示するラベル
display_var = tk.StringVar()
display_label = tk.Label(root, textvariable=display_var, font=("Arial", 24))
display_label.pack()

# 初期値はゼロ
update_display("00000")
root.update()


# api URL 
url_open = "https://mobazy.vercel.app/api/station/open"
url_passcode = "https://mobazy.vercel.app/api/station/passcode"
url_update = "https://mobazy.vercel.app/api/station/update"

# read json from arduino 
# sample data
status =  "Available"

availableBatteries = 0
if status == "Available":
    availableBatteries = 1
else: 
    availableBatteries = 0

# passcode set 
try:
        # passcode reset GET passcode
        response = requests.get(url_passcode)
        response.raise_for_status()  # エラーがあれば例外を発生させる
        data = response.json()
        
        # JSONデータからpasscodeを取り出す
        passcode = data.get("passcode")

        if passcode is not None:
            print("passcode when system boot: ", passcode)
            update_display(passcode)
            root.update()
        else:
            print("passcodeが見つかりませんでした。")
            
            
            
except requests.exceptions.RequestException as e:
        print("APIへのリクエスト中にエラーが発生しました:", e)
except ValueError as e:
        print("JSONデータの解析中にエラーが発生しました:", e)


# setting passcode reset interval
passcode_update_interval = 3000
isopen_update_interval = 10 
delay_time = 1

passcode_update_count = passcode_update_interval
isopen_update_count = isopen_update_interval
 
count = 1
while True:
    # serial monitor
    if ser.in_waiting > 0:
        # Arduinoからデータを読み取り
        line = ser.readline().decode('utf-8').rstrip()
        
        # 読み取ったデータを表示
        # print("Received data from Arduino:", line)
        status = line
        availableBatteries = 0
        if status == "Available":
            availableBatteries = 1
        else: 
            availableBatteries = 0
        
        print(availableBatteries)
        # jsonData send to server
        jsonData = {
        "availableBatteries" : availableBatteries,
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url_update, data=json.dumps(jsonData), headers=headers)
        
        # レスポンスの表示
        print("Status Code:", response.status_code)
        print("Response Content:", response.text)
       
    
    if count % passcode_update_count  == 0:
        try:
            # passcode reset GET passcode
            response = requests.get(url_passcode)
            response.raise_for_status()  # エラーがあれば例外を発生させる
            data = response.json()

             # JSONデータからpasscodeを取り出す
            passcode = data.get("passcode")

            if passcode is not None:
                print("passcode: ", passcode)
                update_display(passcode)
                root.update()
            else:
                print("passcodeが見つかりませんでした。")
            
            
            
        except requests.exceptions.RequestException as e:
            print("APIへのリクエスト中にエラーが発生しました:", e)
        except ValueError as e:
            print("JSONデータの解析中にエラーが発生しました:", e)

    if count % isopen_update_count == 0:
        try:
            # open GET isopen 
            response = requests.get(url_open)
            response.raise_for_status()  # エラーがあれば例外を発生させる
            data = response.json()

            # JSONデータからisOpenを取り出す
            isOpen = data.get("isOpen")

            if isOpen is not None:
                print("isOpen:", isOpen)
                if isOpen == True:
                    # send isopen that was translate bool to int to arduino 
                    data_to_send = "1"
                    ser.write(data_to_send.encode('utf-8'))
                else:
                    # send isopen that was translate bool to int to arduino 
                    data_to_send = "0"
                    ser.write(data_to_send.encode('utf-8'))
            else:
                print("isOpenが見つかりませんでした。")
        
            # update POST availableBatteries

        except requests.exceptions.RequestException as e:
            print("APIへのリクエスト中にエラーが発生しました:", e)
        except ValueError as e:
            print("JSONデータの解析中にエラーが発生しました:", e)
           
    # delay 5 secound
    time.sleep(delay_time)
    count += 1
        
