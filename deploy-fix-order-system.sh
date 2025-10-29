#!/bin/bash

echo "🚀 Corrigindo sistema de pedidos na VPS..."

# Verificar se as variáveis de ambiente estão definidas
echo "🔍 Verificando variáveis de ambiente..."

if [ -z "$SUPABASE_KEY" ]; then
    echo "❌ SUPABASE_KEY não está definida!"
    echo "Execute: export SUPABASE_KEY=your_supabase_key"
    exit 1
fi

if [ -z "$EVOLUTION_API_KEY" ]; then
    echo "⚠️ EVOLUTION_API_KEY não está definida - WhatsApp não funcionará"
fi

if [ -z "$EVOLUTION_INSTANCE_NAME" ]; then
    echo "⚠️ EVOLUTION_INSTANCE_NAME não está definida - WhatsApp não funcionará"
fi

echo "✅ Variáveis principais configuradas"

# Parar containers existentes
echo "⏹️ Parando containers..."
docker-compose -f docker-compose.prod.yml down

# Limpar imagens antigas
echo "🧹 Limpando imagens antigas..."
docker system prune -f

# Rebuild dos containers
echo "🔨 Fazendo rebuild dos containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar containers
echo "▶️ Iniciando containers..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 15

# Verificar se containers estão rodando
echo "🔍 Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

# Verificar logs do backend
echo "📋 Verificando logs do backend..."
docker-compose -f docker-compose.prod.yml logs backend | tail -20

# Testar endpoints
echo "🧪 Testando endpoints..."

echo "Testando API health..."
curl -s https://chatbot-catalog.zv7gpn.easypanel.host/health

echo -e "\nTestando endpoint de produtos..."
curl -s https://chatbot-catalog.zv7gpn.easypanel.host/api/produtos | head -100

echo -e "\nTestando catalogo.html..."
curl -s -I https://chatbot-catalog.zv7gpn.easypanel.host/catalogo.html

# Testar endpoint de pedido
echo -e "\n🧪 Testando endpoint de pedido..."
curl -X POST https://chatbot-catalog.zv7gpn.easypanel.host/api/process-order \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": {"nome": "Teste Deploy", "telefone": "11999999999"},
    "entrega": {"cep": "01310-100", "endereco": "Av Paulista", "numero": "1000", "bairro": "Centro", "cidade": "SP", "estado": "SP"},
    "pagamento": {"forma_pagamento": "PIX", "valor_total": 100.00},
    "produtos": [{"id": 1, "nome": "Teste", "preco_unitario": 100.00, "quantidade": 1, "subtotal": 100.00}]
  }'

echo -e "\n✅ Deploy do sistema de pedidos concluído!"
echo "🔗 Teste o catálogo: https://chatbot-catalog.zv7gpn.easypanel.host/catalogo.html"

echo -e "\n📝 Próximos passos:"
echo "1. Configure as variáveis de ambiente no servidor:"
echo "   - SUPABASE_KEY=sua_chave_supabase"
echo "   - EVOLUTION_API_KEY=sua_chave_evolution"
echo "   - EVOLUTION_INSTANCE_NAME=nome_da_instancia"
echo "   - WHATSAPP_PHONE=seu_numero_whatsapp"
echo "2. Execute novamente este script após configurar as variáveis"