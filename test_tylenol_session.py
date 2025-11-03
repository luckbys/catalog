#!/usr/bin/env python3
"""
Script para criar uma sessão de teste com o produto TYLENOL (ID: 2455342)
que possui a imagem 49046.webp para testar a correção da exibição de imagens.
"""

import requests
import json
from datetime import datetime

# Configurações
API_BASE = "http://localhost:8000"

def criar_sessao_tylenol():
    """Cria uma sessão de teste com o produto TYLENOL"""
    
    # Dados do produto TYLENOL
    tylenol_produto = {
        "id": 2455342,
        "descricao": "TYLENOL",
        "apresentacao": "750 MG C/ 20 CP REV",
        "preco": 47.25,
        "estoque": 10,
        "imagem_url": "https://c4crm-minio.zv7gpn.easypanel.host/produtos/49046.webp",
        "categoria": "Medicamentos",
        "laboratorio": "JANSSEN-CILAG FARMAC"
    }
    
    # Payload para criar sessão
    payload = {
        "cliente_telefone": "+5511999999999",
        "cliente_nome": "Teste TYLENOL",
        "produtos": [tylenol_produto],
        "quantidade_produtos": 1,
        "timestamp": datetime.now().isoformat(),
        "forcar_nova_sessao": True
    }
    
    try:
        print("🧪 Criando sessão de teste com TYLENOL...")
        response = requests.post(f"{API_BASE}/api/produtos/criar-sessao", json=payload)
        response.raise_for_status()
        
        data = response.json()
        print("✅ Sessão criada com sucesso!")
        print(f"   📋 Sessão ID: {data['sessao_id']}")
        print(f"   🔗 URL: {data['url_catalogo']}")
        print(f"   ⏰ Expira em: {data['expira_em']}")
        print(f"   📦 Produtos: {data['produtos_count']}")
        
        return data['sessao_id']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao criar sessão: {e}")
        return None

def verificar_produto_na_sessao(sessao_id):
    """Verifica se o produto TYLENOL está na sessão"""
    try:
        print(f"\n🔍 Verificando produto na sessão {sessao_id}...")
        response = requests.get(f"{API_BASE}/api/produtos/{sessao_id}")
        response.raise_for_status()
        
        data = response.json()
        produtos = data.get('produtos', [])
        
        tylenol = next((p for p in produtos if 'TYLENOL' in p.get('descricao', '')), None)
        
        if tylenol:
            print("✅ TYLENOL encontrado na sessão!")
            print(f"   📋 ID: {tylenol['id']}")
            print(f"   💊 Descrição: {tylenol['descricao']}")
            print(f"   🖼️ Imagem URL: {tylenol['imagem_url']}")
            print(f"   🏭 Laboratório: {tylenol.get('laboratorio', 'N/A')}")
            return True
        else:
            print("❌ TYLENOL não encontrado na sessão")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao verificar sessão: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste de Sessão com TYLENOL - Imagem 49046.webp")
    print("=" * 50)
    
    # Criar sessão
    sessao_id = criar_sessao_tylenol()
    
    if sessao_id:
        # Verificar produto
        if verificar_produto_na_sessao(sessao_id):
            print(f"\n🎯 Teste a correção abrindo:")
            print(f"   http://localhost:8080/catalogo.html?sessao_id={sessao_id}")
            print("\n💡 Verifique se a imagem do TYLENOL aparece corretamente!")
            print("   A URL deve ser convertida para usar o proxy MinIO.")
    else:
        print("❌ Falha no teste - não foi possível criar a sessão")