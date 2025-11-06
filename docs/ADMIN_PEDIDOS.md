# 🛍️ Sistema de Gerenciamento de Pedidos - Admin

## 📋 Visão Geral

Tela completa para o vendedor gerenciar pedidos em tempo real, com controle de status e ações rápidas.

---

## ✨ Funcionalidades

### 1. **Dashboard com Estatísticas** 📊

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ ⏳ Pendentes│ ✅ Confirmados│ 🚚 Em Entrega│ 🎉 Entregues│
│      3      │      5      │      2      │     12      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Métricas em tempo real**:
- ✅ Pedidos pendentes (aguardando confirmação)
- ✅ Pedidos confirmados (aguardando preparo)
- ✅ Pedidos em entrega (a caminho)
- ✅ Pedidos entregues (concluídos)

---

### 2. **Filtros por Status** 🔍

```
[📋 Todos] [⏳ Pendentes] [✅ Confirmados] [📦 Preparando] 
[🚚 Em Entrega] [🎉 Entregues] [❌ Cancelados]
```

**Filtros disponíveis**:
- 📋 **Todos**: Exibe todos os pedidos
- ⏳ **Pendentes**: Aguardando confirmação
- ✅ **Confirmados**: Confirmados, aguardando preparo
- 📦 **Preparando**: Em processo de separação
- 🚚 **Em Entrega**: Saiu para entrega
- 🎉 **Entregues**: Concluídos com sucesso
- ❌ **Cancelados**: Pedidos cancelados

---

### 3. **Card de Pedido Completo** 📦

```
┌─────────────────────────────────────────────┐
│ Pedido #71                    [⏳ Pendente] │
│ 5 min atrás                                 │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 👤 João Silva                           │ │
│ │ 📱 (11) 98765-4321                      │ │
│ │ 📍 Rua das Flores, 123 - Centro         │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Itens do Pedido:                            │
│ 2x Dipirona 500mg          R$ 8,50          │
│ 1x Vitamina C              R$ 15,00         │
│ ─────────────────────────────────────────   │
│ Total                      R$ 32,00         │
│                                             │
│ [✅ Confirmar Pedido]  [❌]                 │
└─────────────────────────────────────────────┘
```

**Informações exibidas**:
- ✅ Número do pedido
- ✅ Tempo desde criação
- ✅ Status atual
- ✅ Dados do cliente (nome, telefone, endereço)
- ✅ Lista de itens com quantidades e preços
- ✅ Valor total
- ✅ Botões de ação contextuais

---

## 🔄 Fluxo de Status

### Ciclo de Vida do Pedido:

```
⏳ Pendente
    ↓ [Confirmar Pedido]
✅ Confirmado
    ↓ [Iniciar Preparo]
📦 Preparando
    ↓ [Enviar para Entrega]
🚚 Em Entrega
    ↓ [Marcar como Entregue]
🎉 Entregue
```

### Ações Disponíveis por Status:

#### 1. **Pendente** ⏳
```
[✅ Confirmar Pedido]  [❌ Cancelar]
```
- **Confirmar**: Move para "Confirmado"
- **Cancelar**: Move para "Cancelado"

#### 2. **Confirmado** ✅
```
[📦 Iniciar Preparo]
```
- **Iniciar Preparo**: Move para "Preparando"

#### 3. **Preparando** 📦
```
[🚚 Enviar para Entrega]
```
- **Enviar**: Move para "Em Entrega"

#### 4. **Em Entrega** 🚚
```
[🎉 Marcar como Entregue]
```
- **Entregar**: Move para "Entregue"

#### 5. **Entregue** 🎉
```
[✓ Pedido Concluído]
```
- Sem ações (status final)

#### 6. **Cancelado** ❌
```
[✗ Pedido Cancelado]
```
- Sem ações (status final)

---

## 🎨 Design e UX

### Cores por Status:

| Status | Cor | Gradiente | Ícone |
|--------|-----|-----------|-------|
| **Pendente** | Amarelo | `#fef3c7 → #fde68a` | ⏳ |
| **Confirmado** | Azul | `#dbeafe → #bfdbfe` | ✅ |
| **Preparando** | Índigo | `#e0e7ff → #c7d2fe` | 📦 |
| **Em Entrega** | Roxo | `#ddd6fe → #c4b5fd` | 🚚 |
| **Entregue** | Verde | `#d1fae5 → #a7f3d0` | 🎉 |
| **Cancelado** | Vermelho | `#fee2e2 → #fecaca` | ❌ |

### Animações:

```css
/* Entrada suave dos cards */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Hover nos cards */
.order-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
    border-color: #10b981;
}
```

---

## 📱 Responsividade

### Mobile (≤768px):
```
┌─────────────┐
│ Stats (2x2) │
├─────────────┤
│ Filtros     │
│ (scroll →)  │
├─────────────┤
│ Pedido #71  │
│ (card full) │
├─────────────┤
│ Pedido #70  │
└─────────────┘
```

### Desktop (≥768px):
```
┌───────────────────────────────────────┐
│ Stats (1x4)                           │
├───────────────────────────────────────┤
│ Filtros (todos visíveis)              │
├───────────────────────────────────────┤
│ Pedido #71          Pedido #70        │
│ (cards lado a lado se necessário)     │
└───────────────────────────────────────┘
```

---

## 🔔 Notificações

### Sistema de Feedback:

```
┌─────────────────────────────────┐
│ ✓ Status atualizado com sucesso!│
└─────────────────────────────────┘
```

**Características**:
- ✅ Aparece no canto superior direito
- ✅ Animação de entrada suave
- ✅ Desaparece após 3 segundos
- ✅ Feedback visual imediato

**Mensagens**:
- "Pedido #71 confirmado!"
- "Pedido #71 em preparo!"
- "Pedido #71 enviado para entrega!"
- "Pedido #71 entregue!"
- "Pedido #71 cancelado!"

---

## 💾 Estrutura de Dados

### Objeto de Pedido:

```javascript
{
    id: 71,
    customer: {
        name: 'João Silva',
        phone: '(11) 98765-4321',
        address: 'Rua das Flores, 123 - Centro'
    },
    items: [
        {
            name: 'Dipirona 500mg',
            quantity: 2,
            price: 8.50
        },
        {
            name: 'Vitamina C',
            quantity: 1,
            price: 15.00
        }
    ],
    total: 32.00,
    status: 'pendente',
    createdAt: new Date(),
    estimatedDelivery: '45-60 min'
}
```

---

## 🔧 Integração com API

### Endpoints Necessários:

#### 1. **Listar Pedidos**
```javascript
GET /api/orders
Response: [
    { id: 71, customer: {...}, items: [...], status: 'pendente', ... }
]
```

#### 2. **Atualizar Status**
```javascript
PUT /api/orders/:id/status
Body: { status: 'confirmado' }
Response: { success: true, order: {...} }
```

#### 3. **Cancelar Pedido**
```javascript
DELETE /api/orders/:id
Response: { success: true, message: 'Pedido cancelado' }
```

### Implementação:

```javascript
// Atualizar status
async function updateOrderStatus(orderId, newStatus) {
    try {
        const response = await fetch(`/api/orders/${orderId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Pedido #${orderId} atualizado!`);
            loadOrders(); // Recarregar lista
        }
    } catch (error) {
        console.error('Erro ao atualizar pedido:', error);
        showNotification('Erro ao atualizar pedido', 'error');
    }
}
```

---

## ⚡ Funcionalidades Avançadas

### 1. **Auto-Refresh** 🔄

```javascript
// Atualiza a cada 30 segundos
setInterval(() => {
    loadOrders();
    updateStats();
}, 30000);
```

### 2. **Filtros em Tempo Real** 🔍

```javascript
function filterOrders(status) {
    const filtered = status === 'todos' 
        ? orders 
        : orders.filter(o => o.status === status);
    
    renderOrders(filtered);
}
```

### 3. **Timestamp Dinâmico** ⏰

```javascript
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'Agora mesmo';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min atrás`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h atrás`;
    return `${Math.floor(seconds / 86400)}d atrás`;
}
```

### 4. **Busca por Pedido** 🔎

```javascript
function searchOrder(query) {
    return orders.filter(order => 
        order.id.toString().includes(query) ||
        order.customer.name.toLowerCase().includes(query.toLowerCase()) ||
        order.customer.phone.includes(query)
    );
}
```

---

## 🎯 Casos de Uso

### Cenário 1: Novo Pedido Chegou
```
1. Cliente faz pedido no catálogo
2. Pedido aparece como "Pendente" no admin
3. Notificação sonora (opcional)
4. Vendedor revisa pedido
5. Vendedor clica "Confirmar Pedido"
6. Status muda para "Confirmado"
7. Cliente recebe notificação
```

### Cenário 2: Preparar e Enviar
```
1. Vendedor vê pedido "Confirmado"
2. Clica "Iniciar Preparo"
3. Status muda para "Preparando"
4. Vendedor separa produtos
5. Clica "Enviar para Entrega"
6. Status muda para "Em Entrega"
7. Entregador recebe notificação
```

### Cenário 3: Finalizar Entrega
```
1. Entregador entrega pedido
2. Vendedor clica "Marcar como Entregue"
3. Status muda para "Entregue"
4. Cliente recebe confirmação
5. Pedido arquivado
```

### Cenário 4: Cancelamento
```
1. Cliente solicita cancelamento
2. Vendedor clica "Cancelar"
3. Status muda para "Cancelado"
4. Cliente recebe confirmação
5. Estoque é restaurado (se aplicável)
```

---

## 📊 Métricas e Analytics

### KPIs Importantes:

```javascript
// Tempo médio de confirmação
const avgConfirmTime = orders
    .filter(o => o.status !== 'pendente')
    .reduce((sum, o) => sum + (o.confirmedAt - o.createdAt), 0) 
    / orders.length;

// Taxa de cancelamento
const cancelRate = orders.filter(o => o.status === 'cancelado').length 
    / orders.length * 100;

// Ticket médio
const avgTicket = orders.reduce((sum, o) => sum + o.total, 0) 
    / orders.length;
```

---

## 🔐 Segurança

### Autenticação:

```javascript
// Verificar se usuário é admin
function checkAuth() {
    const token = localStorage.getItem('adminToken');
    
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    
    return true;
}

// Executar ao carregar página
if (!checkAuth()) {
    // Redirecionar para login
}
```

### Permissões:

```javascript
const permissions = {
    admin: ['view', 'confirm', 'cancel', 'update'],
    manager: ['view', 'confirm', 'update'],
    viewer: ['view']
};
```

---

## 🚀 Melhorias Futuras

### 1. **Notificações Push** 🔔
```javascript
// Web Push API
if ('Notification' in window) {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            new Notification('Novo pedido!', {
                body: 'Pedido #71 aguardando confirmação',
                icon: '/icon.png'
            });
        }
    });
}
```

### 2. **Chat com Cliente** 💬
```html
<button class="chat-btn">
    💬 Conversar com Cliente
</button>
```

### 3. **Impressão de Etiquetas** 🖨️
```javascript
function printLabel(order) {
    window.print();
}
```

### 4. **Exportar Relatórios** 📄
```javascript
function exportToCSV(orders) {
    const csv = orders.map(o => 
        `${o.id},${o.customer.name},${o.total},${o.status}`
    ).join('\n');
    
    downloadCSV(csv, 'pedidos.csv');
}
```

### 5. **Mapa de Entregas** 🗺️
```html
<div id="deliveryMap" class="w-full h-96"></div>
<script src="https://maps.googleapis.com/maps/api/js"></script>
```

---

## ✅ Checklist de Implementação

- [x] Dashboard com estatísticas
- [x] Filtros por status
- [x] Cards de pedidos completos
- [x] Botões de ação contextuais
- [x] Sistema de notificações
- [x] Animações suaves
- [x] Design responsivo
- [x] Timestamps dinâmicos
- [x] Auto-refresh
- [ ] Integração com API real
- [ ] Autenticação de admin
- [ ] Notificações push
- [ ] Chat com cliente
- [ ] Impressão de etiquetas
- [ ] Exportar relatórios

---

## 📚 Como Usar

### 1. **Acessar o Admin**
```
http://localhost/admin-pedidos.html
```

### 2. **Visualizar Pedidos**
- Todos os pedidos aparecem automaticamente
- Use os filtros para ver status específicos

### 3. **Gerenciar Pedido**
- Clique nos botões de ação
- Status é atualizado automaticamente
- Notificação confirma a ação

### 4. **Monitorar Estatísticas**
- Cards no topo mostram totais
- Atualizam em tempo real

---

**Data:** 05/11/2025  
**Status:** ✅ Implementado  
**Arquivo:** admin-pedidos.html
