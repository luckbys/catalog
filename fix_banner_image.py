#!/usr/bin/env python3
"""
Script para corrigir a imagem problemática do banner no Supabase
"""
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

try:
    from supabase import create_client, Client
    
    # Configurações do Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL ou SUPABASE_KEY não configurados")
        sys.exit(1)
    
    # Criar cliente Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("🔧 Corrigindo banner com imagem problemática...")
    
    # Atualizar banner ID 5 para remover a imagem problemática
    result = supabase.table("banners").update({
        "imagem_url": None  # Remove a imagem problemática
    }).eq("id", 5).execute()
    
    if result.data:
        print("✅ Banner ID 5 atualizado com sucesso!")
        print(f"   - Imagem removida do banner: {result.data[0]['titulo']}")
    else:
        print("❌ Erro ao atualizar banner")
        
    # Verificar banners atualizados
    print("\n📋 Banners atuais:")
    banners = supabase.table("banners").select("id, titulo, imagem_url").eq("ativo", True).order("posicao").execute()
    
    for banner in banners.data:
        status = "✅ OK" if not banner['imagem_url'] else "🖼️ COM IMAGEM"
        print(f"   Banner {banner['id']}: {banner['titulo']} - {status}")
        if banner['imagem_url']:
            print(f"     URL: {banner['imagem_url']}")
            
except ImportError:
    print("❌ Biblioteca supabase não instalada. Execute: pip install supabase")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)