#!/usr/bin/env python3
"""
Script para verificar os dados atuais dos banners no Supabase
"""

import os
import sys
sys.path.append('backend')

from order_processor import OrderProcessor

def check_banners():
    print("🔍 Verificando dados atuais dos banners no Supabase...")
    
    try:
        # Inicializar o OrderProcessor
        processor = OrderProcessor()
        
        # Buscar banners
        banners = processor.get_banners()
        
        print(f"\n📊 Total de banners encontrados: {len(banners)}")
        
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
        
        return banners
        
    except Exception as e:
        print(f"❌ Erro ao verificar banners: {e}")
        return None

if __name__ == "__main__":
    banners = check_banners()