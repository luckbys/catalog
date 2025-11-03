#!/usr/bin/env python3
"""
Script para corrigir o problema da imagem do banner usando configuração direta
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar supabase diretamente
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase não instalado. Instalando...")
    import subprocess
    subprocess.check_call(["pip", "install", "supabase"])
    from supabase import create_client, Client

def fix_banner_direct():
    print("🔧 Corrigindo problema da imagem do banner diretamente...")
    
    # Configurações do Supabase (mesmas do order_processor)
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Variáveis SUPABASE_URL e SUPABASE_KEY não configuradas")
        print("💡 Vou tentar usar as configurações padrão do sistema...")
        
        # Tentar configurações alternativas que podem estar sendo usadas
        possible_configs = [
            ("https://your-supabase-url.supabase.co", "your-anon-key"),
            # Adicionar outras possibilidades se necessário
        ]
        
        print("⚠️ Não foi possível acessar as configurações do Supabase")
        return False
    
    try:
        # Criar cliente Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("✅ Cliente Supabase criado com sucesso!")
        
        # 1. Verificar banner atual
        print("\n1️⃣ Verificando banner atual...")
        result = supabase.table('banners').select('*').eq('id', 7).execute()
        
        if not result.data:
            print("❌ Banner ID 7 não encontrado")
            return False
        
        banner = result.data[0]
        print(f"🎯 Banner encontrado: {banner.get('titulo')}")
        print(f"🖼️ URL atual: {banner.get('imagem_url')}")
        
        # 2. Atualizar banner removendo a imagem
        print("\n2️⃣ Removendo URL da imagem problemática...")
        
        update_result = supabase.table('banners').update({
            'imagem_url': None
        }).eq('id', 7).execute()
        
        if update_result.data:
            print("✅ Banner atualizado com sucesso!")
            print("   Imagem URL removida temporariamente")
        else:
            print("❌ Falha ao atualizar banner")
            return False
        
        # 3. Verificar resultado
        print("\n3️⃣ Verificando resultado...")
        verify_result = supabase.table('banners').select('*').eq('ativo', True).order('posicao').execute()
        
        for banner in verify_result.data:
            banner_id = banner.get('id')
            titulo = banner.get('titulo', 'N/A')
            imagem_url = banner.get('imagem_url')
            
            if banner_id == 7:
                if imagem_url is None:
                    print(f"✅ Banner {banner_id} ({titulo}): Imagem removida - OK!")
                else:
                    print(f"❌ Banner {banner_id} ({titulo}): Ainda tem imagem - {imagem_url}")
            else:
                status = "OK" if imagem_url is None else f"Tem imagem: {str(imagem_url)[:50]}..."
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
    success = fix_banner_direct()
    if success:
        print("\n✅ Banner corrigido com sucesso!")
        print("🔄 Recarregue o catálogo para ver as mudanças")
    else:
        print("\n❌ Falha na correção do banner")
        print("💡 Tente verificar as configurações do Supabase")