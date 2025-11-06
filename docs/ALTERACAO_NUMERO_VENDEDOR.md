# 📱 Alteração do Número do Vendedor

## 🔄 Mudança Realizada

### ❌ Número Anterior:
```
5512981443806
```

### ✅ Novo Número:
```
5512976025888
```

---

## 📁 Arquivos Atualizados

### 1. **Backend**

#### `.env`
```env
WHATSAPP_PHONE=5512976025888
```

#### `backend/order_processor.py`
```python
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "5512976025888")
```

---

### 2. **Frontend**

#### `catalogo.html`
```javascript
const SELLER_PHONE = '5512976025888';
```

#### `test-whatsapp.html`
```javascript
const SELLER_PHONE = '5512976025888';
```

---

### 3. **Scripts de Teste**

#### `test-evolution-api.sh`
```bash
PHONE="5512976025888"
```

#### `test-evolution-api.ps1`
```powershell
$PHONE = "5512976025888"
```

---

## 📊 Resumo das Alterações

| Arquivo | Linha/Variável | Valor Anterior | Novo Valor |
|---------|----------------|----------------|------------|
| `.env` | WHATSAPP_PHONE | 5512981443806 | 5512976025888 |
| `order_processor.py` | WHATSAPP_PHONE | 5512981443806 | 5512976025888 |
| `catalogo.html` | SELLER_PHONE | 5512981443806 | 5512976025888 |
| `test-whatsapp.html` | SELLER_PHONE | 5512976021836 | 5512976025888 |
| `test-whatsapp.html` | Display | 5512981443806 | 5512976025888 |
| `test-evolution-api.sh` | PHONE | 5512981443806 | 5512976025888 |
| `test-evolution-api.ps1` | $PHONE | 5512981443806 | 5512976025888 |

**Total**: 7 arquivos atualizados ✅

---

## 🎯 Impacto

### Mensagens que vão para o novo número:

1. **Notificação de Novo Pedido** (Backend)
   - Enviada quando cliente finaliza pedido
   - Contém link para admin
   - Número: 5512976025888

2. **Notificação de Novo Pedido** (Frontend)
   - Enviada diretamente do navegador
   - Backup/redundância
   - Número: 5512976025888

---

## 🚀 Próximos Passos

### 1. Reiniciar Backend:
```bash
docker-compose restart backend
```

### 2. Limpar Cache do Navegador:
```
Ctrl + Shift + R (ou Cmd + Shift + R no Mac)
```

### 3. Fazer Pedido Teste:
```
1. Abrir catalogo.html
2. Adicionar produtos
3. Finalizar pedido
```

### 4. Verificar WhatsApp:
```
Número: 5512976025888
Mensagem: Notificação de novo pedido + link
```

---

## 🧪 Como Testar

### Teste Rápido (test-whatsapp.html):
```
1. Abrir test-whatsapp.html
2. Clicar "Enviar Notificação de Teste"
3. Verificar WhatsApp: 5512976025888
```

### Teste Completo (Pedido Real):
```
1. Abrir catalogo.html
2. Adicionar produtos ao carrinho
3. Preencher dados de entrega
4. Finalizar pedido
5. Verificar 2 mensagens:
   - Cliente: customer_phone
   - Vendedor: 5512976025888
```

---

## 📱 Números Configurados Agora

### Cliente:
```
Dinâmico - vem do formulário
Exemplo: 5512976021836
```

### Vendedor:
```
Fixo - 5512976025888
Recebe: Notificação + Link do Admin
```

---

## ✅ Checklist de Verificação

- [x] `.env` atualizado
- [x] `order_processor.py` atualizado
- [x] `catalogo.html` atualizado
- [x] `test-whatsapp.html` atualizado
- [x] `test-evolution-api.sh` atualizado
- [x] `test-evolution-api.ps1` atualizado
- [ ] Backend reiniciado
- [ ] Cache do navegador limpo
- [ ] Teste realizado
- [ ] Mensagem recebida em 5512976025888

---

## 🔐 Configuração Final

### Evolution API (Backend):
```
URL: https://chatbot-evolution-api.zv7gpn.easypanel.host
API Key: 429683C4C977415CAAFCCE10F7D57E11
Instância: hakimfarma
Vendedor: 5512976025888
```

### Evolution API (Frontend):
```
URL: https://evo.devsible.com.br
API Key: B6D711FCDE4D-4183-9385-D5C9B6E1E119
Instância: hakim
Vendedor: 5512976025888
```

---

## 📊 Fluxo de Mensagens

```
Cliente finaliza pedido
    ↓
Backend processa
    ↓
┌─────────────────────────────────────┐
│ Mensagem 1: Para o CLIENTE          │
│ Número: customer_phone (dinâmico)   │
│ Conteúdo: Confirmação do pedido     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Mensagem 2: Para o VENDEDOR         │
│ Número: 5512976025888 (fixo)        │
│ Conteúdo: Notificação + Link Admin  │
└─────────────────────────────────────┘
```

---

**Status**: ✅ Atualizado  
**Novo Número**: 5512976025888  
**Ação Necessária**: Reiniciar backend e testar
