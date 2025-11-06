# 📱 Integração WhatsApp - Evolution API

## 🎯 Visão Geral

Sistema de notificação automática via WhatsApp para o vendedor quando um novo pedido é finalizado.

---

## ⚙️ Configuração

### Credenciais Evolution API:

```javascript
const EVOLUTION_CONFIG = {
    API_URL: 'https://evo.devsible.com.br',
    API_KEY: 'B6D711FCDE4D-4183-9385-D5C9B6E1E119',
    INSTANCE_NAME: 'hakim',
    SELLER_PHONE: '5512981443806'
};
```

---

## 🔄 Fluxo de Notificação

### 1. Cliente Finaliza Pedido
```
Cliente → [Confirmar Pedido] → Sistema processa
```

### 2. Sistema Envia Notificação
```
Sistema → Evolution API → WhatsApp Vendedor
```

### 3. Vendedor Recebe Mensagem
```
WhatsApp → Notificação → Link para Admin
```

---

## 📨 Formato da Mensagem

### Mensagem Enviada ao Vendedor:

```
🔔 *NOVO PEDIDO RECEBIDO!*

📋 *Pedido:* #71
⏰ *Horário:* 05/11/2025 14:30:15

👤 *CLIENTE*
Nome: João Silva
📱 Telefone: (11) 98765-4321
📍 Endereço: Rua das Flores, 123 - Centro

🛒 *PRODUTOS*
1. *Dipirona 500mg*
   Qtd: 2 | R$ 8.50

2. *Vitamina C*
   Qtd: 1 | R$ 15.00

💰 *TOTAL:* R$ 32.00
💳 *Pagamento:* Dinheiro

🔗 *GERENCIAR PEDIDO:*
https://ma.devsible.com.br/admin-pedidos.html?pedido=71

✅ Acesse o link acima para confirmar e gerenciar este pedido!
```

---

## 🔗 Link Dinâmico

### Estrutura do Link:

```
https://[seu-dominio]/admin-pedidos.html?pedido=[ID]
```

### Exemplo:
```
https://ma.devsible.com.br/admin-pedidos.html?pedido=71
```

### Funcionalidades do Link:
- ✅ Abre diretamente a tela de admin
- ✅ Destaca o pedido específico
- ✅ Permite ações imediatas
- ✅ Funciona em qualquer dispositivo

---

## 💻 Implementação

### Função Principal:

```javascript
async function sendOrderNotificationToSeller(orderData, orderDetails) {
    const EVOLUTION_API_URL = 'https://evo.devsible.com.br';
    const EVOLUTION_API_KEY = 'B6D711FCDE4D-4183-9385-D5C9B6E1E119';
    const INSTANCE_NAME = 'hakim';
    const SELLER_PHONE = '5512981443806';
    
    // Extrair dados do pedido
    const orderId = orderData.order?.order_number || orderData.order?.id;
    const customerName = orderDetails.cliente?.nome;
    const total = orderDetails.pedido?.valor_total;
    
    // Criar link dinâmico
    const adminLink = `${window.location.origin}/admin-pedidos.html?pedido=${orderId}`;
    
    // Montar mensagem
    const message = `🔔 *NOVO PEDIDO RECEBIDO!*
    
📋 *Pedido:* #${orderId}
👤 *Cliente:* ${customerName}
💰 *Total:* R$ ${total.toFixed(2)}

🔗 *GERENCIAR:*
${adminLink}`;
    
    // Enviar via Evolution API v2
    const response = await fetch(`${EVOLUTION_API_URL}/message/sendText/${INSTANCE_NAME}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'apikey': EVOLUTION_API_KEY
        },
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
    });
    
    return response.ok;
}
```

---

## 🔌 Endpoints Evolution API

### 1. Enviar Mensagem de Texto

**Endpoint:**
```
POST /message/sendText/{instance}
```

**Headers:**
```json
{
    "Content-Type": "application/json",
    "apikey": "B6D711FCDE4D-4183-9385-D5C9B6E1E119"
}
```

**Body (Evolution API v2):**
```json
{
    "number": "5512981443806",
    "options": {
        "delay": 1200,
        "presence": "composing"
    },
    "textMessage": {
        "text": "Mensagem aqui"
    }
}
```

**Response:**
```json
{
    "key": {
        "remoteJid": "5512981443806@s.whatsapp.net",
        "fromMe": true,
        "id": "3EB0..."
    },
    "message": {
        "conversation": "Mensagem aqui"
    },
    "messageTimestamp": "1699200000"
}
```

---

### 2. Enviar Mídia

**Endpoint:**
```
POST /message/sendMedia/{instance}
```

**Body:**
```json
{
    "number": "5512981443806",
    "mediaUrl": "https://example.com/image.jpg",
    "caption": "Legenda da imagem",
    "delay": 1200
}
```

---

### 3. Verificar Status da Instância

**Endpoint:**
```
GET /instance/connectionState/{instance}
```

**Response:**
```json
{
    "instance": "hakim",
    "state": "open"
}
```

---

## 🎨 Personalização da Mensagem

### Variáveis Disponíveis:

```javascript
const messageTemplate = {
    orderId: '#71',
    timestamp: '05/11/2025 14:30:15',
    customer: {
        name: 'João Silva',
        phone: '(11) 98765-4321',
        address: 'Rua das Flores, 123'
    },
    products: [
        { name: 'Dipirona', qty: 2, price: 8.50 },
        { name: 'Vitamina C', qty: 1, price: 15.00 }
    ],
    total: 32.00,
    payment: 'Dinheiro',
    adminLink: 'https://...'
};
```

### Emojis Recomendados:

| Elemento | Emoji | Uso |
|----------|-------|-----|
| Alerta | 🔔 | Início da mensagem |
| Pedido | 📋 | Número do pedido |
| Horário | ⏰ | Timestamp |
| Cliente | 👤 | Dados do cliente |
| Telefone | 📱 | Número de contato |
| Endereço | 📍 | Localização |
| Produtos | 🛒 | Lista de itens |
| Total | 💰 | Valor total |
| Pagamento | 💳 | Forma de pagamento |
| Link | 🔗 | URL do admin |
| Confirmar | ✅ | Call to action |

---

## 🔐 Segurança

### Boas Práticas:

1. **API Key Protegida**
```javascript
// ❌ Não fazer (expõe a key)
const API_KEY = 'B6D711FCDE4D-4183-9385-D5C9B6E1E119';

// ✅ Fazer (usar variável de ambiente)
const API_KEY = process.env.EVOLUTION_API_KEY;
```

2. **Validação de Número**
```javascript
function validatePhoneNumber(phone) {
    // Formato: 5512981443806 (país + DDD + número)
    const regex = /^55\d{10,11}$/;
    return regex.test(phone);
}
```

3. **Rate Limiting**
```javascript
// Evitar spam de mensagens
const MESSAGE_DELAY = 1200; // ms entre mensagens
```

4. **Timeout**
```javascript
// Timeout para requisições
const TIMEOUT = 10000; // 10 segundos
```

---

## 🧪 Testes

### Teste Manual:

1. **Fazer um pedido no catálogo**
2. **Verificar console do navegador**:
   ```
   📤 Enviando notificação para vendedor via WhatsApp...
   📱 Número: 5512981443806
   ✅ Notificação enviada com sucesso!
   ```
3. **Verificar WhatsApp do vendedor**
4. **Clicar no link recebido**
5. **Verificar se abre o admin com o pedido**

### Teste com cURL:

```bash
curl -X POST "https://evo.devsible.com.br/message/sendText/hakim" \
  -H "Content-Type: application/json" \
  -H "apikey: B6D711FCDE4D-4183-9385-D5C9B6E1E119" \
  -d '{
    "number": "5512981443806",
    "text": "🔔 Teste de notificação!",
    "delay": 1200
  }'
```

### Teste com JavaScript:

```javascript
async function testNotification() {
    const result = await sendOrderNotificationToSeller(
        { order: { id: 999 } },
        {
            cliente: { nome: 'Teste', telefone: '(11) 99999-9999' },
            pedido: { valor_total: 10.00 },
            produtos: [{ nome: 'Teste', quantidade: 1, preco: 10.00 }]
        }
    );
    
    console.log('Teste:', result ? '✅ Sucesso' : '❌ Falha');
}
```

---

## 📊 Monitoramento

### Logs Importantes:

```javascript
// Sucesso
console.log('✅ Notificação enviada com sucesso!', result);

// Erro de API
console.error('❌ Erro ao enviar notificação:', result);

// Erro de rede
console.error('❌ Erro ao enviar notificação via WhatsApp:', error);
```

### Métricas:

```javascript
const metrics = {
    totalSent: 0,        // Total de notificações enviadas
    totalFailed: 0,      // Total de falhas
    avgResponseTime: 0,  // Tempo médio de resposta
    lastSent: null       // Última notificação enviada
};
```

---

## 🚨 Tratamento de Erros

### Erros Comuns:

#### 1. **Instância Desconectada**
```json
{
    "error": "Instance not connected"
}
```
**Solução**: Reconectar instância no Evolution

#### 2. **API Key Inválida**
```json
{
    "error": "Unauthorized"
}
```
**Solução**: Verificar API Key

#### 3. **Número Inválido**
```json
{
    "error": "Invalid number format"
}
```
**Solução**: Usar formato correto (5512981443806)

#### 4. **Timeout**
```
Error: Request timeout
```
**Solução**: Aumentar timeout ou verificar conexão

---

## 🔄 Retry Logic

### Implementação de Retry:

```javascript
async function sendWithRetry(sendFunction, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const result = await sendFunction();
            if (result) return true;
        } catch (error) {
            console.warn(`Tentativa ${i + 1} falhou:`, error);
            if (i === maxRetries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1)));
        }
    }
    return false;
}

// Uso
await sendWithRetry(() => sendOrderNotificationToSeller(orderData, orderDetails));
```

---

## 📱 Melhorias Futuras

### 1. **Notificação para Cliente**
```javascript
// Enviar confirmação para o cliente também
await sendTextMessage(
    customerPhone,
    `✅ Pedido #${orderId} confirmado!\n\nAcompanhe: ${trackingLink}`
);
```

### 2. **Atualizações de Status**
```javascript
// Notificar cliente sobre mudanças de status
const statusMessages = {
    confirmado: '✅ Seu pedido foi confirmado!',
    preparando: '📦 Estamos preparando seu pedido!',
    enviado: '🚚 Seu pedido saiu para entrega!',
    entregue: '🎉 Pedido entregue com sucesso!'
};
```

### 3. **Mensagens com Mídia**
```javascript
// Enviar foto do produto
await sendMediaMessage(
    customerPhone,
    productImageUrl,
    'Seu pedido está a caminho! 🚚'
);
```

### 4. **Botões Interativos**
```javascript
// Usar botões do WhatsApp Business
const buttons = [
    { id: 'confirm', text: 'Confirmar Pedido' },
    { id: 'cancel', text: 'Cancelar' }
];
```

---

## ✅ Checklist de Implementação

- [x] Configuração da Evolution API
- [x] Função de envio de notificação
- [x] Formatação da mensagem
- [x] Link dinâmico para admin
- [x] Integração com fluxo de pedido
- [x] Logs e monitoramento
- [x] Tratamento de erros
- [ ] Retry logic
- [ ] Notificação para cliente
- [ ] Atualizações de status
- [ ] Mensagens com mídia
- [ ] Botões interativos

---

## 📚 Recursos

### Documentação Evolution API:
- [Documentação Oficial](https://doc.evolution-api.com/)
- [Endpoints](https://doc.evolution-api.com/v2/pt/endpoints)
- [Exemplos](https://doc.evolution-api.com/v2/pt/examples)

### Testes:
- `evolution-api-config.js` - Configuração e funções auxiliares
- `test-whatsapp.html` - Página de teste (criar se necessário)

---

**Data:** 05/11/2025  
**Status:** ✅ Implementado  
**Vendedor:** 5512981443806
