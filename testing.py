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
import boto3

options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.1}

tfnet = TFNet(options) 
_token = '5k7uMtqb0zcem4NRSBKaZRZflCURVUV2ALdoMyxck17' #管理單位
token = 'LUfgCGAPsb8bbG9ZiyPtWFE1UeH96dAZfigid9VAz1O' #維修單位
maintenance_url = 'http://127.0.0.1/api/maintenance/generate'
arnID='arn:aws:sns:ap-northeast-1:769755876697:teammebers'
message='1'
count_dict = {"cam1":0, "cam2":0, "cam3":0, "cam4":0}

OPEN_NOTIFY = False
OPEN_RULE = False

lastSecond = 0

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

def sns(message):
    print("發sns")
    print(message)
    print(type(message))
    sns = boto3.client(
    'sns',
    aws_access_key_id="AKIAIMAEWOGKRCCGOLZA",
    aws_secret_access_key="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",
    region_name='ap-northeast-1',
    )

    sns.publish(
        TargetArn = str(arnID),
        Message = str(message)
    )

    return None

def lineNotify(token, msg, camID):
    headers = {
            "Authorization": "Bearer " + token, 
            }
    payload = {'message': msg}

    if (camID == 0):
        try:
            session = requests.Session()
            r = session.post("https://notify-api.line.me/api/notify", headers = headers, params = payload, timeout=3)
            print(r.status_code)
            print("success(pure message)")
            return None
        except:
            print("error(pure message)")
            return None
    
    url = "C:/Users/Darkflow/Desktop/darkflow/cars/cam"+str(camID)+".jpg"
    imageFile = {'imageFile': open(url, 'rb')}
    
    try:
        session = requests.Session()
        r = session.post("https://notify-api.line.me/api/notify", headers = headers, params = payload, files=imageFile, timeout=3)
        return r.content
    except:
        return None

def isHardwareFail():
    try:
        get_second = requests.get("http://192.168.50.126/", timeout=3)
        print("hardware health")
        return False
    except:
        print('Hardware Failed')
        return True

def getCarCount(url, cam_id):
    carsSeen = 0
    try:
        r = requests.get(url, timeout=5)
    except:
        #鏡頭無回應
        print("camID:", cam_id, " timeout.")
        image = pygame.image.load('cars/error.jpg')
        picture = pygame.transform.scale(image, (640, 360))
        screen.blit(picture, cam_pic[cam_id])
        pygame.display.update()
        #如果開啟通知功能
        if (OPEN_NOTIFY):
            #laravel 產生維修單
            try:
                headers = {'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC8xMjcuMC4wLjFcL2FwaVwvYXV0aFwvbG9naW4iLCJpYXQiOjE1NTgzNDk5MTcsImV4cCI6MTU2Njk4OTkxNywibmJmIjoxNTU4MzQ5OTE3LCJqdGkiOiIxUlNTUlEwU0xDTFhHbEVGIiwic3ViIjoxLCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.Q42vS5ZghcT4uRAFccoQIZfBWHBBx8vLJ-BjYkuQDQY"}
                payload = {'intersections_id': 1, 'content': '[C01]鏡頭1無回應'}
                url = "C:/Users/Darkflow/Desktop/darkflow/cars/cam"+str(cam_id)+".jpg"
                imageFile = {'imageFile': open(url, 'rb')}
                maintenance = requests.post(maintenance_url, headers = headers, params=payload, files = imageFile)
                print(maintenance.content)
            except:
                print('Laravel API Timeout(maintenance)')

            #發sns
            try:
                sns("[C01]鏡頭1無回應")
            except:
                print("sns error")

            #發line notify
            message = '[C01]鏡頭1無回應'
            print(lineNotify(token, message, 0))
            print(lineNotify(token, message, cam_id))
            

        return 0

    curr_img = Image.open(BytesIO(r.content))
    curr_img_cv2 = cv2.cvtColor(np.array(curr_img), cv2.COLOR_RGB2BGR)
    result = tfnet.return_predict(curr_img_cv2)
    draw = ImageDraw.Draw(curr_img)

    for detection in result:
        if detection['label'] == 'car':
            carsSeen += 1
            #curr_img.save('cars/%i.jpg' %calculator)
                
            draw.rectangle([detection['topleft']['x'], detection['topleft']['y'], 
                    detection['bottomright']['x'], detection['bottomright']['y']],
                    outline=(255, 0, 0))
            draw.text([detection['topleft']['x'], detection['topleft']['y'] - 13], detection['label'], fill=(255, 0, 0))        
        
    # if carsSeen >= 0:
    curr_img.save('cars/cam%d.jpg' %(cam_id))

    image = pygame.image.load('cars/cam{}.jpg'.format(cam_id))
    picture = pygame.transform.scale(image, (640, 360))
    screen.blit(picture, cam_pic[cam_id])
    pygame.display.update()
        
    message = "鏡頭"+str(cam_id)+"偵測到車輛:"+str(carsSeen)+"台"
    
    # if (OPEN_NOTIFY):
    #     print(lineNotify(token, message, cam_id))

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

    if (int(round(time.time())) - lastUpdated > 6):
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
        
        road1_car_count = count_dict["cam1"] + count_dict["cam2"]
        road2_car_count = count_dict["cam3"] + count_dict["cam4"]
        
        if OPEN_RULE:
            judgeURL = "http://192.168.50.46/judgeRule/1/{road1}/{road2}/1".format(road1=road1_car_count, road2=road2_car_count)
            lineNotify(_token, '中正路/建國一路交叉口 已套用規則', 0)
        else:
            judgeURL = "http://192.168.50.46/judgeRule/1/{road1}/{road2}/0".format(road1=road1_car_count, road2=road2_car_count)

        print("url:", judgeURL)
        try:
            currentRule = requests.get(judgeURL, timeout=2)
            print("Rule Judge: {id}".format(id=currentRule.content))
        except:
            print("Laravel API Timeout(judge rule)")
        finally:
            lastUpdated = int(round(time.time()))

            #硬體異常
            if (isHardwareFail()):
                #如果開啟通知功能
                if (OPEN_NOTIFY):
                    #laravel 產生維修單
                    try:
                        headers = {'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC8xMjcuMC4wLjFcL2FwaVwvYXV0aFwvbG9naW4iLCJpYXQiOjE1NTgzNDk5MTcsImV4cCI6MTU2Njk4OTkxNywibmJmIjoxNTU4MzQ5OTE3LCJqdGkiOiIxUlNTUlEwU0xDTFhHbEVGIiwic3ViIjoxLCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.Q42vS5ZghcT4uRAFccoQIZfBWHBBx8vLJ-BjYkuQDQY"}
                        payload = {'intersections_id': 1, 'content': '[A01]硬體控制器異常'}
                        maintenance = requests.post(maintenance_url, headers = headers, params=payload)
                        print(maintenance.content)
                    except:
                        print('Laravel API Timeout(hardware maintenance)')

                    #發sns
                    try:
                        sns("[A01]硬體控制器異常")
                    except:
                        print("sns error(hardware)")

                    #發line notify
                    message = '[A01]硬體控制器異常'
                    print(lineNotify(token, message, 0))




