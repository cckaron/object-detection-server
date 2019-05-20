from darkflow.net.build import TFNet
import cv2
import numpy as np
from urllib.request import urlopen
import sys
import math

options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 5}

tfnet = TFNet(options)

#sys.argv[0]
URL = "rtsp://192.168.50.246:8080/h264_pcm.sdp"
ipcam = cv2.VideoCapture(URL)

while True:
    stat, i = ipcam.read()
#    i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR) #<class 'numpy.ndarray'>
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

    

	


