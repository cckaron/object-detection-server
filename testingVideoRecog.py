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

options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.1}

tfnet = TFNet(options)

def handleBird():
    pass

def lineNotify(token, msg):
    headers = {
            "Authorization": "Bearer " + token, 
            "Content-Type" : "application/x-www-form-urlencoded"
            }
    payload = {'message': msg}
    try:
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload, timeout=3)
        return r.status_code
    except:
        return None

def getCarCount(url, cam_id):
    carsSeen = 0
    try:
        vcap = cv2.VideoCapture('http://140.136.155.137:5003/stream')
        
        while(True):
            # Capture frame-by-frame
            ret, frame = vcap.read()
            #print cap.isOpened(), ret
            if frame is not None:
            
#                curr_img = Image.open(BytesIO(frame.content))
#                curr_img_cv2 = cv2.cvtColor(np.array(curr_img), cv2.COLOR_RGB2BGR)
#                result = tfnet.return_predict(curr_img_cv2)
#                draw = ImageDraw.Draw(curr_img)
#                # uncomment below to try your own image
#                #curr_img = cv2.imread('/sample_img/bird.jpeg')
#                result = tfnet.return_predict(curr_img_cv2)
#                draw = ImageDraw.Draw(curr_img)
#                #print(result)
#                for detection in result:
#                    if detection['label'] == 'people':
#                        carsSeen += 1
#                        #curr_img.save('cars/%i.jpg' %calculator)
#                        
#                        draw.rectangle([detection['topleft']['x'], detection['topleft']['y'], 
#                                        detection['bottomright']['x'], detection['bottomright']['y']],
#                            outline=(255, 0, 0))
#                        draw.text([detection['topleft']['x'], detection['topleft']['y'] - 13], detection['label'], fill=(255, 0, 0))
#                        
#                        time = strftime("%Y-%m-%d%H-%M-%S", gmtime())
#                        curr_img.save('cars/cam%d_%s.jpg' %(cam_id, time))
#                
#                # Display the resulting frame
                cv2.imshow('frame',frame)
                # Press q to close the video windows before it ends if you want
                if cv2.waitKey(22) & 0xFF == ord('q'):
                    break
            else:
                print("Frame is None")
                break
    except:
        print("except happen")
            
        

while True:
    que = queue.Queue();
    thread_list = list();
    
    cam_1 = threading.Thread(target=lambda q, arg1, arg2: q.put(getCarCount(arg1, arg2)), args=(que, 'http://192.168.0.103:5000/stream', 1))

    cam_1.start()
    thread_list.append(cam_1);

    

	



