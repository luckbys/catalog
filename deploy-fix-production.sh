#!/bin/bash

# Script para corrigir deploy em produção
# Problema: catalogo.html retornando 404 em produção

echo "🔧 Corrigindo deploy em produção..."

# 1. Parar containers existentes
echo "📦 Parando containers..."
docker-compose -f docker-compose.simple.yml down

# 2. Rebuild com cache limpo
echo "🏗️ Fazendo rebuild dos containers..."
docker-compose -f docker-compose.simple.yml build --no-cache

# 3. Verificar se arquivos estáticos existem
echo "📁 Verificando arquivos estáticos..."
if [ ! -f "catalogo.html" ]; then
    echo "❌ ERRO: catalogo.html não encontrado!"
    exit 1
fi

if [ ! -f "demo.html" ]; then
    echo "❌ ERRO: demo.html não encontrado!"
    exit 1
fi

echo "✅ Arquivos estáticos encontrados"

# 4. Iniciar containers
echo "🚀 Iniciando containers..."
docker-compose -f docker-compose.simple.yml up -d

# 5. Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 10

# 6. Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose -f docker-compose.simple.yml ps

# 7. Testar endpoints
echo "🧪 Testando endpoints..."

# Testar API
echo "Testing API health..."
curl -f http://localhost:8000/health || echo "❌ API health check falhou"

# Testar nginx
echo "Testing nginx..."
curl -f http://localhost/catalogo.html || echo "❌ Nginx catalogo.html falhou"

echo "✅ Deploy corrigido! Verifique os logs se houver problemas:"
echo "docker-compose -f docker-compose.simple.yml logs -f"