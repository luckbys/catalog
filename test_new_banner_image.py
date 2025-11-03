#!/usr/bin/env python3
"""
Script para testar se a nova URL da imagem do banner está acessível
"""

import requests

def test_new_banner_image():
    url = "https://c4crm-minio.zv7gpn.easypanel.host/produtos/banner_baner_novo_1762169544726.png"
    
    print(f"🔍 Testando acessibilidade da nova imagem do banner...")
    print(f"📍 URL: {url}")
    
    try:
        # Fazer requisição HEAD primeiro (mais rápido)
        print("\n🚀 Fazendo requisição HEAD...")
        response = requests.head(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        if response.status_code == 200:
            print("✅ Imagem acessível via HEAD!")
            
            # Agora fazer GET para confirmar
            print("\n🚀 Fazendo requisição GET para confirmar...")
            get_response = requests.get(url, timeout=10)
            
            print(f"📊 GET Status Code: {get_response.status_code}")
            print(f"📏 Tamanho do conteúdo: {len(get_response.content)} bytes")
            
            if get_response.status_code == 200:
                print("✅ Imagem totalmente acessível!")
                return True
            else:
                print(f"❌ Erro no GET: {get_response.status_code}")
                return False
        else:
            print(f"❌ Erro no HEAD: {response.status_code}")
            if response.status_code == 403:
                print("🔒 Erro 403: Access Denied - A imagem não está pública")
            elif response.status_code == 404:
                print("🔍 Erro 404: Not Found - A imagem não existe")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout: A requisição demorou muito para responder")
        return False
    except requests.exceptions.ConnectionError:
        print("🌐 Erro de conexão: Não foi possível conectar ao servidor")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_new_banner_image()
    if success:
        print("\n🎉 A imagem está acessível! O problema pode estar no frontend.")
    else:
        print("\n🚨 A imagem não está acessível. Este é o problema!")