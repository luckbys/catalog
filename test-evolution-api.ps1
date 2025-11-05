# Teste Evolution API v2 - Envio de Mensagem
# Uso: .\test-evolution-api.ps1

Write-Host "🧪 Testando Evolution API v2..." -ForegroundColor Cyan
Write-Host ""

# Configuração
$API_URL = "https://evo.devsible.com.br"
$API_KEY = "B6D711FCDE4D-4183-9385-D5C9B6E1E119"
$INSTANCE = "hakim"
$PHONE = "5512981443806"

# Mensagem de teste
$timestamp = Get-Date -Format "dd/MM/yyyy HH:mm:ss"
$MESSAGE = @"
🔔 *TESTE DE NOTIFICAÇÃO*

📋 Este é um teste da integração Evolution API v2

⏰ Horário: $timestamp

✅ Se você recebeu esta mensagem, a integração está funcionando corretamente!
"@

Write-Host "📤 Enviando mensagem de teste..." -ForegroundColor Yellow
Write-Host "📱 Número: $PHONE" -ForegroundColor Yellow
Write-Host ""

# Preparar body
$body = @{
    number = $PHONE
    options = @{
        delay = 1200
        presence = "composing"
    }
    textMessage = @{
        text = $MESSAGE
    }
} | ConvertTo-Json -Depth 10

# Headers
$headers = @{
    "Content-Type" = "application/json"
    "apikey" = $API_KEY
}

try {
    # Fazer requisição
    $response = Invoke-RestMethod -Uri "$API_URL/message/sendText/$INSTANCE" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "✅ SUCESSO! Mensagem enviada." -ForegroundColor Green
    Write-Host ""
    Write-Host "📄 Resposta:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10 | Write-Host
    
} catch {
    Write-Host "❌ ERRO! Falha ao enviar mensagem." -ForegroundColor Red
    Write-Host ""
    Write-Host "📄 Detalhes do erro:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    
    if ($_.ErrorDetails.Message) {
        Write-Host ""
        Write-Host "📄 Resposta da API:" -ForegroundColor Red
        $_.ErrorDetails.Message | ConvertFrom-Json | ConvertTo-Json -Depth 10 | Write-Host
    }
}

Write-Host ""
Write-Host "🔍 Verifique o WhatsApp: $PHONE" -ForegroundColor Cyan
