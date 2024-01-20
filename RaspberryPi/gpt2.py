import requests
import time
import tkinter as tk
import serial
import json

# Arduinoのシリアルポートを適切なものに変更
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)

if ser is None:
    print("serial port cannot be read")

# GUIの設定
root = tk.Tk()
root.title("passcode")

# 5けたの数値を表示するラベル
display_var = tk.StringVar()
display_label = tk.Label(root, textvariable=display_var, font=("Arial", 200), width=40)
display_label.pack()


# APIのURL
url_open = "https://mobazy.vercel.app/api/station/open"
url_passcode = "https://mobazy.vercel.app/api/station/passcode"
url_update = "https://mobazy.vercel.app/api/station/update"


def update_display(value):
    display_var.set(value)
    root.update()


def get_passcode():
    try:
        response = requests.get(url_passcode)
        response.raise_for_status()
        data = response.json()
        passcode = data.get("passcode")
        if passcode is not None:
            print("passcode: ", passcode)
            update_display(passcode)
        else:
            print("passcodeが見つかりませんでした。")
    except requests.exceptions.RequestException as e:
        print("APIへのリクエスト中にエラーが発生しました:", e)
    except ValueError as e:
        print("JSONデータの解析中にエラーが発生しました:", e)


def send_isopen():
    try:
        response = requests.get(url_open)
        response.raise_for_status()
        data = response.json()
        isOpen = data.get("isOpen")
        if isOpen is not None:
            print("蓋をあける？:", isOpen)
            data_to_send = "1" if isOpen else "0"
            ser.write(data_to_send.encode("utf-8"))
        else:
            print("isOpenが見つかりませんでした。")
    except requests.exceptions.RequestException as e:
        print("APIへのリクエスト中にエラーが発生しました:", e)
    except ValueError as e:
        print("JSONデータの解析中にエラーが発生しました:", e)


# 初期値はゼロ
get_passcode()
root.update()

# setting passcode reset interval
passcode_update_interval = 3000
isopen_update_interval = 10
delay_time = 1

passcode_update_count = passcode_update_interval
isopen_update_count = isopen_update_interval

# 一個前の利用可能なバッテリーの数をキャッシュしてapiに送る頻度を減らす
previous_availableBatteries = 0

count = 1
while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode("utf-8").rstrip()
        status = line
        available_batteries = 1 if status == "Available" else 0
        print("利用可能なバッテリー数: " + str(available_batteries))
        if previous_availableBatteries != available_batteries:
            previous_availableBatteries = available_batteries
            jsonData = {"availableBatteries": available_batteries}
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                url_update, data=json.dumps(jsonData), headers=headers
            )
            print("Status Code:", response.status_code)
            print("Response Content:", response.text)

    if count % passcode_update_count == 0:
        get_passcode()

    if count % isopen_update_count == 0:
        send_isopen()

    time.sleep(delay_time)
    count += 1
