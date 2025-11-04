#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 EXTRAÇÃO DA LÓGICA DE DESCONTO DE PRODUÇÃO
Extrai especificamente a lógica de processamento de desconto do frontend de produção
"""

import requests
import re

def extract_discount_logic():
    """Extrai a lógica de desconto do frontend de produção"""
    
    print("🔍 EXTRAINDO LÓGICA DE DESCONTO DE PRODUÇÃO")
    print("=" * 60)
    
    try:
        # Buscar o HTML de produção
        print("📡 Buscando código de produção...")
        url_producao = "https://hakimfarma.devsible.com.br/catalogo.html?sessao_id=07ib2MEKsa"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url_producao, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar produção: {response.status_code}")
            return
        
        html_content = response.text
        
        # Procurar especificamente pela lógica de processamento de produtos
        print("\n🔍 EXTRAINDO LÓGICA DE PROCESSAMENTO...")
        
        # Padrão para encontrar a função que processa produtos
        pattern = r'data\.produtos\.forEach\(p\s*=>\s*\{(.*?)\}\);'
        
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        if matches:
            print("✅ Lógica de processamento encontrada!")
            
            # Pegar a primeira ocorrência (deve ser a principal)
            main_logic = matches[0]
            
            print("\n📋 CÓDIGO DE PROCESSAMENTO DE PRODUÇÃO:")
            print("-" * 50)
            
            # Limpar e formatar o código
            lines = main_logic.split('\n')
            formatted_lines = []
            
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('//'):  # Ignorar linhas vazias e comentários
                    formatted_lines.append(stripped)
            
            # Mostrar apenas as linhas relacionadas a desconto
            discount_lines = []
            for line in formatted_lines:
                if any(keyword in line.lower() for keyword in ['preco', 'price', 'desconto', 'discount', 'original']):
                    discount_lines.append(line)
            
            if discount_lines:
                print("🎯 LINHAS RELACIONADAS A DESCONTO:")
                for i, line in enumerate(discount_lines, 1):
                    print(f"{i:2d}. {line}")
            else:
                print("❌ Nenhuma linha de desconto encontrada!")
            
            # Salvar o código completo para análise
            with open('d:/catalog/production_discount_logic.js', 'w', encoding='utf-8') as f:
                f.write("// LÓGICA DE DESCONTO EXTRAÍDA DE PRODUÇÃO\n")
                f.write("// URL: " + url_producao + "\n\n")
                f.write("data.produtos.forEach(p => {\n")
                f.write(main_logic)
                f.write("\n});")
            
            print(f"\n💾 Código completo salvo em: production_discount_logic.js")
            
            # Verificar se há diferenças óbvias
            print("\n🔍 VERIFICANDO POSSÍVEIS PROBLEMAS...")
            
            full_code = main_logic.lower()
            
            # Verificações específicas
            checks = [
                ("preco_original", "Campo preco_original"),
                ("percentual_desconto", "Campo percentual_desconto"),
                ("valor_desconto", "Campo valor_desconto"),
                ("originalprice", "Variável originalPrice"),
                ("promoprice", "Variável promoPrice"),
                ("if.*preco_original", "Condição de preco_original"),
                ("if.*percentual_desconto", "Condição de percentual_desconto")
            ]
            
            for check, description in checks:
                if re.search(check, full_code):
                    print(f"  ✅ {description}: PRESENTE")
                else:
                    print(f"  ❌ {description}: AUSENTE")
        
        else:
            print("❌ Lógica de processamento NÃO encontrada!")
            
            # Tentar padrões alternativos
            alt_patterns = [
                r'produtos\.forEach\(.*?\{(.*?)\}',
                r'for.*?produto.*?produtos.*?\{(.*?)\}',
                r'\.map\(p\s*=>\s*\{(.*?)\}'
            ]
            
            for i, alt_pattern in enumerate(alt_patterns, 1):
                alt_matches = re.findall(alt_pattern, html_content, re.DOTALL)
                if alt_matches:
                    print(f"✅ Padrão alternativo {i} encontrado!")
                    break
            else:
                print("❌ Nenhum padrão de processamento encontrado!")
        
    except Exception as e:
        print(f"❌ Erro ao extrair lógica: {e}")

if __name__ == "__main__":
    extract_discount_logic()