#!/bin/bash

echo "=================================="
echo "VERIFICAÇÃO DO SETUP DO ENTREGADOR"
echo "=================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar se arquivo existe
echo "1. Verificando se entregador.html existe..."
if [ -f "entregador.html" ]; then
    echo -e "${GREEN}✓ entregador.html encontrado${NC}"
    ls -lh entregador.html
else
    echo -e "${RED}✗ entregador.html NÃO encontrado${NC}"
    echo "   Arquivo precisa estar na raiz do projeto"
fi
echo ""

# 2. Verificar outros arquivos HTML
echo "2. Verificando outros arquivos HTML..."
for file in catalogo.html status.html admin-pedidos.html; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file${NC}"
    fi
done
echo ""

# 3. Verificar .env
echo "3. Verificando configuração do .env..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env encontrado${NC}"
    
    # Verificar CLIENT_BASE_URL
    if grep -q "CLIENT_BASE_URL" .env; then
        CLIENT_BASE_URL=$(grep "CLIENT_BASE_URL" .env | cut -d '=' -f2)
        echo "   CLIENT_BASE_URL: $CLIENT_BASE_URL"
        
        # Construir URL do entregador
        ENTREGADOR_URL="${CLIENT_BASE_URL}/entregador.html?pedido=123"
        echo "   URL do entregador: $ENTREGADOR_URL"
    else
        echo -e "${RED}   ✗ CLIENT_BASE_URL não encontrado${NC}"
    fi
else
    echo -e "${RED}✗ .env NÃO encontrado${NC}"
fi
echo ""

# 4. Verificar rota no backend
echo "4. Verificando rota no backend/app.py..."
if grep -q '@app.get("/entregador.html")' backend/app.py; then
    echo -e "${GREEN}✓ Rota /entregador.html encontrada${NC}"
else
    echo -e "${RED}✗ Rota /entregador.html NÃO encontrada${NC}"
fi
echo ""

# 5. Verificar git status
echo "5. Verificando status do git..."
if git status entregador.html 2>/dev/null | grep -q "entregador.html"; then
    if git status entregador.html | grep -q "Untracked"; then
        echo -e "${YELLOW}⚠ entregador.html não está no git (untracked)${NC}"
        echo "   Execute: git add entregador.html"
    elif git status entregador.html | grep -q "modified"; then
        echo -e "${YELLOW}⚠ entregador.html foi modificado${NC}"
        echo "   Execute: git add entregador.html && git commit -m 'Update entregador'"
    else
        echo -e "${GREEN}✓ entregador.html está commitado${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Não foi possível verificar status do git${NC}"
fi
echo ""

# 6. Resumo
echo "=================================="
echo "RESUMO"
echo "=================================="
echo ""
echo "Para fazer o deploy funcionar:"
echo "1. git add entregador.html"
echo "2. git commit -m 'Add entregador page'"
echo "3. git push origin main"
echo "4. Fazer redeploy no EasyPanel"
echo ""
echo "Testar localmente:"
echo "cd backend && uvicorn app:app --reload"
echo "Abrir: http://localhost:8000/entregador.html?pedido=123"
echo ""
