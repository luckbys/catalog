# Notificação Automática para Entregador

## Resumo
Sistema automático que envia o link da tela do entregador via WhatsApp quando o status de entrega muda para "Em Trânsito" ou "Saiu para Entrega".

## Fluxo Completo

### 1. Admin Atualiza Status
```
Admin (admin-pedidos.html)
  ↓
Seleciona "Em Trânsito" ou "Saiu para Entrega" no dropdown
  ↓
PUT /api/orders/{id}/delivery-status
```

### 2. Backend Processa
```
Backend (app.py)
  ↓
Atualiza delivery_status no Supabase
  ↓
Verifica se status é 'in_transit' ou 'out_for_delivery'
  ↓
Chama send_delivery_link_to_driver()
```

### 3. Envio via WhatsApp
```
send_delivery_link_to_driver()
  ↓
Constrói mensagem com:
  - Número do pedido
  - Nome do cliente
  - Endereço
  - Valor total
  - Link da tela do entregador
  ↓
Envia via Evolution API
  ↓
Entregador recebe no WhatsApp
```

### 4. Entregador Acessa
```
Entregador
  ↓
Clica no link recebido
  ↓
Abre entregador.html?pedido={id}
  ↓
Vê mapa, dados e ações
```

## Configuração

### Variáveis de Ambiente (.env)
```bash
# Evolution API
EVOLUTION_API_URL=https://chatbot-evolution-api.zv7gpn.easypanel.host
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
EVOLUTION_INSTANCE_NAME=hakimfarma

# Número do Entregador
# Definido no código: 5512976025888

# URL Base (para construir link)
CLIENT_BASE_URL=https://catalogo-hakim
```

### Número do Entregador
Atualmente hardcoded no backend:
```python
DRIVER_PHONE = "5512976025888"
```

## Mensagem Enviada

### Formato
```
🚚 *Nova Entrega Disponível!*

📦 *Pedido #123*
👤 Cliente: João Silva
📍 Endereço: Rua das Flores, 123 - Centro
💰 Valor: R$ 45,90

🔗 Acesse os detalhes da entrega:
https://catalogo-hakim/entregador.html?pedido=123

_Clique no link para ver o mapa e informações completas._
```

### Elementos
- ✅ Emojis para melhor visualização
- ✅ Negrito em informações importantes
- ✅ Link clicável
- ✅ Instruções claras

## Código Backend

### Função Principal
```python
async def send_delivery_link_to_driver(order_id: int, order_data: dict):
    """Envia link da tela do entregador via Evolution API"""
    
    # Configurações
    DRIVER_PHONE = "5512976025888"
    
    # Construir URL
    delivery_url = f"{base_url}/entregador.html?pedido={order_id}"
    
    # Construir mensagem
    message = f"""🚚 *Nova Entrega Disponível!*
    
📦 *Pedido #{order_id}*
👤 Cliente: {customer_name}
📍 Endereço: {customer_address}
💰 Valor: R$ {total:.2f}

🔗 Acesse os detalhes da entrega:
{delivery_url}"""
    
    # Enviar via Evolution API
    response = requests.post(url, json=payload, headers=headers)
```

### Integração com Update Status
```python
@app.put("/api/orders/{order_id}/delivery-status")
async def update_delivery_status(order_id: int, request: dict):
    # ... atualiza status ...
    
    # Enviar link se status for in_transit ou out_for_delivery
    if new_delivery_status in ['in_transit', 'out_for_delivery']:
        try:
            await send_delivery_link_to_driver(order_id, result.data[0])
        except Exception as e:
            print(f"[WARNING] Erro ao enviar link: {e}")
            # Não falha a requisição
```

## Status que Acionam Envio

### Acionam Notificação
- ✅ `in_transit` - Em Trânsito
- ✅ `out_for_delivery` - Saiu para Entrega

### NÃO Acionam
- ❌ `pending` - Pendente
- ❌ `preparing` - Preparando
- ❌ `ready_for_pickup` - Pronto para Retirada
- ❌ `delivered` - Entregue
- ❌ `failed` - Falhou
- ❌ `returned` - Devolvido

## Tratamento de Erros

### Erro no Envio
```python
try:
    await send_delivery_link_to_driver(order_id, order_data)
except Exception as e:
    print(f"[WARNING] Erro ao enviar link: {e}")
    # Não falha a requisição principal
```

### Comportamento
- ✅ Status é atualizado mesmo se WhatsApp falhar
- ✅ Erro é logado mas não interrompe fluxo
- ✅ Admin recebe confirmação de atualização
- ⚠️ Entregador pode não receber link (verificar logs)

### Logs
```
[WHATSAPP] Enviando link do entregador para 5512976025888
[WHATSAPP] URL: https://...
[WHATSAPP] Link: https://catalogo-hakim/entregador.html?pedido=123
[WHATSAPP] Link enviado com sucesso para o entregador
```

## Evolution API

### Endpoint Usado
```
POST /message/sendText/{instance_name}
```

### Headers
```json
{
  "Content-Type": "application/json",
  "apikey": "429683C4C977415CAAFCCE10F7D57E11"
}
```

### Payload
```json
{
  "number": "5512976025888",
  "text": "🚚 *Nova Entrega Disponível!*\n\n..."
}
```

### Response
- **201/200**: Sucesso
- **Outros**: Erro (logado mas não interrompe)

## Melhorias Futuras

### Planejadas
- [ ] Múltiplos entregadores (selecionar no admin)
- [ ] Tabela de entregadores no banco
- [ ] Histórico de notificações enviadas
- [ ] Retry automático em caso de falha
- [ ] Confirmação de leitura
- [ ] Botões interativos no WhatsApp
- [ ] Notificação quando entregador visualiza
- [ ] Tempo estimado de chegada

### Banco de Dados
Criar tabela `delivery_notifications`:
```sql
CREATE TABLE delivery_notifications (
  id SERIAL PRIMARY KEY,
  order_id INTEGER REFERENCES orders(id),
  driver_phone VARCHAR(20),
  message TEXT,
  sent_at TIMESTAMP,
  status VARCHAR(20), -- sent, failed, read
  error_message TEXT
);
```

## Testes

### Testar Manualmente
1. Acesse admin-pedidos.html
2. Selecione um pedido
3. Mude status para "Em Trânsito"
4. Verifique logs do backend
5. Verifique WhatsApp do entregador (5512976025888)

### Verificar Logs
```bash
# Backend deve mostrar:
[WHATSAPP] Enviando link do entregador para 5512976025888
[WHATSAPP] Link enviado com sucesso para o entregador
```

### Testar Link
```
https://catalogo-hakim/entregador.html?pedido=123
```

## Troubleshooting

### Link não enviado
- ✅ Verificar EVOLUTION_API_URL no .env
- ✅ Verificar EVOLUTION_API_KEY no .env
- ✅ Verificar EVOLUTION_INSTANCE_NAME no .env
- ✅ Verificar logs do backend
- ✅ Testar Evolution API manualmente

### Link enviado mas não abre
- ✅ Verificar CLIENT_BASE_URL no .env
- ✅ Verificar se domínio está acessível
- ✅ Testar link manualmente no navegador

### Entregador não recebe
- ✅ Verificar número do telefone (5512976025888)
- ✅ Verificar se WhatsApp está conectado
- ✅ Verificar instância da Evolution API
- ✅ Verificar logs de erro

## Exemplo Completo

### 1. Admin Atualiza
```javascript
// admin-pedidos.html
select.value = 'in_transit';
// Dispara PUT /api/orders/123/delivery-status
```

### 2. Backend Processa
```python
# backend/app.py
new_delivery_status = 'in_transit'
# Atualiza no Supabase
# Envia link via WhatsApp
```

### 3. Entregador Recebe
```
WhatsApp do 5512976025888:
🚚 Nova Entrega Disponível!
📦 Pedido #123
...
🔗 https://catalogo-hakim/entregador.html?pedido=123
```

### 4. Entregador Acessa
```
Clica no link → Abre tela do entregador
Vê mapa → Usa navegação → Confirma entrega
```

## Segurança

### Considerações
- ✅ API Key da Evolution não exposta no frontend
- ✅ Número do entregador não exposto publicamente
- ⚠️ Link do entregador é público (qualquer um com ID pode acessar)
- ⚠️ TODO: Adicionar autenticação na tela do entregador
- ⚠️ TODO: Token de acesso único por entrega

### Melhorias de Segurança
```python
# Gerar token único
token = secrets.token_urlsafe(32)
delivery_url = f"{base_url}/entregador.html?token={token}"

# Validar token no backend
@app.get("/api/delivery/{token}")
def get_delivery_by_token(token: str):
    # Buscar pedido pelo token
    # Retornar dados apenas se token válido
```
