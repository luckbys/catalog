import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
from pydantic import BaseModel, Field
from urllib.parse import quote

# -------------------- Config --------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "hakin t")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "5512976021836")

# -------------------- Models --------------------
class Cliente(BaseModel):
    nome: str
    telefone: str

class Entrega(BaseModel):
    endereco: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str
    complemento: Optional[str] = ""

class Pagamento(BaseModel):
    forma_pagamento: str
    valor_total: float

class Produto(BaseModel):
    nome: str
    codigo: Optional[str] = ""
    preco_unitario: float
    quantidade: int
    subtotal: float

class OrderPayload(BaseModel):
    cliente: Cliente
    entrega: Entrega
    pagamento: Pagamento
    produtos: List[Produto]

# -------------------- Order Processor --------------------
class OrderProcessor:
    def __init__(self):
        print(f"[ORDER PROCESSOR] Inicializando com SUPABASE_URL: {SUPABASE_URL[:50]}..." if SUPABASE_URL else "[ORDER PROCESSOR] SUPABASE_URL não configurada")
        print(f"[ORDER PROCESSOR] SUPABASE_KEY configurada: {'Sim' if SUPABASE_KEY else 'Não'}")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            error_msg = "SUPABASE_URL e SUPABASE_KEY devem ser configurados"
            print(f"[ORDER PROCESSOR] ERRO: {error_msg}")
            raise ValueError(error_msg)
        
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("[ORDER PROCESSOR] Cliente Supabase criado com sucesso")
        except Exception as e:
            print(f"[ORDER PROCESSOR] ERRO ao criar cliente Supabase: {e}")
            raise
    
    def process_order(self, payload: OrderPayload) -> Dict[str, Any]:
        """
        Processa um pedido completo seguindo o fluxo do n8n:
        1. Prepara dados do pedido
        2. Cria pedido no Supabase
        3. Cria itens do pedido
        4. Formata mensagem
        5. Envia mensagem WhatsApp
        """
        try:
            # 1. Preparar dados do pedido
            order_data = self._prepare_order_data(payload)
            
            # 2. Criar pedido no Supabase
            order_result = self._create_order(order_data)
            order_id = order_result['id']
            
            # 3. Criar itens do pedido
            order_items = self._create_order_items(order_id, payload.produtos)
            
            # 4. Formatar mensagem
            message = self._format_message(order_result, order_items)
            
            # 5. Enviar mensagem WhatsApp
            whatsapp_result = self._send_whatsapp_message(message)
            
            return {
                "success": True,
                "order_id": order_id,
                "message": "Pedido processado com sucesso",
                "whatsapp_sent": whatsapp_result.get("success", False),
                "data": {
                    "order": order_result,
                    "items": order_items,
                    "whatsapp_response": whatsapp_result
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao processar pedido"
            }
    
    def _prepare_order_data(self, payload: OrderPayload) -> Dict[str, Any]:
        """Prepara os dados do pedido (equivalente ao 'Edit Fields - Preparar Pedido')"""
        customer_address = (
            f"{payload.entrega.endereco}, Nº {payload.entrega.numero} - "
            f"{payload.entrega.bairro} - {payload.entrega.cidade}/{payload.entrega.estado} - "
            f"CEP {payload.entrega.cep}"
        )
        
        if payload.entrega.complemento:
            customer_address += f" - {payload.entrega.complemento}"
        
        # Mapear formas de pagamento para valores aceitos pela constraint da tabela `orders`
        # Valores válidos: 'cash', 'credit_card', 'debit_card', 'pix', 'bank_transfer'
        pm_upper = payload.pagamento.forma_pagamento.upper()
        payment_method_map = {
            "PIX": "pix",
            "DINHEIRO": "cash",
            "CARTAO": "credit_card",        # fallback genérico para "cartão"
            "CARTÃO": "credit_card",
            "CARTAO_CREDITO": "credit_card",
            "CARTÃO_CREDITO": "credit_card",
            "CARTAO_DEBITO": "debit_card",
            "CARTÃO_DEBITO": "debit_card",
            "TRANSFERENCIA": "bank_transfer",
            "TRANSFERÊNCIA": "bank_transfer",
            "BANK_TRANSFER": "bank_transfer",
        }
        payment_method = payment_method_map.get(pm_upper, "cash")

        # Gerar um número de pedido único (conforme constraint NOT NULL UNIQUE)
        # Formato: ORD-YYYYMMDD-HHMMSS-XXXX (XXXX = sufixo aleatório)
        dt = datetime.utcnow()
        ts = dt.strftime("%Y%m%d-%H%M%S")
        import random
        suffix = f"{random.randint(0, 9999):04d}"
        order_number = f"ORD-{ts}-{suffix}"
        
        return {
            "order_number": order_number,
            "customer_name": payload.cliente.nome,
            "customer_phone": payload.cliente.telefone or "",
            "customer_address": customer_address,
            "payment_method": payment_method,
            "subtotal": payload.pagamento.valor_total,
            "total": payload.pagamento.valor_total,
            "status": "pending",
            "payment_status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria o pedido no Supabase (equivalente ao 'Criar Pedido no Supabase')"""
        try:
            print(f"[ORDER PROCESSOR] Criando pedido no Supabase com dados: {order_data}")
            result = self.supabase.table("orders").insert(order_data).execute()
            print(f"[ORDER PROCESSOR] Resultado da criação do pedido: {result}")
            
            if result.data:
                print(f"[ORDER PROCESSOR] Pedido criado com sucesso: ID {result.data[0].get('id')}")
                return result.data[0]
            else:
                # Tentar extrair detalhes do erro do cliente Supabase
                error_detail = None
                try:
                    error_detail = getattr(result, "error", None)
                except Exception:
                    error_detail = None
                if error_detail:
                    error_msg = f"Falha ao criar pedido no Supabase: {error_detail}"
                else:
                    error_msg = "Falha ao criar pedido no Supabase - sem dados retornados"
                print(f"[ORDER PROCESSOR] ERRO: {error_msg}")
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Erro ao criar pedido: {str(e)}"
            print(f"[ORDER PROCESSOR] ERRO: {error_msg}")
            raise Exception(error_msg)
    
    def _create_order_items(self, order_id: int, produtos: List[Produto]) -> List[Dict[str, Any]]:
        """Cria os itens do pedido (equivalente ao 'Separar Produtos' + 'Edit Fields - Preparar Itens' + 'Criar Itens do Pedido')"""
        order_items = []
        print(f"[ORDER PROCESSOR] Criando {len(produtos)} itens para o pedido {order_id}")
        
        for i, produto in enumerate(produtos):
            # Usar um product_id padrão (1) ou gerar um baseado no código do produto
            # Como a tabela products não existe, vamos usar uma abordagem simplificada
            product_id = hash(produto.codigo or produto.nome) % 1000000 if produto.codigo else 1
            
            item_data = {
                "order_id": order_id,
                "product_id": product_id,
                "product_descricao": produto.nome,
                "product_codigo": produto.codigo or "",
                "unit_price": produto.preco_unitario,
                "quantity": produto.quantidade,
                "subtotal": produto.subtotal
            }
            
            try:
                print(f"[ORDER PROCESSOR] Criando item {i+1}/{len(produtos)}: {produto.nome}")
                result = self.supabase.table("order_items").insert(item_data).execute()
                print(f"[ORDER PROCESSOR] Resultado da criação do item: {result}")
                
                if result.data:
                    order_items.append(result.data[0])
                    print(f"[ORDER PROCESSOR] Item criado com sucesso: {produto.nome}")
                else:
                    # Tentar extrair detalhes do erro do cliente Supabase
                    error_detail = None
                    try:
                        error_detail = getattr(result, "error", None)
                    except Exception:
                        error_detail = None
                    if error_detail:
                        error_msg = f"Falha ao criar item do pedido {produto.nome}: {error_detail}"
                    else:
                        error_msg = f"Falha ao criar item do pedido: {produto.nome} - sem dados retornados"
                    print(f"[ORDER PROCESSOR] ERRO: {error_msg}")
                    raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Erro ao criar item do pedido {produto.nome}: {str(e)}"
                print(f"[ORDER PROCESSOR] ERRO: {error_msg}")
                raise Exception(error_msg)
        
        print(f"[ORDER PROCESSOR] Todos os {len(order_items)} itens criados com sucesso")
        return order_items
    
    def _format_message(self, order: Dict[str, Any], items: List[Dict[str, Any]]) -> str:
        """Formata a mensagem (equivalente ao 'Formatar Mensagem')"""
        produtos_text = "\n".join([
            f"- {item['product_descricao']} (Qtd: {item['quantity']}) - R$ {item['subtotal']:.2f}"
            for item in items
        ])
        
        message = f"""**Informações do Pedido**

* **Cliente:** {order['customer_name']}
* **Telefone:** {order['customer_phone']}
* **Endereço de Entrega:** {order['customer_address']}
* **Forma de Pagamento:** {order['payment_method']}

**Produtos Pedidos:**

{produtos_text}

**Valor Total:** R$ {order['total']:.2f}

**Número do Pedido:** #{order['id']}

Pedido registrado com sucesso! ✅"""
        
        return message
    
    def _send_whatsapp_message(self, message: str) -> Dict[str, Any]:
        """Envia mensagem WhatsApp (equivalente ao 'Enviar Mensagem WhatsApp')"""
        if not EVOLUTION_API_URL or not EVOLUTION_API_KEY:
            return {
                "success": False,
                "error": "Evolution API não configurada",
                "message": "Configurações do WhatsApp não encontradas"
            }
        
        try:
            headers = {
                "Content-Type": "application/json",
                "apikey": EVOLUTION_API_KEY
            }
            
            payload = {
                "number": WHATSAPP_PHONE,
                "text": message
            }
            
            instance_segment = quote(EVOLUTION_INSTANCE_NAME or "", safe="")
            url = f"{EVOLUTION_API_URL}/message/sendText/{instance_segment}"
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "response": response.json(),
                    "message": "Mensagem WhatsApp enviada com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text,
                    "message": "Falha ao enviar mensagem WhatsApp"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Timeout",
                "message": "Timeout ao enviar mensagem WhatsApp"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao enviar mensagem WhatsApp"
            }

# -------------------- Singleton Instance --------------------
order_processor = OrderProcessor()