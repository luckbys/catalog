#!/usr/bin/env python3
"""
Script para testar conexão com Supabase na VPS
"""

import requests
import json
import os
from datetime import datetime

def test_supabase_connection():
    """Testa conexão direta com Supabase"""
    
    # Credenciais do .env local
    SUPABASE_URL = "https://chatbot-supabase1.zv7gpn.easypanel.host"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"
    
    print("🔍 Testando conexão com Supabase...")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:20]}...")
    
    # Headers para Supabase
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # 1. Testar se consegue acessar a tabela orders
    print("\n📋 Testando acesso à tabela 'orders'...")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/orders?limit=1",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Tabela 'orders' acessível")
            data = response.json()
            print(f"Registros encontrados: {len(data)}")
        else:
            print(f"❌ Erro ao acessar tabela 'orders': {response.text}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # 2. Testar inserção de um pedido de teste
    print("\n📝 Testando inserção de pedido...")
    test_order = {
        "cliente_nome": "Teste Conexão VPS",
        "cliente_telefone": "11999999999",
        "entrega_cep": "01310-100",
        "entrega_endereco": "Av Paulista",
        "entrega_numero": "1000",
        "entrega_bairro": "Centro",
        "entrega_cidade": "São Paulo",
        "entrega_estado": "SP",
        "pagamento_forma": "PIX",
        "pagamento_valor": 100.00,
        "status": "novo",
        "data_pedido": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/orders",
            headers=headers,
            json=test_order,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Pedido inserido com sucesso!")
            result = response.json()
            print(f"Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Erro ao inserir pedido: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na inserção: {e}")

def test_vps_backend():
    """Testa o backend da VPS"""
    
    print("\n🌐 Testando backend da VPS...")
    
    # Dados de teste
    test_data = {
        "cliente": {
            "nome": "Teste Backend VPS",
            "telefone": "11999999999"
        },
        "entrega": {
            "cep": "01310-100",
            "endereco": "Avenida Paulista",
            "numero": "1000",
            "complemento": "Teste",
            "bairro": "Bela Vista",
            "cidade": "São Paulo",
            "estado": "SP"
        },
        "pagamento": {
            "forma_pagamento": "PIX",
            "valor_total": 199.99
        },
        "produtos": [
            {
                "id": 1,
                "nome": "Produto Teste",
                "codigo": "TEST001",
                "descricao": "Produto para teste",
                "preco_unitario": 199.99,
                "quantidade": 1,
                "subtotal": 199.99
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://chatbot-catalog.zv7gpn.easypanel.host/api/process-order",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend respondeu corretamente!")
            print(f"Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Backend retornou erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao conectar com backend: {e}")

if __name__ == "__main__":
    print("🧪 Teste de Conexão Supabase + VPS")
    print("=" * 50)
    
    # Testar Supabase diretamente
    test_supabase_connection()
    
    # Testar backend da VPS
    test_vps_backend()
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")