# 🛍️ Sistema de Catálogo de Produtos

Um sistema web moderno para gerenciamento de catálogos de produtos com sessões temporárias e seleção de itens.

## 🚀 Funcionalidades

- ✨ Interface web responsiva e moderna
- 🔄 Sessões temporárias com validade configurável
- 📱 Design mobile-first
- 🐳 Deploy com Docker
- 🔒 Configurações de segurança
- 📊 API RESTful com FastAPI

## 🛠️ Tecnologias

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Deploy**: Docker, Docker Compose

## 🏃‍♂️ Desenvolvimento Local

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (opcional)

### Método 1: Executar diretamente

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd catalog

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env conforme necessário

# 5. Execute o backend
python -m backend.app

# 6. Em outro terminal, sirva o frontend
python -m http.server 5500
```

Acesse: http://localhost:5500/catalogo.html

### Método 2: Docker Compose (Recomendado)

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd catalog

# 2. Configure as variáveis de ambiente
cp .env.example .env

# 3. Execute com Docker Compose
docker-compose up --build

# Para executar em background
docker-compose up -d --build
```

Acesse: http://localhost:3000

## 🌐 Deploy em Produção

### 1. Preparação do Servidor

```bash
# Instale Docker e Docker Compose no servidor
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instale Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Configuração de Produção

```bash
# 1. Clone o projeto no servidor
git clone <seu-repositorio>
cd catalog

# 2. Configure as variáveis de ambiente para produção
cp .env.example .env
nano .env
```

Exemplo de `.env` para produção:
```env
DB_URL=postgresql://usuario:senha@localhost:5432/catalog_db
CLIENT_BASE_URL=https://seu-dominio.com
ALLOWED_ORIGIN=https://seu-dominio.com
SESSION_VALIDITY_HOURS=4
PORT=8000
```

### 3. Docker Compose para Produção

Crie um `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/data
    restart: unless-stopped
    depends_on:
      - db

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./catalogo.html:/usr/share/nginx/html/catalogo.html
      - ./nginx.prod.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl  # Para certificados SSL
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: catalog_db
      POSTGRES_USER: usuario
      POSTGRES_PASSWORD: senha_segura
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### 4. Execute em Produção

```bash
# Execute com o arquivo de produção
docker-compose -f docker-compose.prod.yml up -d --build

# Verifique os logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `DB_URL` | URL do banco de dados | `sqlite:///./backend_data.db` |
| `CLIENT_BASE_URL` | URL base do cliente | `http://localhost:5500` |
| `ALLOWED_ORIGIN` | Origem permitida para CORS | `http://localhost:5500` |
| `SESSION_VALIDITY_HOURS` | Validade da sessão em horas | `4` |
| `PORT` | Porta do servidor | `8000` |

### Frontend - API_BASE

O frontend detecta automaticamente o ambiente:
- **Desenvolvimento**: `http://localhost:8000`
- **Produção**: `https://api.seu-dominio.com`

Para personalizar, edite a constante `API_BASE` em `catalogo.html`.

## 📡 API Endpoints

### Produtos
- `GET /api/produtos` - Lista todos os produtos
- `GET /api/produtos/{session_id}` - Lista produtos de uma sessão

### Sessões
- `POST /api/produtos/{session_id}/selecionar` - Seleciona produtos em uma sessão

### Saúde
- `GET /health` - Verifica saúde da aplicação

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de CORS**
   - Verifique se `ALLOWED_ORIGIN` está configurado corretamente
   - Certifique-se de que o frontend está acessando a URL correta

2. **Banco de dados não conecta**
   - Verifique a `DB_URL` no arquivo `.env`
   - Para PostgreSQL, certifique-se de que o banco existe

3. **Docker não inicia**
   - Verifique se as portas 3000 e 8000 estão livres
   - Execute `docker-compose logs` para ver os erros

### Logs

```bash
# Ver logs do backend
docker-compose logs backend

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs frontend
```

## 🔒 Segurança

- ✅ Headers de segurança configurados
- ✅ CORS configurado adequadamente
- ✅ Validação de dados de entrada
- ✅ Sessões com tempo de expiração
- ✅ Sanitização de inputs

## 📈 Monitoramento

O sistema inclui um endpoint de saúde em `/health` que pode ser usado para:
- Health checks do Docker
- Monitoramento com ferramentas como Prometheus
- Load balancers

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique a seção de [Troubleshooting](#-troubleshooting)
2. Consulte os logs da aplicação
3. Abra uma issue no repositório

---

Feito com ❤️ e muito ☕