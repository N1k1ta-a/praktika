import requests
import json

url = "http://localhost:5000/login"
data = {
    "username": "testuser",
    "password": "testpass"
}

response = requests.post(
    url,
    headers={"Content-Type": "application/json; charset=utf-8"},
    data=json.dumps(data, ensure_ascii=False)
)

print(response.status_code)
print(response.text)