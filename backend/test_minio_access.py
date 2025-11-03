#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import base64

# Configurações do MinIO
MINIO_SERVER_URL = "https://c4crm-minio.zv7gpn.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "Devs@0101"

print("🔍 Testando acesso ao MinIO...")

# Testar diferentes métodos de acesso
test_paths = [
    "/produtos/banner_baner_novo_17621695544726.png",
    "/banner_baner_novo_17621695544726.png",
    "produtos/banner_baner_novo_17621695544726.png"
]

for path in test_paths:
    print(f"\n🎯 Testando caminho: {path}")
    
    # Construir URL
    if not path.startswith('/'):
        path = '/' + path
    minio_url = f"{MINIO_SERVER_URL}{path}"
    
    print(f"📍 URL completa: {minio_url}")
    
    # Método 1: Sem autenticação
    try:
        print("   Método 1: Sem autenticação...")
        response = requests.get(minio_url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCESSO sem autenticação!")
            break
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Método 2: Autenticação básica
    try:
        print("   Método 2: Autenticação básica...")
        credentials = f"{MINIO_ROOT_USER}:{MINIO_ROOT_PASSWORD}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {'Authorization': f'Basic {encoded_credentials}'}
        
        response = requests.get(minio_url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCESSO com autenticação básica!")
            break
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Método 3: Parâmetros de query
    try:
        print("   Método 3: Parâmetros de query...")
        params = {
            'X-Amz-Credential': MINIO_ROOT_USER,
            'X-Amz-Signature': MINIO_ROOT_PASSWORD
        }
        
        response = requests.get(minio_url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCESSO com parâmetros!")
            break
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n🔍 Testando acesso ao bucket raiz...")
try:
    root_url = f"{MINIO_SERVER_URL}/"
    response = requests.get(root_url, timeout=10)
    print(f"Status do bucket raiz: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
except Exception as e:
    print(f"Erro ao acessar raiz: {e}")