import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict
from dotenv import load_dotenv
import base64
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

# Carregar variáveis de ambiente
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, Depends
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import io
from urllib.parse import urlparse
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Numeric, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Configurações do MinIO
MINIO_SERVER_URL = "https://c4crm-minio.zv7gpn.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "Devs@0101"

# Cliente S3 para MinIO
try:
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_SERVER_URL,
        aws_access_key_id=MINIO_ROOT_USER,
        aws_secret_access_key=MINIO_ROOT_PASSWORD,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )
    print("[MINIO] Cliente S3 configurado com sucesso!")
except Exception as e:
    print(f"[MINIO] Erro ao configurar cliente S3: {e}")
    s3_client = None

# Importar order_processor no nível superior (compatível com execução local e via pacote backend)
ORDER_PROCESSOR_AVAILABLE = False
order_processor = None
OrderPayload = None
try:
    # Contexto de produção (Docker): uvicorn backend.app:app
    from backend.order_processor import order_processor, OrderPayload  # type: ignore
    ORDER_PROCESSOR_AVAILABLE = True
except ImportError as e_pkg:
    try:
        # Contexto de desenvolvimento local: uvicorn app:app com cwd em backend/
        from order_processor import order_processor, OrderPayload  # type: ignore
        ORDER_PROCESSOR_AVAILABLE = True
    except ImportError as e_local:
        print(f"[WARNING] Order processor não disponível: pkg={e_pkg} | local={e_local}")

# -------------------- Config --------------------
DB_URL = os.getenv("DB_URL", "sqlite:///./backend_data.db")
CLIENT_BASE_URL = os.getenv("CLIENT_BASE_URL", "http://localhost:8010/catalogo.html")
SESSION_VALIDITY_HOURS = int(os.getenv("SESSION_VALIDITY_HOURS", "4"))
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGIN",
    "http://localhost:5500,http://localhost:3000,http://localhost:8000,http://localhost:8010,http://localhost:8080"
).split(",")  # Permite origens comuns em dev/local
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

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
    preco_original = Column(Numeric(10, 2), nullable=True)  # Preço original (antes do desconto)
    percentual_desconto = Column(Numeric(5, 2), nullable=True)  # Percentual de desconto (ex: 15.50 para 15.5%)
    valor_desconto = Column(Numeric(10, 2), nullable=True)  # Valor fixo de desconto
    estoque = Column(Integer, nullable=False)
    imagem_url = Column(String, nullable=True)
    categoria = Column(String, nullable=True)
    apresentacao = Column(String, nullable=True)
    laboratorio = Column(String, nullable=True)

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
    preco_original: Optional[Decimal] = None  # Preço original (antes do desconto)
    percentual_desconto: Optional[Decimal] = None  # Percentual de desconto
    valor_desconto: Optional[Decimal] = None  # Valor fixo de desconto
    estoque: int
    imagem_url: Optional[str] = None
    categoria: Optional[str] = None
    apresentacao: Optional[str] = None
    laboratorio: Optional[str] = None

class CriarSessaoPayload(BaseModel):
    cliente_telefone: str = Field(..., min_length=10, max_length=50)  # Aumentado para aceitar formato WhatsApp
    cliente_nome: str
    produtos: List[ProdutoIn]
    quantidade_produtos: int
    timestamp: str
    # Permite forçar a criação de uma nova sessão (opcional)
    forcar_nova_sessao: Optional[bool] = False

class SelecionarItemIn(BaseModel):
    produto_id: int
    quantidade: int

class SelecionarPayload(BaseModel):
    produtos_selecionados: List[SelecionarItemIn]
    cliente_telefone: Optional[str] = None
    forma_pagamento: Optional[str] = None  # Novo campo para forma de pagamento

# -------------------- Utils --------------------
def build_catalog_url(request: Request, sessao_id: str) -> str:
    """Montar URL do catálogo usando host e scheme da requisição.
    Considera cabeçalhos de proxy (x-forwarded-*) para ambientes atrás de Nginx.
    Fallback para CLIENT_BASE_URL quando não houver informações suficientes.
    """
    forwarded_proto = request.headers.get("x-forwarded-proto")
    forwarded_host = request.headers.get("x-forwarded-host")
    scheme = forwarded_proto or request.url.scheme
    host = forwarded_host or request.headers.get("host") or request.url.hostname

    if scheme and host:
        return f"{scheme}://{host}/catalogo.html?sessao_id={sessao_id}"

    # Fallback para variável de ambiente
    return f"{CLIENT_BASE_URL}?sessao_id={sessao_id}"
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

# Montar arquivos estáticos com caminho robusto
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCAL_PUBLIC_DIR = os.path.join(BASE_DIR, "public")
if os.path.exists("/app/public"):
    # Docker environment
    app.mount("/public", StaticFiles(directory="/app/public"), name="public")
else:
    # Local development environment
    app.mount("/public", StaticFiles(directory=LOCAL_PUBLIC_DIR), name="public")

# Servir arquivos estáticos
@app.get("/")
async def serve_root():
    """Redireciona a rota raiz para catalogo.html"""
    if os.path.exists("/app/catalogo.html"):
        # Docker environment
        return FileResponse("/app/catalogo.html", media_type="text/html")
    else:
        # Local development environment
        return FileResponse(os.path.join(BASE_DIR, "catalogo.html"), media_type="text/html")

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
        return FileResponse(os.path.join(BASE_DIR, "catalogo.html"), media_type="text/html")

@app.get("/demo.html")
async def serve_demo():
    """Serve o arquivo demo.html"""
    if os.path.exists("/app/demo.html"):
        # Docker environment
        return FileResponse("/app/demo.html", media_type="text/html")
    else:
        # Local development environment
        return FileResponse(os.path.join(BASE_DIR, "demo.html"), media_type="text/html")

@app.get("/status.html")
async def serve_status_page():
    """Serve a página de acompanhamento de status"""
    file_name = "status.html"
    docker_path = f"/app/{file_name}"
    local_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(docker_path):
        return FileResponse(docker_path, media_type="text/html")
    else:
        return FileResponse(local_path, media_type="text/html")

# -------------------- Rotas auxiliares --------------------
@app.post("/api/relay/n8n")
def relay_to_n8n(payload: dict, request: Request, _: None = Depends(rate_limit_dep)):
    """Encaminha payload para o webhook do n8n no servidor, evitando CORS no navegador.
    Define a URL pelo env N8N_WEBHOOK_URL. Retorna corpo e status da resposta do n8n."""
    if not N8N_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="N8N_WEBHOOK_URL não configurada")
    try:
        resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=15)
        return {
            "ok": resp.ok,
            "status_code": resp.status_code,
            "status_text": getattr(resp, 'reason', ''),
            "response": resp.text
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Falha ao encaminhar para n8n: {str(e)}")

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

@app.get("/api/order-status")
def get_order_status(order_id: int):
    """Retorna detalhes do pedido e itens para acompanhamento de status"""
    try:
        if not ORDER_PROCESSOR_AVAILABLE or order_processor is None:
            raise HTTPException(status_code=500, detail="Sistema de pedidos não disponível")

        order_res = order_processor.supabase.table("orders").select("*").eq("id", order_id).limit(1).execute()
        order_data = order_res.data[0] if getattr(order_res, "data", None) else None
        if not order_data:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")

        items_res = order_processor.supabase.table("order_items").select("*").eq("order_id", order_id).execute()
        items_data = getattr(items_res, "data", []) or []

        status = (order_data.get("status") or "pending").lower()
        timeline_steps = [
            {"key": "pending", "label": "Pedido recebido"},
            {"key": "preparing", "label": "Em preparação"},
            {"key": "out_for_delivery", "label": "Saiu para entrega"},
            {"key": "delivered", "label": "Entregue"},
        ]

        status_index = next((i for i, s in enumerate(timeline_steps) if s["key"] == status), 0)
        for i, s in enumerate(timeline_steps):
            s["done"] = i <= status_index

        # ETA refinado com base no horário de criação e médias operacionais
        def _parse_ts(ts):
            try:
                if isinstance(ts, str):
                    if ts.endswith("Z"):
                        ts = ts.replace("Z", "+00:00")
                    return datetime.fromisoformat(ts)
            except Exception:
                return None
            return None

        now = datetime.utcnow()
        created_at = _parse_ts(order_data.get("created_at"))
        elapsed_mins = max(int((now - created_at).total_seconds() / 60), 0) if created_at else 0

        # Totais típicos da operação (pode ser parametrizado por ENV no futuro)
        TOTAL_MIN, TOTAL_MAX = 45, 60
        remaining_min = max(TOTAL_MIN - elapsed_mins, 0)
        remaining_max = max(TOTAL_MAX - elapsed_mins, 0)

        if status == "delivered":
            eta_text = "Entregue ✅"
        else:
            eta_text = f"Estimativa de entrega: ~{remaining_min}–{remaining_max} min"

        return {
            "order": order_data,
            "items": items_data,
            "timeline": timeline_steps,
            "server_time": now.isoformat(),
            "eta": {
                "min": remaining_min,
                "max": remaining_max,
                "text": eta_text,
                "elapsed_minutes": elapsed_mins
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar status: {str(e)}")

@app.get("/api/banners")
def listar_banners():
    """Busca banners ativos do Supabase ordenados por posição"""
    try:
        if not ORDER_PROCESSOR_AVAILABLE or not order_processor:
            print("[BANNERS] Order processor não disponível, usando banners de exemplo")
            # Fallback: retorna banners de exemplo se Supabase não estiver disponível
            return {
                "banners": [
                    {
                        "id": 1,
                        "titulo": "Banner novo",
                        "subtitulo": "SUPER OFERTA",
                        "descricao": "Aproveite descontos incríveis em medicamentos essenciais",
                        "badge_texto": "🏷️ SUPER OFERTA",
                        "cor_primaria": "#10B981",
                        "cor_secundaria": "#14B8A6",
                        "icone": "pill",
                        "tipo_promocao": "desconto_percentual",
                        "percentual_desconto": 50,
                        "posicao": 1,
                        "ativo": True,
                        "imagem_url": "http://localhost:8000/api/local-image?path=padrao.png"
                    },
                    {
                        "id": 2,
                        "titulo": "Vitaminas e Suplementos",
                        "subtitulo": "SAÚDE EM PRIMEIRO LUGAR",
                        "descricao": "Cuide da sua saúde com vitaminas e suplementos",
                        "badge_texto": "💊 VITAMINAS",
                        "cor_primaria": "#8B5CF6",
                        "cor_secundaria": "#A855F7",
                        "icone": "heart",
                        "tipo_promocao": "categoria",
                        "posicao": 2,
                        "ativo": True
                    },
                    {
                        "id": 3,
                        "titulo": "Entrega Grátis",
                        "subtitulo": "FRETE GRÁTIS",
                        "descricao": "Entrega rápida e gratuita em toda a cidade",
                        "badge_texto": "🚚 FRETE GRÁTIS",
                        "cor_primaria": "#3B82F6",
                        "cor_secundaria": "#06B6D4",
                        "icone": "truck",
                        "tipo_promocao": "frete_gratis",
                        "valor_minimo": 50,
                        "posicao": 3,
                        "ativo": True
                    }
                ]
            }
        
        # Buscar banners ativos do Supabase
        print("[BANNERS] Buscando banners do Supabase...")
        result = order_processor.supabase.table("banners").select("*").eq("ativo", True).order("posicao").execute()
        
        if result.data:
            print(f"[BANNERS] Encontrados {len(result.data)} banners no Supabase")
            return {"banners": result.data}
        else:
            print("[BANNERS] Nenhum banner encontrado no Supabase, usando fallback")
            return {"banners": []}
            
    except Exception as e:
        print(f"[ERROR] Erro ao buscar banners: {str(e)}")
        # Em caso de erro, retorna banners de exemplo
        return {
            "banners": [
                {
                    "id": 1,
                    "titulo": "Até 50% OFF em Medicamentos",
                    "subtitulo": "SUPER OFERTA",
                    "descricao": "Aproveite descontos incríveis em medicamentos essenciais",
                    "badge_texto": "🏷️ SUPER OFERTA",
                    "cor_primaria": "#10B981",
                    "cor_secundaria": "#14B8A6",
                    "icone": "pill",
                    "tipo_promocao": "desconto_percentual",
                    "percentual_desconto": 50,
                    "posicao": 1,
                    "ativo": True
                }
            ]
        }

@app.post("/api/fix-banner-image")
def fix_banner_image():
    """Endpoint temporário para corrigir a imagem problemática do banner ID 7"""
    try:
        if not ORDER_PROCESSOR_AVAILABLE or not order_processor:
            raise HTTPException(status_code=503, detail="Order processor não disponível")
        
        # Atualizar o banner ID 7 removendo a imagem problemática
        result = order_processor.supabase.table('banners').update({
            'imagem_url': None
        }).eq('id', 7).execute()
        
        if result.data:
            return {
                "success": True,
                "message": "Banner ID 7 corrigido - imagem removida",
                "banner_id": 7
            }
        else:
            raise HTTPException(status_code=404, detail="Banner ID 7 não encontrado")
            
    except Exception as e:
        print(f"[ERROR] Erro ao corrigir banner: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/proxy-image")
async def proxy_image(url: str):
    """
    Proxy para imagens externas para resolver problemas de CORS
    """
    try:
        # Validar URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="URL inválida")
        
        # Fazer requisição para a imagem
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()
        
        # Verificar se é uma imagem
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="URL não é uma imagem válida")
        
        # Criar stream da imagem
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return StreamingResponse(
            generate(),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache por 1 hora
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=404, detail=f"Erro ao carregar imagem: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/minio-image")
async def minio_image(path: str):
    """
    Proxy específico para imagens do MinIO usando boto3 e URLs pré-assinadas
    """
    try:
        if not s3_client:
            raise HTTPException(status_code=503, detail="Cliente MinIO não disponível")
        
        # Limpar e processar o caminho
        path = path.strip('/')
        
        # Tentar diferentes buckets
        buckets_to_try = ['produtos', 'crm-media-files']
        
        for bucket in buckets_to_try:
            try:
                print(f"[MINIO] Tentando bucket '{bucket}' com arquivo '{path}'")
                
                # Verificar se o objeto existe
                s3_client.head_object(Bucket=bucket, Key=path)
                
                # Gerar URL pré-assinada
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': path},
                    ExpiresIn=3600  # 1 hora
                )
                
                print(f"[MINIO] Sucesso! URL gerada para {bucket}/{path}")
                
                # Fazer requisição para a URL pré-assinada
                response = requests.get(presigned_url, timeout=15, stream=True)
                response.raise_for_status()
                
                # Verificar content-type
                content_type = response.headers.get('content-type', 'image/png')
                if not content_type.startswith('image/'):
                    content_type = 'image/png'
                
                # Criar stream da imagem
                def generate():
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                
                return StreamingResponse(
                    generate(),
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=3600",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET",
                        "Access-Control-Allow-Headers": "*"
                    }
                )
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchKey':
                    print(f"[MINIO] Arquivo não encontrado em {bucket}: {path}")
                    continue
                else:
                    print(f"[MINIO] Erro no bucket {bucket}: {e}")
                    continue
            except Exception as e:
                print(f"[MINIO] Erro geral no bucket {bucket}: {e}")
                continue
        
        # Se chegou aqui, não encontrou em nenhum bucket
        raise HTTPException(status_code=404, detail=f"Imagem não encontrada: {path}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[MINIO] Erro interno: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/minio-url")
async def minio_url(path: str):
    """
    Gera URL pré-assinada para imagem do MinIO (para debug)
    """
    try:
        if not s3_client:
            raise HTTPException(status_code=503, detail="Cliente MinIO não disponível")
        
        path = path.strip('/')
        buckets_to_try = ['produtos', 'crm-media-files']
        
        for bucket in buckets_to_try:
            try:
                s3_client.head_object(Bucket=bucket, Key=path)
                
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': path},
                    ExpiresIn=3600
                )
                
                return {
                    "success": True,
                    "bucket": bucket,
                    "key": path,
                    "presigned_url": presigned_url
                }
                
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchKey':
                    continue
        
        raise HTTPException(status_code=404, detail=f"Imagem não encontrada: {path}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/local-image")
async def local_image(path: str = "padrao.png"):
    """
    Serve imagens locais como fallback quando MinIO não estiver disponível
    """
    try:
        # Mapear caminhos seguros
        safe_paths = {
            "padrao.png": "../public/padrao.png",
            "logo.png": "../public/logo.png",
            "cart.png": "../public/cart.png"
        }
        
        # Verificar se o path é seguro
        if path not in safe_paths:
            path = "padrao.png"  # Fallback para imagem padrão
        
        file_path = safe_paths[path]
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Imagem local não encontrada: {path}")
        
        print(f"[LOCAL IMAGE] Servindo imagem local: {file_path}")
        
        return FileResponse(
            file_path,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[LOCAL IMAGE] Erro interno: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/debug/supabase-status")
def debug_supabase_status():
    """Endpoint para debug - verifica status da conexão Supabase"""
    return {
        "ORDER_PROCESSOR_AVAILABLE": ORDER_PROCESSOR_AVAILABLE,
        "order_processor_exists": order_processor is not None,
        "order_processor_type": str(type(order_processor)) if order_processor else None
    }

@app.get("/api/produtos")
def listar_produtos():
    """Busca produtos do Supabase ou retorna dados de exemplo como fallback"""
    try:
        if not ORDER_PROCESSOR_AVAILABLE or not order_processor:
            print("[PRODUTOS] Order processor não disponível, usando produtos de exemplo")
            # Fallback: retorna produtos de exemplo se Supabase não estiver disponível
            return {
                "produtos": [
                    {
                        "id": 1,
                        "descricao": "Smartphone Galaxy S24",
                        "apresentacao": "Smartphone premium com câmera de 200MP, tela AMOLED 6.8\" e processador Snapdragon 8 Gen 3",
                        "preco": 2499.99,
                        "estoque": 15,
                        "imagem_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
                        "categoria": "Eletrônicos",
                        "laboratorio": "Samsung Electronics"
                    },
                    {
                        "id": 2,
                        "descricao": "Notebook Dell Inspiron",
                        "apresentacao": "Notebook para trabalho e estudos com Intel Core i5, 8GB RAM, SSD 256GB e tela 15.6\"",
                        "preco": 3299.99,
                        "estoque": 8,
                        "imagem_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
                        "categoria": "Informática",
                        "laboratorio": "Dell Technologies"
                    },
                    {
                        "id": 3,
                        "descricao": "Fone Bluetooth Sony",
                        "apresentacao": "Fone sem fio com cancelamento de ruído ativo, bateria de 30h e qualidade de áudio Hi-Res",
                        "preco": 299.99,
                        "estoque": 25,
                        "imagem_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
                        "categoria": "Áudio",
                        "laboratorio": "Sony Corporation"
                    },
                    {
                        "id": 4,
                        "descricao": "Smart TV 55\" 4K",
                        "apresentacao": "Smart TV LED 55 polegadas com resolução 4K UHD, HDR10+ e sistema operacional Android TV",
                        "preco": 1899.99,
                        "estoque": 12,
                        "imagem_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400",
                        "categoria": "TV & Vídeo",
                        "laboratorio": "LG Electronics"
                    },
                    {
                        "id": 5,
                        "descricao": "Câmera Canon EOS",
                        "apresentacao": "Câmera DSLR profissional com sensor APS-C 24.1MP, gravação 4K e lente 18-55mm incluída",
                        "preco": 4599.99,
                        "estoque": 5,
                        "imagem_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400",
                        "categoria": "Fotografia",
                        "laboratorio": "Canon Inc."
                    },
                    {
                        "id": 6,
                        "descricao": "Tablet iPad Air",
                        "apresentacao": "Tablet Apple com chip M1, tela Liquid Retina 10.9\", 64GB de armazenamento e suporte ao Apple Pencil",
                        "preco": 3799.99,
                        "estoque": 10,
                        "imagem_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400",
                        "categoria": "Tablets",
                        "laboratorio": "Apple Inc."
                    }
                ]
            }
        
        # Buscar produtos do Supabase
        print("[PRODUTOS] Buscando produtos do Supabase...")
        result = order_processor.supabase.table("produtos").select("*").execute()
        
        if result.data:
            print(f"[PRODUTOS] Encontrados {len(result.data)} produtos no Supabase")
            # Garantir que todos os produtos tenham o campo laboratorio
            produtos_formatados = []
            for produto in result.data:
                produto_formatado = {
                    "id": produto.get("id"),
                    "descricao": produto.get("descricao") or produto.get("nome") or produto.get("name"),
                    "apresentacao": produto.get("apresentacao") or produto.get("description"),
                    "preco": produto.get("preco") or produto.get("price", 0),
                    "estoque": produto.get("estoque") or produto.get("stock", 0),
                    "imagem_url": produto.get("imagem_url") or produto.get("image_url"),
                    "categoria": produto.get("categoria") or produto.get("category"),
                    "laboratorio": produto.get("laboratorio") or produto.get("laboratory") or produto.get("brand"),
                    # Campos de desconto do Supabase
                    "preco_original": produto.get("preco_original"),
                    "percentual_desconto": produto.get("desconto_percentual"),
                    "valor_desconto": produto.get("desconto_valor")
                }
                produtos_formatados.append(produto_formatado)
            
            return {"produtos": produtos_formatados}
        else:
            print("[PRODUTOS] Nenhum produto encontrado no Supabase, usando fallback")
            # Em caso de erro, retorna produtos de exemplo
            return {
                "produtos": [
                    {
                        "id": 1,
                        "descricao": "Produto de Exemplo",
                        "apresentacao": "Este é um produto de exemplo quando não há dados no Supabase",
                        "preco": 99.99,
                        "estoque": 10,
                        "imagem_url": "/api/local-image?path=padrao.png",
                        "categoria": "Exemplo",
                        "laboratorio": "Laboratório Exemplo"
                    }
                ]
            }
            
    except Exception as e:
        print(f"[PRODUTOS] Erro ao buscar produtos: {str(e)}")
        # Em caso de erro, retorna produtos de exemplo
        return {
            "produtos": [
                {
                    "id": 1,
                    "descricao": "Produto de Exemplo (Erro)",
                    "apresentacao": f"Erro ao carregar produtos: {str(e)}",
                    "preco": 99.99,
                    "estoque": 10,
                    "imagem_url": "/api/local-image?path=padrao.png",
                    "categoria": "Erro",
                    "laboratorio": "Sistema"
                }
            ]
        }

@app.post("/api/demo/criar-sessao")
def criar_sessao_demo(request: Request):
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
            {"id": 1, "descricao": "Smartphone Galaxy S24", "apresentacao": "Smartphone premium com câmera de 200MP, tela AMOLED 6.8\" e processador Snapdragon 8 Gen 3", "preco": 2499.99, "estoque": 15, "imagem_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400", "categoria": "Eletrônicos", "laboratorio": "Samsung Electronics"},
            {"id": 2, "descricao": "Notebook Dell Inspiron", "apresentacao": "Notebook para trabalho e estudos com Intel Core i5, 8GB RAM, SSD 256GB e tela 15.6\"", "preco": 3299.99, "estoque": 8, "imagem_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400", "categoria": "Informática", "laboratorio": "Dell Technologies"},
            {"id": 3, "descricao": "Fone Bluetooth Sony", "apresentacao": "Fone sem fio com cancelamento de ruído ativo, bateria de 30h e qualidade de áudio Hi-Res", "preco": 299.99, "estoque": 25, "imagem_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", "categoria": "Áudio", "laboratorio": "Sony Corporation"},
            {"id": 4, "descricao": "Smart TV 55\" 4K", "apresentacao": "Smart TV LED 55 polegadas com resolução 4K UHD, HDR10+ e sistema operacional Android TV", "preco": 1899.99, "estoque": 12, "imagem_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400", "categoria": "TV & Vídeo", "laboratorio": "LG Electronics"},
            {"id": 5, "descricao": "Câmera Canon EOS", "apresentacao": "Câmera DSLR profissional com sensor APS-C 24.1MP, gravação 4K e lente 18-55mm incluída", "preco": 4599.99, "estoque": 5, "imagem_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400", "categoria": "Fotografia", "laboratorio": "Canon Inc."},
            {"id": 6, "descricao": "Tablet iPad Air", "apresentacao": "Tablet Apple com chip M1, tela Liquid Retina 10.9\", 64GB de armazenamento e suporte ao Apple Pencil", "preco": 3799.99, "estoque": 10, "imagem_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400", "categoria": "Tablets", "laboratorio": "Apple Inc."}
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
                apresentacao=produto.get("apresentacao"),
                laboratorio=produto.get("laboratorio")
            )
            db.add(produto_sessao)
        
        db.commit()
        
        return {
            "success": True,
            "sessao_id": novo_sessao_id,
            "url_catalogo": build_catalog_url(request, novo_sessao_id),
            "expira_em": expira_em.isoformat(),
            "produtos_count": len(produtos_demo)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar sessão: {str(e)}")
    finally:
        db.close()

@app.post("/api/produtos/criar-sessao")
def criar_sessao(request: Request, payload: CriarSessaoPayload, _: None = Depends(rate_limit_dep)):
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        # Verifica se já existe sessão ativa para o telefone
        existing = db.query(Sessao).filter(
            Sessao.cliente_telefone == payload.cliente_telefone,
            Sessao.status == "ativa",
            Sessao.expira_em > now
        ).first()
        if existing and not (payload.forcar_nova_sessao or False):
            # Atualiza produtos da sessão existente para refletir o payload atual
            # 1) Remove produtos antigos
            db.query(ProdutoSessao).filter(ProdutoSessao.sessao_uuid == existing.id).delete(synchronize_session=False)
            # 2) Insere novos produtos
            for p in payload.produtos:
                db.add(ProdutoSessao(
                    sessao_uuid=existing.id,
                    produto_id=p.id,
                    descricao=p.descricao,
                    preco=Decimal(p.preco),
                    preco_original=Decimal(p.preco_original) if p.preco_original else None,
                    percentual_desconto=Decimal(p.percentual_desconto) if p.percentual_desconto else None,
                    valor_desconto=Decimal(p.valor_desconto) if p.valor_desconto else None,
                    estoque=p.estoque,
                    imagem_url=p.imagem_url,
                    categoria=p.categoria,
                    apresentacao=p.apresentacao,
                    laboratorio=p.laboratorio,
                ))
            # 3) Atualiza timestamps e validade
            existing.atualizado_em = now
            existing.expira_em = now + timedelta(hours=SESSION_VALIDITY_HOURS)
            db.commit()
            link = build_catalog_url(request, existing.sessao_id)
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
                preco_original=Decimal(p.preco_original) if p.preco_original else None,
                percentual_desconto=Decimal(p.percentual_desconto) if p.percentual_desconto else None,
                valor_desconto=Decimal(p.valor_desconto) if p.valor_desconto else None,
                estoque=p.estoque,
                imagem_url=p.imagem_url,
                categoria=p.categoria,
                apresentacao=p.apresentacao,
                laboratorio=p.laboratorio,
            ))
        db.commit()
        link = build_catalog_url(request, sessao.sessao_id)
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
                    "preco_original": float(p.preco_original) if p.preco_original else None,
                    "percentual_desconto": float(p.percentual_desconto) if p.percentual_desconto else None,
                    "valor_desconto": float(p.valor_desconto) if p.valor_desconto else None,
                    "estoque": p.estoque,
                    "imagem_url": p.imagem_url,
                    "categoria": p.categoria,
                    "apresentacao": p.apresentacao,
                    "laboratorio": p.laboratorio,
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
        # Verificar se o order_processor está disponível
        if not ORDER_PROCESSOR_AVAILABLE or order_processor is None:
            print("[PROCESS ORDER] ERRO: Order processor não está disponível")
            raise HTTPException(status_code=500, detail="Sistema de processamento de pedidos não disponível")
        
        # Log dos dados recebidos
        print(f"[PROCESS ORDER] Dados recebidos: {data}")
        
        # Validar e converter dados para o modelo
        try:
            payload = OrderPayload(**data)
            print(f"[PROCESS ORDER] Payload validado: {payload}")
        except Exception as e:
            print(f"[PROCESS ORDER] ERRO na validação: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
        
        # Processar pedido
        print("[PROCESS ORDER] Iniciando processamento do pedido...")
        result = order_processor.process_order(payload)
        print(f"[PROCESS ORDER] Resultado do processamento: {result}")
        
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
            # Expor detalhes do erro no 500 para facilitar diagnóstico em produção
            error_detail = result.get("error")
            detail_msg = result["message"] if "message" in result else "Erro ao processar pedido"
            if error_detail:
                detail_msg = f"{detail_msg}: {error_detail}"
            print(f"[PROCESS ORDER] Erro no processamento: {result}")
            raise HTTPException(status_code=500, detail=detail_msg)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[PROCESS ORDER] ERRO GERAL: {str(e)}")
        import traceback
        print(f"[PROCESS ORDER] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[PROCESS ORDER] Erro inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)