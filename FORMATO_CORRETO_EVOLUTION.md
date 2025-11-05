# ✅ Formato CORRETO - Evolution API

## 🎯 Formato Simplificado (Funciona!)

```javascript
{
    number: "5512981443806",
    text: "Sua mensagem aqui"
}
```

**Apenas 2 campos necessários:**
- ✅ `number` - Número com código do país (5512981443806)
- ✅ `text` - Texto da mensagem

---

## 📝 Exemplo Completo

### JavaScript:
```javascript
const response = await fetch('https://evo.devsible.com.br/message/sendText/hakim', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'apikey': 'B6D711FCDE4D-4183-9385-D5C9B6E1E119'
    },
    body: JSON.stringify({
        number: '5512981443806',
        text: '🔔 Teste de mensagem!'
    })
});
```

### cURL:
```bash
curl -X POST "https://evo.devsible.com.br/message/sendText/hakim" \
  -H "Content-Type: application/json" \
  -H "apikey: B6D711FCDE4D-4183-9385-D5C9B6E1E119" \
  -d '{
    "number": "5512981443806",
    "text": "🔔 Teste de mensagem!"
  }'
```

### PowerShell:
```powershell
$body = @{
    number = "5512981443806"
    text = "🔔 Teste de mensagem!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://evo.devsible.com.br/message/sendText/hakim" `
    -Method Post `
    -Headers @{
        "Content-Type" = "application/json"
        "apikey" = "B6D711FCDE4D-4183-9385-D5C9B6E1E119"
    } `
    -Body $body
```

---

## ❌ Formatos que NÃO funcionam

### ❌ Formato v2 Nested (Não aceito):
```javascript
{
    number: "5512981443806",
    options: { delay: 1200 },
    textMessage: { text: "Mensagem" }
}
```
**Erro**: `"instance requires property \"text\""`

### ❌ Formato v1 com delay (Não aceito):
```javascript
{
    number: "5512981443806",
    text: "Mensagem",
    delay: 1200
}
```
**Erro**: Campos extras ignorados ou erro

---

## 🧪 Teste Rápido

### Via test-whatsapp.html:
```
1. Abra: test-whatsapp.html
2. Clique: "Enviar Notificação de Teste"
3. Resultado esperado: ✅ SUCESSO!
4. Verifique: WhatsApp 5512981443806
```

### Via PowerShell:
```powershell
.\test-evolution-api.ps1
```

### Via Bash:
```bash
bash test-evolution-api.sh
```

---

## 📊 Response Esperada

### Sucesso (200):
```json
{
    "key": {
        "remoteJid": "5512981443806@s.whatsapp.net",
        "fromMe": true,
        "id": "3EB0ABC123..."
    },
    "message": {
        "conversation": "🔔 Teste de mensagem!"
    },
    "messageTimestamp": "1699200000",
    "status": "PENDING"
}
```

### Erro (400):
```json
{
    "status": 400,
    "error": "Bad Request",
    "response": {
        "message": [
            ["instance requires property \"text\""]
        ]
    }
}
```

---

## 🔧 Configuração Atual

```javascript
const EVOLUTION_CONFIG = {
    API_URL: 'https://evo.devsible.com.br',
    API_KEY: 'B6D711FCDE4D-4183-9385-D5C9B6E1E119',
    INSTANCE_NAME: 'hakim',
    SELLER_PHONE: '5512981443806'
};
```

---

## ✅ Checklist

- [x] Endpoint correto: `/message/sendText/hakim`
- [x] Header `apikey` presente
- [x] Body com apenas `number` e `text`
- [x] Número no formato correto (5512981443806)
- [x] Texto da mensagem presente
- [ ] Teste realizado com sucesso
- [ ] Mensagem recebida no WhatsApp

---

## 🎯 Próximo Passo

**Teste agora:**
```
1. Abra: test-whatsapp.html
2. Clique: "Enviar Notificação de Teste"
3. Deve retornar: ✅ SUCESSO!
```

Se funcionar, faça um pedido real no catálogo para testar o fluxo completo!

---

**Status**: ✅ Formato Correto  
**Testado**: Aguardando validação  
**Número**: 5512981443806
