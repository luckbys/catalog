#!/usr/bin/env python3
"""
Script para criar uma sessão de teste com produtos que tenham desconto
"""
import requests
import json
from datetime import datetime

# Configurações
API_BASE = "http://localhost:8000"

def criar_sessao_com_desconto():
    """Cria uma sessão de teste com produtos que tenham desconto"""
    
    # 1. Buscar alguns produtos da API
    print("🔍 Buscando produtos da API...")
    response = requests.get(f"{API_BASE}/api/produtos")
    if response.status_code != 200:
        print(f"❌ Erro ao buscar produtos: {response.status_code}")
        return None
    
    produtos_originais = response.json()["produtos"][:5]  # Pegar os primeiros 5 produtos
    print(f"✅ Encontrados {len(produtos_originais)} produtos")
    
    # 2. Modificar produtos para incluir desconto
    produtos_com_desconto = []
    for i, produto in enumerate(produtos_originais):
        produto_modificado = {
            "id": produto["id"],
            "descricao": produto["descricao"],
            "preco": float(produto["preco"]),
            "estoque": produto["estoque"],
            "imagem_url": produto.get("imagem_url"),
            "categoria": produto.get("categoria"),
            "apresentacao": produto.get("apresentacao"),
            "laboratorio": produto.get("laboratorio")
        }
        
        # Adicionar diferentes tipos de desconto
        if i == 0:  # Primeiro produto: desconto percentual
            produto_modificado["preco_original"] = float(produto["preco"])
            produto_modificado["percentual_desconto"] = 15.0  # 15% de desconto
            produto_modificado["preco"] = float(produto["preco"]) * 0.85  # Aplicar desconto
        elif i == 1:  # Segundo produto: desconto por valor
            produto_modificado["preco_original"] = float(produto["preco"])
            produto_modificado["valor_desconto"] = 5.0  # R$ 5,00 de desconto
            produto_modificado["preco"] = max(0, float(produto["preco"]) - 5.0)  # Aplicar desconto
        elif i == 2:  # Terceiro produto: desconto percentual maior
            produto_modificado["preco_original"] = float(produto["preco"])
            produto_modificado["percentual_desconto"] = 25.0  # 25% de desconto
            produto_modificado["preco"] = float(produto["preco"]) * 0.75  # Aplicar desconto
        # Os outros produtos ficam sem desconto para comparação
        
        produtos_com_desconto.append(produto_modificado)
    
    # 3. Criar payload para sessão
    payload = {
        "cliente_telefone": "+5511999887766",
        "cliente_nome": "Teste Desconto",
        "produtos": produtos_com_desconto,
        "quantidade_produtos": len(produtos_com_desconto),
        "timestamp": datetime.now().isoformat(),
        "forcar_nova_sessao": True
    }
    
    # 4. Criar sessão
    print("🚀 Criando sessão com produtos com desconto...")
    response = requests.post(f"{API_BASE}/api/produtos/criar-sessao", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        sessao_id = result["sessao_id"]
        link = result["link_produtos"]
        print(f"✅ Sessão criada com sucesso!")
        print(f"📋 ID da Sessão: {sessao_id}")
        print(f"🔗 Link: {link}")
        
        # 5. Verificar se os produtos foram salvos corretamente
        print("\n🔍 Verificando produtos da sessão...")
        response = requests.get(f"{API_BASE}/api/produtos/{sessao_id}")
        if response.status_code == 200:
            produtos_sessao = response.json()["produtos"]
            print(f"✅ Sessão contém {len(produtos_sessao)} produtos")
            
            for produto in produtos_sessao:
                print(f"\n📦 {produto['descricao']}")
                print(f"   💰 Preço: R$ {produto['preco']}")
                if produto.get('preco_original'):
                    print(f"   💸 Preço Original: R$ {produto['preco_original']}")
                if produto.get('percentual_desconto'):
                    print(f"   📊 Desconto: {produto['percentual_desconto']}%")
                if produto.get('valor_desconto'):
                    print(f"   💵 Desconto: R$ {produto['valor_desconto']}")
        
        return sessao_id
    else:
        print(f"❌ Erro ao criar sessão: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    sessao_id = criar_sessao_com_desconto()
    if sessao_id:
        print(f"\n🎉 Teste concluído! Acesse: http://localhost:8080/catalogo.html?sessao_id={sessao_id}")