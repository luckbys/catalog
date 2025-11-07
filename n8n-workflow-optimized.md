# Workflow N8N Otimizado - Farmácia HAKIM

## 📋 Análise do Sistema Atual

### Backend Endpoints Disponíveis:
- `POST /api/process-order` - Processa pedidos completos
- `POST /api/produtos/criar-sessao` - Cria sessão de catálogo
- `POST /api/produtos/{sessao_id}/selecionar` - Seleciona produtos
- `GET /api/produtos` - Lista produtos do Supabase
- `GET /api/orders` - Lista pedidos
- `PUT /api/orders/{order_id}/status` - Atualiza status do pedido
- `PUT /api/orders/{order_id}/delivery-status` - Atualiza status de entrega

### Fluxo Atual do Sistema:
1. Cliente envia mensagem via WhatsApp
2. AI Agent busca produtos no Supabase
3. Sistema cria sessão com produtos
4. Cliente seleciona produtos e confirma dados
5. Pedido é criado no Supabase via `order_processor`
6. Notificações são enviadas via WhatsApp (cliente + vendedor)
7. Admin gerencia pedidos via `admin-pedidos.html`
8. Entregador recebe link via `entregador.html`

---

## 🤖 SYSTEM PROMPT OTIMIZADO

```
Você é o Atendente Virtual da Farmácia HAKIM.

=== IMPORTANTE: FORMATO DE RESPOSTA COM PRODUTOS ===

QUANDO O CLIENTE PERGUNTAR SOBRE PRODUTOS:
1. Use a tool 'Supabase Tool Produtos' para buscar no banco de dados
2. SEMPRE responda EXATAMENTE neste formato (SEM usar ```json ou ```)

MENSAGEM: Encontrei X produtos! Vou enviar a lista para você escolher. 📋
PRODUTOS_JSON: [cole aqui o array JSON COMPLETO da tool]

EXEMPLO REAL DE RESPOSTA:
MENSAGEM: Encontrei 3 produtos de Dipirona! Vou enviar a lista para você escolher. 📋
PRODUTOS_JSON: [{"id":1,"descricao":"DIPIRONA SODICA","apresentacao":"500MG","laboratorio":"EMS","preco":8.50,"preco_original":10.00,"percentual_desconto":15,"estoque":50}]

REGRAS CRÍTICAS PARA PRODUTOS:
- NUNCA use ```json ou ``` ou qualquer markdown
- NÃO quebre linhas no JSON
- COLE o array JSON EXATAMENTE como a tool retornou
- Use APENAS o formato: MENSAGEM: texto\nPRODUTOS_JSON: [array]
- Sempre mencione quantos produtos foram encontrados
- Se não encontrar produtos, informe educadamente e sugira alternativas

=== FLUXO DE ATENDIMENTO COMPLETO ===

1. SAUDAÇÃO E BUSCA:
   - Cumprimente o cliente pelo nome (se disponível)
   - Pergunte o que ele procura
   - Use a tool para buscar produtos

2. APÓS O CLIENTE ESCOLHER O PRODUTO:
   - Confirme o produto escolhido
   - Pergunte a quantidade desejada
   - Mostre o valor total (quantidade × preço)

3. TIPO DE ENTREGA:
   - Pergunte: "Será para entrega ou retirada na loja?"
   - Se ENTREGA, solicite:
     * Endereço completo (Rua, Número, Bairro)
     * Cidade e Estado
     * CEP
     * Complemento (opcional)
     * Ponto de referência (opcional)
   - Se RETIRADA, confirme o endereço da loja

4. FORMA DE PAGAMENTO:
   - Pergunte: "Como prefere pagar?"
   - Opções disponíveis:
     * PIX (instantâneo)
     * Dinheiro (se sim, pergunte se precisa de troco e quanto)
     * Cartão de Crédito
     * Cartão de Débito
   - Confirme a forma escolhida

5. OBSERVAÇÕES:
   - Pergunte: "Alguma observação adicional sobre o pedido?"
   - Exemplos: "Entregar com o porteiro", "Ligar ao chegar", etc.

6. CONFIRMAÇÃO FINAL:
   - Mostre um RESUMO COMPLETO do pedido:
     * Produtos e quantidades
     * Valor total
     * Tipo de entrega (endereço completo ou retirada)
     * Forma de pagamento
     * Observações (se houver)
   - Pergunte: "Está tudo correto? Posso confirmar o pedido?"

7. FINALIZAÇÃO COM A TOOL:
   Quando o cliente confirmar, use a tool 'criar_pedido' com TODOS os dados:
   ```json
   {
     "cliente_nome": "Nome do Cliente",
     "cliente_telefone": "5512999999999",
     "produtos": [
       {
         "nome": "DIPIRONA SODICA 500MG",
         "codigo": "12345",
         "quantidade": 2,
         "preco_unitario": 8.50,
         "subtotal": 17.00
       }
     ],
     "entrega": {
       "endereco": "Rua das Flores",
       "numero": "123",
       "bairro": "Centro",
       "cidade": "São José dos Campos",
       "estado": "SP",
       "cep": "12345-678",
       "complemento": "Apto 45"
     },
     "pagamento": {
       "forma_pagamento": "PIX",
       "valor_total": 17.00
     }
   }
   ```

8. APÓS CRIAR O PEDIDO:
   - Confirme o número do pedido
   - Informe o tempo estimado de entrega (45-60 minutos)
   - Agradeça e se coloque à disposição

=== REGRAS GERAIS ===

✅ SEMPRE:
- Seja cordial, profissional e empático
- Use emojis para deixar a conversa mais amigável 😊 💊 🚚
- Confirme TODOS os dados antes de finalizar
- Mostre valores formatados (R$ 10,50)
- Mantenha o contexto da conversa

❌ NUNCA:
- Finalize pedido sem confirmação explícita do cliente
- Invente informações sobre produtos ou preços
- Pule etapas do fluxo de atendimento
- Use linguagem técnica ou formal demais

🔄 SE O CLIENTE QUISER ALTERAR:
- Seja flexível e permita alterações
- Confirme as mudanças
- Recalcule valores se necessário
- Mostre o novo resumo

⚠️ TRATAMENTO DE ERROS:
- Se não encontrar produto, sugira alternativas similares
- Se houver dúvida, peça esclarecimento
- Se o cliente desistir, agradeça educadamente
- Em caso de erro técnico, peça desculpas e informe que um atendente entrará em contato

=== EXEMPLOS DE INTERAÇÃO ===

**Exemplo 1 - Fluxo Completo:**
```
Cliente: Oi, preciso de dipirona
Bot: Olá! 👋 Vou buscar dipirona para você...
Bot: Encontrei 3 produtos! Vou enviar a lista para você escolher. 📋
[Sistema envia catálogo]
Cliente: Quero o primeiro
Bot: Perfeito! DIPIRONA SODICA 500MG - R$ 8,50. Quantas unidades você precisa?
Cliente: 2 caixas
Bot: Ótimo! 2 unidades = R$ 17,00. Será para entrega ou retirada na loja?
Cliente: Entrega
Bot: Qual o endereço completo para entrega? (Rua, Número, Bairro, Cidade, Estado, CEP)
Cliente: Rua das Flores, 123, Centro, São José dos Campos, SP, 12345-678
Bot: Perfeito! Como prefere pagar? (PIX, Dinheiro, Cartão de Crédito ou Débito)
Cliente: PIX
Bot: Alguma observação sobre o pedido?
Cliente: Não
Bot: Vou confirmar seu pedido:

📦 RESUMO DO PEDIDO
• 2x DIPIRONA SODICA 500MG = R$ 17,00
💰 Total: R$ 17,00
📍 Entrega: Rua das Flores, 123, Centro, São José dos Campos/SP
💳 Pagamento: PIX

Está tudo correto? Posso confirmar?
Cliente: Sim
Bot: Pedido #1234 confirmado! ✅
Previsão de entrega: 45-60 minutos
Você receberá um link para acompanhar o status.
Obrigado pela preferência! 😊
```

**Exemplo 2 - Produto Não Encontrado:**
```
Cliente: Tem rivotril?
Bot: Deixe-me buscar rivotril para você... 🔍
Bot: No momento não temos rivotril em estoque. 😔
Posso sugerir alternativas para ansiedade/insônia? Ou prefere que eu busque outro medicamento?
```

=== INFORMAÇÕES DA FARMÁCIA ===

**Farmácia HAKIM**
- Horário: Segunda a Sábado, 8h às 22h
- Tempo de entrega: 45-60 minutos
- Área de entrega: São José dos Campos e região
- Formas de pagamento: PIX, Dinheiro, Cartão (Crédito/Débito)
- Retirada na loja: Disponível no mesmo horário

**Políticas:**
- Medicamentos controlados exigem receita
- Entrega grátis acima de R$ 50,00
- Troco disponível para pagamento em dinheiro
- Pedidos podem ser cancelados antes do envio
```

---

## 🔧 AJUSTES RECOMENDADOS NO WORKFLOW N8N

### 1. **Nó "Supabase Tool Produtos"**
```javascript
// Melhorar a busca para ser mais flexível
{
  "operation": "getAll",
  "tableId": "produtos",
  "returnAll": true,
  "filters": {
    "conditions": [
      {
        "keyName": "descricao",
        "condition": "ilike",
        "keyValue": "={{ '%' + $fromAI('search_term', 'termo de busca do medicamento', 'string') + '%' }}"
      }
    ]
  },
  "options": {
    "select": "id,descricao,apresentacao,laboratorio,preco,preco_original,percentual_desconto,valor_desconto,estoque,imagem_url,categoria"
  }
}
```

### 2. **Nó "Processar Resposta"**
Melhorar o parsing do JSON para lidar com diferentes formatos:

```javascript
const output = $input.item.json.output;
const editFieldsData = $('Edit Fields6').first().json;

console.log('🔍 PROCESSANDO OUTPUT');

let produtos = [];
let mensagem = output;
let temProdutos = false;

if (output && typeof output === 'string' && output.includes('PRODUTOS_JSON:')) {
  try {
    const parts = output.split('PRODUTOS_JSON:');
    mensagem = parts[0].replace('MENSAGEM:', '').trim();
    
    let jsonPart = parts[1]
      .trim()
      .replace(/```json/g, '')
      .replace(/```/g, '')
      .replace(/\n/g, '')
      .replace(/\r/g, '')
      .replace(/\t/g, '')
      .trim();
    
    // Encontrar o final do array JSON
    const jsonEndIndex = jsonPart.lastIndexOf(']');
    if (jsonEndIndex !== -1) {
      jsonPart = jsonPart.substring(0, jsonEndIndex + 1);
    }
    
    let produtosRaw = JSON.parse(jsonPart);
    
    // Normalizar estrutura
    if (Array.isArray(produtosRaw)) {
      produtos = produtosRaw;
    } else if (produtosRaw.response && Array.isArray(produtosRaw.response)) {
      produtos = produtosRaw.response;
    } else if (produtosRaw.data && Array.isArray(produtosRaw.data)) {
      produtos = produtosRaw.data;
    } else {
      produtos = [produtosRaw];
    }
    
    // Filtrar e validar produtos
    produtos = produtos
      .filter(p => p && p.descricao)
      .map(p => ({
        id: p.id,
        descricao: p.descricao,
        apresentacao: p.apresentacao || '',
        laboratorio: p.laboratorio || '',
        preco: parseFloat(p.preco) || 0,
        preco_original: p.preco_original ? parseFloat(p.preco_original) : null,
        percentual_desconto: p.percentual_desconto ? parseFloat(p.percentual_desconto) : null,
        valor_desconto: p.valor_desconto ? parseFloat(p.valor_desconto) : null,
        estoque: Math.max(0, parseInt(p.estoque) || 0),
        imagem_url: p.imagem_url || '',
        categoria: p.categoria || 'Medicamentos'
      }));
    
    temProdutos = produtos.length > 0;
    
    console.log(`✅ ${produtos.length} produtos processados com sucesso`);
    
  } catch (error) {
    console.log('❌ Erro ao processar JSON:', error.message);
    produtos = [];
    temProdutos = false;
  }
}

return {
  json: {
    tem_produtos: temProdutos,
    mensagem_cliente: mensagem,
    produtos: produtos,
    quantidade_produtos: produtos.length,
    cliente_telefone: editFieldsData.from || '',
    cliente_nome: editFieldsData.nome || 'Cliente',
    timestamp: new Date().toISOString(),
    sessao_id: editFieldsData.from || ''
  }
};
```

### 3. **Nó "Tool Criar Pedido"**
Atualizar o schema para refletir a estrutura correta do backend:

```json
{
  "cliente": {
    "nome": "string",
    "telefone": "string"
  },
  "entrega": {
    "endereco": "string",
    "numero": "string",
    "bairro": "string",
    "cidade": "string",
    "estado": "string",
    "cep": "string",
    "complemento": "string (opcional)"
  },
  "pagamento": {
    "forma_pagamento": "PIX | DINHEIRO | CARTAO_CREDITO | CARTAO_DEBITO",
    "valor_total": "number"
  },
  "produtos": [
    {
      "nome": "string",
      "codigo": "string (opcional)",
      "preco_unitario": "number",
      "quantidade": "number",
      "subtotal": "number"
    }
  ]
}
```

### 4. **Adicionar Nó de Validação**
Criar um nó antes de "Tool Criar Pedido" para validar dados:

```javascript
const input = $input.first().json;

// Validar campos obrigatórios
const erros = [];

if (!input.cliente?.nome) erros.push("Nome do cliente não informado");
if (!input.cliente?.telefone) erros.push("Telefone não informado");
if (!input.produtos || input.produtos.length === 0) erros.push("Nenhum produto selecionado");
if (!input.pagamento?.forma_pagamento) erros.push("Forma de pagamento não informada");
if (!input.pagamento?.valor_total || input.pagamento.valor_total <= 0) erros.push("Valor total inválido");

// Validar endereço se for entrega
const tipoEntrega = input.tipo_entrega || 'entrega';
if (tipoEntrega === 'entrega') {
  if (!input.entrega?.endereco) erros.push("Endereço não informado");
  if (!input.entrega?.numero) erros.push("Número não informado");
  if (!input.entrega?.bairro) erros.push("Bairro não informado");
  if (!input.entrega?.cidade) erros.push("Cidade não informada");
  if (!input.entrega?.estado) erros.push("Estado não informado");
  if (!input.entrega?.cep) erros.push("CEP não informado");
}

if (erros.length > 0) {
  return {
    json: {
      valido: false,
      erros: erros,
      mensagem: "Dados incompletos: " + erros.join(", ")
    }
  };
}

// Normalizar telefone
let telefone = input.cliente.telefone.replace(/\D/g, '');
if (telefone.length > 20) telefone = telefone.substring(0, 20);

// Normalizar forma de pagamento
const pagamentoMap = {
  "pix": "PIX",
  "dinheiro": "DINHEIRO",
  "cartao": "CARTAO_CREDITO",
  "cartão": "CARTAO_CREDITO",
  "credito": "CARTAO_CREDITO",
  "crédito": "CARTAO_CREDITO",
  "debito": "CARTAO_DEBITO",
  "débito": "CARTAO_DEBITO"
};

const formaPagamento = pagamentoMap[input.pagamento.forma_pagamento.toLowerCase()] || "DINHEIRO";

return {
  json: {
    valido: true,
    dados_validados: {
      cliente: {
        nome: input.cliente.nome,
        telefone: telefone
      },
      entrega: input.entrega || {},
      pagamento: {
        forma_pagamento: formaPagamento,
        valor_total: parseFloat(input.pagamento.valor_total)
      },
      produtos: input.produtos.map(p => ({
        nome: p.nome,
        codigo: p.codigo || '',
        preco_unitario: parseFloat(p.preco_unitario),
        quantidade: parseInt(p.quantidade),
        subtotal: parseFloat(p.subtotal)
      }))
    }
  }
};
```

### 5. **Melhorar Tratamento de Erros**
Adicionar nó "Catch Error" após cada operação crítica:

```javascript
const erro = $input.first().json;

// Log detalhado do erro
console.error('❌ ERRO NO WORKFLOW:', {
  node: erro.node,
  message: erro.message,
  stack: erro.stack,
  timestamp: new Date().toISOString()
});

// Mensagem amigável para o cliente
const mensagemErro = `Desculpe, ocorreu um erro ao processar seu pedido. 😔

Nossa equipe foi notificada e entrará em contato em breve.

Por favor, tente novamente em alguns minutos ou entre em contato pelo telefone: (12) 98144-3806`;

return {
  json: {
    erro: true,
    mensagem_cliente: mensagemErro,
    detalhes_erro: erro.message
  }
};
```

---

## 📊 MÉTRICAS E MONITORAMENTO

### KPIs Recomendados:
1. **Taxa de Conversão**: Mensagens → Pedidos finalizados
2. **Tempo Médio de Atendimento**: Primeira mensagem → Pedido confirmado
3. **Taxa de Abandono**: Em qual etapa os clientes desistem
4. **Produtos Mais Buscados**: Quais medicamentos são mais procurados
5. **Horários de Pico**: Quando há mais atendimentos

### Logs Importantes:
```javascript
// Adicionar em pontos estratégicos do workflow
console.log('[METRICS]', {
  event: 'produto_buscado',
  termo: searchTerm,
  resultados: produtos.length,
  timestamp: new Date().toISOString()
});

console.log('[METRICS]', {
  event: 'pedido_criado',
  order_id: orderId,
  valor_total: valorTotal,
  forma_pagamento: formaPagamento,
  timestamp: new Date().toISOString()
});
```

---

## 🚀 PRÓXIMOS PASSOS

1. **Implementar o novo system prompt** no nó "AI Agent3"
2. **Atualizar os nós de processamento** conforme especificado
3. **Adicionar validações** antes de criar pedidos
4. **Implementar tratamento de erros** robusto
5. **Configurar logs e métricas** para monitoramento
6. **Testar fluxo completo** com diferentes cenários
7. **Documentar casos de uso** e respostas esperadas

---

## ⚠️ PONTOS DE ATENÇÃO

1. **Timeout do AI Agent**: Configurar timeout adequado (30-60s)
2. **Rate Limiting**: Implementar controle de taxa para evitar spam
3. **Validação de Receita**: Para medicamentos controlados
4. **Backup de Dados**: Garantir que pedidos não sejam perdidos
5. **Fallback Manual**: Opção de transferir para atendente humano
6. **Testes A/B**: Testar diferentes versões do prompt
7. **Feedback do Cliente**: Coletar avaliações pós-atendimento

---

**Última atualização**: 2025-11-07
**Versão**: 2.0
**Autor**: Kiro AI Assistant
