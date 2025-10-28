{
  "nodes": [
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "customer_name",
              "name": "customer_name",
              "value": "={{ $json.body.cliente.nome }}",
              "type": "string"
            },
            {
              "id": "customer_phone",
              "name": "customer_phone",
              "value": "={{ $json.body.cliente.telefone || '' }}",
              "type": "string"
            },
            {
              "id": "customer_address",
              "name": "customer_address",
              "value": "={{ `${$json.body.entrega.endereco}, Nº ${$json.body.entrega.numero} - ${$json.body.entrega.bairro} - ${$json.body.entrega.cidade}/${$json.body.entrega.estado} - CEP ${$json.body.entrega.cep}${$json.body.entrega.complemento ? ' - ' + $json.body.entrega.complemento : ''}` }}",
              "type": "string"
            },
            {
              "id": "payment_method",
              "name": "payment_method",
              "value": "={{ $json.body.pagamento.forma_pagamento }}",
              "type": "string"
            },
            {
              "id": "subtotal",
              "name": "subtotal",
              "value": "={{ $json.body.pagamento.valor_total }}",
              "type": "number"
            },
            {
              "id": "total",
              "name": "total",
              "value": "={{ $json.body.pagamento.valor_total }}",
              "type": "number"
            },
            {
              "id": "status",
              "name": "status",
              "value": "pending",
              "type": "string"
            },
            {
              "id": "payment_status",
              "name": "payment_status",
              "value": "pending",
              "type": "string"
            },
            {
              "id": "produtos",
              "name": "produtos",
              "value": "={{ $json.body.produtos }}",
              "type": "object"
            }
          ]
        },
        "options": {}
      },
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [
        544,
        1440
      ],
      "id": "6d9d9fb2-b1d1-4a18-956f-d34870537414",
      "name": "Edit Fields - Preparar Pedido"
    },
    {
      "parameters": {
        "tableId": "orders",
        "dataToSend": "autoMapInputData"
      },
      "type": "n8n-nodes-base.supabase",
      "typeVersion": 1,
      "position": [
        832,
        1440
      ],
      "id": "10b29006-52f5-4bdb-b0b4-3e39c7b8b534",
      "name": "Criar Pedido no Supabase",
      "credentials": {
        "supabaseApi": {
          "id": "yIPm0m5T4MK8AkfA",
          "name": "Supabase account"
        }
      }
    },
    {
      "parameters": {
        "fieldToSplitOut": "produtos",
        "options": {}
      },
      "type": "n8n-nodes-base.splitOut",
      "typeVersion": 1,
      "position": [
        1120,
        1440
      ],
      "id": "dd216d93-55c2-4355-a2f7-359e4b48d072",
      "name": "Separar Produtos"
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "order_id",
              "name": "order_id",
              "value": "={{ $('Criar Pedido no Supabase').item.json.id }}",
              "type": "number"
            },
            {
              "id": "product_descricao",
              "name": "product_descricao",
              "value": "={{ $json.nome }}",
              "type": "string"
            },
            {
              "id": "product_codigo",
              "name": "product_codigo",
              "value": "={{ $json.codigo || '' }}",
              "type": "string"
            },
            {
              "id": "unit_price",
              "name": "unit_price",
              "value": "={{ $json.preco_unitario }}",
              "type": "number"
            },
            {
              "id": "quantity",
              "name": "quantity",
              "value": "={{ $json.quantidade }}",
              "type": "number"
            },
            {
              "id": "subtotal",
              "name": "subtotal",
              "value": "={{ $json.subtotal }}",
              "type": "number"
            }
          ]
        },
        "options": {}
      },
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [
        1344,
        1600
      ],
      "id": "8c6f6806-6d49-4548-957e-d3731836dcab",
      "name": "Edit Fields - Preparar Itens"
    },
    {
      "parameters": {
        "tableId": "order_items",
        "dataToSend": "autoMapInputData"
      },
      "type": "n8n-nodes-base.supabase",
      "typeVersion": 1,
      "position": [
        1600,
        1440
      ],
      "id": "2128958d-8343-4f0f-8bee-1a7c57264b57",
      "name": "Criar Itens do Pedido",
      "credentials": {
        "supabaseApi": {
          "id": "yIPm0m5T4MK8AkfA",
          "name": "Supabase account"
        }
      }
    },
    {
      "parameters": {
        "mode": "combine",
        "options": {}
      },
      "type": "n8n-nodes-base.merge",
      "typeVersion": 3,
      "position": [
        1840,
        1440
      ],
      "id": "993e31eb-82af-42b0-b037-24f9aa1e3acc",
      "name": "Merge - Combinar Dados"
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "=**Informações do Pedido**\n\n* **Cliente:** {{ $('Criar Pedido no Supabase').item.json.customer_name }}\n* **Telefone:** {{ $('Criar Pedido no Supabase').item.json.customer_phone }}\n* **Endereço de Entrega:** {{ $('Criar Pedido no Supabase').item.json.customer_address }}\n* **Forma de Pagamento:** {{ $('Criar Pedido no Supabase').item.json.payment_method }}\n\n**Produtos Pedidos:**\n\n{{ $('Criar Itens do Pedido').all().map(item => `- ${item.json.product_descricao} (Qtd: ${item.json.quantity}) - R$ ${item.json.subtotal.toFixed(2)}`).join('\\n') }}\n\n**Valor Total:** R$ {{ $('Criar Pedido no Supabase').item.json.total.toFixed(2) }}\n\n**Número do Pedido:** #{{ $('Criar Pedido no Supabase').item.json.id }}\n\nPedido registrado com sucesso! ✅",
        "batching": {}
      },
      "type": "@n8n/n8n-nodes-langchain.chainLlm",
      "typeVersion": 1.7,
      "position": [
        2080,
        1440
      ],
      "id": "253e8d22-3176-4550-8da0-b5e7344c73f3",
      "name": "Formatar Mensagem"
    },
    {
      "parameters": {
        "resource": "messages-api",
        "instanceName": "hakin t",
        "remoteJid": "5512976021836",
        "messageText": "={{ $json.text }}",
        "options_message": {}
      },
      "type": "n8n-nodes-evolution-api.evolutionApi",
      "typeVersion": 1,
      "position": [
        2416,
        1440
      ],
      "id": "b7f180e2-0813-4063-be68-a70cea81d673",
      "name": "Enviar Mensagem WhatsApp",
      "credentials": {
        "evolutionApi": {
          "id": "f4u8xEbHpc6JLVBT",
          "name": "Evolution account"
        }
      }
    },
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "env_pedido",
        "options": {}
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2.1,
      "position": [
        -64,
        1440
      ],
      "id": "0814c94a-9e05-4437-807c-781e3e084827",
      "name": "Webhook2",
      "webhookId": "ec9f1c82-11e4-422f-9fa7-f6d9ca0bccac"
    },
    {
      "parameters": {
        "text": "={{ $json.body.cliente.nome }},={{ $json.body.entrega.cep }}={{ $json.body.entrega.endereco }}={{ $json.body.entrega.numero }}={{ $json.body.entrega.bairro }}={{ $json.body.entrega.cidade }}={{ $json.body.pagamento.forma_pagamento }}={{ $json.body.pagamento.valor_total }}={{ $json.body.produtos[0].nome }}={{ $json.body.produtos[0].preco_unitario }}={{ $json.body.produtos[0].subtotal }}={{ $json.body.produtos[0].quantidade }}",
        "attributes": {
          "attributes": [
            {
              "name": "nome do cliente",
              "description": "nome do cliente"
            },
            {
              "name": "endereço de entrega",
              "description": "endereço de entrega completo"
            },
            {
              "name": "itens do pedido",
              "description": "lista de itens do pedido"
            },
            {
              "name": "valor de cada itens e o total e forma de pagamento",
              "description": "valor de cada itens e o total e forma de pagamento"
            }
          ]
        },
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.informationExtractor",
      "typeVersion": 1.2,
      "position": [
        192,
        1440
      ],
      "id": "ef61f4b4-3c7c-463f-aae0-7c43f1a5572a",
      "name": "Information Extractor1",
      "alwaysOutputData": false
    },
    {
      "parameters": {
        "model": "llama-3.3-70b-versatile",
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.lmChatGroq",
      "typeVersion": 1,
      "position": [
        192,
        1632
      ],
      "id": "21e83ef9-4725-40d9-aee0-293782b825c5",
      "name": "Groq Chat Model2",
      "credentials": {
        "groqApi": {
          "id": "uOnB6ZteUlE6fIFd",
          "name": "Groq account"
        }
      }
    },
    {
      "parameters": {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.lmChatGroq",
      "typeVersion": 1,
      "position": [
        2080,
        1616
      ],
      "id": "e604f62c-bb2c-401c-bc03-3afc19706807",
      "name": "Groq Chat Model3",
      "credentials": {
        "groqApi": {
          "id": "uOnB6ZteUlE6fIFd",
          "name": "Groq account"
        }
      }
    }
  ],
  "connections": {
    "Edit Fields - Preparar Pedido": {
      "main": [
        [
          {
            "node": "Criar Pedido no Supabase",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Criar Pedido no Supabase": {
      "main": [
        [
          {
            "node": "Separar Produtos",
            "type": "main",
            "index": 0
          },
          {
            "node": "Merge - Combinar Dados",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Separar Produtos": {
      "main": [
        [
          {
            "node": "Edit Fields - Preparar Itens",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Edit Fields - Preparar Itens": {
      "main": [
        [
          {
            "node": "Criar Itens do Pedido",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Criar Itens do Pedido": {
      "main": [
        [
          {
            "node": "Merge - Combinar Dados",
            "type": "main",
            "index": 1
          }
        ]
      ]
    },
    "Merge - Combinar Dados": {
      "main": [
        [
          {
            "node": "Formatar Mensagem",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Formatar Mensagem": {
      "main": [
        [
          {
            "node": "Enviar Mensagem WhatsApp",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Webhook2": {
      "main": [
        [
          {
            "node": "Edit Fields - Preparar Pedido",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Information Extractor1": {
      "main": [
        [
          {
            "node": "Edit Fields - Preparar Pedido",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Groq Chat Model2": {
      "ai_languageModel": [
        [
          {
            "node": "Information Extractor1",
            "type": "ai_languageModel",
            "index": 0
          }
        ]
      ]
    },
    "Groq Chat Model3": {
      "ai_languageModel": [
        [
          {
            "node": "Formatar Mensagem",
            "type": "ai_languageModel",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "77f30554d2102f542e00b67be9506d390e9827f42a3e24a5d0de8d5fb8d2944f"
  }
}