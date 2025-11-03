#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

print("🔍 Verificando status do banner após correção...")

try:
    # Buscar banners
    response = requests.get('http://localhost:8000/api/banners')
    data = response.json()
    
    # Encontrar banner ID 7
    banner = None
    for b in data['banners']:
        if b['id'] == 7:
            banner = b
            break
    
    if banner:
        print(f"🎯 Banner ID 7 encontrado:")
        print(f"📝 Título: {banner['titulo']}")
        print(f"🖼️ Imagem URL: {banner.get('imagem_url', 'None')}")
        
        if banner.get('imagem_url') is None:
            print("✅ SUCESSO! Banner corrigido - imagem removida!")
        else:
            print("❌ Banner ainda tem imagem problemática")
            print(f"   URL problemática: {banner['imagem_url']}")
    else:
        print("❌ Banner ID 7 não encontrado")
        
except Exception as e:
    print(f"❌ Erro ao verificar: {e}")