#!/bin/bash

echo "🚀 Iniciando deploy da correção para produção..."

# Parar containers existentes
echo "⏹️ Parando containers..."
docker-compose -f docker-compose.prod.yml down

# Rebuild dos containers
echo "🔨 Fazendo rebuild dos containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar containers
echo "▶️ Iniciando containers..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 10

# Verificar se containers estão rodando
echo "🔍 Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

# Testar endpoints
echo "🧪 Testando endpoints..."
echo "Testando API health..."
curl -s https://hakimfarma.devsible.com.br/health

echo -e "\nTestando catalogo.html via FastAPI..."
curl -s -I https://hakimfarma.devsible.com.br/catalogo.html

echo -e "\nTestando demo.html via FastAPI..."
curl -s -I https://hakimfarma.devsible.com.br/demo.html

echo -e "\n✅ Deploy concluído! Agora o catalogo.html é servido diretamente pelo FastAPI."
echo "🔗 Teste o link: https://hakimfarma.devsible.com.br/catalogo.html?sessao_id=TESTE"