import requests

try:
    response = requests.get('http://localhost:8000/api/produtos')
    data = response.json()
    
    if data.get('produtos'):
        produto = data['produtos'][0]
        print('📋 Estrutura do produto:')
        for key, value in produto.items():
            print(f'   {key}: {value} (tipo: {type(value).__name__})')
        
        produtos_com_desconto = [p for p in data['produtos'] if p.get('percentual_desconto') and p.get('percentual_desconto') > 0]
        print(f'\n🏷️ Produtos com desconto encontrados: {len(produtos_com_desconto)}')
        
        if produtos_com_desconto:
            for produto in produtos_com_desconto[:3]:
                print(f'📦 Produto: {produto.get("descricao", "N/A")}')
                print(f'   💰 Preço: R$ {produto.get("preco", 0)}')
                print(f'   💸 Preço Original: R$ {produto.get("preco_original", "N/A")}')
                print(f'   📊 Desconto: {produto.get("percentual_desconto", 0)}%')
                print()
    else:
        print('❌ Nenhum produto encontrado')
        
except Exception as e:
    print(f'❌ Erro: {e}')