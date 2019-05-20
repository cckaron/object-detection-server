# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 13:29:40 2019

@author: chaos
"""

from darkflow.net.build import TFNet
import cv2

from io import BytesIO
import time
import requests
from PIL import Image, ImageDraw
import numpy as np

options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.1}

tfnet = TFNet(options)

carsSeen = 0
calculator = 0
def handleBird():
    pass

while True:
    r = requests.get('https://oralcancerfoundation.org/wp-content/uploads/2016/03/people.jpg') # replace with your ip address
    curr_img = Image.open(BytesIO(r.content))
    curr_img_cv2 = cv2.cvtColor(np.array(curr_img), cv2.COLOR_RGB2BGR)
    calculator += 1
    
    # uncomment below to try your own image
    #curr_img = cv2.imread('/sample_img/bird.jpeg')
    result = tfnet.return_predict(curr_img_cv2)
    draw = ImageDraw.Draw(curr_img)
    #print(result)
    for detection in result:
        if detection['label'] == 'person':
            print("car detected")
            carsSeen += 1
            #curr_img.save('cars/%i.jpg' %calculator)
            
            draw.rectangle([detection['topleft']['x'], detection['topleft']['y'], 
                    detection['bottomright']['x'], detection['bottomright']['y']],
                    outline=(255, 0, 0))
            draw.text([detection['topleft']['x'], detection['topleft']['y'] - 13], detection['label'], fill=(255, 0, 0))
    curr_img.save('cars/%i.jpg' %calculator)
    print('running again')
    time.sleep(4)