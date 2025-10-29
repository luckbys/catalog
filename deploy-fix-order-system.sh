#!/bin/bash

# Script para corrigir o sistema de pedidos na VPS
# Problema: Backend não está rodando, endpoint /api/process-order retorna 404

echo "🚀 Iniciando correção do sistema de pedidos na VPS"
echo "=================================================="

# 1. Verificar variáveis de ambiente necessárias
echo "🔍 Verificando variáveis de ambiente..."
echo "SUPABASE_URL: https://chatbot-supabase1.zv7gpn.easypanel.host"
echo "SUPABASE_KEY: [CONFIGURADO NO DOCKER-COMPOSE]"
echo "EVOLUTION_API_URL: ${EVOLUTION_API_URL:-https://c4crm-evolution-api.zv7gpn.easypanel.host}"
echo "EVOLUTION_API_KEY: ${EVOLUTION_API_KEY:-E7Bp3tlb9zQxd54rHzBzVOxDEwF8BDbZ9cR16WeEGXGpEeZMorP8cdrGWhpkfDQODlwh5CuO1aN8pTpj2Fwmc2ARYPgibsnoB8oXIynzcifVqhWTI7R4PCHsQcDFQM0p}"
echo "EVOLUTION_INSTANCE_NAME: ${EVOLUTION_INSTANCE_NAME:-hakim t}"
echo "WHATSAPP_PHONE: ${WHATSAPP_PHONE:-5512981443806}"

# 2. Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down

# 3. Limpar containers e imagens antigas
echo "🧹 Limpando containers e imagens antigas..."
docker system prune -f
docker image prune -f

# 4. Reconstruir e iniciar containers
echo "🔨 Reconstruindo e iniciando containers..."
docker-compose -f docker-compose.prod.yml up --build -d

# 5. Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 30

# 6. Verificar status dos containers
echo "📊 Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

# 7. Verificar logs do backend
echo "📋 Verificando logs do backend..."
docker-compose -f docker-compose.prod.yml logs backend

# 8. Testar endpoints
echo "🧪 Testando endpoints..."

# Teste 1: Health check
echo "1. Testando /health..."
curl -s -o /dev/null -w "%{http_code}" https://chatbot-catalog.zv7gpn.easypanel.host/health
echo ""

# Teste 2: Produtos
echo "2. Testando /api/produtos..."
curl -s -o /dev/null -w "%{http_code}" https://chatbot-catalog.zv7gpn.easypanel.host/api/produtos
echo ""

# Teste 3: Catalogo HTML
echo "3. Testando catalogo.html..."
curl -s -o /dev/null -w "%{http_code}" https://chatbot-catalog.zv7gpn.easypanel.host/catalogo.html
echo ""

# Teste 4: Process Order (POST)
echo "4. Testando /api/process-order..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": {
      "nome": "Teste VPS",
      "telefone": "11999999999"
    },
    "entrega": {
      "endereco": "Rua Teste",
      "numero": "123",
      "bairro": "Centro",
      "cidade": "São Paulo",
      "estado": "SP",
      "cep": "01234-567",
      "complemento": ""
    },
    "pagamento": {
      "forma_pagamento": "pix",
      "valor_total": 25.50
    },
    "produtos": [
      {
        "nome": "Produto Teste",
        "codigo": "TEST001",
        "preco_unitario": 25.50,
        "quantidade": 1,
        "subtotal": 25.50
      }
    ]
  }' \
  -s -o /dev/null -w "%{http_code}" \
  https://chatbot-catalog.zv7gpn.easypanel.host/api/process-order
echo ""

echo "✅ Deploy concluído! Verifique os códigos de status acima:"
echo "   - 200: OK"
echo "   - 404: Endpoint não encontrado"
echo "   - 500: Erro interno do servidor"