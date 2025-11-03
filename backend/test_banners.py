#!/usr/bin/env python3
"""
Script simples para verificar banners no Supabase
"""

from dotenv import load_dotenv
load_dotenv()

from order_processor import OrderProcessor

def main():
    print("🔍 Verificando banners no Supabase...")
    
    try:
        processor = OrderProcessor()
        
        # Buscar todos os banners (ativos e inativos)
        print("\n📊 Buscando TODOS os banners...")
        result_all = processor.supabase.table("banners").select("*").execute()
        
        print(f"📊 Total de banners: {len(result_all.data)}")
        
        for i, banner in enumerate(result_all.data, 1):
            print(f"\n🎯 Banner {i}:")
            print(f"   ID: {banner.get('id')}")
            print(f"   Título: {banner.get('titulo')}")
            print(f"   Subtítulo: {banner.get('subtitulo')}")
            print(f"   Ativo: {banner.get('ativo')}")
            print(f"   Posição: {banner.get('posicao')}")
            print(f"   Imagem: {banner.get('imagem_url', 'NULL')}")
            
        # Buscar apenas banners ativos (como o endpoint faz)
        print("\n🟢 Buscando apenas banners ATIVOS...")
        result_active = processor.supabase.table("banners").select("*").eq("ativo", True).order("posicao").execute()
        
        print(f"🟢 Banners ativos: {len(result_active.data)}")
        
        for i, banner in enumerate(result_active.data, 1):
            print(f"\n✅ Banner ativo {i}:")
            print(f"   ID: {banner.get('id')}")
            print(f"   Título: {banner.get('titulo')}")
            print(f"   Subtítulo: {banner.get('subtitulo')}")
            print(f"   Posição: {banner.get('posicao')}")
            print(f"   Imagem: {banner.get('imagem_url', 'NULL')}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()