#!/usr/bin/env python3
"""
Script para debugar a estrutura da tabela produtos no Supabase de produção
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

def debug_supabase_produtos():
    """Debug da tabela produtos no Supabase"""
    
    # Configurações do Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    print("🔍 DEBUG SUPABASE PRODUÇÃO")
    print("=" * 50)
    print(f"URL: {SUPABASE_URL}")
    print(f"KEY: {'*' * 20}...{SUPABASE_KEY[-10:] if SUPABASE_KEY else 'N/A'}")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL ou SUPABASE_KEY não configurados")
        return
    
    try:
        # Conectar ao Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Conexão com Supabase estabelecida")
        
        # 1. Verificar total de produtos
        print("\n1️⃣ Verificando total de produtos...")
        result = supabase.table("produtos").select("id", count="exact").execute()
        total_produtos = len(result.data) if result.data else 0
        print(f"📦 Total de produtos: {total_produtos}")
        
        if total_produtos == 0:
            print("❌ Nenhum produto encontrado na tabela!")
            return
        
        # 2. Verificar estrutura da tabela (primeiros 3 produtos)
        print("\n2️⃣ Verificando estrutura da tabela...")
        result = supabase.table("produtos").select("*").limit(3).execute()
        
        if result.data:
            produto = result.data[0]
            print(f"📋 Estrutura do produto (ID: {produto.get('id')}):")
            for key, value in produto.items():
                print(f"   {key}: {value} (tipo: {type(value).__name__})")
        
        # 3. Buscar produtos com campos de desconto
        print("\n3️⃣ Verificando campos de desconto...")
        
        # Verificar se existe campo percentual_desconto
        result = supabase.table("produtos").select("id, descricao, preco, percentual_desconto").not_.is_("percentual_desconto", "null").limit(5).execute()
        
        if result.data:
            print(f"✅ Encontrados {len(result.data)} produtos com percentual_desconto não nulo:")
            for produto in result.data:
                print(f"   ID: {produto.get('id')} | {produto.get('descricao', 'N/A')}")
                print(f"      Preço: R$ {produto.get('preco', 0)} | Desconto: {produto.get('percentual_desconto', 0)}%")
        else:
            print("❌ Nenhum produto com percentual_desconto encontrado!")
        
        # 4. Verificar se existe campo desconto_percentual (nome alternativo)
        print("\n4️⃣ Verificando campo desconto_percentual...")
        try:
            result = supabase.table("produtos").select("id, descricao, preco, desconto_percentual").not_.is_("desconto_percentual", "null").limit(5).execute()
            
            if result.data:
                print(f"✅ Encontrados {len(result.data)} produtos com desconto_percentual não nulo:")
                for produto in result.data:
                    print(f"   ID: {produto.get('id')} | {produto.get('descricao', 'N/A')}")
                    print(f"      Preço: R$ {produto.get('preco', 0)} | Desconto: {produto.get('desconto_percentual', 0)}%")
            else:
                print("❌ Nenhum produto com desconto_percentual encontrado!")
        except Exception as e:
            print(f"❌ Campo desconto_percentual não existe: {e}")
        
        # 5. Verificar produtos específicos que deveriam ter desconto
        print("\n5️⃣ Verificando produtos específicos...")
        produtos_teste = [2465302, 2465034, 2455206]  # IDs que têm desconto no local
        
        for produto_id in produtos_teste:
            result = supabase.table("produtos").select("*").eq("id", produto_id).execute()
            
            if result.data:
                produto = result.data[0]
                print(f"\n📦 Produto ID {produto_id}:")
                print(f"   Descrição: {produto.get('descricao', 'N/A')}")
                print(f"   Preço: R$ {produto.get('preco', 0)}")
                print(f"   Percentual Desconto: {produto.get('percentual_desconto', 'N/A')}")
                print(f"   Desconto Percentual: {produto.get('desconto_percentual', 'N/A')}")
                print(f"   Valor Desconto: {produto.get('valor_desconto', 'N/A')}")
            else:
                print(f"❌ Produto ID {produto_id} não encontrado!")
        
        # 6. Verificar se há algum produto com desconto > 0
        print("\n6️⃣ Buscando qualquer produto com desconto...")
        
        # Tentar diferentes campos de desconto
        campos_desconto = ['percentual_desconto', 'desconto_percentual', 'desconto', 'discount']
        
        for campo in campos_desconto:
            try:
                result = supabase.table("produtos").select(f"id, descricao, preco, {campo}").gt(campo, 0).limit(3).execute()
                
                if result.data:
                    print(f"✅ Encontrados produtos com {campo} > 0:")
                    for produto in result.data:
                        print(f"   ID: {produto.get('id')} | {produto.get('descricao', 'N/A')}")
                        print(f"      {campo}: {produto.get(campo, 0)}")
                    break
            except Exception as e:
                print(f"❌ Campo {campo} não existe ou erro: {e}")
        else:
            print("❌ Nenhum produto com desconto encontrado em nenhum campo!")
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")

if __name__ == "__main__":
    debug_supabase_produtos()