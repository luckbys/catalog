#!/usr/bin/env python3
"""
Script para verificar a estrutura da tabela orders no Supabase
"""
import os
from supabase import create_client, Client

# Configurações do Supabase
SUPABASE_URL = "https://chatbot-supabase1.zv7gpn.easypanel.host"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"

def main():
    print("🔍 Verificando estrutura da tabela 'orders' no Supabase")
    print("=" * 60)
    
    try:
        # Conectar ao Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Tentar fazer uma query vazia para ver a estrutura
        print("📋 Fazendo query para verificar estrutura...")
        result = supabase.table("orders").select("*").limit(1).execute()
        
        print(f"Status: {result}")
        
        if result.data:
            print("✅ Tabela encontrada!")
            print(f"Dados de exemplo: {result.data[0]}")
            print(f"Colunas disponíveis: {list(result.data[0].keys())}")
        else:
            print("⚠️ Tabela vazia, tentando inserir dados de teste...")
            
            # Tentar inserir com diferentes estruturas
            test_data_v1 = {
                "customer_name": "Teste Cliente",
                "customer_phone": "11999999999",
                "order_number": "TEST001",
                "total": 10.50,
                "subtotal": 10.50
            }
            
            test_data_v2 = {
                "cliente_nome": "Teste Cliente",
                "cliente_telefone": "11999999999", 
                "numero_pedido": "TEST002",
                "total": 10.50,
                "subtotal": 10.50
            }
            
            print("🧪 Testando estrutura v1 (customer_name)...")
            try:
                result_v1 = supabase.table("orders").insert(test_data_v1).execute()
                print(f"✅ Estrutura v1 funcionou: {result_v1}")
            except Exception as e:
                print(f"❌ Estrutura v1 falhou: {e}")
                
                print("🧪 Testando estrutura v2 (cliente_nome)...")
                try:
                    result_v2 = supabase.table("orders").insert(test_data_v2).execute()
                    print(f"✅ Estrutura v2 funcionou: {result_v2}")
                except Exception as e2:
                    print(f"❌ Estrutura v2 também falhou: {e2}")
        
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    main()