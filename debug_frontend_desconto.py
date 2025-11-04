#!/usr/bin/env python3
"""
🔍 DEBUG FRONTEND DESCONTO
Script para simular exatamente como o frontend processa os produtos com desconto
"""

import requests
import json

def debug_frontend_processing():
    """Simula o processamento do frontend para produtos com desconto"""
    print("🔍 DEBUG DO PROCESSAMENTO FRONTEND")
    print("=" * 60)
    
    try:
        # Testar API local
        print("📡 Buscando produtos da API local...")
        response = requests.get("http://localhost:8000/api/produtos", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            produtos = data.get('produtos', [])
            print(f"✅ API retornou {len(produtos)} produtos")
            
            # Simular exatamente o processamento do frontend (linha 2798-2827 do catalogo.html)
            products_data = []
            produtos_com_desconto_processados = []
            
            for p in produtos:
                # Calcular preço promocional se houver desconto (linha 2798-2811)
                original_price = None
                promo_price = None
                
                if p.get('preco_original') and (p.get('percentual_desconto') or p.get('valor_desconto')):
                    original_price = float(p['preco_original'])
                    promo_price = float(p['preco'])
                    print(f"🎯 CASO 1 - Produto {p.get('id')}: preco_original={original_price}, promo_price={promo_price}")
                    
                elif p.get('percentual_desconto') and p.get('percentual_desconto') > 0:
                    # Se só temos percentual de desconto, calcular preço original
                    original_price = float(p['preco']) / (1 - (p['percentual_desconto'] / 100))
                    promo_price = float(p['preco'])
                    print(f"🎯 CASO 2 - Produto {p.get('id')}: percentual={p['percentual_desconto']}%, original_calculado={original_price}, promo={promo_price}")
                    
                elif p.get('valor_desconto') and p.get('valor_desconto') > 0:
                    # Se só temos valor de desconto, calcular preço original
                    original_price = float(p['preco']) + float(p['valor_desconto'])
                    promo_price = float(p['preco'])
                    print(f"🎯 CASO 3 - Produto {p.get('id')}: valor_desconto={p['valor_desconto']}, original_calculado={original_price}, promo={promo_price}")
                
                # Criar objeto produto como no frontend (linha 2813-2827)
                product_obj = {
                    'id': str(p.get('id')),
                    'name': p.get('descricao'),
                    'description': p.get('apresentacao') or p.get('categoria') or p.get('descricao'),
                    'price': float(p.get('preco')),
                    'originalPrice': original_price,
                    'promoPrice': promo_price,
                    'percentualDesconto': float(p['percentual_desconto']) if p.get('percentual_desconto') else None,
                    'valorDesconto': float(p['valor_desconto']) if p.get('valor_desconto') else None,
                    'imageUrl': p.get('imagem_url'),
                    'laboratorio': p.get('laboratorio')
                }
                
                products_data.append(product_obj)
                
                # Se tem desconto, adicionar à lista de debug
                if original_price and promo_price:
                    produtos_com_desconto_processados.append(product_obj)
            
            print(f"\n📊 RESULTADO DO PROCESSAMENTO:")
            print(f"   Total de produtos processados: {len(products_data)}")
            print(f"   Produtos com desconto (originalPrice && promoPrice): {len(produtos_com_desconto_processados)}")
            
            if produtos_com_desconto_processados:
                print(f"\n🎯 PRODUTOS COM DESCONTO PROCESSADOS:")
                print("-" * 50)
                
                for i, produto in enumerate(produtos_com_desconto_processados, 1):
                    print(f"{i}. ID: {produto['id']}")
                    print(f"   📦 Nome: {produto['name'][:50]}...")
                    print(f"   💰 Preço atual: R$ {produto['price']:.2f}")
                    print(f"   💸 Preço original: R$ {produto['originalPrice']:.2f}")
                    print(f"   🏷️ Preço promo: R$ {produto['promoPrice']:.2f}")
                    
                    if produto['percentualDesconto']:
                        print(f"   📊 Percentual desconto: {produto['percentualDesconto']}%")
                    if produto['valorDesconto']:
                        print(f"   💵 Valor desconto: R$ {produto['valorDesconto']:.2f}")
                    
                    # Simular a condição do frontend para exibir badge de desconto (linha 2172)
                    show_discount_badge = produto['originalPrice'] and produto['promoPrice']
                    print(f"   🏷️ Exibiria badge de desconto: {'✅ SIM' if show_discount_badge else '❌ NÃO'}")
                    
                    if show_discount_badge:
                        if produto['percentualDesconto']:
                            badge_text = f"-{round(produto['percentualDesconto'])}%"
                        elif produto['valorDesconto']:
                            badge_text = f"-R$ {produto['valorDesconto']:.2f}"
                        else:
                            badge_text = "DESCONTO"
                        print(f"   🎫 Texto do badge: {badge_text}")
                    
                    print()
            else:
                print("\n❌ NENHUM PRODUTO COM DESCONTO PROCESSADO!")
                print("   Isso significa que a condição originalPrice && promoPrice não está sendo atendida")
                
                # Debug: mostrar alguns produtos para entender por que não têm desconto
                print(f"\n🔍 DEBUG: Primeiros 3 produtos (para análise):")
                for i, produto in enumerate(products_data[:3], 1):
                    print(f"{i}. ID: {produto['id']}")
                    print(f"   originalPrice: {produto['originalPrice']}")
                    print(f"   promoPrice: {produto['promoPrice']}")
                    print(f"   percentualDesconto: {produto['percentualDesconto']}")
                    print(f"   valorDesconto: {produto['valorDesconto']}")
                    print()
            
        else:
            print(f"❌ API retornou status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API local")
        print("   Certifique-se de que o servidor backend está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    debug_frontend_processing()