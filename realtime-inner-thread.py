# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 13:42:23 2019

@author: chaos
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 13:29:40 2019

@author: chaos
"""

from darkflow.net.build import TFNet
import cv2
import numpy as np
from urllib.request import urlopen
import sys
import math
import threading
import time

options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.2}

tfnet = TFNet(options)



 
class MyThread (threading.Thread):
 
    def __init__(self, url):
        self.__url = url
        self.bytes = bytes()
        threading.Thread.__init__(self)
 
    def run (self):
        stream = urlopen(self.__url)
        
        while True:
            self.bytes += stream.read(1024)
            a = self.bytes.find(b'\xff\xd8')
            b = self.bytes.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg =  self.bytes[a:b+2]
                self.bytes =  self.bytes[b+2:]
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
        
                cv2.imshow('i', i)
                if cv2.waitKey(1) == 27:
                    exit(0)
 
# Start 10 threads.
MyThread('http://192.168.50.172:5000/stream').start()
MyThread('http://192.168.50.172:5001/stream').start()
MyThread('http://192.168.50.206:5002/stream').start()

