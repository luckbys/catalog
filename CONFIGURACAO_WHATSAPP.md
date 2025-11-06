# 📱 Configuração WhatsApp - Números e Credenciais

## 🎯 Número do Vendedor

### ✅ Configuração Correta:
```
5512981443806
```

**Formato**: País (55) + DDD (12) + Número (981443806)

---

## 📋 Configurações por Arquivo

### 1. **Backend (.env)**
```env
WHATSAPP_PHONE=5512981443806
EVOLUTION_API_URL=https://chatbot-evolution-api.zv7gpn.easypanel.host
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
EVOLUTION_INSTANCE_NAME=hakimfarma
```
✅ **Status**: Correto

### 2. **Backend (order_processor.py)**
```python
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "5512981443806")  # ✅ Corrigido
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "hakimfarma")  # ✅ Corrigido
```
✅ **Status**: Corrigido agora

### 3. **Frontend (catalogo.html)**
```javascript
const SELLER_PHONE = '5512981443806';  // ✅ Correto
const INSTANCE_NAME = 'hakim';  // ⚠️ Diferente do backend
```
⚠️ **Atenção**: Frontend usa instância "hakim", backend usa "hakimfarma"

---

## 🔧 Correções Aplicadas

### Antes:
```python
# ❌ ERRADO - Número do cliente
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "5512976021836")

# ❌ ERRADO - Instância com espaço
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "hakin t")
```

### Depois:
```python
# ✅ CORRETO - Número do vendedor
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "5512981443806")

# ✅ CORRETO - Instância correta
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "hakimfarma")
```

---

## 🔍 Verificação de Instância

### Backend usa:
```
hakimfarma
```

### Frontend usa:
```
hakim
```

### ⚠️ Possível Problema:
Se as instâncias forem diferentes, o frontend pode estar enviando para uma instância e o backend para outra.

---

## 🧪 Como Testar

### 1. Reiniciar Backend:
```bash
# Docker
docker-compose restart backend

# Local
uvicorn backend.app:app --reload
```

### 2. Fazer Pedido:
```
1. Abrir catalogo.html
2. Adicionar produtos
3. Finalizar pedido
```

### 3. Verificar Logs:
```json
{
    "whatsapp_sent": true,
    "whatsapp_response": {
        "success": true,
        "message": "Mensagem WhatsApp enviada com sucesso"
    }
}
```

### 4. Verificar WhatsApp:
```
Número: 5512981443806
Mensagem deve chegar com:
- Dados do pedido
- Link para admin
```

---

## 📊 Fluxo de Envio

### Backend (order_processor.py):
```
1. Cliente finaliza pedido
2. Backend processa pedido
3. Backend envia para Evolution API
   - URL: https://chatbot-evolution-api.zv7gpn.easypanel.host
   - Instância: hakimfarma
   - Número: 5512981443806
4. Evolution API envia WhatsApp
```

### Frontend (catalogo.html):
```
1. Cliente finaliza pedido
2. Frontend envia para Evolution API (direto)
   - URL: https://evo.devsible.com.br
   - Instância: hakim
   - Número: 5512981443806
3. Evolution API envia WhatsApp
```

---

## ⚠️ Atenção: Duas URLs Diferentes!

### Backend usa:
```
https://chatbot-evolution-api.zv7gpn.easypanel.host
```

### Frontend usa:
```
https://evo.devsible.com.br
```

**São servidores diferentes!**

---

## 🎯 Recomendação

### Opção 1: Usar apenas Backend
```javascript
// No frontend, remover envio direto
// Deixar apenas o backend enviar
```

### Opção 2: Unificar URLs
```javascript
// Frontend usar mesma URL do backend
const EVOLUTION_API_URL = 'https://chatbot-evolution-api.zv7gpn.easypanel.host';
const INSTANCE_NAME = 'hakimfarma';
```

---

## 📝 Checklist

- [x] Número do vendedor correto: 5512981443806
- [x] Backend corrigido (order_processor.py)
- [x] .env configurado corretamente
- [x] Frontend com número correto
- [ ] Reiniciar backend
- [ ] Testar envio
- [ ] Verificar recebimento no WhatsApp
- [ ] Unificar instâncias (hakim vs hakimfarma)
- [ ] Unificar URLs (se necessário)

---

## 🔐 Credenciais

### Evolution API (Backend):
```
URL: https://chatbot-evolution-api.zv7gpn.easypanel.host
API Key: 429683C4C977415CAAFCCE10F7D57E11
Instância: hakimfarma
```

### Evolution API (Frontend):
```
URL: https://evo.devsible.com.br
API Key: B6D711FCDE4D-4183-9385-D5C9B6E1E119
Instância: hakim
```

**São credenciais diferentes!**

---

## 🚀 Próximos Passos

1. **Reiniciar Backend**
   ```bash
   docker-compose restart backend
   ```

2. **Fazer Pedido Teste**
   ```
   Usar catalogo.html
   ```

3. **Verificar Logs**
   ```
   Confirmar: whatsapp_sent: true
   ```

4. **Verificar WhatsApp**
   ```
   Número: 5512981443806
   ```

5. **Decidir sobre Instâncias**
   ```
   Usar "hakim" ou "hakimfarma"?
   Unificar URLs?
   ```

---

**Status**: ✅ Número Corrigido  
**Número Vendedor**: 5512981443806  
**Ação Necessária**: Reiniciar backend
