import urllib.request
import json

url = "http://localhost:8000/api/orders"

payload = {
    "customer_name": "Teste Urllib",
    "customer_phone": "11977777777",
    "customer_address": "Rua Urllib, 50",
    "items": [
        {
            "name": "Item Urllib",
            "quantity": 3,
            "price": 15.00
        }
    ],
    "payment_method": "cash",
    "cash_received": 100.00,
    "cash_change": 55.00
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(response.read().decode('utf-8'))
except urllib.error.URLError as e:
    print(f"Error: {e}")
