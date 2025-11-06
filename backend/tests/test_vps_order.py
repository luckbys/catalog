#!/usr/bin/env python3
"""
Script para testar o endpoint de finalização de pedido na VPS
"""

import requests
import json
import sys

def test_vps_order():
    # URL da VPS
    vps_url = "https://hakimfarma.devsible.com.br/api/process-order"
    
    # Dados de teste
    test_data = {
        "cliente": {
            "nome": "João Silva Teste VPS",
            "telefone": "11999999999"
        },
        "entrega": {
            "cep": "01310-100",
            "endereco": "Avenida Paulista",
            "numero": "1000",
            "complemento": "Apto 101",
            "bairro": "Bela Vista",
            "cidade": "São Paulo",
            "estado": "SP"
        },
        "pagamento": {
            "forma_pagamento": "PIX",
            "valor_total": 299.98
        },
        "produtos": [
            {
                "id": 1,
                "nome": "Smartphone Samsung Galaxy",
                "codigo": "SAMS001",
                "descricao": "Smartphone Samsung Galaxy A54",
                "preco_unitario": 149.99,
                "quantidade": 2,
                "subtotal": 299.98
            }
        ]
    }
    
    print("🧪 Testando endpoint de pedido na VPS...")
    print(f"URL: {vps_url}")
    print(f"Dados: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Fazer requisição
        response = requests.post(
            vps_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def test_health_endpoint():
    """Testa o endpoint de health da VPS"""
    health_url = "https://hakimfarma.devsible.com.br/health"
    
    print(f"\n🏥 Testando endpoint de health...")
    print(f"URL: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Health OK: {response.text}")
        else:
            print(f"❌ Health Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")

if __name__ == "__main__":
    print("🔍 Testando VPS - Finalização de Pedido")
    print("=" * 50)
    
    # Testar health primeiro
    test_health_endpoint()
    
    # Testar endpoint de pedido
    test_vps_order()
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")