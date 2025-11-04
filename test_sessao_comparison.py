#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 TESTE DE COMPARAÇÃO: API COM E SEM SESSAO_ID
Vamos descobrir se o parâmetro sessao_id está afetando os descontos!
"""

import requests
import json
from datetime import datetime

API_BASE = 'https://hakimfarma.devsible.com.br'
SESSAO_ID = '07ib2MEKsa'  # Sessão mencionada pelo usuário

def log_result(message, data=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    if data:
        print(f"           {data}")

def test_api_endpoint(endpoint_name, url):
    """Testa um endpoint da API e retorna os dados"""
    try:
        log_result(f"🔄 Testando {endpoint_name}...")
        log_result(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        log_result(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            produtos = data.get('produtos', [])
            log_result(f"   ✅ Sucesso: {len(produtos)} produtos encontrados")
            return produtos
        else:
            log_result(f"   ❌ Erro: Status {response.status_code}")
            return None
            
    except Exception as e:
        log_result(f"   ❌ Exceção: {str(e)}")
        return None

def analyze_discounts(produtos, label):
    """Analisa os descontos nos produtos"""
    if not produtos:
        log_result(f"❌ {label}: Nenhum produto para analisar")
        return
    
    log_result(f"📊 ANÁLISE DE DESCONTOS - {label}")
    log_result(f"   Total de produtos: {len(produtos)}")
    
    discount_count = 0
    discount_details = []
    
    for i, p in enumerate(produtos):
        has_discount = False
        discount_info = {
            'id': p.get('id'),
            'nome': p.get('descricao', 'N/A'),
            'preco': p.get('preco'),
            'preco_original': p.get('preco_original'),
            'percentual_desconto': p.get('percentual_desconto'),
            'valor_desconto': p.get('valor_desconto'),
            'metodo_desconto': None
        }
        
        # Método 1: preco_original existe
        if p.get('preco_original') and (p.get('percentual_desconto') or p.get('valor_desconto')):
            has_discount = True
            discount_info['metodo_desconto'] = 'preco_original'
        
        # Método 2: percentual_desconto > 0
        elif p.get('percentual_desconto') and float(p.get('percentual_desconto', 0)) > 0:
            has_discount = True
            discount_info['metodo_desconto'] = 'percentual_desconto'
        
        # Método 3: valor_desconto > 0
        elif p.get('valor_desconto') and float(p.get('valor_desconto', 0)) > 0:
            has_discount = True
            discount_info['metodo_desconto'] = 'valor_desconto'
        
        if has_discount:
            discount_count += 1
            discount_details.append(discount_info)
    
    log_result(f"   🎯 Produtos com desconto: {discount_count}")
    
    if discount_details:
        log_result(f"   📋 DETALHES DOS DESCONTOS:")
        for detail in discount_details:
            log_result(f"      • {detail['nome']} (ID: {detail['id']})")
            log_result(f"        Método: {detail['metodo_desconto']}")
            log_result(f"        Preço: R$ {detail['preco']}")
            if detail['preco_original']:
                log_result(f"        Preço Original: R$ {detail['preco_original']}")
            if detail['percentual_desconto']:
                log_result(f"        Percentual: {detail['percentual_desconto']}%")
            if detail['valor_desconto']:
                log_result(f"        Valor Desconto: R$ {detail['valor_desconto']}")
            log_result("")
    
    return discount_count, discount_details

def compare_products(produtos_sem_sessao, produtos_com_sessao):
    """Compara os produtos entre as duas chamadas"""
    log_result("🔍 COMPARAÇÃO DETALHADA")
    
    if not produtos_sem_sessao or not produtos_com_sessao:
        log_result("❌ Não é possível comparar - uma das listas está vazia")
        return
    
    # Comparar quantidades
    log_result(f"   Sem sessão: {len(produtos_sem_sessao)} produtos")
    log_result(f"   Com sessão: {len(produtos_com_sessao)} produtos")
    
    # Criar dicionários por ID para comparação
    sem_sessao_dict = {str(p.get('id')): p for p in produtos_sem_sessao}
    com_sessao_dict = {str(p.get('id')): p for p in produtos_com_sessao}
    
    # Verificar produtos que existem em uma lista mas não na outra
    ids_sem_sessao = set(sem_sessao_dict.keys())
    ids_com_sessao = set(com_sessao_dict.keys())
    
    apenas_sem_sessao = ids_sem_sessao - ids_com_sessao
    apenas_com_sessao = ids_com_sessao - ids_sem_sessao
    comuns = ids_sem_sessao & ids_com_sessao
    
    if apenas_sem_sessao:
        log_result(f"   ⚠️ Produtos apenas SEM sessão: {len(apenas_sem_sessao)}")
        for pid in list(apenas_sem_sessao)[:3]:  # Mostrar apenas os primeiros 3
            produto = sem_sessao_dict[pid]
            log_result(f"      • {produto.get('descricao')} (ID: {pid})")
    
    if apenas_com_sessao:
        log_result(f"   ⚠️ Produtos apenas COM sessão: {len(apenas_com_sessao)}")
        for pid in list(apenas_com_sessao)[:3]:  # Mostrar apenas os primeiros 3
            produto = com_sessao_dict[pid]
            log_result(f"      • {produto.get('descricao')} (ID: {pid})")
    
    log_result(f"   ✅ Produtos em comum: {len(comuns)}")
    
    # Comparar preços dos produtos em comum
    diferencas_preco = []
    for pid in comuns:
        p1 = sem_sessao_dict[pid]
        p2 = com_sessao_dict[pid]
        
        preco1 = float(p1.get('preco', 0))
        preco2 = float(p2.get('preco', 0))
        
        if abs(preco1 - preco2) > 0.01:  # Diferença maior que 1 centavo
            diferencas_preco.append({
                'id': pid,
                'nome': p1.get('descricao'),
                'preco_sem_sessao': preco1,
                'preco_com_sessao': preco2,
                'diferenca': preco2 - preco1
            })
    
    if diferencas_preco:
        log_result(f"   🚨 DIFERENÇAS DE PREÇO ENCONTRADAS: {len(diferencas_preco)}")
        for diff in diferencas_preco[:5]:  # Mostrar apenas os primeiros 5
            log_result(f"      • {diff['nome']} (ID: {diff['id']})")
            log_result(f"        Sem sessão: R$ {diff['preco_sem_sessao']:.2f}")
            log_result(f"        Com sessão: R$ {diff['preco_com_sessao']:.2f}")
            log_result(f"        Diferença: R$ {diff['diferenca']:.2f}")
    else:
        log_result("   ✅ Nenhuma diferença de preço encontrada")

def main():
    print("=" * 80)
    print("🔍 TESTE DE COMPARAÇÃO: API COM E SEM SESSAO_ID")
    print("=" * 80)
    
    # Testar sem sessão
    url_sem_sessao = f"{API_BASE}/api/produtos"
    produtos_sem_sessao = test_api_endpoint("API SEM SESSÃO", url_sem_sessao)
    
    print()
    
    # Testar com sessão
    url_com_sessao = f"{API_BASE}/api/produtos?sessao_id={SESSAO_ID}"
    produtos_com_sessao = test_api_endpoint("API COM SESSÃO", url_com_sessao)
    
    print()
    print("=" * 80)
    
    # Analisar descontos em ambas
    if produtos_sem_sessao:
        count1, details1 = analyze_discounts(produtos_sem_sessao, "SEM SESSÃO")
    else:
        count1, details1 = 0, []
    
    print()
    
    if produtos_com_sessao:
        count2, details2 = analyze_discounts(produtos_com_sessao, "COM SESSÃO")
    else:
        count2, details2 = 0, []
    
    print()
    print("=" * 80)
    
    # Comparar resultados
    compare_products(produtos_sem_sessao, produtos_com_sessao)
    
    print()
    print("=" * 80)
    print("📊 RESUMO FINAL")
    print("=" * 80)
    log_result(f"Produtos com desconto SEM sessão: {count1}")
    log_result(f"Produtos com desconto COM sessão: {count2}")
    
    if count1 != count2:
        log_result("🚨 DIFERENÇA DETECTADA! O parâmetro sessao_id está afetando os descontos!")
    else:
        log_result("✅ Mesma quantidade de descontos em ambos os casos")
    
    print("=" * 80)

if __name__ == "__main__":
    main()