import requests
import json

url = "http://localhost:8000/api/admin/banners"

payload = {
    "titulo": "Banner Teste Script",
    "subtitulo": "Subtitulo Teste",
    "descricao": "Descricao Teste",
    "badge_texto": "TESTE",
    "cor_primaria": "#000000",
    "cor_secundaria": "#ffffff",
    "icone": "star",
    "tipo_promocao": "desconto_percentual",
    "posicao": 1,
    "ativo": True
}

headers = {
    'Content-Type': 'application/json'
}

try:
    print(f"Sending POST to {url}")
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
