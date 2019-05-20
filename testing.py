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
from time import gmtime, strftime
import threading
import queue
import time
import pygame 


options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.1}

tfnet = TFNet(options)
#token = '4uYSu9DwcB8AnOBSleXZeRptHgsPWqjBpZrawAlvuqd'
token = '36bGvXvbE6ZMOfruJSF5Poq7GDwHQAF6HmCcleehSoK'

count_dict = {"cam1":0, "cam2":0, "cam3":0, "cam4":0}
OPEN_NOTIFY = False
OPEN_RULE = False
lastUpdated = int(round(time.time()))
pygame.init() 

cam_pic = {
    1: [0, 0],
    2: [640, 0],
    3: [0, 360],
    4: [640, 360]
}
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('監控台')

def lineNotify(token, msg, camID):
    headers = {
            "Authorization": "Bearer " + token, 
            }
    url = "C:/Users/Darkflow/Desktop/darkflow/cars/cam"+str(camID)+".jpg"
    imageFile = {'imageFile': open(url, 'rb')}
    payload = {'message': msg}
    try:
        session = requests.Session()
        r = session.post("https://notify-api.line.me/api/notify", headers = headers, params = payload, files=imageFile, timeout=3)
        return r.content
    except:
        return None

def getCarCount(url, cam_id):
    carsSeen = 0
    try:
        r = requests.get(url, timeout=5)
    except:
        print("camID:", cam_id, " timeout.")
        return 0

    curr_img = Image.open(BytesIO(r.content))
    curr_img_cv2 = cv2.cvtColor(np.array(curr_img), cv2.COLOR_RGB2BGR)
    result = tfnet.return_predict(curr_img_cv2)
    draw = ImageDraw.Draw(curr_img)
    # uncomment below to try your own image
    #curr_img = cv2.imread('/sample_img/bird.jpeg')
#        result = tfnet.return_predict(curr_img_cv2)
#        draw = ImageDraw.Draw(curr_img)
    #print(result)
    for detection in result:
        if detection['label'] == 'car'or detection['label'] == 'motorbike':
            carsSeen += 1
            #curr_img.save('cars/%i.jpg' %calculator)
                
            draw.rectangle([detection['topleft']['x'], detection['topleft']['y'], 
                    detection['bottomright']['x'], detection['bottomright']['y']],
                    outline=(255, 0, 0))
            draw.text([detection['topleft']['x'], detection['topleft']['y'] - 13], detection['label'], fill=(255, 0, 0))
        
#        time = strftime("%Y-%m-%d%H-%M-%S", gmtime())
        
        
    if carsSeen >= 0:
#            curr_img.save('cars/cam%d_%s.jpg' %(cam_id, time))
        curr_img.save('cars/cam%d.jpg' %(cam_id))

        image = pygame.image.load('cars/cam{}.jpg'.format(cam_id))
        picture = pygame.transform.scale(image, (640, 360))
        screen.blit(picture, cam_pic[cam_id])
        pygame.display.update()
            
        message = "鏡頭"+str(cam_id)+"偵測到車輛:"+str(carsSeen)+"台"
        
        if (OPEN_NOTIFY):
            print(lineNotify(token, message, cam_id))
    
        print("camera %d: %d cars detected"%(cam_id, carsSeen))

    count_dict["cam"+str(cam_id)] = carsSeen
    return carsSeen

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                if (OPEN_NOTIFY == True):
                    OPEN_NOTIFY = False
                    print("CLOSE NOTIFY")
                else:
                    OPEN_NOTIFY = True
                    print("OPEN NOTIFY")
            elif event.key == pygame.K_b:
                if (OPEN_RULE == True):
                    OPEN_RULE = False
                    print("CLOSE RULE")
                else:
                    OPEN_RULE = True
                    print("OPEN RULE")

    key = pygame.key.get_pressed()
    if key[pygame.K_ESCAPE]:
        exit()

    if (int(round(time.time())) - lastUpdated > 3):
        que = queue.Queue();
        thread_list = list();
        
        cam_1 = threading.Thread(target=lambda q, arg1, arg2: q.put(getCarCount(arg1, arg2)), args=(que, 'http://192.168.50.172:5000/image', 1))
        cam_2 = threading.Thread(target=lambda q, arg1, arg2: q.put(getCarCount(arg1, arg2)), args=(que, 'http://192.168.50.172:5001/image', 2))
        cam_3 = threading.Thread(target=lambda q, arg1, arg2: q.put(getCarCount(arg1, arg2)), args=(que, 'http://192.168.50.206:5002/image', 3))
        cam_4 = threading.Thread(target=lambda q, arg1, arg2: q.put(getCarCount(arg1, arg2)), args=(que, 'http://192.168.50.206:5003/image', 4))
        cam_1.start()
        thread_list.append(cam_1);
        cam_2.start()
        thread_list.append(cam_2);
        cam_3.start()
        thread_list.append(cam_3);
        cam_4.start()
        thread_list.append(cam_4);

        print("thread_list:", thread_list)
        for t in thread_list:
            t.join()

        while que.qsize() != 4:
            continue

        cam1_count = que.get()
        cam2_count = que.get()
        cam3_count = que.get()
        cam4_count = que.get()

        print("cam1:", count_dict["cam1"])
        print("cam2:", count_dict["cam2"])
        print("cam3:", count_dict["cam3"])
        print("cam4:", count_dict["cam4"])
        
        #road1_car_count = cam1_count +  cam2_count
        #road2_car_count = cam3_count + cam4_count
        road1_car_count = count_dict["cam1"] + count_dict["cam2"]
        road2_car_count = count_dict["cam3"] + count_dict["cam4"]
        
        if OPEN_RULE:
            judgeURL = "http://192.168.50.46/judgeRule/1/{road1}/{road2}/1".format(road1=road1_car_count, road2=road2_car_count)
        else:
            judgeURL = "http://192.168.50.46/judgeRule/1/{road1}/{road2}/0".format(road1=road1_car_count, road2=road2_car_count)

        print("url:", judgeURL)
        try:
            currentRule = requests.get(judgeURL, timeout=2)
            print("Rule Judge: {id}".format(id=currentRule.content))
        except:
            print("laravel time out")
        finally:
            lastUpdated = int(round(time.time()))



