# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 15:21:08 2019

@author: Darkflow
"""

# -*- coding: utf-8 -*-
import cv2
import time
import threading

from darkflow.net.build import TFNet
import cv2
import numpy as np
from urllib.request import urlopen
import sys
import math

options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.005}

tfnet = TFNet(options)



# 接收攝影機串流影像，採用多執行緒的方式，降低緩衝區堆疊圖幀的問題。
class ipcamCapture:
    def __init__(self, URL):
        self.Frame = []
        self.status = False
        self.isstop = False
		
	# 攝影機連接。
        self.capture = cv2.VideoCapture(URL)

    def start(self):
	# 把程式放進子執行緒，daemon=True 表示該執行緒會隨著主執行緒關閉而關閉。
        print('ipcam started!')
        threading.Thread(target=self.queryframe, daemon=True, args=()).start()

    def stop(self):
	# 記得要設計停止無限迴圈的開關。
        self.isstop = True
        print('ipcam stopped!')
   
    def getframe(self):
	# 當有需要影像時，再回傳最新的影像。
        return self.Frame
        
    def queryframe(self):
        while (not self.isstop):
            self.status, self.Frame = self.capture.read()
        
        self.capture.release()

#sys.argv[0]
stream = urlopen('http://192.168.50.172:5000/stream')

URL = "rtsp://admin:admin@192.168.1.1/video.h264"

# 連接攝影機
ipcam = ipcamCapture(URL)

# 啟動子執行緒
ipcam.start()

# 暫停1秒，確保影像已經填充
time.sleep(1)

bytes = bytes()
# 使用無窮迴圈擷取影像，直到按下Esc鍵結束
while True:
    # 使用 getframe 取得最新的影像
    I = ipcam.getframe()
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR) #<class 'numpy.ndarray'>
        result = tfnet.return_predict(i)
#        print(result)
        
        for detection in result:
            if detection['label'] == 'car':   
                cv2.rectangle(i, (detection['topleft']['x'], detection['topleft']['y']), 
                              (detection['bottomright']['x'], detection['bottomright']['y']), 
                              3)
                cv2.putText(i, detection['label'], 
                            (detection['topleft']['x'], detection['topleft']['y'] - 13),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
    #            print(detection)
                cv2.putText(i, str(math.floor(detection['confidence']*100)), 
                            (detection['topleft']['x'], detection['topleft']['y'] + 13),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA) 
    
    cv2.imshow('Image', I)
    if cv2.waitKey(1000) == 27:
        cv2.destroyAllWindows()
        ipcam.stop()
        break