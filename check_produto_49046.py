#!/usr/bin/env python3
"""
Script para verificar produto específico 49046 no Supabase
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

try:
    from backend.order_processor import order_processor  # type: ignore
except ImportError:
    try:
        from order_processor import order_processor  # type: ignore
    except ImportError as e:
        print(f"❌ Erro ao importar order_processor: {e}")
        exit(1)

try:
    
    print("🔍 Buscando produto 49046 no Supabase...")
    
    # Busca produto específico
    result = order_processor.supabase.table("produtos").select("*").eq("id", 49046).execute()
    
    if result.data:
        produto = result.data[0]
        print(f"✅ Produto encontrado:")
        print(f"   ID: {produto.get('id')}")
        print(f"   Descrição: {produto.get('descricao')}")
        print(f"   Preço: {produto.get('preco')}")
        print(f"   Imagem URL: {produto.get('imagem_url')}")
        print(f"   Laboratório: {produto.get('laboratorio')}")
        print(f"   Categoria: {produto.get('categoria')}")
        print(f"   Apresentação: {produto.get('apresentacao')}")
        
        # Verifica se a imagem_url está preenchida
        if produto.get('imagem_url'):
            print(f"🖼️  URL da imagem: {produto.get('imagem_url')}")
        else:
            print("❌ Campo imagem_url está vazio ou nulo")
            
    else:
        print("❌ Produto 49046 não encontrado no Supabase")
        
        # Busca produtos similares (IDs próximos)
        print("\n🔍 Buscando produtos com IDs próximos...")
        result_similar = order_processor.supabase.table("produtos").select("id, descricao, imagem_url").gte("id", 49040).lte("id", 49050).execute()
        
        if result_similar.data:
            print("📋 Produtos encontrados na faixa 49040-49050:")
            for p in result_similar.data:
                print(f"   ID: {p.get('id')} - {p.get('descricao')} - Imagem: {p.get('imagem_url') or 'Sem imagem'}")
        else:
            print("❌ Nenhum produto encontrado na faixa 49040-49050")
            
        # Busca produtos que contenham "49046" na descrição ou outros campos
        print("\n🔍 Buscando produtos que contenham '49046' na descrição...")
        result_desc = order_processor.supabase.table("produtos").select("id, descricao, imagem_url").ilike("descricao", "%49046%").execute()
        
        if result_desc.data:
            print("📋 Produtos com '49046' na descrição:")
            for p in result_desc.data:
                print(f"   ID: {p.get('id')} - {p.get('descricao')} - Imagem: {p.get('imagem_url') or 'Sem imagem'}")
        else:
            print("❌ Nenhum produto encontrado com '49046' na descrição")
            
        # Busca alguns produtos que tenham imagem_url preenchida para comparação
        print("\n🔍 Buscando alguns produtos com imagens para comparação...")
        result_with_images = order_processor.supabase.table("produtos").select("id, descricao, imagem_url").not_.is_("imagem_url", "null").limit(5).execute()
        
        if result_with_images.data:
            print("📋 Exemplos de produtos com imagens:")
            for p in result_with_images.data:
                print(f"   ID: {p.get('id')} - {p.get('descricao')[:50]}... - Imagem: {p.get('imagem_url')}")
        else:
            print("❌ Nenhum produto encontrado com imagens")

except Exception as e:
    print(f"❌ Erro ao conectar com Supabase: {e}")