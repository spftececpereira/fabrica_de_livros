#!/bin/bash
set -e

# Script de deploy para produção
echo "🚀 Deploy - Ambiente de Produção"
echo "================================"

# Verificações de segurança
if [[ "$USER" == "root" ]]; then
    echo "❌ Não execute este script como root por segurança!"
    exit 1
fi

# Verificar se todas as variáveis necessárias estão definidas
REQUIRED_VARS=(
    "DATABASE_URL"
    "REDIS_URL"
    "SECRET_KEY"
    "CORS_ORIGINS"
    "GEMINI_API_KEY"
    "ACME_EMAIL"
    "API_HOST"
    "VERSION"
)

missing_vars=()
for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var}" ]]; then
        missing_vars+=("$var")
    fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
    echo "❌ Variáveis de ambiente obrigatórias não definidas:"
    printf '   %s\n' "${missing_vars[@]}"
    echo ""
    echo "Configure essas variáveis antes de fazer deploy:"
    echo "export DATABASE_URL='postgresql://user:pass@host:port/db'"
    echo "export REDIS_URL='redis://host:port/0'"
    echo "export SECRET_KEY='sua-chave-super-secreta'"
    echo "export CORS_ORIGINS='https://app.fabrica-livros.com'"
    echo "export GEMINI_API_KEY='sua-chave-gemini'"
    echo "export ACME_EMAIL='admin@fabrica-livros.com'"
    echo "export API_HOST='api.fabrica-livros.com'"
    echo "export VERSION='2.0.0'"
    exit 1
fi

# Definir variáveis
COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="fabrica-livros-prod"
BACKUP_DIR="/opt/fabrica-livros/backups"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse HEAD 2>/dev/null || echo "unknown")

# Exportar variáveis para docker-compose
export BUILD_DATE
export VCS_REF

# Função para logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Função para backup
backup_database() {
    log "💾 Fazendo backup do banco de dados..."
    mkdir -p $BACKUP_DIR
    
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
    
    if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_FILE; then
        log "✅ Backup salvo em: $BACKUP_FILE"
        
        # Manter apenas os 10 backups mais recentes
        cd $BACKUP_DIR && ls -t backup_*.sql | tail -n +11 | xargs -r rm
    else
        log "❌ Falha no backup do banco de dados!"
        exit 1
    fi
}

# Verificar modo de deploy
if [[ "$1" == "--blue-green" ]]; then
    log "🔵 Iniciando deploy Blue-Green..."
    DEPLOY_MODE="blue-green"
elif [[ "$1" == "--rollback" ]]; then
    log "↩️ Iniciando rollback..."
    DEPLOY_MODE="rollback"
else
    log "⚡ Iniciando deploy padrão..."
    DEPLOY_MODE="standard"
fi

# Health check function
health_check() {
    local service_url=$1
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$service_url/health" > /dev/null; then
            return 0
        fi
        echo "Health check tentativa $attempt/$max_attempts..."
        sleep 10
        ((attempt++))
    done
    return 1
}

# Deploy baseado no modo
case $DEPLOY_MODE in
    "blue-green")
        log "🔵 Implementando estratégia Blue-Green..."
        
        # Fazer backup antes de qualquer mudança
        backup_database
        
        # Build da nova versão
        log "🏗️ Fazendo build da versão $VERSION..."
        docker-compose -f $COMPOSE_FILE -p "${PROJECT_NAME}-green" build
        
        # Iniciar ambiente Green
        log "🟢 Iniciando ambiente Green..."
        docker-compose -f $COMPOSE_FILE -p "${PROJECT_NAME}-green" up -d
        
        # Health check do ambiente Green
        log "🔍 Verificando health do ambiente Green..."
        if health_check "http://localhost:8001"; then
            log "✅ Ambiente Green está saudável!"
            
            # Parar ambiente Blue
            log "🔵 Parando ambiente Blue (antigo)..."
            docker-compose -f $COMPOSE_FILE -p "${PROJECT_NAME}-blue" down
            
            # Renomear Green para Blue
            log "🔄 Promovendo Green para Blue..."
            # Implementar lógica de troca de portas/load balancer aqui
            
        else
            log "❌ Health check falhou no ambiente Green!"
            log "🧹 Removendo ambiente Green com falha..."
            docker-compose -f $COMPOSE_FILE -p "${PROJECT_NAME}-green" down
            exit 1
        fi
        ;;
        
    "rollback")
        log "↩️ Fazendo rollback para versão anterior..."
        
        # Parar versão atual
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down
        
        # Restaurar backup mais recente
        LATEST_BACKUP=$(ls -t $BACKUP_DIR/backup_*.sql 2>/dev/null | head -n1)
        if [[ -n "$LATEST_BACKUP" ]]; then
            log "📥 Restaurando backup: $LATEST_BACKUP"
            # Implementar lógica de restore aqui
        fi
        
        # Iniciar versão anterior
        # Implementar lógica para versão anterior aqui
        ;;
        
    "standard")
        # Fazer backup
        if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps | grep -q postgres; then
            backup_database
        fi
        
        # Build das imagens
        log "🏗️ Fazendo build das imagens versão $VERSION..."
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME build --pull
        
        # Parar serviços de aplicação (manter infra)
        log "🛑 Parando serviços de aplicação..."
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME stop backend celery-worker celery-beat
        
        # Iniciar serviços atualizados
        log "⚡ Iniciando serviços atualizados..."
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
        
        # Health check
        log "🔍 Verificando health dos serviços..."
        if health_check "http://localhost:8000"; then
            log "✅ Deploy concluído com sucesso!"
        else
            log "❌ Health check falhou após deploy!"
            exit 1
        fi
        ;;
esac

# Mostrar status final
log "📊 Status final dos containers:"
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps

# Limpeza de imagens antigas
log "🧹 Limpando imagens antigas..."
docker image prune -f

echo ""
echo "🎉 Deploy de produção concluído!"
echo ""
echo "🌐 Serviços em produção:"
echo "   API: https://$API_HOST"
echo "   Health: https://$API_HOST/health"
echo ""
echo "📊 Monitoramento:"
echo "   Grafana: http://localhost:3001"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "🔧 Comandos úteis:"
echo "   Ver logs: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f [service]"
echo "   Backup manual: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec postgres pg_dump..."
echo "   Rollback: $0 --rollback"
echo ""
echo "📋 Próximos passos:"
echo "   1. Verificar métricas no Grafana"
echo "   2. Monitorar logs por possíveis erros"
echo "   3. Testar funcionalidades críticas"
echo ""