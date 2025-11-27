#!/bin/bash
set -e

# Script de deploy para ambiente de desenvolvimento
echo "🚀 Deploy - Ambiente de Desenvolvimento"
echo "======================================"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Definir variáveis
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="fabrica_de_livros"
BACKEND_CONTAINER="fabrica-api-dev"
CELERY_CONTAINER="fabrica-celery-dev"
POSTGRES_CONTAINER="fabrica-postgres-dev"
REDIS_CONTAINER="fabrica-redis-dev"

# Função para logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Limpar containers antigos se solicitado
if [[ "$1" == "--clean" ]]; then
    log "🧹 Limpando containers e volumes antigos..."
    docker compose -f $COMPOSE_FILE down -v --remove-orphans
    docker system prune -f
fi

# Parar containers se estiverem rodando
log "🛑 Parando containers existentes..."
docker compose -f $COMPOSE_FILE down

# Build das imagens
log "🏗️ Fazendo build das imagens..."
docker compose -f $COMPOSE_FILE build --no-cache

# Verificar se .env existe
if [ ! -f .env ]; then
    log "📝 Criando arquivo .env a partir do exemplo..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANTE: Configure as variáveis em .env antes de continuar"
    echo "   Principais configurações para desenvolvimento:"
    echo "   - GEMINI_API_KEY=sua_chave_aqui"
    echo "   - OPENAI_API_KEY=sua_chave_aqui (opcional)"
    echo ""
    read -p "Pressione Enter para continuar após configurar o .env..."
fi

# Iniciar serviços de infraestrutura primeiro
log "📊 Iniciando serviços de infraestrutura..."
docker compose -f $COMPOSE_FILE up -d postgres redis

# Aguardar serviços ficarem prontos
log "⏳ Aguardando serviços de infraestrutura..."
sleep 10

# Verificar se PostgreSQL está pronto
log "🔍 Verificando PostgreSQL..."
until docker exec $POSTGRES_CONTAINER pg_isready -U postgres; do
    echo "PostgreSQL ainda não está pronto - aguardando..."
    sleep 2
done

# Verificar se Redis está pronto
log "🔍 Verificando Redis..."
until docker exec $REDIS_CONTAINER redis-cli ping | grep -q PONG; do
    echo "Redis ainda não está pronto - aguardando..."
    sleep 2
done

# Iniciar backend
log "⚡ Iniciando backend..."
docker compose -f $COMPOSE_FILE up -d

# Aguardar backend ficar pronto
log "⏳ Aguardando backend..."
sleep 15

# Verificar health do backend
log "🔍 Verificando health do backend..."
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo "Backend ainda não está pronto - aguardando..."
    sleep 5
done

# Iniciar workers Celery
log "👷 Iniciando Celery workers..."
docker compose -f $COMPOSE_FILE up -d celery-worker

# Mostrar status dos containers
log "📊 Status dos containers:"
docker compose -f $COMPOSE_FILE ps

# Mostrar logs do backend
log "📝 Últimas linhas do log do backend:"
docker compose -f $COMPOSE_FILE logs --tail=20 backend

echo ""
echo "✅ Deploy de desenvolvimento concluído!"
echo ""
echo "🌐 Serviços disponíveis:"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo ""
echo "📊 Monitoramento:"
echo "   PostgreSQL: localhost:5432"
echo "   Redis: localhost:6379"
echo ""
echo "🔧 Comandos úteis:"
echo "   Ver logs: docker compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f [service]"
echo "   Parar: docker compose -f $COMPOSE_FILE -p $PROJECT_NAME down"
echo "   Rebuild: $0 --clean"
echo ""
echo "🎯 Para desenvolvimento frontend:"
echo "   cd frontend && npm run dev"
echo ""