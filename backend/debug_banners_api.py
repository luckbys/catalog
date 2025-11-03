#!/usr/bin/env python3
"""
Script para debugar a resposta da API de banners
"""

import requests
import json

def debug_banners_api():
    print("🔍 Debugando API de banners...")
    
    try:
        # URL da API local
        api_url = "http://localhost:8000/api/banners"
        
        print(f"📍 Fazendo requisição para: {api_url}")
        response = requests.get(api_url)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📝 Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        print("\n📄 Resposta bruta:")
        print(f"Tipo: {type(response.text)}")
        print(f"Conteúdo: {response.text}")
        
        # Tentar fazer parse do JSON
        try:
            json_data = response.json()
            print(f"\n✅ JSON válido!")
            print(f"Tipo: {type(json_data)}")
            print(f"Dados: {json_data}")
            
            if isinstance(json_data, list):
                print(f"📊 Lista com {len(json_data)} itens")
                for i, item in enumerate(json_data):
                    print(f"  Item {i}: {type(item)} - {item}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao fazer parse do JSON: {e}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_banners_api()