import requests

url = "http://localhost:5000/cart/add"  # Эндпоинт для добавления товара
token = "your_jwt_token"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Данные товара для добавления
data = {
    "product_id": 1,  # ID товара
    "quantity": 1     # Количество (по умолчанию 1)
}

response = requests.post(  # Отправка POST-запроса
    url,
    headers=headers,
    json=data
)

print(response.status_code)  # Вывод HTTP-статуса
print(response.text)         # Вывод ответа сервера