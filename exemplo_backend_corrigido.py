"""
Exemplo de código backend corrigido para envio de WhatsApp via Evolution API

Este código mostra como corrigir o problema do HTTP 201 sendo interpretado como erro.
"""

import requests
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppService:
    """Serviço para envio de mensagens via Evolution API"""
    
    def __init__(self):
        self.api_url = "https://evo.devsible.com.br"
        self.api_key = "B6D711FCDE4D-4183-9385-D5C9B6E1E119"
        self.instance_name = "hakim"
        self.seller_phone = "5512981443806"
    
    def send_order_notification(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia notificação de pedido para o vendedor
        
        Args:
            order_data: Dados do pedido
            
        Returns:
            Dict com resultado do envio
        """
        try:
            # Montar mensagem
            message = self._build_order_message(order_data)
            
            # Enviar mensagem
            result = self._send_message(self.seller_phone, message)
            
            if result["success"]:
                logger.info(f"✅ Mensagem enviada com sucesso para {self.seller_phone}")
            else:
                logger.error(f"❌ Falha ao enviar mensagem: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.exception(f"❌ Erro ao processar notificação: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao processar notificação"
            }
    
    def _send_message(self, phone: str, text: str) -> Dict[str, Any]:
        """
        Envia mensagem de texto via Evolution API
        
        Args:
            phone: Número do destinatário (com código do país)
            text: Texto da mensagem
            
        Returns:
            Dict com success, data/error e message
        """
        url = f"{self.api_url}/message/sendText/{self.instance_name}"
        
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        
        payload = {
            "number": phone,
            "text": text
        }
        
        try:
            logger.info(f"📤 Enviando mensagem para {phone}...")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            logger.info(f"📊 Status HTTP: {response.status_code}")
            
            # ✅ CORREÇÃO: Aceitar qualquer código 2xx (200-299)
            # Usar response.ok ao invés de verificar apenas 200
            if response.ok:  # Equivalente a: 200 <= status_code < 300
                data = response.json()
                
                logger.info(f"✅ Resposta da API: {data}")
                
                return {
                    "success": True,
                    "data": data,
                    "status_code": response.status_code,
                    "message": "Mensagem enviada com sucesso"
                }
            else:
                error_text = response.text
                
                logger.error(f"❌ Erro HTTP {response.status_code}: {error_text}")
                
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response": error_text,
                    "message": "Falha ao enviar mensagem WhatsApp"
                }
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout ao enviar mensagem")
            return {
                "success": False,
                "error": "Timeout",
                "message": "Timeout ao enviar mensagem WhatsApp"
            }
            
        except requests.exceptions.ConnectionError:
            logger.error("❌ Erro de conexão")
            return {
                "success": False,
                "error": "Connection Error",
                "message": "Erro de conexão com Evolution API"
            }
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"❌ Erro na requisição: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao enviar mensagem WhatsApp"
            }
    
    def _build_order_message(self, order_data: Dict[str, Any]) -> str:
        """
        Monta mensagem formatada do pedido
        
        Args:
            order_data: Dados do pedido
            
        Returns:
            Mensagem formatada
        """
        order = order_data.get("order", {})
        items = order_data.get("items", [])
        
        # Informações básicas
        order_id = order.get("order_number") or order.get("id", "N/A")
        customer_name = order.get("customer_name", "Cliente")
        customer_phone = order.get("customer_phone", "Não informado")
        customer_address = order.get("customer_address", "Não informado")
        payment_method = order.get("payment_method", "Não informado")
        total = order.get("total", 0)
        
        # Link para admin
        admin_link = f"https://ma.devsible.com.br/admin-pedidos.html?pedido={order_id}"
        
        # Montar lista de produtos
        products_list = []
        for idx, item in enumerate(items, 1):
            product_name = item.get("product_descricao", "Produto")
            quantity = item.get("quantity", 1)
            unit_price = item.get("unit_price", 0)
            
            products_list.append(
                f"{idx}. *{product_name}*\n   Qtd: {quantity} | R$ {unit_price:.2f}"
            )
        
        products_text = "\n\n".join(products_list) if products_list else "Nenhum produto"
        
        # Montar mensagem completa
        message = f"""🔔 *NOVO PEDIDO RECEBIDO!*

📋 *Pedido:* #{order_id}
⏰ *Horário:* {self._get_current_time()}

👤 *CLIENTE*
Nome: {customer_name}
📱 Telefone: {customer_phone}
📍 Endereço: {customer_address}

🛒 *PRODUTOS*
{products_text}

💰 *TOTAL:* R$ {total:.2f}
💳 *Pagamento:* {payment_method}

🔗 *GERENCIAR PEDIDO:*
{admin_link}

✅ Acesse o link acima para confirmar e gerenciar este pedido!"""
        
        return message
    
    def _get_current_time(self) -> str:
        """Retorna data/hora atual formatada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


# ============================================
# EXEMPLO DE USO EM ROTA FLASK
# ============================================

from flask import Flask, request, jsonify

app = Flask(__name__)
whatsapp_service = WhatsAppService()


@app.route("/api/process-order", methods=["POST"])
def process_order():
    """Processa pedido e envia notificação WhatsApp"""
    try:
        order_data = request.json
        
        # Processar pedido (salvar no banco, etc)
        # ... seu código aqui ...
        
        # Enviar notificação WhatsApp
        whatsapp_result = whatsapp_service.send_order_notification(order_data)
        
        return jsonify({
            "success": True,
            "order_id": order_data.get("order", {}).get("id"),
            "message": "Pedido processado com sucesso",
            "whatsapp_sent": whatsapp_result["success"],  # ✅ Agora será True!
            "whatsapp_response": whatsapp_result
        }), 200
        
    except Exception as e:
        logger.exception(f"Erro ao processar pedido: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Erro ao processar pedido"
        }), 500


# ============================================
# EXEMPLO DE USO EM ROTA FASTAPI
# ============================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app_fastapi = FastAPI()
whatsapp_service = WhatsAppService()


class OrderRequest(BaseModel):
    order: dict
    items: list


@app_fastapi.post("/api/process-order")
async def process_order_fastapi(order_request: OrderRequest):
    """Processa pedido e envia notificação WhatsApp"""
    try:
        order_data = order_request.dict()
        
        # Processar pedido (salvar no banco, etc)
        # ... seu código aqui ...
        
        # Enviar notificação WhatsApp
        whatsapp_result = whatsapp_service.send_order_notification(order_data)
        
        return {
            "success": True,
            "order_id": order_data.get("order", {}).get("id"),
            "message": "Pedido processado com sucesso",
            "whatsapp_sent": whatsapp_result["success"],  # ✅ Agora será True!
            "whatsapp_response": whatsapp_result
        }
        
    except Exception as e:
        logger.exception(f"Erro ao processar pedido: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TESTES
# ============================================

def test_send_message():
    """Teste simples de envio de mensagem"""
    service = WhatsAppService()
    
    result = service._send_message(
        phone="5512981443806",
        text="🔔 Teste de mensagem!"
    )
    
    print(f"\n{'='*50}")
    print(f"Resultado do teste:")
    print(f"{'='*50}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Data: {result.get('data')}")
    else:
        print(f"Error: {result.get('error')}")
    print(f"{'='*50}\n")
    
    return result


if __name__ == "__main__":
    # Executar teste
    print("🧪 Testando envio de mensagem...")
    test_send_message()
