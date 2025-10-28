# Sistema de Processamento de Pedidos Independente

Este documento descreve o sistema de processamento de pedidos independente que substitui o workflow n8n, oferecendo maior controle, confiabilidade e facilidade de manutenção.

## 🎯 Objetivo

Criar um sistema autônomo que processa pedidos sem depender do n8n, mantendo todas as funcionalidades:
- ✅ Processamento de pedidos
- ✅ Integração com Supabase
- ✅ Envio de mensagens WhatsApp via Evolution API
- ✅ Formatação de mensagens
- ✅ Fallback para sistema n8n

## 🏗️ Arquitetura

### Componentes Principais

1. **OrderProcessor** (`backend/order_processor.py`)
   - Classe principal que replica o workflow n8n
   - Processa pedidos de forma determinística
   - Integra com Supabase e Evolution API

2. **API Endpoint** (`backend/app.py`)
   - Endpoint `/api/process-order` para receber pedidos
   - Validação de dados usando Pydantic
   - Tratamento de erros robusto

3. **Frontend Atualizado** (`catalogo.html`)
   - Tenta primeiro o sistema independente
   - Fallback automático para n8n em caso de falha
   - Feedback melhorado para o usuário

## 🔄 Fluxo de Processamento

```
Frontend → /api/process-order → OrderProcessor → Supabase → WhatsApp
    ↓ (fallback em caso de erro)
Frontend → n8n webhook → n8n workflow → Supabase → WhatsApp
```

### Etapas Detalhadas

1. **Preparação dos Dados**
   - Extrai informações do cliente, entrega, pagamento e produtos
   - Formata endereço completo
   - Define status padrão do pedido

2. **Criação do Pedido**
   - Insere registro na tabela `orders` do Supabase
   - Retorna ID do pedido criado

3. **Criação dos Itens**
   - Para cada produto, cria registro na tabela `order_items`
   - Vincula ao pedido através do `order_id`

4. **Formatação da Mensagem**
   - Gera mensagem formatada com detalhes do pedido
   - Inclui informações do cliente, produtos e total

5. **Envio WhatsApp**
   - Envia mensagem via Evolution API
   - Retorna status do envio

## 📋 Modelos de Dados

### Payload de Entrada
```json
{
  "cliente": {
    "nome": "João Silva",
    "telefone": "11999999999"
  },
  "entrega": {
    "endereco": "Rua das Flores",
    "numero": "123",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "01234-567",
    "complemento": "Apto 45"
  },
  "pagamento": {
    "forma_pagamento": "PIX",
    "valor_total": 150.00
  },
  "produtos": [
    {
      "nome": "Produto A",
      "codigo": "PROD001",
      "preco_unitario": 50.00,
      "quantidade": 2,
      "subtotal": 100.00
    }
  ]
}
```

### Resposta de Sucesso
```json
{
  "status": "success",
  "message": "Pedido processado com sucesso",
  "order_id": 123,
  "whatsapp_sent": true,
  "data": {
    "order": { /* dados do pedido */ },
    "items": [ /* itens do pedido */ ],
    "whatsapp_response": { /* resposta do WhatsApp */ }
  }
}
```

## ⚙️ Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://your-evolution-api.com
EVOLUTION_API_KEY=your-api-key
EVOLUTION_INSTANCE_NAME=your-instance
WHATSAPP_PHONE=5511999999999
```

### Dependências

```bash
pip install -r backend/requirements.txt
```

### Estrutura do Banco (Supabase)

#### Tabela `orders`
```sql
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  customer_name VARCHAR NOT NULL,
  customer_phone VARCHAR,
  customer_address TEXT NOT NULL,
  payment_method VARCHAR NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  status VARCHAR DEFAULT 'pending',
  payment_status VARCHAR DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### Tabela `order_items`
```sql
CREATE TABLE order_items (
  id SERIAL PRIMARY KEY,
  order_id INTEGER REFERENCES orders(id),
  product_descricao VARCHAR NOT NULL,
  product_codigo VARCHAR,
  unit_price DECIMAL(10,2) NOT NULL,
  quantity INTEGER NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Execução

### Desenvolvimento
```bash
cd backend
python app.py
```

### Produção
```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000
```

## 🧪 Testes

### Teste Manual
1. Acesse o catálogo: `http://localhost:3000/catalogo.html`
2. Adicione produtos ao carrinho
3. Finalize o pedido
4. Verifique os logs do backend
5. Confirme criação no Supabase
6. Verifique mensagem WhatsApp

### Teste via API
```bash
curl -X POST http://localhost:8000/api/process-order \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

## 🔍 Monitoramento

### Logs
- Frontend: Console do navegador
- Backend: Logs do FastAPI
- Supabase: Dashboard do Supabase
- WhatsApp: Logs da Evolution API

### Métricas
- Taxa de sucesso de pedidos
- Tempo de processamento
- Taxa de envio WhatsApp
- Erros de fallback para n8n

## 🛠️ Manutenção

### Atualizações
1. Modifique `order_processor.py` para lógica de negócio
2. Atualize modelos Pydantic em `app.py` para validação
3. Ajuste frontend para novos campos

### Troubleshooting
- **Erro Supabase**: Verifique credenciais e estrutura das tabelas
- **Erro WhatsApp**: Confirme configuração Evolution API
- **Fallback ativo**: Sistema independente indisponível, usando n8n

## 📈 Vantagens vs n8n

| Aspecto | Sistema Independente | n8n |
|---------|---------------------|-----|
| **Controle** | ✅ Total | ❌ Limitado |
| **Debugging** | ✅ Fácil | ❌ Complexo |
| **Performance** | ✅ Otimizada | ⚠️ Dependente |
| **Manutenção** | ✅ Simples | ❌ Interface gráfica |
| **Escalabilidade** | ✅ Flexível | ⚠️ Limitada |
| **Dependências** | ✅ Mínimas | ❌ n8n + LLM |
| **Determinismo** | ✅ 100% | ❌ LLM variável |

## 🔄 Migração

O sistema foi projetado para migração gradual:
1. **Fase 1**: Sistema independente como primário, n8n como fallback ✅
2. **Fase 2**: Monitoramento e ajustes
3. **Fase 3**: Remoção completa do n8n (opcional)

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique logs do backend
2. Confirme configurações do `.env`
3. Teste conectividade com Supabase e Evolution API
4. Consulte documentação das APIs externas