#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 DEBUG FRONTEND DE PRODUÇÃO REAL
Analisa o código JavaScript do frontend de produção para encontrar diferenças
"""

import requests
import re

def analyze_production_frontend():
    """Analisa o frontend de produção para encontrar diferenças no código"""
    
    print("🔍 ANALISANDO FRONTEND DE PRODUÇÃO")
    print("=" * 50)
    
    try:
        # Buscar o HTML de produção
        print("📡 Buscando HTML de produção...")
        url_producao = "https://hakimfarma.devsible.com.br/catalogo.html?sessao_id=07ib2MEKsa"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url_producao, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar produção: {response.status_code}")
            return
        
        html_content = response.text
        print(f"Tamanho do HTML: {len(html_content)} caracteres")
        
        # Procurar pela lógica de desconto no JavaScript
        print("\n🔍 PROCURANDO LÓGICA DE DESCONTO...")
        
        # Padrões para procurar
        patterns = [
            r'originalPrice\s*=.*?preco_original',
            r'promoPrice\s*=.*?preco',
            r'percentual_desconto',
            r'badge.*?desconto',
            r'discount.*?badge',
            r'preco_original.*?preco'
        ]
        
        found_patterns = []
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                found_patterns.extend(matches)
        
        if found_patterns:
            print("✅ Lógica de desconto encontrada:")
            for i, match in enumerate(found_patterns[:5]):  # Mostrar apenas os primeiros 5
                print(f"  {i+1}. {match[:100]}...")
        else:
            print("❌ Lógica de desconto NÃO encontrada!")
        
        # Procurar especificamente pela função de processamento de produtos
        print("\n🔍 PROCURANDO FUNÇÃO DE PROCESSAMENTO...")
        
        # Procurar por função que processa produtos
        process_patterns = [
            r'function.*?processProducts.*?\{.*?\}',
            r'processProducts.*?=.*?function.*?\{.*?\}',
            r'produtos\.forEach.*?\{.*?\}',
            r'for.*?produto.*?produtos.*?\{.*?\}'
        ]
        
        process_found = False
        for pattern in process_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                print("✅ Função de processamento encontrada:")
                for match in matches[:2]:  # Mostrar apenas as primeiras 2
                    print(f"  {match[:200]}...")
                process_found = True
                break
        
        if not process_found:
            print("❌ Função de processamento NÃO encontrada!")
        
        # Verificar se há comentários ou código comentado
        print("\n🔍 VERIFICANDO CÓDIGO COMENTADO...")
        commented_discount = re.findall(r'//.*?desconto.*?', html_content, re.IGNORECASE)
        if commented_discount:
            print("⚠️ Código de desconto comentado encontrado:")
            for comment in commented_discount[:3]:
                print(f"  {comment}")
        else:
            print("✅ Nenhum código de desconto comentado")
        
        # Verificar versão ou timestamp
        print("\n🔍 VERIFICANDO VERSÃO/TIMESTAMP...")
        version_patterns = [
            r'version.*?["\']([^"\']+)["\']',
            r'timestamp.*?["\']([^"\']+)["\']',
            r'build.*?["\']([^"\']+)["\']',
            r'updated.*?["\']([^"\']+)["\']'
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                print(f"📅 Versão/Timestamp encontrado: {matches[0]}")
                break
        else:
            print("❓ Nenhuma informação de versão encontrada")
        
        # Verificar se há erros JavaScript inline
        print("\n🔍 VERIFICANDO ERROS JAVASCRIPT...")
        error_patterns = [
            r'console\.error.*?desconto',
            r'throw.*?desconto',
            r'error.*?desconto'
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                print(f"⚠️ Possível erro relacionado a desconto: {matches[0]}")
        
        # Salvar uma amostra do código para análise manual
        print("\n💾 SALVANDO AMOSTRA DO CÓDIGO...")
        
        # Extrair JavaScript relacionado a produtos
        js_matches = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        
        with open('d:/catalog/frontend_producao_sample.js', 'w', encoding='utf-8') as f:
            f.write("// AMOSTRA DO JAVASCRIPT DE PRODUÇÃO\n")
            f.write("// Extraído em: " + str(requests.utils.default_headers()) + "\n\n")
            
            for i, js_code in enumerate(js_matches):
                if any(keyword in js_code.lower() for keyword in ['produto', 'desconto', 'preco', 'price']):
                    f.write(f"// === SCRIPT {i+1} ===\n")
                    f.write(js_code[:2000])  # Primeiros 2000 caracteres
                    f.write("\n\n")
        
        print("✅ Amostra salva em frontend_producao_sample.js")
        
    except Exception as e:
        print(f"❌ Erro ao analisar frontend de produção: {e}")

if __name__ == "__main__":
    analyze_production_frontend()