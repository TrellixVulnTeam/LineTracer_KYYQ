# コマンドの送信用gui
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
# Kivy 上で Matplotlib を使うために必要な準備
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
import re
import serial
import threading

# 定数
FRAME_TIME = 10 # 更新間隔(ms)
FRAME_NUM = 200 # 画面に表示するデータ数

commands = [] # 送信待ちコマンド
light1 = np.zeros(FRAME_NUM)
light2 = np.zeros(FRAME_NUM)

class MainScreen3(BoxLayout):
    def on_enter(self, value):
        global commands
        commands.append(value)
        print(value)

class GraphView(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        global FRAME_TIME
        global FRAME_NUM

        # 初期化に用いるデータ
        x = np.linspace(1,FRAME_NUM,FRAME_NUM)
        y1 = y2 = np.zeros(FRAME_NUM)

        # Figure, Axis を保存しておく
        self.fig, self.ax = plt.subplots()
        # 最初に描画したときの Line も保存しておく
        self.line1, = self.ax.plot(x, y1)
        self.line2, = self.ax.plot(x, y2)

        # ウィジェットとしてグラフを追加する
        widget = FigureCanvasKivyAgg(self.fig)
        self.add_widget(widget)

        # frame_time秒ごとに表示を更新するタイマーを仕掛ける
        Clock.schedule_interval(self.update_view, FRAME_TIME/1000)

    def update_view(self, *args, **kwargs):

        global light1
        global light2

        # データを更新する
        x = np.linspace(1,FRAME_NUM,FRAME_NUM)
        y1 = light1[-FRAME_NUM:]
        y2 = light2[-FRAME_NUM:]

        # Line にデータを設定する
        self.line1.set_data(x, y1)
        self.line2.set_data(x, y2)
        # グラフの見栄えを調整する
        self.ax.relim()
        self.ax.autoscale_view()
        # 再描画する
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

class Controller3App(App):
    def __init__(self, **kwargs):
        super(Controller3App, self).__init__(**kwargs)

    def build(self):
        serialClient = SerialClient()
        serialClient.start()
        screen = MainScreen3()
        return screen

# シリアル通信受信クラス
class SerialClient():
    def start(self):
        serial_thread = threading.Thread(target=self.serial_method, daemon=True)
        serial_thread.start()
    
    # シリアル通信用スレッドの実装部
    def serial_method(self):
        global commands
        ser = serial.Serial("COM5",9600) # シリアル通信

        while True:
            line = ser.readline()
            line = line.decode().rstrip('\r\n')
            receives = re.split(',', line)
            for receive in receives:
                x = re.split(':', receive)
                if x[0] == 'light1':
                    global light1
                    light1 = np.append(light1, int(x[1]))
                elif x[0] == 'light2':
                    global light2
                    light2 = np.append(light2, int(x[1]))

            # 送信
            if len(commands) > 0:
                for command in commands:
                    ser.write(command)
                commands = []   

if __name__ == '__main__':
    Controller3App().run()