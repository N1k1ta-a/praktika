import requests

url = "http://localhost:5000/cart/remove/1"  # Удаление элемента корзины с ID=1
token = "your_jwt_token"  # JWT-токен авторизации
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.delete(
    url,
    headers=headers
)

print(response.status_code)  # Вывод статуса ответа (200, 404 и т.д.)
print(response.text)         # Вывод текста ответа
