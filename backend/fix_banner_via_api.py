#!/usr/bin/env python3
"""
Script para corrigir o problema da imagem do banner via API
"""

import requests
import json

def fix_banner_via_api():
    print("🔧 Corrigindo problema da imagem do banner via API...")
    
    try:
        # URL da API local
        api_base = "http://localhost:8000"
        
        # 1. Verificar banners atuais
        print("\n1️⃣ Verificando banners atuais...")
        response = requests.get(f"{api_base}/api/banners")
        
        if response.status_code != 200:
            print(f"❌ Erro ao buscar banners: {response.status_code}")
            return False
        
        response_data = response.json()
        banners = response_data.get('banners', [])
        print(f"📊 Encontrados {len(banners)} banners")
        
        # Encontrar o banner problemático
        banner_problema = None
        for banner in banners:
            if banner.get('id') == 7:
                banner_problema = banner
                break
        
        if not banner_problema:
            print("❌ Banner ID 7 não encontrado")
            return False
        
        print(f"🎯 Banner encontrado: {banner_problema.get('titulo')}")
        print(f"🖼️ URL atual: {banner_problema.get('imagem_url')}")
        
        # 2. Atualizar o banner removendo a imagem
        print("\n2️⃣ Removendo URL da imagem problemática...")
        
        # Preparar dados para atualização
        update_data = {
            "titulo": banner_problema.get('titulo'),
            "descricao": banner_problema.get('descricao'),
            "imagem_url": None,  # Remover a imagem
            "ativo": banner_problema.get('ativo', True)
        }
        
        # Fazer a atualização via PUT
        update_response = requests.put(
            f"{api_base}/api/banners/{banner_problema['id']}", 
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if update_response.status_code == 200:
            print("✅ Banner atualizado com sucesso!")
        else:
            print(f"❌ Erro ao atualizar banner: {update_response.status_code}")
            print(f"Resposta: {update_response.text}")
            return False
        
        # 3. Verificar o resultado
        print("\n3️⃣ Verificando resultado...")
        verify_response = requests.get(f"{api_base}/api/banners")
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            updated_banners = verify_data.get('banners', [])
            for banner in updated_banners:
                if banner.get('id') == 7:
                    if banner.get('imagem_url') is None:
                        print("✅ Correção confirmada - imagem removida!")
                    else:
                        print(f"❌ Imagem ainda presente: {banner.get('imagem_url')}")
                    break
        
        print("\n🎉 Correção concluída!")
        print("💡 O banner agora funcionará sem imagem até que uma URL pública seja configurada")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir banner: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_banner_via_api()
    if success:
        print("\n✅ Banner corrigido com sucesso!")
        print("🔄 Recarregue o catálogo para ver as mudanças")
    else:
        print("\n❌ Falha na correção do banner")