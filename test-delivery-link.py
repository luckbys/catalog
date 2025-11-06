#!/usr/bin/env python3
"""
Script para testar a construção do link do entregador
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_url_construction():
    """Testa diferentes formatos de CLIENT_BASE_URL"""
    
    test_cases = [
        "https://catalogo-hakim/catalogo.html",
        "https://catalogo-hakim.zv7gpn.easypanel.host/catalogo.html",
        "https://catalogo-hakim.zv7gpn.easypanel.host",
        "catalogo-hakim.zv7gpn.easypanel.host",
        "http://localhost:8000",
    ]
    
    order_id = 123
    
    print("=" * 80)
    print("TESTE DE CONSTRUÇÃO DE URL DO ENTREGADOR")
    print("=" * 80)
    print()
    
    for base_url in test_cases:
        print(f"INPUT: {base_url}")
        
        # Processar URL
        processed_url = base_url
        
        # Se CLIENT_BASE_URL tem /catalogo.html, remover
        if '/catalogo.html' in processed_url:
            processed_url = processed_url.split('/catalogo.html')[0]
        
        # Se não tem protocolo, adicionar https://
        if not processed_url.startswith('http://') and not processed_url.startswith('https://'):
            processed_url = f"https://{processed_url}"
        
        # Remover barra final se existir
        processed_url = processed_url.rstrip('/')
        
        # Construir URL completa
        delivery_url = f"{processed_url}/entregador.html?pedido={order_id}"
        
        print(f"  → Base processada: {processed_url}")
        print(f"  → URL final: {delivery_url}")
        print()
    
    print("=" * 80)
    print("URL ATUAL DO .ENV")
    print("=" * 80)
    
    current_base = os.getenv("CLIENT_BASE_URL", "http://localhost:8000")
    print(f"CLIENT_BASE_URL: {current_base}")
    
    # Processar
    processed = current_base
    if '/catalogo.html' in processed:
        processed = processed.split('/catalogo.html')[0]
    if not processed.startswith('http://') and not processed.startswith('https://'):
        processed = f"https://{processed}"
    processed = processed.rstrip('/')
    
    final_url = f"{processed}/entregador.html?pedido={order_id}"
    
    print(f"Base processada: {processed}")
    print(f"URL final: {final_url}")
    print()
    print("✅ Teste esta URL no navegador para verificar se abre!")
    print()

if __name__ == "__main__":
    test_url_construction()
