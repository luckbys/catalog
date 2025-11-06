#!/usr/bin/env python3
"""
🔍 TESTE DA API DE PRODUÇÃO - DESCONTOS
Testa especificamente se a API de produção está retornando produtos com desconto
"""

import requests
import json
from datetime import datetime

def test_api_producao_desconto():
    """Testa a API de produção para verificar se retorna descontos"""
    print("🌐 TESTE DA API DE PRODUÇÃO - DESCONTOS")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # URL da API de produção
    api_url = "https://hakimfarma.devsible.com.br/api/produtos"
    
    try:
        print(f"🔗 Testando: {api_url}")
        print("📡 Fazendo requisição...")
        
        # Fazer requisição com headers para evitar cache
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        response = requests.get(api_url, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📏 Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            try:
                data = response.json()
                produtos = data.get('produtos', [])
                
                print(f"✅ API respondeu com {len(produtos)} produtos")
                print()
                
                # Verificar produtos com desconto
                produtos_com_desconto = []
                produtos_sem_desconto_mas_com_promocional = []
                
                for produto in produtos:
                    percentual_desconto = produto.get('percentual_desconto')
                    preco = produto.get('preco', 0)
                    preco_original = produto.get('preco_original')
                    
                    # Produto com desconto explícito
                    if percentual_desconto and percentual_desconto > 0:
                        produtos_com_desconto.append(produto)
                    
                    # Produto com preço original (indica desconto calculado)
                    elif preco_original and preco_original > preco:
                        produtos_sem_desconto_mas_com_promocional.append(produto)
                
                # Relatório de produtos com desconto
                if produtos_com_desconto:
                    print(f"🎯 ENCONTRADOS {len(produtos_com_desconto)} PRODUTOS COM DESCONTO:")
                    print("-" * 50)
                    for i, produto in enumerate(produtos_com_desconto[:5], 1):  # Mostrar apenas os primeiros 5
                        print(f"{i}. ID: {produto['id']}")
                        print(f"   📦 Produto: {produto['descricao'][:60]}...")
                        print(f"   💰 Preço atual: R$ {produto['preco']}")
                        print(f"   🏷️ Desconto: {produto['percentual_desconto']}%")
                        if produto.get('preco_original'):
                            print(f"   💸 Preço original: R$ {produto['preco_original']}")
                        print()
                else:
                    print("❌ NENHUM PRODUTO COM DESCONTO ENCONTRADO NA API DE PRODUÇÃO!")
                    print()
                
                # Relatório de produtos com preço original
                if produtos_sem_desconto_mas_com_promocional:
                    print(f"🔍 PRODUTOS COM PREÇO ORIGINAL (mas sem percentual_desconto): {len(produtos_sem_desconto_mas_com_promocional)}")
                    for i, produto in enumerate(produtos_sem_desconto_mas_com_promocional[:3], 1):
                        print(f"{i}. ID: {produto['id']} | {produto['descricao'][:40]}...")
                        print(f"   Preço: R$ {produto['preco']} | Original: R$ {produto['preco_original']}")
                        desconto_calc = ((produto['preco_original'] - produto['preco']) / produto['preco_original']) * 100
                        print(f"   Desconto calculado: {desconto_calc:.2f}%")
                        print()
                
                # Verificar produtos específicos que sabemos que têm desconto
                print("🔍 VERIFICANDO PRODUTOS ESPECÍFICOS COM DESCONTO:")
                print("-" * 50)
                produtos_teste = [2465302, 2465034, 2455206]  # IDs que sabemos que têm desconto
                
                for produto_id in produtos_teste:
                    produto_encontrado = None
                    for produto in produtos:
                        if produto.get('id') == produto_id:
                            produto_encontrado = produto
                            break
                    
                    if produto_encontrado:
                        print(f"✅ Produto {produto_id} ENCONTRADO:")
                        print(f"   📦 {produto_encontrado['descricao'][:50]}...")
                        print(f"   💰 Preço: R$ {produto_encontrado['preco']}")
                        print(f"   🏷️ Percentual desconto: {produto_encontrado.get('percentual_desconto', 'N/A')}")
                        print(f"   💸 Preço original: {produto_encontrado.get('preco_original', 'N/A')}")
                    else:
                        print(f"❌ Produto {produto_id} NÃO ENCONTRADO na resposta da API")
                    print()
                
                # Salvar amostra da resposta para análise
                amostra = {
                    'timestamp': datetime.now().isoformat(),
                    'total_produtos': len(produtos),
                    'produtos_com_desconto': len(produtos_com_desconto),
                    'primeiros_5_produtos': produtos[:5] if produtos else [],
                    'produtos_com_desconto_sample': produtos_com_desconto[:3] if produtos_com_desconto else []
                }
                
                with open('debug_api_producao_response.json', 'w', encoding='utf-8') as f:
                    json.dump(amostra, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Amostra da resposta salva em: debug_api_producao_response.json")
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"📄 Primeiros 500 caracteres da resposta:")
                print(response.text[:500])
                
        else:
            print(f"❌ API retornou status {response.status_code}")
            print(f"📄 Resposta: {response.text[:500]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout ao conectar com a API de produção")
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def compare_with_local():
    """Compara com a API local para referência"""
    print("\n🏠 COMPARAÇÃO COM API LOCAL")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/api/produtos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            produtos = data.get('produtos', [])
            
            produtos_com_desconto = [p for p in produtos if p.get('percentual_desconto', 0) > 0]
            
            print(f"✅ API Local: {len(produtos)} produtos, {len(produtos_com_desconto)} com desconto")
            
            if produtos_com_desconto:
                print("🎯 Produtos com desconto na API local:")
                for produto in produtos_com_desconto[:3]:
                    print(f"   ID: {produto['id']} | Desconto: {produto['percentual_desconto']}%")
        else:
            print(f"❌ API Local retornou status {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Não foi possível conectar à API local: {e}")

if __name__ == "__main__":
    test_api_producao_desconto()
    compare_with_local()