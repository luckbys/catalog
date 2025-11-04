#!/usr/bin/env python3
"""
🔍 COMPARAÇÃO PRODUÇÃO VS LOCAL
Script para comparar as respostas das APIs e identificar diferenças
"""

import requests
import json
from datetime import datetime

def compare_apis():
    """Compara as APIs de produção e local"""
    print("🔍 COMPARAÇÃO: PRODUÇÃO VS LOCAL")
    print("=" * 60)
    
    # URLs das APIs
    api_producao = "https://hakimfarma.devsible.com.br/api/produtos"
    api_local = "http://localhost:8000/api/produtos"
    
    # Produtos específicos que sabemos que têm desconto
    produtos_teste = [2465302, 2465034, 2455206]
    
    print("📡 Testando APIs...")
    
    # Testar API de produção
    try:
        print(f"\n🌐 API DE PRODUÇÃO: {api_producao}")
        response_prod = requests.get(api_producao, timeout=15)
        
        if response_prod.status_code == 200:
            data_prod = response_prod.json()
            produtos_prod = data_prod.get('produtos', [])
            print(f"✅ Status: {response_prod.status_code}")
            print(f"📦 Produtos: {len(produtos_prod)}")
            
            # Encontrar produtos com desconto na produção
            produtos_desconto_prod = []
            for produto in produtos_prod:
                if produto.get('id') in produtos_teste:
                    produtos_desconto_prod.append(produto)
            
            print(f"🎯 Produtos de teste encontrados: {len(produtos_desconto_prod)}")
            
        else:
            print(f"❌ Status: {response_prod.status_code}")
            produtos_desconto_prod = []
            
    except Exception as e:
        print(f"❌ Erro na API de produção: {e}")
        produtos_desconto_prod = []
    
    # Testar API local
    try:
        print(f"\n🏠 API LOCAL: {api_local}")
        response_local = requests.get(api_local, timeout=10)
        
        if response_local.status_code == 200:
            data_local = response_local.json()
            produtos_local = data_local.get('produtos', [])
            print(f"✅ Status: {response_local.status_code}")
            print(f"📦 Produtos: {len(produtos_local)}")
            
            # Encontrar produtos com desconto no local
            produtos_desconto_local = []
            for produto in produtos_local:
                if produto.get('id') in produtos_teste:
                    produtos_desconto_local.append(produto)
            
            print(f"🎯 Produtos de teste encontrados: {len(produtos_desconto_local)}")
            
        else:
            print(f"❌ Status: {response_local.status_code}")
            produtos_desconto_local = []
            
    except Exception as e:
        print(f"❌ Erro na API local: {e}")
        produtos_desconto_local = []
    
    # Comparar os produtos
    print(f"\n📊 COMPARAÇÃO DETALHADA")
    print("=" * 60)
    
    for produto_id in produtos_teste:
        print(f"\n🔍 PRODUTO ID: {produto_id}")
        print("-" * 40)
        
        # Encontrar produto na produção
        produto_prod = None
        for p in produtos_desconto_prod:
            if p.get('id') == produto_id:
                produto_prod = p
                break
        
        # Encontrar produto no local
        produto_local = None
        for p in produtos_desconto_local:
            if p.get('id') == produto_id:
                produto_local = p
                break
        
        # Comparar
        if produto_prod and produto_local:
            print("🌐 PRODUÇÃO:")
            print(f"   📦 Descrição: {produto_prod.get('descricao', 'N/A')}")
            print(f"   💰 Preço: R$ {produto_prod.get('preco', 0)}")
            print(f"   💸 Preço original: {produto_prod.get('preco_original', 'N/A')}")
            print(f"   📊 Percentual desconto: {produto_prod.get('percentual_desconto', 'N/A')}")
            print(f"   💵 Valor desconto: {produto_prod.get('valor_desconto', 'N/A')}")
            
            print("\n🏠 LOCAL:")
            print(f"   📦 Descrição: {produto_local.get('descricao', 'N/A')}")
            print(f"   💰 Preço: R$ {produto_local.get('preco', 0)}")
            print(f"   💸 Preço original: {produto_local.get('preco_original', 'N/A')}")
            print(f"   📊 Percentual desconto: {produto_local.get('percentual_desconto', 'N/A')}")
            print(f"   💵 Valor desconto: {produto_local.get('valor_desconto', 'N/A')}")
            
            # Verificar se são iguais
            campos_importantes = ['preco', 'preco_original', 'percentual_desconto', 'valor_desconto']
            diferencas = []
            
            for campo in campos_importantes:
                val_prod = produto_prod.get(campo)
                val_local = produto_local.get(campo)
                
                if val_prod != val_local:
                    diferencas.append(f"{campo}: PROD={val_prod} vs LOCAL={val_local}")
            
            if diferencas:
                print(f"\n⚠️ DIFERENÇAS ENCONTRADAS:")
                for diff in diferencas:
                    print(f"   🔸 {diff}")
            else:
                print(f"\n✅ DADOS IDÊNTICOS!")
                
        elif produto_prod:
            print("🌐 PRODUÇÃO: ✅ Encontrado")
            print("🏠 LOCAL: ❌ Não encontrado")
            
        elif produto_local:
            print("🌐 PRODUÇÃO: ❌ Não encontrado")
            print("🏠 LOCAL: ✅ Encontrado")
            
        else:
            print("🌐 PRODUÇÃO: ❌ Não encontrado")
            print("🏠 LOCAL: ❌ Não encontrado")
    
    # Verificar estrutura geral das respostas
    print(f"\n🔍 ESTRUTURA DAS RESPOSTAS")
    print("=" * 60)
    
    if produtos_desconto_prod and produtos_desconto_local:
        produto_exemplo_prod = produtos_desconto_prod[0]
        produto_exemplo_local = produtos_desconto_local[0]
        
        print("🌐 CAMPOS NA PRODUÇÃO:")
        for key in sorted(produto_exemplo_prod.keys()):
            print(f"   📋 {key}: {type(produto_exemplo_prod[key]).__name__}")
        
        print("\n🏠 CAMPOS NO LOCAL:")
        for key in sorted(produto_exemplo_local.keys()):
            print(f"   📋 {key}: {type(produto_exemplo_local[key]).__name__}")
        
        # Campos diferentes
        campos_prod = set(produto_exemplo_prod.keys())
        campos_local = set(produto_exemplo_local.keys())
        
        campos_so_prod = campos_prod - campos_local
        campos_so_local = campos_local - campos_prod
        
        if campos_so_prod:
            print(f"\n🌐 CAMPOS APENAS NA PRODUÇÃO:")
            for campo in sorted(campos_so_prod):
                print(f"   🔸 {campo}")
        
        if campos_so_local:
            print(f"\n🏠 CAMPOS APENAS NO LOCAL:")
            for campo in sorted(campos_so_local):
                print(f"   🔸 {campo}")
        
        if not campos_so_prod and not campos_so_local:
            print(f"\n✅ ESTRUTURAS IDÊNTICAS!")

if __name__ == "__main__":
    compare_apis()