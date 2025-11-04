#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 TESTE DE RENDERIZAÇÃO DE BADGES
Verifica se os badges de desconto estão sendo renderizados no frontend de produção
"""

import requests
import re

def test_badge_rendering():
    """Testa se os badges de desconto estão sendo renderizados"""
    
    print("🔍 TESTANDO RENDERIZAÇÃO DE BADGES DE DESCONTO")
    print("=" * 60)
    
    try:
        # Buscar o HTML de produção
        print("📡 Buscando HTML de produção...")
        url_producao = "https://hakimfarma.devsible.com.br/catalogo.html?sessao_id=07ib2MEKsa"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url_producao, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar produção: {response.status_code}")
            return
        
        html_content = response.text
        
        # Procurar pela lógica de renderização de badges
        print("\n🔍 PROCURANDO LÓGICA DE RENDERIZAÇÃO DE BADGES...")
        
        # Padrões para encontrar a renderização de badges
        badge_patterns = [
            r'badge.*?desconto',
            r'discount.*?badge',
            r'originalPrice.*?promoPrice.*?badge',
            r'percentual.*?badge',
            r'class.*?discount',
            r'class.*?badge.*?discount'
        ]
        
        badge_found = False
        for pattern in badge_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"✅ Padrão de badge encontrado: {pattern}")
                for match in matches[:3]:  # Mostrar apenas os primeiros 3
                    print(f"  - {match[:100]}...")
                badge_found = True
        
        if not badge_found:
            print("❌ Nenhuma lógica de badge encontrada!")
        
        # Procurar especificamente pela função que cria os cards de produto
        print("\n🔍 PROCURANDO FUNÇÃO DE CRIAÇÃO DE CARDS...")
        
        # Padrão para encontrar a função createProductCard
        card_pattern = r'function\s+createProductCard.*?\{(.*?)\n\s*\}'
        card_matches = re.findall(card_pattern, html_content, re.DOTALL)
        
        if card_matches:
            print("✅ Função createProductCard encontrada!")
            
            card_code = card_matches[0]
            
            # Verificar se há lógica de badge na função
            if 'badge' in card_code.lower() or 'discount' in card_code.lower():
                print("✅ Lógica de badge presente na função createProductCard")
                
                # Extrair linhas relacionadas a badge
                lines = card_code.split('\n')
                badge_lines = [line.strip() for line in lines if 'badge' in line.lower() or 'discount' in line.lower()]
                
                if badge_lines:
                    print("🎯 LINHAS DE BADGE NA FUNÇÃO:")
                    for i, line in enumerate(badge_lines[:5], 1):
                        print(f"  {i}. {line}")
            else:
                print("❌ Nenhuma lógica de badge na função createProductCard!")
        else:
            print("❌ Função createProductCard NÃO encontrada!")
        
        # Procurar por condições que podem estar impedindo a exibição
        print("\n🔍 PROCURANDO CONDIÇÕES DE EXIBIÇÃO...")
        
        # Padrões que podem estar bloqueando a exibição
        blocking_patterns = [
            r'if\s*\(.*originalPrice.*\)',
            r'if\s*\(.*promoPrice.*\)',
            r'if\s*\(.*percentual.*\)',
            r'display:\s*none',
            r'hidden',
            r'visibility:\s*hidden'
        ]
        
        for pattern in blocking_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                print(f"⚠️ Possível condição bloqueadora: {pattern}")
                for match in matches[:2]:
                    print(f"  - {match}")
        
        # Salvar a função createProductCard para análise
        if card_matches:
            with open('d:/catalog/production_createProductCard.js', 'w', encoding='utf-8') as f:
                f.write("// FUNÇÃO createProductCard DE PRODUÇÃO\n")
                f.write("// Extraída de: " + url_producao + "\n\n")
                f.write("function createProductCard(product) {\n")
                f.write(card_matches[0])
                f.write("\n}")
            
            print(f"\n💾 Função createProductCard salva em: production_createProductCard.js")
        
    except Exception as e:
        print(f"❌ Erro ao testar renderização: {e}")

if __name__ == "__main__":
    test_badge_rendering()