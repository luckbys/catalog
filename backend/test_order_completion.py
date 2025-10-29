#!/usr/bin/env python3
"""
Script para testar a finalização de pedidos localmente
"""
import requests
import json

# Dados de teste para simular um pedido
test_order_data = {
    "cliente": {
        "nome": "João Silva",
        "telefone": "5511999999999"
    },
    "entrega": {
        "endereco": "Rua das Flores, 123",
        "numero": "123",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01234-567",
        "complemento": "Apto 45"
    },
    "pagamento": {
        "forma_pagamento": "PIX",
        "valor_total": 25.50
    },
    "produtos": [
        {
            "nome": "Produto Teste 1",
            "codigo": "PROD001",
            "preco_unitario": 12.75,
            "quantidade": 1,
            "subtotal": 12.75
        },
        {
            "nome": "Produto Teste 2",
            "codigo": "PROD002",
            "preco_unitario": 12.75,
            "quantidade": 1,
            "subtotal": 12.75
        }
    ]
}

def test_order_completion():
    """Testa a finalização de um pedido"""
    url = "http://localhost:8000/api/process-order"
    
    print("🧪 Testando finalização de pedido...")
    print(f"📡 URL: {url}")
    print(f"📦 Dados do pedido: {json.dumps(test_order_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=test_order_data, timeout=30)
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Erro! Status: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão! Verifique se o servidor está rodando em http://localhost:8000")
    except requests.exceptions.Timeout:
        print("⏰ Timeout! O servidor demorou muito para responder")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    test_order_completion()