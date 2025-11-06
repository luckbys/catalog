#!/bin/bash

# Teste Evolution API v2 - Envio de Mensagem
# Uso: bash test-evolution-api.sh

echo "🧪 Testando Evolution API v2..."
echo ""

# Configuração
API_URL="https://evo.devsible.com.br"
API_KEY="B6D711FCDE4D-4183-9385-D5C9B6E1E119"
INSTANCE="hakim"
PHONE="5512976025888"

# Mensagem de teste
MESSAGE="🔔 *TESTE DE NOTIFICAÇÃO*

📋 Este é um teste da integração Evolution API v2

⏰ Horário: $(date '+%d/%m/%Y %H:%M:%S')

✅ Se você recebeu esta mensagem, a integração está funcionando corretamente!"

echo "📤 Enviando mensagem de teste..."
echo "📱 Número: $PHONE"
echo ""

# Fazer requisição
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/message/sendText/$INSTANCE" \
  -H "Content-Type: application/json" \
  -H "apikey: $API_KEY" \
  -d "{
    \"number\": \"$PHONE\",
    \"text\": \"$MESSAGE\"
  }")

# Separar body e status code
HTTP_BODY=$(echo "$RESPONSE" | head -n -1)
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

echo "📊 Status HTTP: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
    echo "✅ SUCESSO! Mensagem enviada."
    echo ""
    echo "📄 Resposta:"
    echo "$HTTP_BODY" | jq '.' 2>/dev/null || echo "$HTTP_BODY"
else
    echo "❌ ERRO! Falha ao enviar mensagem."
    echo ""
    echo "📄 Resposta:"
    echo "$HTTP_BODY" | jq '.' 2>/dev/null || echo "$HTTP_BODY"
fi

echo ""
echo "🔍 Verifique o WhatsApp: $PHONE"
