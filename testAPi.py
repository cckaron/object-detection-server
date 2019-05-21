import requests
maintenance_url = 'http://127.0.0.1/api/maintenance/generate'
test_url = 'http://127.0.0.1/api/auth/login'

headers = {'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC8xMjcuMC4wLjFcL2FwaVwvYXV0aFwvbG9naW4iLCJpYXQiOjE1NTgzNDk5MTcsImV4cCI6MTU2Njk4OTkxNywibmJmIjoxNTU4MzQ5OTE3LCJqdGkiOiIxUlNTUlEwU0xDTFhHbEVGIiwic3ViIjoxLCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.Q42vS5ZghcT4uRAFccoQIZfBWHBBx8vLJ-BjYkuQDQY"}
payload = {'intersections_id': 1, 'content': '[C01]鏡頭1無回應'}
url = "C:/Users/Darkflow/Desktop/darkflow/cars/cam1.jpg"
imageFile = {'imageFile': open(url, 'rb')}
maintenance = requests.post(maintenance_url, headers = headers, params=payload, files = imageFile)
print(maintenance.content)

# test = requests.post(test_url, params={'account':'admin', 'password':'admin'})
# print(test.content)