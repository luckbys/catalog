#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 TESTE API COM SESSÃO PERSONALIZADA
Verifica se o parâmetro sessao_id está afetando os produtos retornados
"""

import requests
import json

def test_api_with_session():
    """Testa a API com e sem o parâmetro de sessão"""
    
    print("🔍 TESTANDO API COM SESSÃO PERSONALIZADA")
    print("=" * 50)
    
    # URLs para testar
    api_sem_sessao = "https://hakimfarma.devsible.com.br/api/produtos"
    api_com_sessao = "https://hakimfarma.devsible.com.br/api/produtos?sessao_id=07ib2MEKsa"
    
    try:
        print("\n📡 Testando API SEM sessão...")
        response_sem = requests.get(api_sem_sessao, timeout=10)
        print(f"Status: {response_sem.status_code}")
        
        if response_sem.status_code == 200:
            data_sem = response_sem.json()
            produtos_sem = data_sem.get('produtos', [])
            print(f"Total de produtos SEM sessão: {len(produtos_sem)}")
            
            # Procurar produtos com desconto
            produtos_desconto_sem = []
            for produto in produtos_sem:
                preco = produto.get('preco', 0)
                preco_original = produto.get('preco_original', 0)
                
                if preco_original and preco_original > preco:
                    produtos_desconto_sem.append({
                        'id': produto.get('id'),
                        'nome': produto.get('nome', 'N/A'),
                        'preco': preco,
                        'preco_original': preco_original,
                        'percentual_desconto': produto.get('percentual_desconto', 0)
                    })
            
            print(f"Produtos com desconto SEM sessão: {len(produtos_desconto_sem)}")
            for p in produtos_desconto_sem:
                print(f"  - {p['nome']} (ID: {p['id']}) - {p['percentual_desconto']}% desconto")
        
        print("\n📡 Testando API COM sessão...")
        response_com = requests.get(api_com_sessao, timeout=10)
        print(f"Status: {response_com.status_code}")
        
        if response_com.status_code == 200:
            data_com = response_com.json()
            produtos_com = data_com.get('produtos', [])
            print(f"Total de produtos COM sessão: {len(produtos_com)}")
            
            # Procurar produtos com desconto
            produtos_desconto_com = []
            for produto in produtos_com:
                preco = produto.get('preco', 0)
                preco_original = produto.get('preco_original', 0)
                
                if preco_original and preco_original > preco:
                    produtos_desconto_com.append({
                        'id': produto.get('id'),
                        'nome': produto.get('nome', 'N/A'),
                        'preco': preco,
                        'preco_original': preco_original,
                        'percentual_desconto': produto.get('percentual_desconto', 0)
                    })
            
            print(f"Produtos com desconto COM sessão: {len(produtos_desconto_com)}")
            for p in produtos_desconto_com:
                print(f"  - {p['nome']} (ID: {p['id']}) - {p['percentual_desconto']}% desconto")
        
        # Comparação
        print("\n🔍 COMPARAÇÃO:")
        print("=" * 30)
        
        if response_sem.status_code == 200 and response_com.status_code == 200:
            print(f"Produtos SEM sessão: {len(produtos_sem)}")
            print(f"Produtos COM sessão: {len(produtos_com)}")
            print(f"Diferença: {len(produtos_sem) - len(produtos_com)}")
            
            print(f"\nDescontos SEM sessão: {len(produtos_desconto_sem)}")
            print(f"Descontos COM sessão: {len(produtos_desconto_com)}")
            
            if len(produtos_desconto_sem) != len(produtos_desconto_com):
                print("🚨 PROBLEMA ENCONTRADO! A sessão está filtrando produtos com desconto!")
            else:
                print("✅ Sessão não afeta produtos com desconto")
        
        # Verificar se os IDs específicos estão presentes
        print("\n🎯 VERIFICANDO PRODUTOS ESPECÍFICOS:")
        ids_teste = [2465302, 2465034, 2455206]  # Tadalafila, 070330731769, Rivotril
        
        for api_name, produtos in [("SEM sessão", produtos_sem if response_sem.status_code == 200 else []), 
                                  ("COM sessão", produtos_com if response_com.status_code == 200 else [])]:
            print(f"\n{api_name}:")
            for id_teste in ids_teste:
                produto_encontrado = next((p for p in produtos if p.get('id') == id_teste), None)
                if produto_encontrado:
                    print(f"  ✅ ID {id_teste}: {produto_encontrado.get('nome', 'N/A')}")
                else:
                    print(f"  ❌ ID {id_teste}: NÃO ENCONTRADO")
        
    except Exception as e:
        print(f"❌ Erro ao testar APIs: {e}")

if __name__ == "__main__":
    test_api_with_session()