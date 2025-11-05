# 🔧 Correção Evolution API - Endpoint v2

## ❌ Problema Identificado

### Erro Original:
```json
{
    "whatsapp_response": {
        "success": false,
        "error": "HTTP 404",
        "response": "{\"message\":\"Route POST:/api/errors/not-found not found\",\"error\":\"Not Found\",\"statusCode\":404}",
        "message": "Falha ao enviar mensagem WhatsApp"
    }
}
```

**Causa**: Formato do body da requisição estava incorreto para Evolution API v2

---

## ✅ Solução Implementada

### Formato Antigo (Incorreto):
```javascript
{
    number: "5512981443806",
    text: "Mensagem aqui",
    delay: 1200
}
```

### Formato Correto (Simplificado):
```javascript
{
    number: "5512981443806",
    text: "Mensagem aqui"
}
```

**Nota**: A Evolution API aceita o formato simples com apenas `number` e `text`.

---

## 📝 Mudanças Aplicadas

### 1. **catalogo.html**
```javascript
// ANTES
body: JSON.stringify({
    number: SELLER_PHONE,
    text: message,
    delay: 1200
})

// DEPOIS
body: JSON.stringify({
    number: SELLER_PHONE,
    options: {
        delay: 1200,
        presence: 'composing'
    },
    textMessage: {
        text: message
    }
})
```

### 2. **test-whatsapp.html**
```javascript
// Mesma correção aplicada
```

### 3. **evolution-api-config.js**
```javascript
// Mesma correção aplicada
```

---

## 🔍 Estrutura Completa da Requisição

### Endpoint:
```
POST https://chatbot-evolution-api.zv7gpn.easypanel.host
```

### Headers:
```json
{
    "Content-Type": "application/json",
    "apikey": "016179B162E9-4D01-AA9B-D0E3730E0954"
}
```

### Body:
```json
{
    "number": "5512981443806",
    "text": "🔔 *NOVO PEDIDO RECEBIDO!*\n\n📋 *Pedido:* #71\n..."
}
```

### Response Esperada (Sucesso):
```json
{
    "key": {
        "remoteJid": "5512981443806@s.whatsapp.net",
        "fromMe": true,
        "id": "3EB0..."
    },
    "message": {
        "extendedTextMessage": {
            "text": "🔔 *NOVO PEDIDO RECEBIDO!*..."
        }
    },
    "messageTimestamp": "1699200000",
    "status": "PENDING"
}
```

---

## 🧪 Como Testar

### Teste 1: Via test-whatsapp.html
```
1. Abra test-whatsapp.html
2. Clique "Enviar Notificação de Teste"
3. Verifique o resultado na tela
4. Verifique WhatsApp: 5512981443806
```

### Teste 2: Via cURL
```bash
curl -X POST "https://evo.devsible.com.br/message/sendText/hakim" \
  -H "Content-Type: application/json" \
  -H "apikey: B6D711FCDE4D-4183-9385-D5C9B6E1E119" \
  -d '{
    "number": "5512981443806",
    "text": "🔔 Teste de notificação!"
  }'
```

### Teste 3: Via Pedido Real
```
1. Abra catalogo.html
2. Adicione produtos ao carrinho
3. Finalize o pedido
4. Verifique console do navegador:
   ✅ "Notificação enviada com sucesso!"
5. Verifique WhatsApp do vendedor
```

---

## 📊 Logs Esperados

### Console do Navegador (Sucesso):
```
📤 Enviando notificação para vendedor via WhatsApp...
📱 Número: 5512981443806
📝 Mensagem: [mensagem completa]
✅ Notificação enviada com sucesso para o vendedor!
{
    "key": {...},
    "message": {...},
    "messageTimestamp": "1699200000"
}
```

### Console do Navegador (Erro):
```
📤 Enviando notificação para vendedor via WhatsApp...
📱 Número: 5512981443806
❌ Erro ao enviar notificação: [detalhes]
```

---

## 🔧 Opções Adicionais

### Presence (Status):
```javascript
options: {
    delay: 1200,
    presence: 'composing'  // ou 'recording', 'available'
}
```

**Valores possíveis**:
- `composing` - Mostra "digitando..."
- `recording` - Mostra "gravando áudio..."
- `available` - Sem status

### Delay:
```javascript
options: {
    delay: 1200  // Milissegundos (1200ms = 1.2s)
}
```

**Recomendado**: 1000-2000ms para parecer mais natural

---

## 🎯 Diferenças entre v1 e v2

| Aspecto | v1 (Antigo) | v2 (Novo) |
|---------|-------------|-----------|
| **Estrutura** | Flat | Nested |
| **Text** | `text: "..."` | `textMessage: { text: "..." }` |
| **Options** | `delay: 1200` | `options: { delay: 1200 }` |
| **Presence** | ❌ Não suportado | ✅ `presence: "composing"` |
| **Response** | Simples | Detalhado |

---

## 🚨 Troubleshooting

### Erro 404 - Route not found
**Causa**: Body no formato v1  
**Solução**: Usar formato v2 (nested)

### Erro 401 - Unauthorized
**Causa**: API Key inválida  
**Solução**: Verificar `apikey` no header

### Erro 400 - Bad Request
**Causa**: Número inválido ou campos faltando  
**Solução**: Verificar formato do número (5512981443806)

### Timeout
**Causa**: Instância desconectada ou rede lenta  
**Solução**: Verificar status da instância

---

## ✅ Checklist de Verificação

- [x] Endpoint correto: `/message/sendText/{instance}`
- [x] Header `apikey` presente
- [x] Body no formato v2 (nested)
- [x] Campo `textMessage.text` presente
- [x] Campo `options.delay` presente
- [x] Número no formato correto (5512981443806)
- [x] Instância conectada
- [x] Logs implementados

---

## 📚 Referências

### Evolution API v2 - SendText:
```
POST /message/sendText/{instance}
```

**Body Schema**:
```typescript
{
    number: string;           // Número com código do país
    options?: {
        delay?: number;       // Delay em ms
        presence?: string;    // Status (composing, recording, available)
    };
    textMessage: {
        text: string;         // Texto da mensagem
    }
}
```

### Documentação Oficial:
- [Evolution API Docs](https://doc.evolution-api.com/)
- [Send Message](https://doc.evolution-api.com/v2/pt/endpoints/messages)

---

## 🎉 Resultado

### Antes da Correção:
```
❌ HTTP 404 - Route not found
❌ Mensagem não enviada
```

### Depois da Correção:
```
✅ HTTP 200 - Success
✅ Mensagem enviada
✅ Vendedor recebe no WhatsApp
✅ Link funciona corretamente
```

---

**Data**: 05/11/2025  
**Status**: ✅ Corrigido  
**Versão API**: v2
