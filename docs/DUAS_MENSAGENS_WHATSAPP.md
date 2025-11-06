# 📱 Sistema de Duas Mensagens WhatsApp

## 🎯 Objetivo

Enviar **DUAS mensagens** quando um pedido é finalizado:

1. ✅ **Mensagem para o CLIENTE** - Confirmação do pedido
2. ✅ **Mensagem para o VENDEDOR** - Notificação com link do admin

---

## 📊 Fluxo Implementado

```
Cliente finaliza pedido
    ↓
Backend processa pedido
    ↓
┌─────────────────────────────────────┐
│ 1. Enviar para CLIENTE              │
│    Número: customer_phone           │
│    Mensagem: Confirmação do pedido  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Enviar para VENDEDOR             │
│    Número: 5512981443806            │
│    Mensagem: Notificação + Link     │
└─────────────────────────────────────┘
```

---

## 💬 Mensagens

### 1. Mensagem para o Cliente

```
**Informações do Pedido**

* **Cliente:** LUCAS HENRIQUE BORGES
* **Telefone:** 5512976021836
* **Endereço de Entrega:** Rua Bernardo Priante, Nº 207
* **Forma de Pagamento:** pix

**Produtos Pedidos:**

- DORFLEX 30X10 (Qtd: 1) - R$ 8.25

**Valor Total:** R$ 8.25

**Número do Pedido:** #80

Pedido registrado com sucesso! ✅
```

**Enviado para**: `customer_phone` (ex: 5512976021836)

---

### 2. Mensagem para o Vendedor

```
🔔 *NOVO PEDIDO RECEBIDO!*

📋 *Pedido:* #80
⏰ *Horário:* 05/11/2025 20:30:55

👤 *CLIENTE*
Nome: LUCAS HENRIQUE BORGES
📱 Telefone: 5512976021836
📍 Endereço: Rua Bernardo Priante, Nº 207

🛒 *PRODUTOS*
1. *DORFLEX 30X10*
   Qtd: 1 | R$ 8.25

💰 *TOTAL:* R$ 8.25
💳 *Pagamento:* pix

🔗 *GERENCIAR PEDIDO:*
https://ma.devsible.com.br/admin-pedidos.html?pedido=80

✅ Acesse o link acima para confirmar e gerenciar este pedido!
```

**Enviado para**: `WHATSAPP_PHONE` (5512981443806)

---

## 🔧 Implementação

### Função Principal (process_order):

```python
# 4. Formatar mensagem para o cliente
message_cliente = self._format_message(order_result, order_items)

# 5. Enviar mensagem WhatsApp para o cliente
whatsapp_result = self._send_whatsapp_message(
    message_cliente, 
    order_result['customer_phone']  # ✅ Número do cliente
)

# 6. Enviar notificação para o vendedor
message_vendedor = self._format_seller_notification(order_result, order_items)
seller_result = self._send_whatsapp_message(
    message_vendedor,
    WHATSAPP_PHONE  # ✅ Número do vendedor (5512981443806)
)
```

---

### Função de Envio (modificada):

```python
def _send_whatsapp_message(self, message: str, phone_number: str = None) -> Dict[str, Any]:
    """Envia mensagem WhatsApp para um número específico"""
    
    # Usar número fornecido ou padrão (vendedor)
    target_phone = phone_number or WHATSAPP_PHONE
    
    payload = {
        "number": target_phone,  # ✅ Número dinâmico
        "text": message
    }
    
    # ... resto do código
```

---

### Nova Função para Mensagem do Vendedor:

```python
def _format_seller_notification(self, order: Dict[str, Any], items: List[Dict[str, Any]]) -> str:
    """Formata mensagem de notificação para o vendedor com link do admin"""
    
    # Montar lista de produtos
    produtos_text = "\n".join([
        f"{idx}. *{item['product_descricao']}*\n   Qtd: {item['quantity']} | R$ {item['unit_price']:.2f}"
        for idx, item in enumerate(items, 1)
    ])
    
    # Link para o admin
    admin_link = f"https://ma.devsible.com.br/admin-pedidos.html?pedido={order['id']}"
    
    # Timestamp atual
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    message = f"""🔔 *NOVO PEDIDO RECEBIDO!*

📋 *Pedido:* #{order['id']}
⏰ *Horário:* {timestamp}

👤 *CLIENTE*
Nome: {order['customer_name']}
📱 Telefone: {order['customer_phone']}
📍 Endereço: {order['customer_address']}

🛒 *PRODUTOS*
{produtos_text}

💰 *TOTAL:* R$ {order['total']:.2f}
💳 *Pagamento:* {order['payment_method']}

🔗 *GERENCIAR PEDIDO:*
{admin_link}

✅ Acesse o link acima para confirmar e gerenciar este pedido!"""
    
    return message
```

---

## 📊 Response da API

### Antes:
```json
{
    "success": true,
    "order_id": 80,
    "whatsapp_sent": true,
    "data": {
        "whatsapp_response": {...}
    }
}
```

### Depois:
```json
{
    "success": true,
    "order_id": 80,
    "whatsapp_sent": true,  // Cliente
    "seller_notified": true,  // ✅ Vendedor
    "data": {
        "whatsapp_response": {...},  // Resposta do cliente
        "seller_notification": {...}  // ✅ Resposta do vendedor
    }
}
```

---

## 🔍 Diferenças entre as Mensagens

| Aspecto | Cliente | Vendedor |
|---------|---------|----------|
| **Destinatário** | customer_phone | 5512981443806 |
| **Formato** | Simples | Com emojis e formatação |
| **Link Admin** | ❌ Não | ✅ Sim |
| **Timestamp** | ❌ Não | ✅ Sim |
| **Produtos** | Lista simples | Lista numerada |
| **Objetivo** | Confirmação | Ação (gerenciar) |

---

## 🧪 Como Testar

### 1. Reiniciar Backend:
```bash
docker-compose restart backend
```

### 2. Fazer Pedido:
```
1. Abrir catalogo.html
2. Adicionar produtos
3. Preencher dados (telefone do cliente)
4. Finalizar pedido
```

### 3. Verificar Logs:
```json
{
    "whatsapp_sent": true,  // ✅ Cliente recebeu
    "seller_notified": true  // ✅ Vendedor recebeu
}
```

### 4. Verificar WhatsApp:

#### Cliente (ex: 5512976021836):
```
✅ Deve receber: Confirmação do pedido
```

#### Vendedor (5512981443806):
```
✅ Deve receber: Notificação com link do admin
```

---

## 📱 Números Configurados

### Cliente:
```
Dinâmico - vem do formulário
Exemplo: 5512976021836
```

### Vendedor:
```
Fixo - configurado no .env
WHATSAPP_PHONE=5512981443806
```

---

## ⚠️ Importante

### Antes da Correção:
- ❌ Apenas 1 mensagem era enviada
- ❌ Ia para o número fixo (vendedor)
- ❌ Cliente não recebia confirmação
- ❌ Vendedor não recebia link do admin

### Depois da Correção:
- ✅ 2 mensagens são enviadas
- ✅ Cliente recebe confirmação
- ✅ Vendedor recebe notificação com link
- ✅ Números corretos para cada destinatário

---

## 🎯 Resultado Final

### Cliente recebe:
```
📱 WhatsApp: customer_phone
📄 Mensagem: Confirmação simples
🎯 Objetivo: Tranquilizar o cliente
```

### Vendedor recebe:
```
📱 WhatsApp: 5512981443806
📄 Mensagem: Notificação completa + link
🎯 Objetivo: Gerenciar o pedido
```

---

## 🔐 Segurança

### Validação de Números:
```python
# Garantir formato correto
if not phone_number or len(phone_number) < 10:
    phone_number = WHATSAPP_PHONE  # Fallback
```

### Timeout:
```python
response = requests.post(url, json=payload, headers=headers, timeout=30)
```

### Retry (futuro):
```python
# Implementar retry em caso de falha
for attempt in range(3):
    result = send_message()
    if result["success"]:
        break
```

---

## ✅ Checklist

- [x] Função `_send_whatsapp_message` aceita número como parâmetro
- [x] Função `_format_seller_notification` criada
- [x] Mensagem para cliente enviada
- [x] Mensagem para vendedor enviada
- [x] Link do admin incluído na mensagem do vendedor
- [x] Response da API atualizado
- [x] Logs incluem ambos os resultados
- [ ] Reiniciar backend
- [ ] Testar com pedido real
- [ ] Confirmar recebimento em ambos os números

---

**Status**: ✅ Implementado  
**Mensagens**: 2 (Cliente + Vendedor)  
**Vendedor**: 5512981443806
