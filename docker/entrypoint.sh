#!/bin/bash
set -e

# Script de inicialização para produção
echo "🚀 Starting Fabrica de Livros API v2.0.0"
echo "Environment: ${ENVIRONMENT:-production}"

# Aguardar banco de dados
echo "⏳ Waiting for database..."
until pg_isready -h "${DATABASE_HOST:-postgres}" -p "${DATABASE_PORT:-5432}" -U "${DATABASE_USER:-postgres}"; do
  echo "Database is unavailable - sleeping"
  sleep 2
done
echo "✅ Database is ready!"

# Aguardar Redis
echo "⏳ Waiting for Redis..."
until redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" ping | grep -q PONG; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is ready!"

# Executar migrações apenas se for o processo principal
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "📊 Running database migrations..."
  alembic upgrade head
  echo "✅ Migrations completed!"
fi

# Criar diretório de logs se não existir
mkdir -p logs
echo "📝 Logs directory ready"

# Log de inicialização
echo "🏁 Starting application with command: $@"

# Executar comando fornecido
exec "$@"