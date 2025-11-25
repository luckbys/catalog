import requests
import json

url = "http://localhost:8000/api/orders"

payload = {
    "customer_name": "Teste Integracao",
    "customer_phone": "11999999999",
    "customer_address": "Rua Teste, 123",
    "items": [
        {
            "name": "Produto Teste 1",
            "quantity": 2,
            "price": 10.50
        },
        {
            "name": "Produto Teste 2",
            "quantity": 1,
            "price": 20.00
        }
    ],
    "payment_method": "pix",
    "cash_received": 0,
    "cash_change": 0
}

headers = {
    'Content-Type': 'application/json'
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
