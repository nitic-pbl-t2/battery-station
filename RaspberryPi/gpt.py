import wx
import requests
import time
import serial
import json
import threading
import os


class MyFrame(wx.Frame):
    url_open = "https://mobazy.vercel.app/api/station/open"
    url_passcode = "https://mobazy.vercel.app/api/station/passcode"
    url_update = "https://mobazy.vercel.app/api/station/update"

    # シリアルポートの読み込み
    ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
    if ser is None:
        print("シリアルポートを開けませんでした。")

    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        panel = wx.Panel(self)
        self.display_label = wx.StaticText(
            panel, label="00000", pos=(10, 10), style=wx.ALIGN_CENTER
        )
        self.display_label.SetFont(wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        self.Bind(wx.EVT_CLOSE, self.on_close)

        # スレッドを作成してデータの取得・表示を実行
        self.thread = threading.Thread(target=self.update_data)
        self.thread.daemon = True
        self.thread.start()

        self.Show()

    def on_close(self, event):
        # ウィンドウが閉じられたときにスレッドを停止する
        self.thread.join()
        event.Skip()

    def update_display(self, value):
        wx.CallAfter(self.display_label.SetLabel, str(value))

    def passcode_update(self):
        try:
            # passcode reset GET passcode
            response = requests.get(self.url_passcode)
            response.raise_for_status()  # エラーがあれば例外を発生させる
            data = response.json()

            # JSONデータからpasscodeを取り出す
            passcode = data.get("passcode")

            if passcode is not None:
                print("passcode: ", passcode)
                self.update_display(passcode)
            else:
                print("passcodeが見つかりませんでした.")

        except requests.exceptions.RequestException as e:
            print("APIへのリクエスト中にエラーが発生しました:", e)
        except ValueError as e:
            print("JSONデータの解析中にエラーが発生しました:", e)

    def isopen_update(self):
        try:
            # open GET isopen
            response = requests.get(self.url_open)
            response.raise_for_status()  # エラーがあれば例外を発生させる
            data = response.json()

            # JSONデータからisOpenを取り出す
            isOpen = data.get("isOpen")

            if isOpen is not None:
                print("isOpen:", isOpen)
                if isOpen:
                    # send isopen that was translate bool to int to arduino
                    data_to_send = "1"
                    self.ser.write(data_to_send.encode("utf-8"))
                else:
                    # send isopen that was translate bool to int to arduino
                    data_to_send = "0"
                    self.ser.write(data_to_send.encode("utf-8"))
            else:
                print("isOpenが見つかりませんでした.")

        except requests.exceptions.RequestException as e:
            print("APIへのリクエスト中にエラーが発生しました:", e)
        except ValueError as e:
            print("JSONデータの解析中にエラーが発生しました:", e)

    def update_data(self):
        passcode_update_interval = 3000
        isopen_update_interval = 10
        delay_time = 1

        passcode_update_count = passcode_update_interval
        isopen_update_count = isopen_update_interval

        count = 1
        while True:
            # serial monitor
            # if ser.in_waiting > 0:
            #     line = ser.readline().decode('utf-8').rstrip()
            #     status = line
            #     availableBatteries = 0
            #     if status == "Available":
            #         availableBatteries = 1
            #     else:
            #         availableBatteries = 0

            #     print(availableBatteries)
            #     # jsonData send to server
            #     jsonData = {
            #         "availableBatteries": availableBatteries,
            #     }
            #     headers = {"Content-Type": "application/json"}
            #     response = requests.post(self.url_update, data=json.dumps(jsonData), headers=headers)

            #     # レスポンスの表示
            #     print("Status Code:", response.status_code)
            #     print("Response Content:", response.text)

            if count % passcode_update_count == 0:
                self.passcode_update()

            if count % isopen_update_count == 0:
                self.isopen_update()

            # delay 1 sec
            time.sleep(delay_time)
            count += 1


if __name__ == "__main__":
    os.system("sudo bash ./boot.sh")
    app = wx.App(False)
    frame = MyFrame(None, title="wxPython Example")
    app.MainLoop()
