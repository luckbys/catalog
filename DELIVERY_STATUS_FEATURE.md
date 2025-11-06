# Feature: Status de Entrega

## Resumo
Implementação de um campo específico para rastreamento do status de entrega dos pedidos, separado do status geral do pedido.

## Alterações no Banco de Dados

### Novo Campo: `delivery_status`
- **Tipo**: `character varying(20)`
- **Default**: `'pending'`
- **Valores permitidos**:
  - `pending` - Pendente
  - `preparing` - Preparando Pedido
  - `ready_for_pickup` - Pronto para Retirada
  - `in_transit` - Em Trânsito
  - `out_for_delivery` - Saiu para Entrega
  - `delivered` - Entregue
  - `failed` - Falha na Entrega
  - `returned` - Devolvido

### Migration SQL
Execute o arquivo `add_delivery_status_field.sql` no Supabase para:
1. Adicionar o campo `delivery_status`
2. Criar constraint de validação
3. Criar índice para performance
4. Atualizar pedidos existentes baseado no status atual

## Alterações no Frontend (admin-pedidos.html)

### Nova Seção de Status de Entrega
Cada card de pedido agora exibe:
- Status de entrega atual com ícone e label
- Dropdown para atualizar o status de entrega
- Atualização em tempo real via API

### Funcionalidades
- Seleção visual do status de entrega
- Atualização automática ao mudar o select
- Notificação de sucesso/erro
- Reload automático dos pedidos após atualização

## Alterações no Backend (backend/app.py)

### Nova Rota
```
PUT /api/orders/{order_id}/delivery-status
```

**Body:**
```json
{
  "delivery_status": "in_transit"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Status de entrega atualizado com sucesso",
  "order_id": 123,
  "new_delivery_status": "in_transit"
}
```

### Atualização na Rota GET /api/orders
Agora retorna o campo `delivery_status` em cada pedido.

## Como Usar

1. **Execute a migration SQL** no Supabase
2. **Reinicie o backend** para carregar as novas rotas
3. **Acesse admin-pedidos.html**
4. **Selecione o status de entrega** no dropdown de cada pedido
5. **O status será atualizado automaticamente** no banco de dados

## Diferença entre `status` e `delivery_status`

- **status**: Status geral do pedido (pending, confirmed, processing, shipped, delivered, cancelled)
- **delivery_status**: Status específico da entrega (pending, preparing, ready_for_pickup, in_transit, out_for_delivery, delivered, failed, returned)

Isso permite um controle mais granular do processo de entrega, independente do status geral do pedido.
