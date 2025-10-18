#!/bin/bash

# Script de Troubleshooting para Deploy em Produção
# Execute este script na sua VPS para diagnosticar problemas

echo "🔍 DIAGNÓSTICO DO SISTEMA DE CATÁLOGO - PRODUÇÃO"
echo "================================================"
echo ""

# Verificar se Docker está instalado e rodando
echo "1. Verificando Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker instalado: $(docker --version)"
    if docker info &> /dev/null; then
        echo "✅ Docker daemon rodando"
    else
        echo "❌ Docker daemon não está rodando"
        echo "   Execute: sudo systemctl start docker"
    fi
else
    echo "❌ Docker não instalado"
    echo "   Instale o Docker primeiro"
fi
echo ""

# Verificar Docker Compose
echo "2. Verificando Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose instalado: $(docker-compose --version)"
else
    echo "❌ Docker Compose não instalado"
fi
echo ""

# Verificar arquivos necessários
echo "3. Verificando arquivos necessários..."
files=("docker-compose.prod.yml" "nginx.prod.conf" "Dockerfile" "demo.html" "catalogo.html" "backend/app.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file existe"
    else
        echo "❌ $file não encontrado"
    fi
done
echo ""

# Verificar containers
echo "4. Verificando containers..."
if docker ps &> /dev/null; then
    echo "Containers rodando:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "Todos os containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo "❌ Não foi possível listar containers"
fi
echo ""

# Verificar logs dos containers
echo "5. Verificando logs dos containers..."
containers=("catalog-backend-1" "catalog-frontend-1")
for container in "${containers[@]}"; do
    if docker ps -a --format "{{.Names}}" | grep -q "$container"; then
        echo "📋 Logs do $container (últimas 10 linhas):"
        docker logs --tail 10 "$container" 2>&1
        echo ""
    else
        echo "⚠️  Container $container não encontrado"
    fi
done

# Verificar portas
echo "6. Verificando portas..."
ports=(80 443 8000)
for port in "${ports[@]}"; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✅ Porta $port está em uso"
    else
        echo "⚠️  Porta $port não está em uso"
    fi
done
echo ""

# Verificar conectividade
echo "7. Testando conectividade..."
echo "Testando backend (porta 8000):"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo "✅ Backend respondendo na porta 8000"
else
    echo "❌ Backend não responde na porta 8000"
fi

echo "Testando frontend (porta 80):"
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
    echo "✅ Frontend respondendo na porta 80"
else
    echo "❌ Frontend não responde na porta 80"
fi
echo ""

# Verificar variáveis de ambiente
echo "8. Verificando arquivo .env..."
if [ -f ".env" ]; then
    echo "✅ Arquivo .env existe"
    echo "Variáveis definidas:"
    grep -v '^#' .env | grep -v '^$' || echo "Nenhuma variável encontrada"
else
    echo "⚠️  Arquivo .env não encontrado"
    echo "   Copie .env.example para .env e configure"
fi
echo ""

# Verificar SSL (se aplicável)
echo "9. Verificando SSL..."
if [ -d "ssl" ]; then
    echo "✅ Diretório SSL existe"
    if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
        echo "✅ Certificados SSL encontrados"
    else
        echo "⚠️  Certificados SSL não encontrados"
    fi
else
    echo "⚠️  Diretório SSL não existe"
fi
echo ""

# Sugestões de correção
echo "🔧 SUGESTÕES DE CORREÇÃO"
echo "========================"
echo ""
echo "Se o sistema não estiver funcionando:"
echo ""
echo "1. Para desenvolvimento local:"
echo "   docker-compose up --build"
echo ""
echo "2. Para produção:"
echo "   docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "3. Para ver logs em tempo real:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "4. Para reiniciar os serviços:"
echo "   docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "5. Para limpar e reconstruir:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo "   docker system prune -f"
echo "   docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "6. Verificar firewall (se aplicável):"
echo "   sudo ufw allow 80"
echo "   sudo ufw allow 443"
echo ""
echo "7. Para SSL com Let's Encrypt:"
echo "   sudo apt install certbot"
echo "   sudo certbot certonly --standalone -d seu-dominio.com"
echo "   sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem ssl/cert.pem"
echo "   sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem ssl/key.pem"
echo ""
echo "✨ Diagnóstico concluído!"