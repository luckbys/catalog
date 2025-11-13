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

from fastapi import FastAPI, HTTPException, Request, Depends, Response
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
import io
import asyncio
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
ADMIN_INSTANCIAS_PASSWORD = os.getenv("ADMIN_INSTANCIAS_PASSWORD", "Devs2522*")
ADMIN_INSTANCIAS_COOKIE_NAME = "admin_instancias_auth"

# Configuração de follow-up/encerramento automático de pedidos
# - AUTO_CLOSE_AFTER_HOURS: horas até encerrar automaticamente se não entregue
# - FOLLOWUP_AFTER_HOURS: horas até enviar um lembrete ao cliente
# - AUTO_CLOSE_CHECK_INTERVAL_SECONDS: intervalo de checagem do worker
AUTO_CLOSE_AFTER_HOURS = float(os.getenv("AUTO_CLOSE_AFTER_HOURS", "3"))
FOLLOWUP_AFTER_HOURS = float(os.getenv("FOLLOWUP_AFTER_HOURS", "2"))
AUTO_CLOSE_CHECK_INTERVAL_SECONDS = int(os.getenv("AUTO_CLOSE_CHECK_INTERVAL_SECONDS", "180"))  # 3 min

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

# -------------------- Config Dinâmica de Contatos --------------------
# Arquivo JSON para armazenar números de vendedores e entregadores (persistente)
# Usa variável de ambiente `CONTACTS_CONFIG_PATH` com default para volume `/data`
CONTACTS_CONFIG_PATH = os.getenv("CONTACTS_CONFIG_PATH", "/data/contacts.json")

def _ensure_contacts_file():
    """Garante diretório e arquivo de contatos em volume persistente.

    - Cria o diretório destino (ex.: /data) se necessário
    - Migra arquivo legado de backend/contacts.json caso exista
    - Inicializa com defaults sensatos se não houver arquivo
    """
    try:
        target_dir = os.path.dirname(CONTACTS_CONFIG_PATH)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
    except Exception as e:
        print(f"[CONFIG] Falha ao criar diretório de contatos: {e}")

    if not os.path.exists(CONTACTS_CONFIG_PATH):
        # Migração de caminho legado, se existir
        legacy_path = os.path.join(os.path.dirname(__file__), "contacts.json")
        try:
            if os.path.exists(legacy_path):
                import shutil
                shutil.copyfile(legacy_path, CONTACTS_CONFIG_PATH)
        except Exception as e:
            print(f"[CONFIG] Falha ao migrar contacts.json legado: {e}")

    if not os.path.exists(CONTACTS_CONFIG_PATH):
        default_cfg = {
            "seller_phones": [os.getenv("WHATSAPP_PHONE", "5512976025888")],
            "driver_phones": [os.getenv("DRIVER_PHONE", "5512976025888")]
        }
        try:
            import json
            with open(CONTACTS_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(default_cfg, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CONFIG] Falha ao criar contacts.json: {e}")

def load_contacts_config() -> Dict[str, List[str]]:
    """Carrega configuração de contatos (vendedores/entregadores) do JSON"""
    import json
    _ensure_contacts_file()
    try:
        with open(CONTACTS_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Normalizar
            sellers = [str(x).strip() for x in (data.get("seller_phones") or []) if str(x).strip()]
            drivers = [str(x).strip() for x in (data.get("driver_phones") or []) if str(x).strip()]
            return {"seller_phones": sellers, "driver_phones": drivers}
    except Exception as e:
        print(f"[CONFIG] Erro ao ler contacts.json: {e}")
        return {
            "seller_phones": [os.getenv("WHATSAPP_PHONE", "5512976025888")],
            "driver_phones": [os.getenv("DRIVER_PHONE", "5512976025888")]
        }

def save_contacts_config(cfg: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Salva configuração de contatos no JSON, com validação simples"""
    import json
    def _valid_phone(p: str) -> bool:
        p = (p or "").strip()
        return p.isdigit() and len(p) >= 11
    sellers = [p for p in (cfg.get("seller_phones") or []) if _valid_phone(p)]
    drivers = [p for p in (cfg.get("driver_phones") or []) if _valid_phone(p)]
    normalized = {"seller_phones": sellers, "driver_phones": drivers}
    try:
        with open(CONTACTS_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)
        return normalized
    except Exception as e:
        print(f"[CONFIG] Erro ao salvar contacts.json: {e}")
        raise HTTPException(status_code=500, detail="Falha ao salvar configuração de contatos")

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

# -------------------- Schemas de Configuração --------------------
class ContactsPayload(BaseModel):
    seller_phones: Optional[List[str]] = None
    driver_phones: Optional[List[str]] = None

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

@app.get("/admin-pedidos.html")
async def serve_admin_pedidos():
    """Serve a página de gerenciamento de pedidos (admin)"""
    file_name = "admin-pedidos.html"
    docker_path = f"/app/{file_name}"
    local_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(docker_path):
        return FileResponse(docker_path, media_type="text/html")
    else:
        return FileResponse(local_path, media_type="text/html")

def _is_admin_instancias_authenticated(request: Request) -> bool:
    return request.cookies.get(ADMIN_INSTANCIAS_COOKIE_NAME) == "ok"

@app.get("/admin-instancias.html")
async def serve_admin_instancias_html(request: Request):
    """Serve a página de administração de instâncias WhatsApp, com gate de senha."""
    if not _is_admin_instancias_authenticated(request):
        # Login minimalista com POST para /api/admin-instancias/login
        html = """
        <!doctype html>
        <html lang="pt-br">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Login - Admin Instâncias</title>
          <style>
            body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,'Helvetica Neue',sans-serif;background:#0b1020;color:#e5e7eb;margin:0}
            .wrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
            .card{background:#111827;border:1px solid #1f2937;border-radius:12px;max-width:360px;width:100%;padding:24px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
            .title{font-size:18px;margin:0 0 12px;color:#93c5fd}
            .desc{font-size:14px;color:#9ca3af;margin-bottom:16px}
            label{font-size:12px;color:#9ca3af}
            input{width:100%;padding:10px 12px;border-radius:8px;border:1px solid #374151;background:#0f172a;color:#e5e7eb;margin-top:6px}
            button{width:100%;margin-top:16px;padding:10px;border-radius:8px;border:1px solid #2563eb;background:#1d4ed8;color:#fff;font-weight:600;cursor:pointer}
            button:hover{background:#2563eb}
            .error{margin-top:12px;color:#fca5a5;font-size:12px;display:none}
          </style>
        </head>
        <body>
          <div class="wrap">
            <div class="card">
              <h1 class="title">Admin Instâncias</h1>
              <p class="desc">Insira a senha para continuar.</p>
              <form id="loginForm">
                <label for="password">Senha</label>
                <input id="password" name="password" type="password" placeholder="••••••••" required />
                <button type="submit">Entrar</button>
                <div id="error" class="error">Senha inválida. Tente novamente.</div>
              </form>
            </div>
          </div>
          <script>
            const form = document.getElementById('loginForm');
            const error = document.getElementById('error');
            form.addEventListener('submit', async (e) => {
              e.preventDefault();
              error.style.display = 'none';
              const pwd = document.getElementById('password').value;
              try {
                const r = await fetch('/api/admin-instancias/login', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ password: pwd })
                });
                const j = await r.json();
                if (r.ok && j?.ok) {
                  window.location.href = '/admin-instancias.html';
                } else {
                  error.textContent = j?.error || 'Senha inválida.';
                  error.style.display = 'block';
                }
              } catch (err) {
                error.textContent = 'Erro de conexão.';
                error.style.display = 'block';
              }
            });
          </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=401)

    file_name = "admin-instancias.html"
    docker_path = f"/app/{file_name}"
    local_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(docker_path):
        return FileResponse(docker_path, media_type="text/html")
    else:
        return FileResponse(local_path, media_type="text/html")

@app.get("/admin-instancias")
async def serve_admin_instancias_alias(request: Request):
    """Alias sem extensão para admin-instancias.html"""
    return await serve_admin_instancias_html(request)

# ---- Auth endpoints para Admin Instâncias ----
@app.post("/api/admin-instancias/login")
def admin_instancias_login(payload: dict, response: Response):
    pwd = str(payload.get("password") or "")
    if not pwd:
        return {"ok": False, "error": "Senha não fornecida"}
    if pwd != ADMIN_INSTANCIAS_PASSWORD:
        return {"ok": False, "error": "Senha inválida"}
    # Define cookie simples (gate básico)
    max_age = 8 * 60 * 60  # 8 horas
    response.set_cookie(
        key=ADMIN_INSTANCIAS_COOKIE_NAME,
        value="ok",
        max_age=max_age,
        httponly=True,
        samesite="lax"
    )
    return {"ok": True}

@app.post("/api/admin-instancias/logout")
def admin_instancias_logout(response: Response):
    response.delete_cookie(ADMIN_INSTANCIAS_COOKIE_NAME)
    return {"ok": True}

@app.get("/test-api-orders.html")
async def serve_test_api_orders():
    """Serve a página de teste da API de pedidos"""
    file_name = "test-api-orders.html"
    docker_path = f"/app/{file_name}"
    local_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(docker_path):
        return FileResponse(docker_path, media_type="text/html")
    else:
        return FileResponse(local_path, media_type="text/html")

@app.get("/entregador.html")
async def serve_entregador():
    """Serve a página do entregador"""
    file_name = "entregador.html"
    docker_path = f"/app/{file_name}"
    local_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(docker_path):
        return FileResponse(docker_path, media_type="text/html")
    else:
        return FileResponse(local_path, media_type="text/html")

@app.get("/admin-config.html")
async def serve_admin_config():
    """Serve a página de configuração de contatos (admin-config)"""
    file_name = "admin-config.html"
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

# -------------------- Evolution API (Status) --------------------
@app.get("/api/evolution/connection-state")
def evolution_connection_state(instance: Optional[str] = None):
    """Consulta o estado de conexão da instância na Evolution API via backend.
    Evita problemas de CORS no navegador e unifica configuração usando variáveis de ambiente.

    Query:
    - instance: nome da instância (opcional, usa EVOLUTION_INSTANCE_NAME se ausente)
    """
    EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
    EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
    DEFAULT_INSTANCE = os.getenv("EVOLUTION_INSTANCE_NAME", "hakimfarma")
    name = (instance or DEFAULT_INSTANCE).strip()

    if not EVOLUTION_API_URL or not EVOLUTION_API_KEY:
        return {"ok": False, "connected": False, "error": "Evolution API não configurada"}

    headers = {
        "Accept": "application/json",
        "apikey": EVOLUTION_API_KEY,
        "x-api-key": EVOLUTION_API_KEY,
        "Authorization": f"Bearer {EVOLUTION_API_KEY}",
    }

    from urllib.parse import quote
    inst_q = quote(name, safe="")
    urls = [
        f"{EVOLUTION_API_URL}/instance/connectionState/{inst_q}",
        f"{EVOLUTION_API_URL}/instance/connectionState?instance={inst_q}",
        f"{EVOLUTION_API_URL}/instances/{inst_q}/connectionState",
    ]

    last_resp = None
    data: Dict[str, any] = {}
    used_url = None
    try:
        for u in urls:
            try:
                resp = requests.get(u, headers=headers, timeout=10)
                last_resp = resp
                used_url = u
                try:
                    data = resp.json()
                except Exception:
                    data = {"raw": resp.text}
                if resp.ok:
                    break
            except requests.RequestException:
                continue

        # Normalizar estado
        state_raw = str(data.get("state") or data.get("status") or data.get("connectionStatus") or "").lower()
        connected_flag = (
            bool(last_resp and last_resp.ok) and (
                "connected" in state_raw or "open" in state_raw or bool(data.get("connected") is True) or
                "connected" in str(data.get("result", "")).lower()
            )
        )

        return {
            "ok": bool(last_resp and last_resp.ok),
            "connected": connected_flag,
            "state": state_raw or None,
            "status_code": getattr(last_resp, "status_code", None),
            "url": used_url,
            "data": data,
            "instance": name,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha ao consultar Evolution API: {str(e)}")

@app.get("/favicon.ico")
async def serve_favicon():
    """Serve o favicon.ico"""
    if os.path.exists("/app/favicon.ico"):
        # Docker environment
        return FileResponse("/app/favicon.ico", media_type="image/x-icon")
    else:
        # Local development environment
        return FileResponse("../favicon.ico", media_type="image/x-icon")

# -------------------- API de Configuração de Contatos --------------------
@app.get("/api/config/contacts")
def get_contacts_config():
    """Obtém números de vendedores e entregadores"""
    return load_contacts_config()

@app.put("/api/config/contacts")
def update_contacts_config(payload: ContactsPayload):
    """Atualiza números de vendedores e entregadores"""
    cfg = {
        "seller_phones": payload.seller_phones or [],
        "driver_phones": payload.driver_phones or []
    }
    saved = save_contacts_config(cfg)
    return {"success": True, "data": saved}

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Permitir envio do Referer para serviços externos (Google Maps/Geocoder)
    # mantendo privacidade razoável. Isso é necessário para chaves restritas por HTTP referrer.
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# -------------------- Endpoints --------------------
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/orders")
def get_orders():
    """Retorna lista de pedidos do Supabase"""
    try:
        print("[API] GET /api/orders - Iniciando...")
        
        if not ORDER_PROCESSOR_AVAILABLE or order_processor is None:
            print("[API] ERROR: Order processor não disponível")
            raise HTTPException(status_code=503, detail="Sistema de pedidos não disponível")
        
        print("[API] Buscando pedidos do Supabase...")
        # Buscar pedidos do Supabase
        orders_res = order_processor.supabase.table("orders").select("*").order("created_at", desc=True).limit(50).execute()
        orders_data = getattr(orders_res, "data", []) or []
        print(f"[API] Pedidos encontrados: {len(orders_data)}")
        
        # Função auxiliar para extrair dados de dinheiro/troco das notas
        def _extract_cash_info(notes: str):
            try:
                if not notes:
                    return None, None
                import re
                # Aceita com ou sem emojis
                rx_received = re.search(r"(Troco\s*para|Valor\s*recebido)\s*:\s*R\$\s*([0-9]+(?:[\.,][0-9]{1,2})?)", notes, re.IGNORECASE)
                rx_change = re.search(r"Troco\s*:\s*R\$\s*([0-9]+(?:[\.,][0-9]{1,2})?)", notes, re.IGNORECASE)
                received = float(rx_received.group(2).replace(',', '.')) if rx_received else None
                change = float(rx_change.group(1).replace(',', '.')) if rx_change else None
                return received, change
            except Exception:
                return None, None

        # Formatar pedidos para o frontend
        formatted_orders = []
        for order in orders_data:
            # Buscar itens do pedido
            items_res = order_processor.supabase.table("order_items").select("*").eq("order_id", order["id"]).execute()
            items_data = getattr(items_res, "data", []) or []
            
            # Mapear status do banco para o frontend
            status_map = {
                "pending": "pendente",
                "confirmed": "confirmado",
                "processing": "preparando",
                "shipped": "enviado",
                "delivered": "entregue",
                "cancelled": "cancelado"
            }
            db_status = order.get("status", "pending")
            frontend_status = status_map.get(db_status, "pendente")
            
            # Extrair notas para valores de dinheiro/troco
            notes_text = order.get("notes", "") or ""
            cash_received, cash_change = _extract_cash_info(notes_text)

            formatted_orders.append({
                "id": order["id"],
                "customer": {
                    "name": order.get("customer_name", "Cliente"),
                    "phone": order.get("customer_phone", ""),
                    "address": order.get("customer_address", "")
                },
                "items": [
                    {
                        "name": item.get("product_descricao", "Produto"),
                        "quantity": item.get("quantity", 1),
                        "price": float(item.get("unit_price", 0))
                    }
                    for item in items_data
                ],
                "total": float(order.get("total", 0)),
                "status": frontend_status,
                "delivery_status": order.get("delivery_status", "pending"),
                "createdAt": order.get("created_at", ""),
                "estimatedDelivery": "45-60 min",
                "paymentMethod": order.get("payment_method", ""),
                # Campos extras para pagamento em dinheiro
                "cashReceived": cash_received,
                "cashChange": cash_change,
                "notes": notes_text
            })
        
        print(f"[API] Retornando {len(formatted_orders)} pedidos formatados")
        return {"orders": formatted_orders}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] Erro ao buscar pedidos: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pedidos: {str(e)}")

@app.get("/api/orders/{order_id}")
def get_order_by_id(order_id: int):
    """Retorna os detalhes de um pedido específico."""
    try:
        print(f"[API] GET /api/orders/{order_id} - Iniciando...")

        if not ORDER_PROCESSOR_AVAILABLE or order_processor is None:
            print("[API] ERROR: Order processor não disponível")
            raise HTTPException(status_code=503, detail="Sistema de pedidos não disponível")

        # Buscar pedido do Supabase
        order_res = order_processor.supabase.table("orders").select("*").eq("id", order_id).single().execute()
        order_data = getattr(order_res, "data", None)

        if not order_data:
            print(f"[API] ERROR: Pedido {order_id} não encontrado")
            raise HTTPException(status_code=404, detail="Pedido não encontrado")

        print(f"[API] Pedido {order_id} encontrado.")

        # Buscar itens do pedido
        items_res = order_processor.supabase.table("order_items").select("*").eq("order_id", order_id).execute()
        items_data = getattr(items_res, "data", []) or []
        print(f"[API] Itens do pedido encontrados: {len(items_data)}")

        # Formatar a resposta
        formatted_order = {
            "order": {
                "id": order_data["id"],
                "customer_name": order_data.get("customer_name", "Cliente"),
                "customer_phone": order_data.get("customer_phone", ""),
                "customer_address": order_data.get("customer_address", ""),
                "total": float(order_data.get("total", 0)),
                "status": order_data.get("status", "pending"),
                "delivery_status": order_data.get("delivery_status", "pending"),
                "created_at": order_data.get("created_at", ""),
                "payment_method": order_data.get("payment_method", ""),
                "payment_status": order_data.get("payment_status", "pending"),
                "notes": order_data.get("notes", "")
            },
            "items": [
                {
                    "product_descricao": item.get("product_descricao", "Produto"),
                    "quantity": item.get("quantity", 1),
                    "unit_price": float(item.get("unit_price", 0))
                }
                for item in items_data
            ]
        }

        print(f"[API] Retornando pedido {order_id} formatado.")
        return formatted_order

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] Erro ao buscar pedido {order_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pedido: {str(e)}")

@app.put("/api/orders/{order_id}/status")
def update_order_status(order_id: int, request: dict):
    """Atualiza o status de um pedido"""
    try:
        print(f"[API] PUT /api/orders/{order_id}/status")
        print(f"[API] Request body: {request}")
        
        if not ORDER_PROCESSOR_AVAILABLE or order_processor is None:
            print("[API] ERROR: Order processor não disponível")
            raise HTTPException(status_code=503, detail="Sistema de pedidos não disponível")
        
        new_status = request.get("status")
        if not new_status:
            raise HTTPException(status_code=400, detail="Status não fornecido")
        
        # Validar status
        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status inválido: {new_status}")
        
        print(f"[API] Atualizando pedido {order_id} para status: {new_status}")
        
        # Atualizar no Supabase
        result = order_processor.supabase.table("orders").update({
            "status": new_status,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", order_id).execute()
        
        if not result.data:
            print(f"[API] ERROR: Pedido {order_id} não encontrado")
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        print(f"[API] Pedido {order_id} atualizado com sucesso")
        return {
            "success": True,
            "message": "Status atualizado com sucesso",
            "order_id": order_id,
            "new_status": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] Erro ao atualizar status: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")

# Função auxiliar para enviar link do entregador via WhatsApp
async def send_delivery_link_to_driver(order_id: int, order_data: dict, base_url_override: Optional[str] = None):
    """Envia link da tela do entregador via Evolution API"""
    try:
        # Configurações da Evolution API
        EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "")
        EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
        EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "hakimfarma")
        # Carregar números de entregadores dinamicamente
        cfg = load_contacts_config()
        driver_phones = [p for p in (cfg.get("driver_phones") or []) if p]
        # Fallback: se não houver configuração, usar env ou default
        if not driver_phones:
            env_driver = os.getenv("DRIVER_PHONE", "5512976025888")
            driver_phones = [env_driver] if env_driver else ["5512976025888"]
        
        if not EVOLUTION_API_URL or not EVOLUTION_API_KEY:
            print("[WARNING] Evolution API não configurada")
            return
        
        # Construir URL da tela do entregador
        base_url = base_url_override or os.getenv("CLIENT_BASE_URL", "http://localhost:8000")
        
        # Limpar e construir URL corretamente
        # Se CLIENT_BASE_URL tem /catalogo.html, remover
        if '/catalogo.html' in base_url:
            base_url = base_url.split('/catalogo.html')[0]
        
        # Se não tem protocolo, adicionar https://
        if not base_url.startswith('http://') and not base_url.startswith('https://'):
            base_url = f"https://{base_url}"
        
        # Remover barra final se existir
        base_url = base_url.rstrip('/')

        # Validar se domínio parece válido para linkificação do WhatsApp
        try:
            parsed = urlparse(base_url)
            host = parsed.netloc or parsed.path
            # Se host não tem um ponto (TLD ausente), o WhatsApp pode não tornar clicável
            if host and '.' not in host and base_url_override:
                # Preferir override quando disponível (Origin/Host da requisição)
                base_url = base_url_override.rstrip('/')
        except Exception:
            # Em caso de parsing falho, manter base_url como está
            pass
        
        # Construir URL completa
        delivery_url = f"{base_url}/entregador.html?pedido={order_id}"
        
        print(f"[DEBUG] CLIENT_BASE_URL original: {os.getenv('CLIENT_BASE_URL')}")
        print(f"[DEBUG] Base URL processada: {base_url}")
        print(f"[DEBUG] URL final do entregador: {delivery_url}")
        
        # Construir mensagem
        customer_name = order_data.get("customer_name", "Cliente")
        customer_address = order_data.get("customer_address", "Endereço não informado")
        total = float(order_data.get("total", 0))
        
        message = f"""🚚 *Nova Entrega Disponível!*

📦 *Pedido #{order_id}*
👤 Cliente: {customer_name}
📍 Endereço: {customer_address}
💰 Valor: R$ {total:.2f}

🔗 Acesse os detalhes da entrega:
<{delivery_url}>

_Clique no link para ver o mapa e informações completas._"""
        
        # Preparar payload para Evolution API
        from urllib.parse import quote
        instance_segment = quote(EVOLUTION_INSTANCE_NAME, safe="")
        url = f"{EVOLUTION_API_URL}/message/sendText/{instance_segment}"
        
        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY
        }
        
        print(f"[WHATSAPP] Enviando link do entregador para {len(driver_phones)} número(s): {', '.join(driver_phones)}")
        print(f"[WHATSAPP] URL: {url}")
        print(f"[WHATSAPP] Link: {delivery_url}")
        
        results = []
        success_count = 0
        for phone in driver_phones:
            payload = {
                "number": phone,
                "text": message
            }
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                ok = 200 <= response.status_code < 300
                results.append({
                    "phone": phone,
                    "status_code": response.status_code,
                    "ok": ok,
                    "response": (response.json() if ok else response.text)
                })
                if ok:
                    success_count += 1
            except Exception as e:
                results.append({
                    "phone": phone,
                    "ok": False,
                    "error": str(e)
                })
        
        if success_count > 0:
            print(f"[WHATSAPP] Link enviado com sucesso para {success_count} entregador(es)")
            return {"success": True, "sent": success_count, "results": results}
        else:
            print(f"[WHATSAPP ERROR] Falha ao enviar link para todos os entregadores")
            return {"success": False, "sent": 0, "results": results}
            
    except Exception as e:
        print(f"[WHATSAPP ERROR] Exceção ao enviar link: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.put("/api/orders/{order_id}/delivery-status")
async def update_delivery_status(order_id: int, request: Request, payload: dict):
    """Atualiza o status de entrega de um pedido"""
    try:
        print(f"[API] PUT /api/orders/{order_id}/delivery-status")
        print(f"[API] Request body: {payload}")
        
        if not ORDER_PROCESSOR_AVAILABLE or order_processor is None:
            print("[API] ERROR: Order processor não disponível")
            raise HTTPException(status_code=503, detail="Sistema de pedidos não disponível")
        
        new_delivery_status = payload.get("delivery_status")
        if not new_delivery_status:
            raise HTTPException(status_code=400, detail="delivery_status não fornecido")
        
        # Validar delivery_status
        valid_delivery_statuses = [
            'pending', 'preparing', 'ready_for_pickup', 'in_transit', 
            'out_for_delivery', 'delivered', 'failed', 'returned'
        ]
        if new_delivery_status not in valid_delivery_statuses:
            raise HTTPException(status_code=400, detail=f"delivery_status inválido: {new_delivery_status}")
        
        print(f"[API] Atualizando pedido {order_id} para delivery_status: {new_delivery_status}")
        
        # Atualizar no Supabase
        result = order_processor.supabase.table("orders").update({
            "delivery_status": new_delivery_status,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", order_id).execute()
        
        if not result.data:
            print(f"[API] ERROR: Pedido {order_id} não encontrado")
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        print(f"[API] Pedido {order_id} delivery_status atualizado com sucesso")
        
        # Enviar link do entregador via WhatsApp quando status for in_transit ou out_for_delivery
        if new_delivery_status in ['in_transit', 'out_for_delivery']:
            try:
                # Construir base usando Origin/Host da requisição para garantir domínio válido
                origin = request.headers.get("origin")
                if not origin:
                    host = request.headers.get("host")
                    scheme = request.url.scheme
                    if host:
                        origin = f"{scheme}://{host}"
                    else:
                        # Fallback: usar base da própria URL da requisição sem path
                        origin = str(request.url).split(request.url.path)[0].rstrip('/')

                await send_delivery_link_to_driver(order_id, result.data[0], base_url_override=origin)
            except Exception as e:
                print(f"[WARNING] Erro ao enviar link para entregador: {str(e)}")
                # Não falha a requisição se o envio do WhatsApp falhar
        
        return {
            "success": True,
            "message": "Status de entrega atualizado com sucesso",
            "order_id": order_id,
            "new_delivery_status": new_delivery_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] Erro ao atualizar delivery_status: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar delivery_status: {str(e)}")

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

        # Usar delivery_status ao invés de status geral
        delivery_status = (order_data.get("delivery_status") or "pending").lower()
        
        # Timeline baseada no delivery_status
        timeline_steps = [
            {"key": "pending", "label": "Pedido recebido"},
            {"key": "preparing", "label": "Em preparação"},
            {"key": "ready_for_pickup", "label": "Pronto para retirada"},
            {"key": "out_for_delivery", "label": "Saiu para entrega"},
            {"key": "delivered", "label": "Entregue"},
        ]

        # Mapear delivery_status para índice da timeline
        status_map = {
            "pending": 0,
            "preparing": 1,
            "ready_for_pickup": 2,
            "in_transit": 3,
            "out_for_delivery": 3,
            "delivered": 4,
            "failed": 3,
            "returned": 3
        }
        
        status_index = status_map.get(delivery_status, 0)
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

        if delivery_status == "delivered":
            eta_text = "Entregue ✅"
        elif delivery_status == "failed":
            eta_text = "Falha na entrega ❌"
        elif delivery_status == "returned":
            eta_text = "Pedido devolvido ↩️"
        else:
            eta_text = f"Estimativa de entrega: ~{remaining_min}–{remaining_max} min"

        # Incluir delivery_status no retorno para o frontend usar
        order_data_with_status = {**order_data, "status": delivery_status}

        return {
            "order": order_data_with_status,
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

# -------------------- Proxy para API de Produção --------------------
@app.get("/api/proxy/produtos")
def proxy_produtos(sessao_id: Optional[str] = None):
    """Proxy simples para buscar produtos da API de produção, evitando CORS no navegador.
    Aceita opcionalmente o parâmetro sessao_id e repassa para a API de produção.
    """
    base_url = "https://hakimfarma.devsible.com.br/api/produtos"
    url = base_url if not sessao_id else f"{base_url}?sessao_id={sessao_id}"
    try:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Connection": "keep-alive"
        }
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        try:
            data = resp.json()
        except ValueError:
            raise HTTPException(status_code=500, detail="Resposta inválida da API de produção (não é JSON)")
        return data
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Falha ao buscar produtos na produção: {str(e)}")

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
            print(f"[DEBUG] Iniciando processamento de {len(result.data)} produtos...")
            for i, produto in enumerate(result.data):
                # Debug geral
                if i < 5:  # Primeiros 5 produtos
                    print(f"[DEBUG] Produto {i}: ID={produto.get('id')}, Desc={produto.get('descricao')}")
                
                # Obter valores básicos
                preco_raw = produto.get("preco") or produto.get("price", 0)
                desconto_raw = produto.get("desconto_percentual", 0) or 0
                
                try:
                    preco_atual = float(preco_raw)
                    percentual_desconto = float(desconto_raw)
                except (ValueError, TypeError) as e:
                    print(f"[ERROR] Erro na conversão para produto {produto.get('id')}: {e}")
                    preco_atual = 0.0
                    percentual_desconto = 0.0
                
                valor_desconto = produto.get("desconto_valor")
                
                # Debug específico para produto 2465302 (verificar tipo do ID)
                produto_id = produto.get("id")
                if produto_id == 2465302 or produto_id == "2465302" or str(produto_id) == "2465302":
                    print(f"[DEBUG 2465302] ENCONTRADO! ID: {produto_id} (tipo: {type(produto_id)})")
                    print(f"[DEBUG 2465302] Descrição: {produto.get('descricao')}")
                    print(f"[DEBUG 2465302] Preço atual: {preco_atual} (tipo: {type(preco_atual)})")
                    print(f"[DEBUG 2465302] Percentual desconto: {percentual_desconto} (tipo: {type(percentual_desconto)})")
                    print(f"[DEBUG 2465302] Condição percentual_desconto > 0: {percentual_desconto > 0}")
                
                # Calcular preço original se há desconto percentual
                preco_original = None
                if percentual_desconto > 0:
                    preco_original = preco_atual / (1 - percentual_desconto/100)
                    # Debug específico para produtos com desconto
                    if produto_id == 2465302 or produto_id == "2465302" or str(produto_id) == "2465302":
                        print(f"[DEBUG 2465302] Preço original calculado: {preco_original}")
                
                produto_formatado = {
                    "id": produto.get("id"),
                    "descricao": produto.get("descricao") or produto.get("nome") or produto.get("name"),
                    "apresentacao": produto.get("apresentacao") or produto.get("description"),
                    "preco": preco_atual,
                    "estoque": produto.get("estoque") or produto.get("stock", 0),
                    "imagem_url": produto.get("imagem_url") or produto.get("image_url"),
                    "categoria": produto.get("categoria") or produto.get("category"),
                    "laboratorio": produto.get("laboratorio") or produto.get("laboratory") or produto.get("brand"),
                    # Campos de desconto calculados corretamente
                    "preco_original": preco_original,
                    "percentual_desconto": percentual_desconto if percentual_desconto > 0 else None,
                    "valor_desconto": float(valor_desconto) if valor_desconto else None
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

# -------------------- Auto Close / Follow-up Worker --------------------

def _parse_iso_dt(ts) -> Optional[datetime]:
    try:
        if isinstance(ts, str):
            if ts.endswith("Z"):
                ts = ts.replace("Z", "+00:00")
            return datetime.fromisoformat(ts)
    except Exception:
        return None
    return None

def _compose_followup_message(order: Dict[str, any]) -> str:
    name = (order.get("customer_name") or "cliente").strip()
    order_id = order.get("id")
    total = float(order.get("total") or 0)
    return (
        f"Olá {name}! 👋\n"
        f"Estamos acompanhando seu pedido #{order_id}. Ainda não recebemos confirmação de entrega.\n"
        f"Total: R$ {total:.2f}. Se já recebeu, tudo certo ✅.\n"
        f"Se houve algum problema, responda aqui para te ajudarmos. 🧪💊"
    )

def _compose_autoclose_message(order: Dict[str, any]) -> str:
    name = (order.get("customer_name") or "cliente").strip()
    order_id = order.get("id")
    return (
        f"Oi {name}! ⏱️\n"
        f"Encerramos automaticamente o pedido #{order_id} após 3 horas sem confirmação de entrega.\n"
        f"Se você não recebeu ou precisa reabrir, responda esta mensagem que resolvemos rapidinho. 💬"
    )

async def _auto_close_loop():
    if not ORDER_PROCESSOR_AVAILABLE or order_processor is None:
        print("[AUTO CLOSE] Order processor indisponível; worker não será iniciado")
        return
    print("[AUTO CLOSE] Worker iniciado. Intervalo:", AUTO_CLOSE_CHECK_INTERVAL_SECONDS, "s")
    while True:
        try:
            res = order_processor.supabase.table("orders").select("*").execute()
            orders = getattr(res, "data", []) or []
            now = datetime.utcnow()
            checked = 0
            for order in orders:
                try:
                    status = (order.get("status") or "pending").lower()
                    dstatus = (order.get("delivery_status") or "pending").lower()
                    notes = (order.get("notes") or "")
                    created_dt = _parse_iso_dt(order.get("created_at"))
                    if not created_dt:
                        continue
                    elapsed_hours = (now - created_dt).total_seconds() / 3600.0

                    # Follow-up (uma vez)
                    if (
                        elapsed_hours >= FOLLOWUP_AFTER_HOURS
                        and "[FOLLOWUP_3H_SENT]" not in notes
                        and dstatus != "delivered"
                        and status != "cancelled"
                    ):
                        phone = order.get("customer_phone") or None
                        if phone:
                            try:
                                order_processor._send_whatsapp_message(_compose_followup_message(order), phone)  # type: ignore
                                notes = (notes + f"\n[FOLLOWUP_3H_SENT] {now.isoformat()}").strip()
                                order_processor.supabase.table("orders").update({"notes": notes}).eq("id", order["id"]).execute()
                                print(f"[AUTO CLOSE] Follow-up enviado para pedido {order['id']}")
                            except Exception as e:
                                print(f"[AUTO CLOSE] Erro ao enviar follow-up para {order.get('id')}: {e}")

                    # Encerramento automático (uma vez)
                    if (
                        elapsed_hours >= AUTO_CLOSE_AFTER_HOURS
                        and "[AUTO_CLOSED_3H]" not in notes
                        and dstatus != "delivered"
                        and status != "cancelled"
                    ):
                        phone = order.get("customer_phone") or None
                        if phone:
                            try:
                                order_processor._send_whatsapp_message(_compose_autoclose_message(order), phone)  # type: ignore
                            except Exception as e:
                                print(f"[AUTO CLOSE] Erro ao enviar mensagem de encerramento para {order.get('id')}: {e}")

                        updated = {
                            "status": "cancelled",
                            "delivery_status": "failed",
                            "notes": (notes + f"\n[AUTO_CLOSED_3H] {now.isoformat()}").strip()
                        }
                        try:
                            order_processor.supabase.table("orders").update(updated).eq("id", order["id"]).execute()
                            print(f"[AUTO CLOSE] Pedido {order['id']} encerrado automaticamente")
                        except Exception as e:
                            print(f"[AUTO CLOSE] Erro ao atualizar pedido {order.get('id')}: {e}")
                finally:
                    checked += 1
            print(f"[AUTO CLOSE] Loop: {checked} pedidos verificados")
        except Exception as e:
            print(f"[AUTO CLOSE] Erro no loop principal: {e}")
        await asyncio.sleep(AUTO_CLOSE_CHECK_INTERVAL_SECONDS)

@app.on_event("startup")
async def _start_auto_close_worker():
    try:
        asyncio.create_task(_auto_close_loop())
    except Exception as e:
        print(f"[AUTO CLOSE] Falha ao iniciar worker: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)