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

from io import BytesIO
import requests
from PIL import Image, ImageDraw
import numpy as np
from time import gmtime, strftime
import threading
import queue
from urllib.request import urlopen
import scipy.misc
from skimage.draw import line_aa


options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.1}

tfnet = TFNet(options)

stream = urlopen('http://140.136.155.137:5002/stream')
bytes = bytes()
while True:
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
        
        cv2.imshow('i', i)
        if cv2.waitKey(1) == 27:
            exit(0)

    

	


