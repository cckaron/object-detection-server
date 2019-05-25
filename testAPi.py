import requests

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

maintenance_url = 'http://127.0.0.1/api/maintenance/generate'
test_url = 'http://127.0.0.1/api/auth/login'
token = 'LUfgCGAPsb8bbG9ZiyPtWFE1UeH96dAZfigid9VAz1O' #維修單位

headers = {'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC8xMjcuMC4wLjFcL2FwaVwvYXV0aFwvbG9naW4iLCJpYXQiOjE1NTgzNDk5MTcsImV4cCI6MTU2Njk4OTkxNywibmJmIjoxNTU4MzQ5OTE3LCJqdGkiOiIxUlNTUlEwU0xDTFhHbEVGIiwic3ViIjoxLCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.Q42vS5ZghcT4uRAFccoQIZfBWHBBx8vLJ-BjYkuQDQY"}
payload = {'intersections_id': 1, 'content': '[CAM]鏡頭1無回應'}
payload1 = {'intersections_id': 1, 'content': '[HAW]硬體通訊介面無回應'}
url = "C:/Users/Darkflow/Desktop/darkflow/cars/cam1.jpg"
imageFile = {'imageFile': open(url, 'rb')}
maintenance = requests.post(maintenance_url, headers = headers, params=payload, files = imageFile)
maintenance = requests.post(maintenance_url, headers = headers, params=payload1, files = imageFile)

# print(maintenance.content)

# test = requests.post(test_url, params={'account':'admin', 'password':'admin'})
# print(test.content)

message = '錯誤事件:[A01]硬體控制器無回應'
print(lineNotify(token, message, 0))

message = '建議維修零件: 通訊模組、POWER模組、線纜'
print(lineNotify(token, message, 0))

message = '推測故障原因: POWER模組異常、通訊模組無預警關閉、線路鬆脫'
print(lineNotify(token, message, 0))