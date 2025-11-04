#!/usr/bin/env python3
"""
🔍 TESTE DE DESCONTO EM PRODUÇÃO
Verifica se há produtos com desconto no Supabase e testa a API local
"""

import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

def test_supabase_desconto():
    """Testa produtos com desconto no Supabase"""
    print("🔍 TESTE DE DESCONTO NO SUPABASE")
    print("=" * 50)
    
    # Configurar Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Variáveis SUPABASE_URL ou SUPABASE_KEY não encontradas")
        return
    
    print(f"URL: {url}")
    print(f"KEY: {'*' * 20}...{key[-10:]}")
    
    try:
        supabase: Client = create_client(url, key)
        print("✅ Conexão com Supabase estabelecida")
        
        # 1. Buscar produtos com desconto_percentual > 0
        print("\n1️⃣ Buscando produtos com desconto_percentual > 0...")
        response = supabase.table("produtos").select("*").gt("desconto_percentual", 0).limit(5).execute()
        
        if response.data:
            print(f"📦 Encontrados {len(response.data)} produtos com desconto_percentual > 0:")
            for produto in response.data:
                print(f"   ID: {produto['id']} | {produto['descricao'][:50]}...")
                print(f"   Preço: R$ {produto['preco']} | Desconto: {produto['desconto_percentual']}%")
                print(f"   Preço promocional: R$ {produto['preco_promocional']}")
                print()
        else:
            print("❌ Nenhum produto encontrado com desconto_percentual > 0")
        
        # 2. Buscar produtos com desconto_valor > 0
        print("\n2️⃣ Buscando produtos com desconto_valor > 0...")
        response = supabase.table("produtos").select("*").not_.is_("desconto_valor", "null").limit(5).execute()
        
        if response.data:
            print(f"📦 Encontrados {len(response.data)} produtos com desconto_valor:")
            for produto in response.data:
                print(f"   ID: {produto['id']} | {produto['descricao'][:50]}...")
                print(f"   Preço: R$ {produto['preco']} | Desconto valor: R$ {produto['desconto_valor']}")
                print(f"   Preço promocional: R$ {produto['preco_promocional']}")
                print()
        else:
            print("❌ Nenhum produto encontrado com desconto_valor")
        
        # 3. Buscar produtos onde preco_promocional < preco
        print("\n3️⃣ Buscando produtos onde preço promocional < preço normal...")
        # Usar RPC para comparação de campos
        try:
            response = supabase.rpc("get_produtos_com_promocao").execute()
            if response.data:
                print(f"📦 Encontrados {len(response.data)} produtos com preço promocional menor:")
                for produto in response.data[:5]:  # Mostrar apenas os primeiros 5
                    print(f"   ID: {produto['id']} | {produto['descricao'][:50]}...")
                    print(f"   Preço: R$ {produto['preco']} | Promocional: R$ {produto['preco_promocional']}")
                    desconto_calc = ((produto['preco'] - produto['preco_promocional']) / produto['preco']) * 100
                    print(f"   Desconto calculado: {desconto_calc:.2f}%")
                    print()
            else:
                print("❌ Nenhum produto encontrado com preço promocional menor")
        except Exception as e:
            print(f"⚠️ RPC não disponível, fazendo busca manual: {e}")
            # Busca manual - pegar alguns produtos e verificar
            response = supabase.table("produtos").select("*").limit(100).execute()
            produtos_com_promocao = []
            
            for produto in response.data:
                preco = float(produto.get('preco', 0))
                preco_promocional = float(produto.get('preco_promocional', 0))
                
                if preco_promocional > 0 and preco_promocional < preco:
                    produtos_com_promocao.append(produto)
                    if len(produtos_com_promocao) >= 5:
                        break
            
            if produtos_com_promocao:
                print(f"📦 Encontrados {len(produtos_com_promocao)} produtos com preço promocional menor:")
                for produto in produtos_com_promocao:
                    print(f"   ID: {produto['id']} | {produto['descricao'][:50]}...")
                    print(f"   Preço: R$ {produto['preco']} | Promocional: R$ {produto['preco_promocional']}")
                    desconto_calc = ((produto['preco'] - produto['preco_promocional']) / produto['preco']) * 100
                    print(f"   Desconto calculado: {desconto_calc:.2f}%")
                    print()
            else:
                print("❌ Nenhum produto encontrado com preço promocional menor")
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")

def test_api_local():
    """Testa a API local para ver se está retornando descontos"""
    print("\n🌐 TESTE DA API LOCAL")
    print("=" * 50)
    
    try:
        # Testar endpoint de produtos
        response = requests.get("http://localhost:8000/api/produtos", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            produtos = data.get('produtos', [])
            
            print(f"✅ API respondeu com {len(produtos)} produtos")
            
            # Verificar se há produtos com desconto
            produtos_com_desconto = []
            for produto in produtos:
                if produto.get('percentual_desconto') and produto.get('percentual_desconto') > 0:
                    produtos_com_desconto.append(produto)
            
            if produtos_com_desconto:
                print(f"🎯 Encontrados {len(produtos_com_desconto)} produtos com desconto na API:")
                for produto in produtos_com_desconto[:3]:  # Mostrar apenas os primeiros 3
                    print(f"   ID: {produto['id']} | {produto['descricao'][:50]}...")
                    print(f"   Preço: R$ {produto['preco']} | Desconto: {produto['percentual_desconto']}%")
                    if produto.get('preco_original'):
                        print(f"   Preço original: R$ {produto['preco_original']}")
                    print()
            else:
                print("❌ Nenhum produto com desconto encontrado na API")
                
                # Mostrar alguns produtos para debug
                print("\n🔍 Primeiros 3 produtos da API (para debug):")
                for produto in produtos[:3]:
                    print(f"   ID: {produto['id']} | {produto['descricao'][:50]}...")
                    print(f"   Preço: R$ {produto['preco']}")
                    print(f"   Percentual desconto: {produto.get('percentual_desconto')}")
                    print(f"   Preço original: {produto.get('preco_original')}")
                    print()
        else:
            print(f"❌ API retornou status {response.status_code}")
            print(f"Resposta: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API local (http://localhost:8000)")
        print("   Certifique-se de que o servidor está rodando")
    except Exception as e:
        print(f"❌ Erro ao testar API local: {e}")

if __name__ == "__main__":
    test_supabase_desconto()
    test_api_local()