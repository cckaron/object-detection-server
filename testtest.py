import requests
import json
maintenance_url = 'http://127.0.0.1/api/maintenance/generate'

headers = {'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC8xMjcuMC4wLjFcL2FwaVwvYXV0aFwvbG9naW4iLCJpYXQiOjE1NTgzNDk5MTcsImV4cCI6MTU2Njk4OTkxNywibmJmIjoxNTU4MzQ5OTE3LCJqdGkiOiIxUlNTUlEwU0xDTFhHbEVGIiwic3ViIjoxLCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.Q42vS5ZghcT4uRAFccoQIZfBWHBBx8vLJ-BjYkuQDQY"}
payload = {'intersections_id': 1, 'content': '[A01]硬體控制器異常'}
maintenance = requests.post(maintenance_url, headers = headers, params=payload)
response_data = json.loads(maintenance.text)

print("response_data:", response_data)
print(response_data["notify"])