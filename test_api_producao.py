import requests
import json

def test_production_api():
    """Testa a API de produção baseada na URL da imagem fornecida"""
    
    # URL base da produção
    base_url = "https://halofarma.devisible.com.br"
    
    print("🔍 Testando API de Produção")
    print("=" * 50)
    
    # 1. Testar endpoint de produtos geral
    print("\n1️⃣ Testando /api/produtos")
    try:
        response = requests.get(f'{base_url}/api/produtos', timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            produtos = data.get('produtos', [])
            print(f"✅ Total de produtos: {len(produtos)}")
            
            if produtos:
                # Verificar produtos com desconto
                produtos_com_desconto = [p for p in produtos if p.get('percentual_desconto') and p.get('percentual_desconto') > 0]
                print(f"🏷️ Produtos com desconto: {len(produtos_com_desconto)}")
                
                if produtos_com_desconto:
                    print("\n📦 Produtos com desconto encontrados:")
                    for produto in produtos_com_desconto[:5]:  # Primeiros 5
                        print(f"   ID: {produto.get('id')} | {produto.get('descricao', 'N/A')}")
                        print(f"      Preço: R$ {produto.get('preco', 0)} | Desconto: {produto.get('percentual_desconto', 0)}%")
                        print(f"      Preço Original: {produto.get('preco_original', 'N/A')}")
                        print()
                else:
                    print("❌ PROBLEMA: Nenhum produto com desconto encontrado em produção!")
                    
                    # Verificar se há produtos com campos de desconto
                    produtos_com_campo_desconto = [p for p in produtos if 'percentual_desconto' in p or 'desconto_percentual' in p]
                    print(f"🔍 Produtos com campo desconto: {len(produtos_com_campo_desconto)}")
                    
                    # Mostrar estrutura de alguns produtos
                    print("\n📋 Estrutura dos primeiros 3 produtos:")
                    for i, produto in enumerate(produtos[:3]):
                        print(f"\nProduto {i+1}:")
                        for key, value in produto.items():
                            if 'desconto' in key.lower() or 'preco' in key.lower():
                                print(f"   🔍 {key}: {value}")
            else:
                print("❌ Nenhum produto retornado")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text[:300]}...")
            
    except Exception as e:
        print(f"❌ Erro ao testar /api/produtos: {e}")
    
    # 2. Testar com sessão específica (se necessário)
    print("\n2️⃣ Testando com sessão específica")
    try:
        # Primeiro, vamos ver se conseguimos criar uma sessão
        sessao_url = f'{base_url}/api/produtos/criar-sessao'
        print(f"Testando: {sessao_url}")
        
        # Payload de teste baseado na estrutura do código
        payload = {
            "cliente_nome": "Teste API",
            "cliente_telefone": "11999999999",
            "produtos": [
                {
                    "id": 1,
                    "descricao": "Produto Teste",
                    "preco": 10.0,
                    "estoque": 1,
                    "imagem_url": "",
                    "categoria": "Teste",
                    "apresentacao": "Teste"
                }
            ],
            "quantidade_produtos": 1
        }
        
        response = requests.post(sessao_url, json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sessão criada: {data.get('sessao_id', 'N/A')}")
        else:
            print(f"❌ Erro: {response.text[:300]}...")
            
    except Exception as e:
        print(f"❌ Erro ao testar sessão: {e}")

if __name__ == "__main__":
    test_production_api()