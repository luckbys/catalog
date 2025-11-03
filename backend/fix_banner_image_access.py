#!/usr/bin/env python3
"""
Script para corrigir o problema da imagem do banner removendo a URL não pública
"""

from order_processor import OrderProcessor

def fix_banner_image():
    print("🔧 Corrigindo problema da imagem do banner...")
    
    try:
        # Inicializar o OrderProcessor
        processor = OrderProcessor()
        
        # Buscar o banner problemático (ID 7)
        print("\n1️⃣ Buscando banner com imagem problemática...")
        
        # Atualizar o banner para remover a imagem não pública
        result = processor.supabase.table('banners').update({
            'imagem_url': None
        }).eq('id', 7).execute()
        
        if result.data:
            print("✅ Banner ID 7 atualizado com sucesso!")
            print("   Imagem URL removida temporariamente")
        else:
            print("❌ Falha ao atualizar banner")
            return False
        
        # Verificar o resultado
        print("\n2️⃣ Verificando banners após correção...")
        banners = processor.get_banners()
        
        for banner in banners:
            banner_id = banner.get('id')
            titulo = banner.get('titulo', 'N/A')
            imagem_url = banner.get('imagem_url')
            
            if banner_id == 7:
                if imagem_url is None:
                    print(f"✅ Banner {banner_id} ({titulo}): Imagem removida - OK!")
                else:
                    print(f"❌ Banner {banner_id} ({titulo}): Ainda tem imagem - {imagem_url}")
            else:
                status = "OK" if imagem_url is None else f"Tem imagem: {imagem_url[:50]}..."
                print(f"ℹ️ Banner {banner_id} ({titulo}): {status}")
        
        print("\n🎉 Correção concluída!")
        print("💡 O banner agora funcionará sem imagem até que uma URL pública seja configurada")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir banner: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_banner_image()
    if success:
        print("\n✅ Banner corrigido com sucesso!")
        print("🔄 Recarregue o catálogo para ver as mudanças")
    else:
        print("\n❌ Falha na correção do banner")