#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 TESTE FINAL DE BADGES
Verifica se a lógica EXATA de renderização de badges está presente em produção
"""

import requests
import re

def final_badge_test():
    """Teste final para encontrar a lógica específica de badges"""
    
    print("🔍 TESTE FINAL DE RENDERIZAÇÃO DE BADGES")
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
        
        # Procurar pela lógica EXATA de renderização de badges
        print("\n🔍 PROCURANDO LÓGICA EXATA DE BADGES...")
        
        # Padrão específico que deve estar presente
        exact_patterns = [
            r'product\.originalPrice\s*&&\s*product\.promoPrice',
            r'discount-badge',
            r'Math\.round\(product\.percentualDesconto\)',
            r'product\.valorDesconto\.toFixed\(2\)',
            r'OFERTA'
        ]
        
        results = {}
        for pattern in exact_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            results[pattern] = len(matches) > 0
            
            if matches:
                print(f"✅ {pattern}: ENCONTRADO ({len(matches)} ocorrências)")
            else:
                print(f"❌ {pattern}: NÃO ENCONTRADO")
        
        # Verificar se TODA a lógica está presente
        all_present = all(results.values())
        
        print(f"\n🎯 RESULTADO FINAL:")
        if all_present:
            print("✅ TODA a lógica de badges está presente em produção!")
            print("   O problema deve estar em outro lugar...")
        else:
            print("❌ Lógica de badges INCOMPLETA em produção!")
            missing = [pattern for pattern, found in results.items() if not found]
            print("   Padrões ausentes:")
            for pattern in missing:
                print(f"   - {pattern}")
        
        # Procurar especificamente pelo template de produto
        print("\n🔍 PROCURANDO TEMPLATE DE PRODUTO...")
        
        # Padrão para encontrar o template HTML do produto
        template_pattern = r'`\s*<div[^>]*class="[^"]*product[^"]*"[^>]*>.*?</div>\s*`'
        template_matches = re.findall(template_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        if template_matches:
            print(f"✅ Template de produto encontrado! ({len(template_matches)} templates)")
            
            # Verificar se o template contém a lógica de badge
            for i, template in enumerate(template_matches):
                if 'discount-badge' in template:
                    print(f"✅ Template {i+1} contém discount-badge")
                    
                    # Salvar o template para análise
                    with open(f'd:/catalog/production_template_{i+1}.html', 'w', encoding='utf-8') as f:
                        f.write(f"<!-- TEMPLATE DE PRODUTO {i+1} DE PRODUÇÃO -->\n")
                        f.write(template)
                    
                    print(f"💾 Template salvo em: production_template_{i+1}.html")
                else:
                    print(f"❌ Template {i+1} NÃO contém discount-badge")
        else:
            print("❌ Nenhum template de produto encontrado!")
        
        # Verificar se há CSS para discount-badge
        print("\n🔍 VERIFICANDO CSS DE DISCOUNT-BADGE...")
        
        css_pattern = r'\.discount-badge\s*\{[^}]*\}'
        css_matches = re.findall(css_pattern, html_content, re.DOTALL)
        
        if css_matches:
            print(f"✅ CSS de discount-badge encontrado! ({len(css_matches)} regras)")
            for i, css in enumerate(css_matches):
                print(f"  Regra {i+1}: {css[:100]}...")
        else:
            print("❌ CSS de discount-badge NÃO encontrado!")
        
    except Exception as e:
        print(f"❌ Erro no teste final: {e}")

if __name__ == "__main__":
    final_badge_test()