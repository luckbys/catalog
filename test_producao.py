import requests
import json

def test_api(base_url, name):
    print(f"\n🔍 Testando {name}: {base_url}")
    try:
        response = requests.get(f'{base_url}/api/produtos', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            produtos = data.get('produtos', [])
            
            print(f"✅ Status: {response.status_code}")
            print(f"📦 Total de produtos: {len(produtos)}")
            
            if produtos:
                # Analisar primeiro produto
                produto = produtos[0]
                print(f"\n📋 Estrutura do primeiro produto:")
                for key, value in produto.items():
                    print(f"   {key}: {value} (tipo: {type(value).__name__})")
                
                # Buscar produtos com desconto
                produtos_com_desconto = [p for p in produtos if p.get('percentual_desconto') and p.get('percentual_desconto') > 0]
                print(f"\n🏷️ Produtos com desconto: {len(produtos_com_desconto)}")
                
                if produtos_com_desconto:
                    for i, produto in enumerate(produtos_com_desconto[:3]):
                        print(f"\n📦 Produto {i+1} com desconto:")
                        print(f"   ID: {produto.get('id')}")
                        print(f"   Descrição: {produto.get('descricao', 'N/A')}")
                        print(f"   Preço: R$ {produto.get('preco', 0)}")
                        print(f"   Preço Original: R$ {produto.get('preco_original', 'N/A')}")
                        print(f"   Desconto: {produto.get('percentual_desconto', 0)}%")
                        print(f"   Valor Desconto: R$ {produto.get('valor_desconto', 'N/A')}")
                else:
                    print("❌ Nenhum produto com desconto encontrado!")
            else:
                print("❌ Nenhum produto retornado pela API")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Resposta: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout ao conectar com {name}")
    except requests.exceptions.ConnectionError:
        print(f"🔌 Erro de conexão com {name}")
    except Exception as e:
        print(f"❌ Erro: {e}")

# URLs para testar
urls = {
    "Local": "http://localhost:8000",
    "Produção": "https://halofarma.devisible.com.br/api/produtos/criar-sessao"  # Baseado na imagem da API
}

print("🧪 Comparando APIs Local vs Produção")
print("=" * 50)

for name, url in urls.items():
    test_api(url, name)

print("\n" + "=" * 50)
print("🎯 Análise concluída!")