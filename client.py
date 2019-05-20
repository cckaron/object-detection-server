from darkflow.net.build import TFNet
import cv2

from io import BytesIO
import time
import requests
from PIL import Image
import numpy as np

options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.1}

tfnet = TFNet(options)

carsSeen = 0
def handleBird():
    pass

while True:
    r = requests.get('https://i.imgur.com/xbUazh2.jpg') # replace with your ip address
    curr_img = Image.open(BytesIO(r.content))
    curr_img_cv2 = cv2.cvtColor(np.array(curr_img), cv2.COLOR_RGB2BGR)

    # uncomment below to try your own image
    #curr_img = cv2.imread('/sample_img/bird.jpeg')
    result = tfnet.return_predict(curr_img_cv2)
    #print(result)
    for detection in result:
        if detection['label'] == 'car' or detection['label'] == 'truck':
            print("car detected")
            carsSeen += 1
            curr_img.save('cars/%i.jpg' % carsSeen)
    curr_img.save('cars/%i.jpg' % carsSeen)
    print('running again')
    time.sleep(4)