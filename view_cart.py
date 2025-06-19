import requests

url = "http://localhost:5000/cart"  # Эндпоинт для просмотра корзины
token = "your_jwt_token"
headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(  # Отправка GET-запроса
    url,
    headers=headers
)

print(response.status_code)  # Вывод HTTP-статуса
print(response.text)         # Вывод содержимого корзины
