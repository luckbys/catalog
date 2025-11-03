#!/usr/bin/env python3
"""
Script para verificar os banners através da API do backend
"""

import requests
import json

def check_banners_via_api():
    print("🔍 Verificando banners através da API do backend...")
    
    try:
        # Fazer requisição para o endpoint de banners
        response = requests.get('http://localhost:8000/api/banners')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API respondeu com status 200")
            
            # Verificar se a resposta tem a chave 'banners'
            if 'banners' in data:
                banners = data['banners']
                print(f"📊 Total de banners encontrados: {len(banners)}")
                
                for i, banner in enumerate(banners, 1):
                    print(f"\n🎯 Banner {i}:")
                    print(f"   ID: {banner.get('id', 'N/A')}")
                    print(f"   Título: {banner.get('titulo', 'N/A')}")
                    print(f"   Ativo: {banner.get('ativo', 'N/A')}")
                    print(f"   Posição: {banner.get('posicao', 'N/A')}")
                    print(f"   Imagem URL: {banner.get('imagem_url', 'NULL')}")
                    
                    # Verificar se tem a nova URL
                    if banner.get('imagem_url') and 'banner_baner_novo_1762169544726.png' in banner.get('imagem_url', ''):
                        print("   ✅ Esta é a nova imagem do banner!")
                    elif banner.get('imagem_url'):
                        print("   📷 Tem imagem, mas não é a nova")
                    else:
                        print("   ❌ Sem imagem")
                
                return banners
            else:
                print(f"📊 Resposta não tem chave 'banners': {data}")
                return None
            
            return banners
        else:
            print(f"❌ Erro na API: Status {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return None

if __name__ == "__main__":
    banners = check_banners_via_api()