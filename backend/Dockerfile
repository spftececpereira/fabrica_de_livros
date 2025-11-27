# Multi-stage Dockerfile para otimizar produção
FROM python:3.12-slim AS base

# Definir argumentos de build
ARG ENVIRONMENT=production
ARG BUILD_DATE
ARG VCS_REF

# Labels para metadados da imagem
LABEL maintainer="Fabrica de Livros Team" \
      version="2.0.0" \
      description="API da Fábrica de Livros - Geração de livros infantis com IA" \
      build-date=$BUILD_DATE \
      vcs-ref=$VCS_REF \
      environment=$ENVIRONMENT

# Configurar variáveis de ambiente Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Criar diretórios necessários
RUN mkdir -p /app/logs && \
    chown -R appuser:appgroup /app

WORKDIR /app

# ===== STAGE: Development =====
FROM base AS development

# Instalar dependências de desenvolvimento
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código fonte
COPY --chown=appuser:appgroup . .

# Mudar para usuário não-root
USER appuser

# Comando para desenvolvimento (com reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ===== STAGE: Production =====
FROM base AS production

# Instalar dependências de produção
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt gunicorn && \
    pip cache purge

# Copiar código fonte (apenas necessário)
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini ./

# Mudar para usuário não-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expor porta
EXPOSE 8000

# Comando de produção
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
