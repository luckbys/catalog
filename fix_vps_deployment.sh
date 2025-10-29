#!/bin/bash

# Script para corrigir o deployment na VPS
# Diagnóstico completo e correção do problema

echo "🚀 CORREÇÃO DO DEPLOYMENT VPS - $(date)"
echo "=============================================="

# Função para imprimir cabeçalhos
print_header() {
    echo ""
    echo "=============================================="
    echo "🔍 $1"
    echo "=============================================="
}

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_header "1. VERIFICANDO AMBIENTE"

# Verificar se Docker está instalado
if command_exists docker; then
    echo "✅ Docker está instalado"
    docker --version
else
    echo "❌ Docker não está instalado!"
    exit 1
fi

# Verificar se Docker Compose está instalado
if command_exists docker-compose; then
    echo "✅ Docker Compose está instalado"
    docker-compose --version
else
    echo "❌ Docker Compose não está instalado!"
    exit 1
fi

print_header "2. VERIFICANDO CONTAINERS ATUAIS"

echo "📋 Containers em execução:"
docker ps

echo ""
echo "📋 Todos os containers:"
docker ps -a

print_header "3. PARANDO SERVIÇOS EXISTENTES"

echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down

echo "🧹 Removendo containers órfãos..."
docker-compose -f docker-compose.prod.yml down --remove-orphans

print_header "4. LIMPANDO IMAGENS ANTIGAS"

echo "🗑️ Removendo imagens não utilizadas..."
docker system prune -f

print_header "5. VERIFICANDO CONFIGURAÇÃO"

echo "📄 Verificando docker-compose.prod.yml..."
if [ -f "docker-compose.prod.yml" ]; then
    echo "✅ Arquivo docker-compose.prod.yml encontrado"
    echo "📋 Conteúdo das variáveis de ambiente:"
    grep -E "SUPABASE_URL|SUPABASE_KEY" docker-compose.prod.yml
else
    echo "❌ Arquivo docker-compose.prod.yml não encontrado!"
    exit 1
fi

print_header "6. CONSTRUINDO E INICIANDO SERVIÇOS"

echo "🔨 Construindo imagens..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Iniciando serviços..."
docker-compose -f docker-compose.prod.yml up -d

print_header "7. AGUARDANDO INICIALIZAÇÃO"

echo "⏳ Aguardando 30 segundos para inicialização..."
sleep 30

print_header "8. VERIFICANDO STATUS DOS SERVIÇOS"

echo "📋 Status dos containers:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "📋 Logs do backend:"
docker-compose -f docker-compose.prod.yml logs backend | tail -20

print_header "9. TESTANDO ENDPOINTS"

echo "🧪 Testando endpoint de saúde local..."
curl -f http://localhost:8000/health || echo "❌ Endpoint de saúde local falhou"

echo ""
echo "🧪 Testando endpoint de saúde público..."
curl -f https://chatbot-catalog.zv7gpn.easypanel.host/api/health || echo "❌ Endpoint de saúde público falhou"

echo ""
echo "🧪 Testando endpoint de pedidos..."
curl -X POST https://chatbot-catalog.zv7gpn.easypanel.host/api/process-order \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": {
      "nome": "Teste VPS",
      "telefone": "11999999999"
    },
    "entrega": {
      "cep": "01310-100",
      "endereco": "Avenida Paulista",
      "numero": "1000"
    },
    "pagamento": {
      "forma_pagamento": "PIX",
      "valor_total": 100.00
    },
    "produtos": [
      {
        "id": 1,
        "nome": "Produto Teste",
        "preco_unitario": 100.00,
        "quantidade": 1,
        "subtotal": 100.00
      }
    ]
  }' || echo "❌ Endpoint de pedidos falhou"

print_header "10. DIAGNÓSTICO FINAL"

echo "🔍 Verificando portas em uso:"
netstat -tlnp | grep -E ":80|:443|:8000" || ss -tlnp | grep -E ":80|:443|:8000"

echo ""
echo "🔍 Verificando logs de erro do backend:"
docker-compose -f docker-compose.prod.yml logs backend | grep -i error | tail -10

echo ""
echo "🔍 Verificando logs de erro do frontend:"
docker-compose -f docker-compose.prod.yml logs frontend | grep -i error | tail -10

print_header "RESULTADO FINAL"

# Verificar se os containers estão rodando
backend_running=$(docker-compose -f docker-compose.prod.yml ps backend | grep -c "Up")
frontend_running=$(docker-compose -f docker-compose.prod.yml ps frontend | grep -c "Up")

if [ "$backend_running" -gt 0 ] && [ "$frontend_running" -gt 0 ]; then
    echo "✅ SUCESSO! Todos os serviços estão rodando"
    echo "🌐 Frontend: https://chatbot-catalog.zv7gpn.easypanel.host"
    echo "🔧 Backend: https://chatbot-catalog.zv7gpn.easypanel.host/api"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Testar o catálogo no navegador"
    echo "2. Fazer um pedido de teste"
    echo "3. Verificar se o pedido foi salvo no Supabase"
else
    echo "❌ FALHA! Alguns serviços não estão rodando corretamente"
    echo ""
    echo "🛠️ Comandos para diagnóstico:"
    echo "docker-compose -f docker-compose.prod.yml logs"
    echo "docker-compose -f docker-compose.prod.yml ps"
    echo "docker system df"
fi

echo ""
echo "=============================================="
echo "🏁 Script concluído - $(date)"
echo "=============================================="