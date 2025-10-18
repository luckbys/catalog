FROM python:3.13-slim

# Definir diretório de trabalho
WORKDIR /app

# Variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Copiar código da aplicação
COPY . /app

# Criar diretório para dados persistentes
RUN mkdir -p /data

# Definir porta padrão
ENV PORT=8000

# Expor porta
EXPOSE $PORT

# Comando para iniciar a aplicação
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]