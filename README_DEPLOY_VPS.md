# 🚨 Correção: Sistema de Pedidos não funciona na VPS

## 🔍 Problema Identificado

O sistema de finalização de pedidos funciona no **localhost** mas **não funciona na VPS**. 

### Diagnóstico:
- ✅ **Localhost**: Endpoint `/api/process-order` responde corretamente
- ❌ **VPS**: Endpoint retorna `404 Not Found`
- ❌ **Backend não está rodando** ou não está configurado corretamente na VPS

## 🛠️ Solução

### 1. Variáveis de Ambiente Faltando

O sistema precisa das seguintes variáveis de ambiente na VPS:

```bash
# Supabase (OBRIGATÓRIO para salvar pedidos)
SUPABASE_URL=https://chatbot-supabase1.zv7gpn.easypanel.host
SUPABASE_KEY=sua_chave_supabase_aqui

# WhatsApp (OPCIONAL - sistema funciona sem)
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua_chave_evolution
EVOLUTION_INSTANCE_NAME=nome_da_instancia
WHATSAPP_PHONE=5512976021836
```

### 2. Configuração do Docker Atualizada

O arquivo `docker-compose.prod.yml` foi atualizado para incluir todas as variáveis necessárias.

### 3. Script de Deploy Criado

Execute o script `deploy-fix-order-system.sh` na VPS:

```bash
# 1. Configure as variáveis de ambiente
export SUPABASE_KEY="sua_chave_supabase"
export EVOLUTION_API_KEY="sua_chave_evolution"
export EVOLUTION_INSTANCE_NAME="nome_da_instancia"
export WHATSAPP_PHONE="5512976021836"

# 2. Execute o script de correção
chmod +x deploy-fix-order-system.sh
./deploy-fix-order-system.sh
```

## 🧪 Como Testar

### Teste Local (funciona):
```bash
python test_order_completion.py
```

### Teste VPS (deve funcionar após correção):
```bash
python test_vps_order.py
```

## 📋 Checklist de Correção

- [ ] **Configurar variáveis de ambiente na VPS**
- [ ] **Executar script de deploy atualizado**
- [ ] **Verificar se containers estão rodando**
- [ ] **Testar endpoint `/api/process-order`**
- [ ] **Testar finalização no frontend**

## 🔧 Comandos de Diagnóstico na VPS

```bash
# Verificar containers
docker-compose -f docker-compose.prod.yml ps

# Verificar logs do backend
docker-compose -f docker-compose.prod.yml logs backend

# Testar health
curl https://chatbot-catalog.zv7gpn.easypanel.host/health

# Testar endpoint de pedido
curl -X POST https://chatbot-catalog.zv7gpn.easypanel.host/api/process-order \
  -H "Content-Type: application/json" \
  -d '{"cliente":{"nome":"Teste"},"produtos":[]}'
```

## ⚠️ Notas Importantes

1. **SUPABASE_KEY é obrigatória** - sem ela o sistema não consegue salvar pedidos
2. **WhatsApp é opcional** - pedidos são salvos mesmo se WhatsApp falhar
3. **Backend deve estar rodando na porta 8000** dentro do container
4. **Nginx deve fazer proxy para o backend** na VPS

## 🎯 Resultado Esperado

Após a correção:
- ✅ Endpoint `/api/process-order` deve responder com status 200
- ✅ Pedidos devem ser salvos no Supabase
- ✅ Frontend deve finalizar pedidos sem erro
- ⚠️ WhatsApp pode falhar (mas não impede o pedido)