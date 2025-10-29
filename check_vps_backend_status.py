#!/usr/bin/env python3
"""
Script para verificar o status do backend na VPS
Diagnóstico completo do problema de produção
"""

import requests
import json
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def test_vps_endpoints():
    """Testa diferentes endpoints da VPS para diagnosticar o problema"""
    
    base_url = "https://chatbot-catalog.zv7gpn.easypanel.host"
    
    endpoints = [
        "/",
        "/api",
        "/api/health",
        "/api/process-order",
        "/health",
        "/status"
    ]
    
    print_header("TESTE DE ENDPOINTS DA VPS")
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🌐 Testando: {url}")
        
        try:
            # Teste GET
            response = requests.get(url, timeout=10)
            print(f"   GET Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Sucesso!")
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        print(f"   📄 Resposta: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        pass
                else:
                    print(f"   📄 Conteúdo: {response.text[:100]}...")
            else:
                print(f"   ❌ Erro {response.status_code}")
                print(f"   📄 Resposta: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Erro de conexão: {e}")
    
    # Teste específico do endpoint de pedidos
    print_header("TESTE ESPECÍFICO DO ENDPOINT DE PEDIDOS")
    
    order_data = {
        "cliente": {
            "nome": "Teste VPS",
            "telefone": "11999999999"
        },
        "entrega": {
            "cep": "01310-100",
            "endereco": "Avenida Paulista",
            "numero": "1000"
        },
        "pagamento": {
            "forma_pagamento": "PIX",
            "valor_total": 100.00
        },
        "produtos": [
            {
                "id": 1,
                "nome": "Produto Teste",
                "preco_unitario": 100.00,
                "quantidade": 1,
                "subtotal": 100.00
            }
        ]
    }
    
    url = f"{base_url}/api/process-order"
    print(f"\n🎯 POST para: {url}")
    
    try:
        response = requests.post(
            url,
            json=order_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.text:
            try:
                data = response.json()
                print(f"Resposta JSON: {json.dumps(data, indent=2)}")
            except:
                print(f"Resposta texto: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"💥 Erro: {e}")

def check_docker_status():
    """Verifica se há informações sobre containers Docker"""
    
    print_header("DIAGNÓSTICO DO PROBLEMA")
    
    print("""
🔍 ANÁLISE DO PROBLEMA:

1. ❌ Endpoint /api/process-order retorna 404
2. ❌ Backend não está respondendo corretamente
3. ✅ Local funciona perfeitamente
4. ❌ Produção (VPS) não funciona

🎯 POSSÍVEIS CAUSAS:

1. Backend não está rodando na VPS
2. Docker containers não estão ativos
3. Configuração de ambiente incorreta
4. Problema de roteamento/proxy
5. Porta não está exposta corretamente

🛠️ SOLUÇÕES RECOMENDADAS:

1. Verificar se os containers Docker estão rodando
2. Verificar logs dos containers
3. Verificar configuração do docker-compose.prod.yml
4. Verificar variáveis de ambiente
5. Reiniciar os serviços

📋 COMANDOS PARA EXECUTAR NA VPS:

# Verificar containers
docker ps -a

# Verificar logs
docker-compose -f docker-compose.prod.yml logs

# Reiniciar serviços
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Verificar se o backend está rodando
curl http://localhost:5000/api/health
    """)

if __name__ == "__main__":
    print(f"🚀 Diagnóstico VPS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_vps_endpoints()
    check_docker_status()
    
    print(f"\n{'='*60}")
    print("🏁 Diagnóstico concluído!")
    print("📋 Próximos passos: Executar comandos na VPS para corrigir o problema")
    print(f"{'='*60}")