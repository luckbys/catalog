#!/usr/bin/env python3
"""
Script para testar o proxy de imagens diretamente
"""

import requests
from urllib.parse import quote

def test_proxy_image():
    # URL da imagem que está dando problema
    image_url = "https://c4crm-minio.zv7gpn.easypanel.host/produtos/banner_baner_novo_1762169544726.png"
    
    # URL do proxy
    proxy_url = f"http://localhost:8000/api/proxy-image?url={quote(image_url)}"
    
    print(f"🔍 Testando proxy de imagens...")
    print(f"📍 Imagem original: {image_url}")
    print(f"🔗 URL do proxy: {proxy_url}")
    print("-" * 80)
    
    try:
        # Testar a imagem original primeiro
        print("1️⃣ Testando imagem original...")
        original_response = requests.head(image_url, timeout=10)
        print(f"   Status: {original_response.status_code}")
        
        if original_response.status_code != 200:
            print(f"   ❌ Imagem original não acessível: {original_response.status_code}")
            if original_response.status_code == 403:
                print("   🔒 Erro 403: A imagem não está pública no MinIO")
        else:
            print("   ✅ Imagem original acessível")
        
        # Testar o proxy
        print("\n2️⃣ Testando proxy...")
        proxy_response = requests.get(proxy_url, timeout=10)
        print(f"   Status: {proxy_response.status_code}")
        
        if proxy_response.status_code == 200:
            print("   ✅ Proxy funcionando!")
            print(f"   Content-Type: {proxy_response.headers.get('content-type', 'N/A')}")
            print(f"   Tamanho: {len(proxy_response.content)} bytes")
        else:
            print(f"   ❌ Proxy retornou erro: {proxy_response.status_code}")
            print(f"   Resposta: {proxy_response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_proxy_image()