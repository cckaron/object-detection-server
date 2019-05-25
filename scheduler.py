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
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from time import gmtime, strftime
import threading
import queue
import pygame 
import boto3
import json
import webbrowser

#darkflow
options = {"model": "cfg/yolo.cfg", "load": "bin/yolov2.weights", "threshold": 0.1}
tfnet = TFNet(options) 

#line notify
_token = '5k7uMtqb0zcem4NRSBKaZRZflCURVUV2ALdoMyxck17' #管理單位
token = 'LUfgCGAPsb8bbG9ZiyPtWFE1UeH96dAZfigid9VAz1O' #維修單位

#laravel API
maintenance_url = 'http://127.0.0.1/api/maintenance/generate'

#sns
arnID='arn:aws:sns:ap-northeast-1:158673690354:teammebers'
count_dict = {"cam1":0, "cam2":0, "cam3":0, "cam4":0}

#功能開關(default=False)
OPEN_NOTIFY = False
OPEN_RULE = False

#排程時間
timegap = 1

#記錄 物件辨識最後一次的執行時間
lastUpdated = int(round(time.time()))

#pygame 基本設定
pygame.init() 
pygame.font.init()
screen = pygame.display.set_mode((1280, 870))
image = pygame.image.load('cars/error.jpg')
icon = pygame.image.load('images/icon.png')
warning = pygame.image.load("warning.png")
pygame.display.set_caption('監控台')
pygame.display.set_icon(icon)

#pygame 各鏡頭圖片位置
camPic_pos = {
    1: [0, 150],
    2: [640, 150],
    3: [0, 510],
    4: [640, 510]
}

#pygame 各鏡頭文字位置
camTitle_pos = {
    1: [1, 160],
    2: [650, 160],
    3: [10, 520],
    4: [650, 520]
}

cam_title = {
    1: pygame.image.load('images/cam1_title.png'),
    2: pygame.image.load('images/cam2_title.png'),
    3: pygame.image.load('images/cam3_title.png'),
    4: pygame.image.load('images/cam4_title.png')
}

#初始畫面
icon_color = pygame.image.load('images/icon_color.png')
icon = pygame.transform.scale(icon_color, (300, 300))
screen.blit(icon, (160, 230))

#pygame 文字位置
font_title = pygame.font.Font('fonts/NotoSansCJKtc-Regular.otf', 40)
font_init_message = pygame.font.Font('fonts/NotoSansCJKtc-Regular.otf',80)

#起始訊息
init_message = font_init_message.render("監控系統啟動中", True, (255, 255, 255))
screen.blit(init_message, (450, 350))

#地址
district = font_title.render("新北市 新莊區", True, (255, 255, 0))
street = font_title.render("中正路/建國一路 交叉口", True, (0, 255, 0))
screen.blit(district, (10, 10))
screen.blit(street, (10, 70))

#模式
rule_status_title = font_title.render("號誌控制模式: ", True, (255, 255, 255))
rule_status = font_title.render("手動", True, (255, 0, 0))
screen.blit(rule_status_title, (840, 10))
screen.blit(rule_status, (1100, 10))

#開啟網站系統
btn_openWebsite = pygame.image.load('images/icon_color.png')
icon = pygame.transform.scale(icon_color, (80, 80))
screen.blit(icon, (1200, 10))

#推播
notify_status_title = font_title.render("推播功能: ", True, (255, 255, 255))
notify_status = font_title.render("關閉", True, (255, 0, 0))
screen.blit(notify_status_title, (920, 70))
screen.blit(notify_status, (1100, 70))

#更新畫面
pygame.display.update()

#PIL draw on picture
pilFont = ImageFont.truetype("fonts/NotoSansCJKtc-Regular.otf", 40)

def pygame_event():
    global OPEN_NOTIFY
    global OPEN_RULE

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            
            #符合點擊區域
            if (pos[0] > 1100 and pos[0] < 1200):
                #規則
                if (pos[1] > 0 and pos[1] < 60):
                    screen.fill(pygame.Color("black"), (1100, 0, 1500, 65))
                    if (OPEN_RULE == True):
                        OPEN_RULE = False
                        rule_status = font_title.render("手動", True, (255, 0, 0))
                        screen.blit(rule_status, (1100, 10))
                        print("close rule")
                    else:
                        OPEN_RULE = True
                        rule_status = font_title.render("自動", True, (255, 255, 0))
                        screen.blit(rule_status, (1100, 10))
                        print("open rule")
                    return True
                #通知
                elif (pos[1] > 60 and pos[1] < 120):
                    screen.fill(pygame.Color("black"), (1100, 70, 1500, 120))
                    if (OPEN_NOTIFY == True):
                        OPEN_NOTIFY = False
                        notify_status = font_title.render("關閉", True, (255, 0, 0))
                        screen.blit(notify_status, (1100, 70))
                        print("close notify")
                    else:
                        OPEN_NOTIFY = True
                        notify_status = font_title.render("開啟", True, (255, 255, 0))
                        screen.blit(notify_status, (1100, 70))
                        print("open notify")
                    return True
    return False

def sns(message):
    print("發sns")
    print(message)
    print(type(message))
    sns = boto3.client(
    'sns',
    aws_access_key_id="ASIASJ4NQL3ZFNARXOVT",
    aws_secret_access_key="yb1raszFyYPRhSRfx13LPgvqENwjxgy3LcxGWkT0",
    aws_session_token='FQoGZXIvYXdzEL3//////////wEaDGqM9KmXLyko7i5S4SKEA7LLcdJk5KDDu/peNrbZxUCB4p7A6Nrb/tbQrjGEiybmLfrUNwOgwKuabFc5UOUUXiCqeztloZBfgzuL2mvqxeYSabms5Y98ZuYNldoFkc9xjyialmil4V71cD0WCkDAd/OStwBfKglmLM2fGpYYKEB70AQIh7OLKnSNn4Eh9NbyGpM0uhiQuedv/TuQj1+Tno3XDVFyOVJn8QTj3ik8vJMmNSf/78GVVW89QVWY27jONcKN1bz/00dF9Q7tUCVx7KIjun7SSqD7AMsRrTkWJn+mzh88j6o6YtoB0CLxd93XAs6OS29a4pqDRSQywqT9z0bUgKjhP1aqdr3CQejWnKmv4UgEO1VZ2cgYSF5gX8xbGqoqxinNix7erraNvNztjLncDlqA2HL9/9T6RV1pK1OK+ogdVZmqChIErXPxbTAs4rP6Ar3lcnj7D2nh0WAzhn2Mkld3qsMvFXeE/EEsvf/ktpFvA9huif0C8N+A4BDXt14B/5PlTrCR0M8vA57ZbsMO8Z0ohZ6Y5wU=',
    region_name='ap-southeast-2',
    )

    sns.publish(
        TopicArn='arn:aws:sns:ap-southeast-2:158673690354:mytopic',
        Message = message
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

def isHardwareAlive():
    try:
        get_second = requests.get("http://192.168.50.126/", timeout=3)
        print("hardware health")
        return True
    except:
        print('Hardware Failed')
        return False

def hardwareHealthCheck():
    #硬體無回應
    if not isHardwareAlive():
        if (OPEN_NOTIFY):
            #laravel 產生維修單
            try:
                headers = {'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC8xMjcuMC4wLjFcL2FwaVwvYXV0aFwvbG9naW4iLCJpYXQiOjE1NTgzNDk5MTcsImV4cCI6MTU2Njk4OTkxNywibmJmIjoxNTU4MzQ5OTE3LCJqdGkiOiIxUlNTUlEwU0xDTFhHbEVGIiwic3ViIjoxLCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.Q42vS5ZghcT4uRAFccoQIZfBWHBBx8vLJ-BjYkuQDQY"}
                payload = {'intersections_id': 1, 'content': '[A01]硬體控制器異常'}
                maintenance = requests.post(maintenance_url, headers = headers, params=payload)
                response_data = json.loads(maintenance.text)

                #代表維修單正常生成，未重複
                if (response_data["notify"] == 1):
                    #發sns
                    try:
                        sns("[A01]硬體控制器異常")
                    except:
                        print("sns error(hardware)")

                    #發line notify
                    message = '錯誤事件:[A01]硬體控制器無回應'
                    print(lineNotify(token, message, 0))

                    message = '建議維修零件: 通訊模組、POWER模組、線纜'
                    print(lineNotify(token, message, 0))

                    message = '推測故障原因: POWER模組異常、通訊模組無預警關閉、線路鬆脫'
                    print(lineNotify(token, message, 0))
                
            except:
                print('Laravel API Timeout(hardware maintenance)')
                return None


def getCarCount(url, cam_id):
    try:
        r = requests.get(url, timeout=5)
    except:
        #鏡頭無回應
        print("camID:", cam_id, " timeout.")
        
        #顯示"warning"圖片
        picture = pygame.transform.scale(warning, (640, 360))
        screen.blit(picture, camPic_pos[cam_id])
        screen.blit(cam_title[cam_id], camTitle_pos[cam_id]) #顯示標題
        pygame.display.flip()

        #推播
        if (OPEN_NOTIFY):
            #laravel 產生維修單
            try:
                headers = {'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC8xMjcuMC4wLjFcL2FwaVwvYXV0aFwvbG9naW4iLCJpYXQiOjE1NTgzNDk5MTcsImV4cCI6MTU2Njk4OTkxNywibmJmIjoxNTU4MzQ5OTE3LCJqdGkiOiIxUlNTUlEwU0xDTFhHbEVGIiwic3ViIjoxLCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.Q42vS5ZghcT4uRAFccoQIZfBWHBBx8vLJ-BjYkuQDQY"}
                payload = {'intersections_id': 1, 'content': '[C01]鏡頭1無回應'}
                url = "C:/Users/Darkflow/Desktop/darkflow/cars/cam"+str(cam_id)+".jpg"
                imageFile = {'imageFile': open(url, 'rb')}
                maintenance = requests.post(maintenance_url, headers = headers, params=payload, files = imageFile)
                response_data = json.loads(maintenance.text)

                #代表維修單正常生成，未重複
                if (response_data["notify"] == 1):
                    #發sns
                    try:
                        sns("[C01]鏡頭1無回應")
                    except:
                        print("sns error")

                    #發line notify
                    message = '[C01]鏡頭1無回應'
                    print(lineNotify(token, message, cam_id))
            except:
                print('Laravel API Timeout(maintenance)')
        return 0

    #影像處理
    curr_img = Image.open(BytesIO(r.content))
    curr_img_cv2 = cv2.cvtColor(np.array(curr_img), cv2.COLOR_RGB2BGR)

    #辨識物體
    result = tfnet.return_predict(curr_img_cv2)

    #影像轉 PIL ImageDraw Object
    draw = ImageDraw.Draw(curr_img)
    
    #圈出物體位置
    cars = drawCar(draw, result)

    #保存畫完的圖片到 local
    curr_img.save('cars/cam%d.jpg' %(cam_id))

    #在pygame顯示圖片
    
    image = pygame.image.load('cars/cam{}.jpg'.format(cam_id)) #讀取上一行保存的圖片
    picture = pygame.transform.scale(image, (640, 360)) #調整圖片尺寸
    screen.blit(picture, camPic_pos[cam_id]) #放到screen
    screen.blit(cam_title[cam_id], camTitle_pos[cam_id]) #顯示標題
    pygame.display.update() #更新畫面
    
    message = "鏡頭"+str(cam_id)+"偵測到車輛:"+str(cars)+"台"
    print("camera %d: %d cars detected"%(cam_id, cars))

    #存入車輛數
    count_dict["cam"+str(cam_id)] = cars

    return None

def drawCar(image, result):
    carsSeen = 0

    for detection in result:
        if detection['label'] == 'car' or detection['label'] == 'motorbike':
            #curr_img.save('cars/%i.jpg' %calculator)
            x_range = detection['bottomright']['x'] - detection['topleft']['x']
            if (x_range < 300):
                carsSeen += 1

                if detection['label'] == 'car':
                    image.rectangle([detection['topleft']['x'], detection['topleft']['y'], 
                            detection['bottomright']['x'], detection['bottomright']['y']],
                            outline=(99, 54, 254), width=5)
                    
                    image.rectangle([detection['topleft']['x'], detection['topleft']['y'] - 42, 
                            detection['topleft']['x'] + 80, detection['topleft']['y']],
                            fill=(99, 54, 254))
                else: #motorbike
                    image.rectangle([detection['topleft']['x'], detection['topleft']['y'], 
                            detection['bottomright']['x'], detection['bottomright']['y']],
                            outline=(255, 255, 0), width=5)
                    
                    image.rectangle([detection['topleft']['x'], detection['topleft']['y'] - 42, 
                            detection['topleft']['x'] + 200, detection['topleft']['y']],
                            fill=(255, 255, 0))
                image.text((detection['topleft']['x'] + 8, detection['topleft']['y'] - 48), detection['label'], font=pilFont, fill=(0,0,0,255))

    return carsSeen

def detectAndCount():
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

    que.get()
    que.get()
    que.get()
    que.get()

    print("cam1:", count_dict["cam1"])
    print("cam2:", count_dict["cam2"])
    print("cam3:", count_dict["cam3"])
    print("cam4:", count_dict["cam4"])
    return None

def judgeRule(isOPENRULE, r1_car_count, r2_car_count):
    if isOPENRULE:
            judgeURL = "http://192.168.50.46/judgeRule/1/{road1}/{road2}/1".format(road1=r1_car_count, road2=r2_car_count)
            lineNotify(_token, '中正路/建國一路交叉口 已套用規則', 0)
    else:
        judgeURL = "http://192.168.50.46/judgeRule/1/{road1}/{road2}/0".format(road1=r1_car_count, road2=r2_car_count)
    
    try:
        currentRule = requests.get(judgeURL, timeout=2)
        result = "Rule Judge: {id}".format(id=currentRule.content)
        return result
    except:
        err = "Laravel API Timeout(judge rule)"
        return err

def main():
    global lastUpdated
    global timegap

    while True:
        #如果pygame發生事件
        if pygame_event():
            #更新畫面
            pygame.display.flip()

        #執行排程任務
        if (int(round(time.time())) - lastUpdated > timegap):
            #辨識車輛數
            detectAndCount()
            
            #取得車輛數
            road1_car_count = count_dict["cam1"] + count_dict["cam2"]
            road2_car_count = count_dict["cam3"] + count_dict["cam4"]
            
            #規則比較
            if (OPEN_RULE):
                result = judgeRule(OPEN_RULE, road1_car_count, road2_car_count)
                print(result)

            #重置計時器
            lastUpdated = int(round(time.time()))

            #硬體健康檢測
            hardwareHealthCheck()

if __name__ == '__main__':
    main()

