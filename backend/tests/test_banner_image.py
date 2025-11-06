#!/usr/bin/env python3
import requests

def test_image_url():
    url = 'https://c4crm-minio.zv7gpn.easypanel.host/produtos/banner_oferta_especial__amoxicilina_1762167190535.png'
    
    print(f"🔍 Testando URL: {url}")
    print("-" * 80)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('content-length', 'N/A')}")
        
        if response.status_code == 200:
            print("✅ Imagem acessível!")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_image_url()