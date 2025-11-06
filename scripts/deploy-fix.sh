#!/bin/bash

# 🚀 Script de Correção para Deploy em Produção
# Este script resolve o problema de 404 nas páginas

echo "🔧 Iniciando correção do deploy em produção..."

# 1. Parar containers existentes
echo "⏹️  Parando containers existentes..."
docker-compose down 2>/dev/null || true

# 2. Verificar se os arquivos necessários existem
echo "📋 Verificando arquivos necessários..."
required_files=("docker-compose.simple.yml" "nginx.simple.conf" "demo.html" "catalogo.html")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Arquivos faltando: ${missing_files[*]}"
    echo "   Execute este script no diretório raiz do projeto!"
    exit 1
fi

# 3. Criar diretório de dados se não existir
echo "📁 Criando diretório de dados..."
mkdir -p data

# 4. Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando a partir do exemplo..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Arquivo .env criado. EDITE-O com suas configurações!"
        echo "   Principalmente: CLIENT_BASE_URL e ALLOWED_ORIGIN"
    else
        echo "❌ Arquivo .env.example não encontrado!"
        exit 1
    fi
fi

# 5. Construir e iniciar com a configuração correta
echo "🏗️  Construindo e iniciando containers..."
docker-compose -f docker-compose.simple.yml up -d --build

# 6. Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 10

# 7. Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose -f docker-compose.simple.yml ps

# 8. Testar conectividade
echo "🔍 Testando conectividade..."

# Testar backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend funcionando (porta 8000)"
else
    echo "❌ Backend não responde na porta 8000"
fi

# Testar frontend
if curl -s http://localhost:80 > /dev/null; then
    echo "✅ Frontend funcionando (porta 80)"
else
    echo "❌ Frontend não responde na porta 80"
fi

# 9. Mostrar logs se houver problemas
echo "📝 Últimas linhas dos logs:"
docker-compose -f docker-compose.simple.yml logs --tail=10

echo ""
echo "🎉 Deploy corrigido!"
echo ""
echo "📍 URLs de acesso:"
echo "   • Demo: http://localhost/ ou http://seu-dominio.com/"
echo "   • Catálogo: http://localhost/catalogo.html ou http://seu-dominio.com/catalogo.html"
echo "   • API: http://localhost:8000/api/ ou http://seu-dominio.com/api/"
echo ""
echo "⚙️  Para monitorar:"
echo "   docker-compose -f docker-compose.simple.yml logs -f"
echo ""
echo "🛑 Para parar:"
echo "   docker-compose -f docker-compose.simple.yml down"