import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Numeric, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# -------------------- Config --------------------
DB_URL = os.getenv("DB_URL", "sqlite:///./backend_data.db")
CLIENT_BASE_URL = os.getenv("CLIENT_BASE_URL", "http://localhost:5500/catalogo.html")
SESSION_VALIDITY_HOURS = int(os.getenv("SESSION_VALIDITY_HOURS", "4"))
ALLOWED_ORIGINS = ["*"]  # Permite todas as origens - ajuste conforme necessidade de segurança

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# -------------------- Models --------------------
class Sessao(Base):
    __tablename__ = "sessoes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sessao_id = Column(String, unique=True, index=True, nullable=False)
    cliente_telefone = Column(String, nullable=False)
    cliente_nome = Column(String, nullable=False)
    status = Column(String, default="ativa", nullable=False)  # ativa, expirada, finalizada
    criado_em = Column(DateTime, default=datetime.utcnow)
    expira_em = Column(DateTime, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow)

    produtos = relationship("ProdutoSessao", back_populates="sessao", cascade="all, delete-orphan")

class ProdutoSessao(Base):
    __tablename__ = "produtos_sessao"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sessao_uuid = Column(String, ForeignKey("sessoes.id"), nullable=False)
    produto_id = Column(Integer, nullable=False)
    descricao = Column(String, nullable=False)
    preco = Column(Numeric(10, 2), nullable=False)
    estoque = Column(Integer, nullable=False)
    imagem_url = Column(String, nullable=True)
    categoria = Column(String, nullable=True)
    apresentacao = Column(String, nullable=True)

    sessao = relationship("Sessao", back_populates="produtos")

class SelecaoItem(Base):
    __tablename__ = "selecoes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    selecao_id = Column(String, index=True, nullable=False)
    sessao_uuid = Column(String, nullable=False)
    produto_id = Column(Integer, nullable=False)
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Numeric(10, 2), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    forma_pagamento = Column(String, nullable=True)  # Novo campo para forma de pagamento
    criado_em = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# -------------------- Schemas --------------------
class ProdutoIn(BaseModel):
    id: int
    descricao: str
    preco: Decimal
    estoque: int
    imagem_url: Optional[str] = None
    categoria: Optional[str] = None
    apresentacao: Optional[str] = None

class CriarSessaoPayload(BaseModel):
    cliente_telefone: str = Field(..., min_length=10, max_length=50)  # Aumentado para aceitar formato WhatsApp
    cliente_nome: str
    produtos: List[ProdutoIn]
    quantidade_produtos: int
    timestamp: str

class SelecionarItemIn(BaseModel):
    produto_id: int
    quantidade: int

class SelecionarPayload(BaseModel):
    produtos_selecionados: List[SelecionarItemIn]
    cliente_telefone: Optional[str] = None
    forma_pagamento: Optional[str] = None  # Novo campo para forma de pagamento

# -------------------- Utils --------------------
def gerar_sessao_id(length: int = 10) -> str:
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Rate limiting simples em memória (100 req/h por IP)
_rate_limiter: Dict[str, Dict[str, any]] = {}

def rate_limit_dep(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = datetime.utcnow()
    window = _rate_limiter.get(ip)
    if not window or (now - window["start"]).total_seconds() > 3600:
        _rate_limiter[ip] = {"start": now, "count": 1}
    else:
        if window["count"] >= 100:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        window["count"] += 1

# -------------------- App --------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos (ajustar caminho para o diretório pai)
import os
if os.path.exists("/app/public"):
    # Docker environment
    app.mount("/public", StaticFiles(directory="/app/public"), name="public")
else:
    # Local development environment
    app.mount("/public", StaticFiles(directory="../public"), name="public")

# Servir arquivos estáticos
@app.get("/test_order.html")
async def serve_test_order():
    return FileResponse("test_order.html")

@app.get("/catalogo.html")
async def serve_catalogo():
    """Serve o arquivo catalogo.html"""
    if os.path.exists("/app/catalogo.html"):
        # Docker environment
        return FileResponse("/app/catalogo.html", media_type="text/html")
    else:
        # Local development environment
        return FileResponse("../catalogo.html", media_type="text/html")

@app.get("/demo.html")
async def serve_demo():
    """Serve o arquivo demo.html"""
    if os.path.exists("/app/demo.html"):
        # Docker environment
        return FileResponse("/app/demo.html", media_type="text/html")
    else:
        # Local development environment
        return FileResponse("../demo.html", media_type="text/html")

@app.get("/favicon.ico")
async def serve_favicon():
    """Serve o favicon.ico"""
    if os.path.exists("/app/favicon.ico"):
        # Docker environment
        return FileResponse("/app/favicon.ico", media_type="image/x-icon")
    else:
        # Local development environment
        return FileResponse("../favicon.ico", media_type="image/x-icon")

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

# -------------------- Endpoints --------------------
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/produtos")
def listar_produtos_demo():
    """Endpoint para demonstração - lista produtos de exemplo"""
    produtos_demo = [
        {
            "id": 1,
            "descricao": "Smartphone Galaxy S24",
            "apresentacao": "Smartphone premium com câmera de 200MP, tela AMOLED 6.8\" e processador Snapdragon 8 Gen 3",
            "preco": 2499.99,
            "estoque": 15,
            "imagem_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
            "categoria": "Eletrônicos"
        },
        {
            "id": 2,
            "descricao": "Notebook Dell Inspiron",
            "apresentacao": "Notebook para trabalho e estudos com Intel Core i5, 8GB RAM, SSD 256GB e tela 15.6\"",
            "preco": 3299.99,
            "estoque": 8,
            "imagem_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
            "categoria": "Informática"
        },
        {
            "id": 3,
            "descricao": "Fone Bluetooth Sony",
            "apresentacao": "Fone sem fio com cancelamento de ruído ativo, bateria de 30h e qualidade de áudio Hi-Res",
            "preco": 299.99,
            "estoque": 25,
            "imagem_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
            "categoria": "Áudio"
        },
        {
            "id": 4,
            "descricao": "Smart TV 55\" 4K",
            "apresentacao": "Smart TV LED 55 polegadas com resolução 4K UHD, HDR10+ e sistema operacional Android TV",
            "preco": 1899.99,
            "estoque": 12,
            "imagem_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400",
            "categoria": "TV & Vídeo"
        },
        {
            "id": 5,
            "descricao": "Câmera Canon EOS",
            "apresentacao": "Câmera DSLR profissional com sensor APS-C 24.1MP, gravação 4K e lente 18-55mm incluída",
            "preco": 4599.99,
            "estoque": 5,
            "imagem_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400",
            "categoria": "Fotografia"
        },
        {
            "id": 6,
            "descricao": "Tablet iPad Air",
            "apresentacao": "Tablet Apple com chip M1, tela Liquid Retina 10.9\", 64GB de armazenamento e suporte ao Apple Pencil",
            "preco": 3799.99,
            "estoque": 10,
            "imagem_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400",
            "categoria": "Tablets"
        }
    ]
    return {"produtos": produtos_demo}

@app.post("/api/demo/criar-sessao")
def criar_sessao_demo():
    """Cria uma sessão de demonstração com produtos pré-definidos"""
    try:
        db = SessionLocal()
        
        # Gera ID único para a sessão
        novo_sessao_id = gerar_sessao_id()
        expira_em = datetime.utcnow() + timedelta(hours=SESSION_VALIDITY_HOURS)
        
        # Cria nova sessão
        nova_sessao = Sessao(
            sessao_id=novo_sessao_id,
            cliente_telefone="11999999999",
            cliente_nome="Cliente Demonstração",
            expira_em=expira_em
        )
        db.add(nova_sessao)
        db.flush()  # Para obter o ID
        
        # Produtos de demonstração
        produtos_demo = [
            {"id": 1, "descricao": "Smartphone Galaxy S24", "apresentacao": "Smartphone premium com câmera de 200MP, tela AMOLED 6.8\" e processador Snapdragon 8 Gen 3", "preco": 2499.99, "estoque": 15, "imagem_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400", "categoria": "Eletrônicos"},
            {"id": 2, "descricao": "Notebook Dell Inspiron", "apresentacao": "Notebook para trabalho e estudos com Intel Core i5, 8GB RAM, SSD 256GB e tela 15.6\"", "preco": 3299.99, "estoque": 8, "imagem_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400", "categoria": "Informática"},
            {"id": 3, "descricao": "Fone Bluetooth Sony", "apresentacao": "Fone sem fio com cancelamento de ruído ativo, bateria de 30h e qualidade de áudio Hi-Res", "preco": 299.99, "estoque": 25, "imagem_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", "categoria": "Áudio"},
            {"id": 4, "descricao": "Smart TV 55\" 4K", "apresentacao": "Smart TV LED 55 polegadas com resolução 4K UHD, HDR10+ e sistema operacional Android TV", "preco": 1899.99, "estoque": 12, "imagem_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400", "categoria": "TV & Vídeo"},
            {"id": 5, "descricao": "Câmera Canon EOS", "apresentacao": "Câmera DSLR profissional com sensor APS-C 24.1MP, gravação 4K e lente 18-55mm incluída", "preco": 4599.99, "estoque": 5, "imagem_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400", "categoria": "Fotografia"},
            {"id": 6, "descricao": "Tablet iPad Air", "apresentacao": "Tablet Apple com chip M1, tela Liquid Retina 10.9\", 64GB de armazenamento e suporte ao Apple Pencil", "preco": 3799.99, "estoque": 10, "imagem_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400", "categoria": "Tablets"}
        ]
        
        # Adiciona produtos à sessão
        for produto in produtos_demo:
            produto_sessao = ProdutoSessao(
                sessao_uuid=nova_sessao.id,
                produto_id=produto["id"],
                descricao=produto["descricao"],
                preco=produto["preco"],
                estoque=produto["estoque"],
                imagem_url=produto["imagem_url"],
                categoria=produto["categoria"],
                apresentacao=produto.get("apresentacao")
            )
            db.add(produto_sessao)
        
        db.commit()
        
        return {
            "success": True,
            "sessao_id": novo_sessao_id,
            "url_catalogo": f"{CLIENT_BASE_URL}?sessao_id={novo_sessao_id}",
            "expira_em": expira_em.isoformat(),
            "produtos_count": len(produtos_demo)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar sessão: {str(e)}")
    finally:
        db.close()

@app.post("/api/produtos/criar-sessao")
def criar_sessao(payload: CriarSessaoPayload, _: None = Depends(rate_limit_dep)):
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        # Verifica se já existe sessão ativa para o telefone
        existing = db.query(Sessao).filter(
            Sessao.cliente_telefone == payload.cliente_telefone,
            Sessao.status == "ativa",
            Sessao.expira_em > now
        ).first()
        if existing:
            link = f"{CLIENT_BASE_URL}?sessao_id={existing.sessao_id}"
            return {
                "success": True,
                "sessao_id": existing.sessao_id,
                "link_produtos": link,
                "expira_em": existing.expira_em.isoformat(),
                "validade_horas": SESSION_VALIDITY_HOURS
            }
        # Cria nova sessão
        sessao_id = gerar_sessao_id()
        sessao = Sessao(
            sessao_id=sessao_id,
            cliente_telefone=payload.cliente_telefone,
            cliente_nome=payload.cliente_nome,
            status="ativa",
            criado_em=now,
            expira_em=now + timedelta(hours=SESSION_VALIDITY_HOURS),
            atualizado_em=now,
        )
        db.add(sessao)
        db.flush()  # obtém sessao.id
        # Insere produtos
        for p in payload.produtos:
            db.add(ProdutoSessao(
                sessao_uuid=sessao.id,
                produto_id=p.id,
                descricao=p.descricao,
                preco=Decimal(p.preco),
                estoque=p.estoque,
                imagem_url=p.imagem_url,
                categoria=p.categoria,
                apresentacao=p.apresentacao,
            ))
        db.commit()
        link = f"{CLIENT_BASE_URL}?sessao_id={sessao.sessao_id}"
        return {
            "success": True,
            "sessao_id": sessao.sessao_id,
            "link_produtos": link,
            "expira_em": sessao.expira_em.isoformat(),
            "validade_horas": SESSION_VALIDITY_HOURS
        }
    finally:
        db.close()

@app.get("/api/produtos/{sessao_id}")
def obter_sessao(sessao_id: str, _: None = Depends(rate_limit_dep)):
    db = SessionLocal()
    try:
        s = db.query(Sessao).filter(Sessao.sessao_id == sessao_id).first()
        if not s:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        now = datetime.utcnow()
        status = s.status
        if now > s.expira_em and status == "ativa":
            status = "expirada"
        produtos = db.query(ProdutoSessao).filter(ProdutoSessao.sessao_uuid == s.id).all()
        return {
            "success": True,
            "sessao_id": s.sessao_id,
            "cliente_nome": s.cliente_nome,
            "cliente_telefone": s.cliente_telefone,
            "produtos": [
                {
                    "id": p.produto_id,
                    "descricao": p.descricao,
                    "preco": float(p.preco),
                    "estoque": p.estoque,
                    "imagem_url": p.imagem_url,
                    "categoria": p.categoria,
                    "apresentacao": p.apresentacao,
                }
                for p in produtos
            ],
            "status": status,
            "criado_em": s.criado_em.isoformat(),
            "expira_em": s.expira_em.isoformat(),
        }
    finally:
        db.close()

@app.post("/api/produtos/{sessao_id}/selecionar")
def selecionar_produtos(sessao_id: str, payload: SelecionarPayload, _: None = Depends(rate_limit_dep)):
    db = SessionLocal()
    try:
        s = db.query(Sessao).filter(Sessao.sessao_id == sessao_id).first()
        if not s:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        now = datetime.utcnow()
        if now > s.expira_em or s.status != "ativa":
            raise HTTPException(status_code=400, detail="Sessão não está ativa")
        # Mapear preços
        produtos_db = db.query(ProdutoSessao).filter(ProdutoSessao.sessao_uuid == s.id).all()
        preco_map = {p.produto_id: Decimal(p.preco) for p in produtos_db}
        selecao_id = str(uuid.uuid4())
        total = Decimal("0.00")
        for item in payload.produtos_selecionados:
            if item.produto_id not in preco_map:
                raise HTTPException(status_code=400, detail=f"Produto {item.produto_id} inválido para sessão")
            unit = preco_map[item.produto_id]
            subtotal = unit * item.quantidade
            total += subtotal
            db.add(SelecaoItem(
                selecao_id=selecao_id,
                sessao_uuid=s.id,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                valor_unitario=unit,
                valor_total=subtotal,
                forma_pagamento=payload.forma_pagamento,  # Incluindo forma de pagamento
            ))
        db.commit()
        return {
            "success": True,
            "selecao_id": selecao_id,
            "valor_total": float(total),
            "produtos_selecionados": [{"produto_id": i.produto_id, "quantidade": i.quantidade} for i in payload.produtos_selecionados],
            "forma_pagamento": payload.forma_pagamento,  # Retornando forma de pagamento na resposta
        }
    finally:
        db.close()

@app.get("/api/produtos/{sessao_id}/status")
def status_sessao(sessao_id: str, _: None = Depends(rate_limit_dep)):
    db = SessionLocal()
    try:
        s = db.query(Sessao).filter(Sessao.sessao_id == sessao_id).first()
        if not s:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        now = datetime.utcnow()
        status = s.status
        if now > s.expira_em and status == "ativa":
            status = "expirada"
        return {"success": True, "status": status, "expira_em": s.expira_em.isoformat()}
    finally:
        db.close()

@app.post("/api/webhook/n8n")
def webhook_n8n(data: dict, _: None = Depends(rate_limit_dep)):
    """
    Webhook para receber dados do n8n e processar pedidos
    """
    try:
        # Log dos dados recebidos
        print(f"[WEBHOOK N8N] Dados recebidos: {data}")
        
        # Validação básica dos dados
        if not data:
            raise HTTPException(status_code=400, detail="Dados não fornecidos")
        
        # Extrair informações do cliente
        cliente_info = data.get("cliente", {})
        if not cliente_info:
            raise HTTPException(status_code=400, detail="Informações do cliente não fornecidas")
        
        cliente_nome = cliente_info.get("nome", "")
        cliente_telefone = cliente_info.get("telefone", "")
        
        if not cliente_nome or not cliente_telefone:
            raise HTTPException(status_code=400, detail="Nome e telefone do cliente são obrigatórios")
        
        # Extrair informações de entrega
        entrega_info = data.get("entrega", {})
        endereco = entrega_info.get("endereco", "")
        numero = entrega_info.get("numero", "")
        bairro = entrega_info.get("bairro", "")
        cidade = entrega_info.get("cidade", "")
        cep = entrega_info.get("cep", "")
        
        # Extrair informações de pagamento
        pagamento_info = data.get("pagamento", {})
        forma_pagamento = pagamento_info.get("forma_pagamento", "")
        valor_total = pagamento_info.get("valor_total", 0)
        
        # Extrair produtos
        produtos = data.get("produtos", [])
        if not produtos:
            raise HTTPException(status_code=400, detail="Lista de produtos não fornecida")
        
        # Processar cada produto
        produtos_processados = []
        for produto in produtos:
            produto_processado = {
                "nome": produto.get("nome", ""),
                "codigo": produto.get("codigo", ""),
                "preco_unitario": produto.get("preco_unitario", 0),
                "quantidade": produto.get("quantidade", 0),
                "subtotal": produto.get("subtotal", 0)
            }
            produtos_processados.append(produto_processado)
        
        # Simular processamento do pedido
        # Aqui você pode integrar com sistemas externos, banco de dados, etc.
        
        response_data = {
            "status": "success",
            "message": "Pedido processado com sucesso",
            "pedido_id": f"PED-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "cliente": {
                "nome": cliente_nome,
                "telefone": cliente_telefone
            },
            "entrega": {
                "endereco_completo": f"{endereco}, {numero} - {bairro} - {cidade} - CEP: {cep}"
            },
            "pagamento": {
                "forma": forma_pagamento,
                "valor_total": valor_total
            },
            "produtos": produtos_processados,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"[WEBHOOK N8N] Resposta: {response_data}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[WEBHOOK N8N] Erro: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/api/process-order")
def process_order(data: dict, _: None = Depends(rate_limit_dep)):
    """
    Endpoint para processar pedidos usando o sistema independente (sem n8n)
    """
    try:
        from order_processor import order_processor, OrderPayload
        
        # Log dos dados recebidos
        print(f"[PROCESS ORDER] Dados recebidos: {data}")
        
        # Validar e converter dados para o modelo
        try:
            payload = OrderPayload(**data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
        
        # Processar pedido
        result = order_processor.process_order(payload)
        
        if result["success"]:
            print(f"[PROCESS ORDER] Sucesso: {result}")
            return {
                "status": "success",
                "message": result["message"],
                "order_id": result["order_id"],
                "whatsapp_sent": result["whatsapp_sent"],
                "data": result["data"]
            }
        else:
            print(f"[PROCESS ORDER] Erro: {result}")
            raise HTTPException(status_code=500, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[PROCESS ORDER] Erro inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)