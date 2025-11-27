# 🚀 **GUIA DE DEPLOY - FÁBRICA DE LIVROS V2**

## 📋 **Visão Geral**

Este documento detalha o processo completo de deploy para os ambientes de desenvolvimento e produção da Fábrica de Livros v2.

## 🏗️ **Arquitetura de Deploy**

### **Ambientes Disponíveis**
- **Development**: Para desenvolvimento local e testes
- **Staging**: Para testes de integração e validação
- **Production**: Ambiente de produção com alta disponibilidade

### **Estratégias de Deploy**
- **Development**: Hot reload com volumes montados
- **Staging**: Deploy automático via CI/CD
- **Production**: Deploy Blue-Green com aprovação manual

---

## 🔧 **PRÉ-REQUISITOS**

### **Ferramentas Necessárias**
- Docker 24.0+
- Docker Compose 2.0+
- Git
- curl (para health checks)

### **Variáveis de Ambiente Obrigatórias**

#### **Development**
```bash
# Automáticas via docker compose.yml
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/fabrica_livros_dev
REDIS_URL=redis://redis:6379/0
SECRET_KEY=dev-secret-key-change-in-production
```

#### **Production**
```bash
# Configurar antes do deploy
export DATABASE_URL="postgresql://user:pass@host:port/db"
export REDIS_URL="redis://host:port/0"
export SECRET_KEY="sua-chave-super-secreta"
export CORS_ORIGINS="https://app.fabrica-livros.com"
export GEMINI_API_KEY="sua-chave-gemini"
export ACME_EMAIL="admin@fabrica-livros.com"
export API_HOST="api.fabrica-livros.com"
export VERSION="2.0.0"
export POSTGRES_DB="fabrica_livros"
export POSTGRES_USER="fabrica_user"
export POSTGRES_PASSWORD="senha-super-secreta"
export GRAFANA_ADMIN_PASSWORD="admin-password"
```

---

## 🏃‍♂️ **DEPLOY DEVELOPMENT**

### **Deploy Rápido**
```bash
# Clone do repositório
git clone https://github.com/seu-usuario/fabrica-de-livros.git
cd fabrica-de-livros

# Executar script de deploy
chmod +x scripts/deploy-dev.sh
./scripts/deploy-dev.sh
```

### **Deploy Manual**
```bash
# 1. Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# 2. Iniciar serviços
docker compose up -d

# 3. Verificar health
curl http://localhost:8000/health
```

### **Deploy com Limpeza**
```bash
# Remover containers e volumes antigos
./scripts/deploy-dev.sh --clean
```

### **Serviços Disponíveis**
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Logs**: `docker compose logs -f backend`

---

## 🏭 **DEPLOY PRODUCTION**

### **Pré-Deploy Checklist**
- [ ] Backup do banco de dados
- [ ] Variáveis de ambiente configuradas
- [ ] Certificados SSL válidos
- [ ] Monitoramento funcionando
- [ ] Rollback plan definido

### **Deploy Standard**
```bash
# 1. Configurar variáveis (ver seção de pré-requisitos)
# 2. Executar deploy
chmod +x scripts/deploy-prod.sh
./scripts/deploy-prod.sh
```

### **Deploy Blue-Green**
```bash
# Deploy com zero downtime
./scripts/deploy-prod.sh --blue-green
```

### **Rollback**
```bash
# Voltar para versão anterior
./scripts/deploy-prod.sh --rollback
```

### **Serviços em Produção**
- **API**: https://api.fabrica-livros.com
- **Frontend**: https://app.fabrica-livros.com
- **Grafana**: https://monitoring.fabrica-livros.com:3001
- **Prometheus**: https://monitoring.fabrica-livros.com:9090

---

## 🔄 **CI/CD PIPELINE**

### **Fluxo Automático**

```mermaid
graph LR
    A[Push Code] --> B[Run Tests]
    B --> C[Build Image]
    C --> D{Branch?}
    D -->|develop| E[Deploy Dev]
    D -->|main| F[Deploy Staging]
    F --> G[Integration Tests]
    G --> H[Manual Approval]
    H --> I[Deploy Production]
    I --> J[Smoke Tests]
```

### **Triggers de Deploy**
- **Development**: Push para branch `develop`
- **Staging**: Push de tags `v*` (ex: v2.0.0)
- **Production**: Aprovação manual após staging

### **Secrets Necessários no GitHub**
```
STAGING_DATABASE_URL
STAGING_REDIS_URL
STAGING_SECRET_KEY

PROD_DATABASE_URL
PROD_REDIS_URL
PROD_SECRET_KEY
PROD_CORS_ORIGINS
PROD_GEMINI_API_KEY
PROD_API_HOST
PROD_ACME_EMAIL

SLACK_WEBHOOK (opcional)
```

---

## 📊 **MONITORAMENTO E SAÚDE**

### **Health Checks Disponíveis**
```bash
# Health básico
curl https://api.fabrica-livros.com/health

# Health detalhado
curl https://api.fabrica-livros.com/health/detailed

# Métricas (admin only)
curl https://api.fabrica-livros.com/metrics
```

### **Dashboards de Monitoramento**
- **Grafana**: Métricas de sistema e aplicação
- **Prometheus**: Coleta de métricas
- **Loki**: Agregação de logs
- **Alertmanager**: Alertas automáticos

### **Logs Estruturados**
```bash
# Ver logs em tempo real
docker compose logs -f backend

# Logs por categoria
docker exec fabrica-api-prod tail -f /app/logs/application.log
docker exec fabrica-api-prod tail -f /app/logs/security.log
docker exec fabrica-api-prod tail -f /app/logs/audit.log
```

---

## 🔐 **SEGURANÇA E BACKUP**

### **Backup Automático**
```bash
# Backup manual
docker compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker compose exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB < backup_file.sql
```

### **Rotação de Secrets**
1. Gerar nova SECRET_KEY
2. Atualizar variáveis de ambiente
3. Restart rolling dos containers
4. Verificar logs de autenticação

### **Certificados SSL**
- **Automático**: Let's Encrypt via Traefik
- **Renovação**: Automática a cada 60 dias
- **Monitoramento**: Alertas de expiração

---

## 🚨 **TROUBLESHOOTING**

### **Problemas Comuns**

#### **1. Container não inicia**
```bash
# Verificar logs
docker compose logs backend

# Verificar recursos
docker stats

# Verificar network
docker network ls
```

#### **2. Banco de dados não conecta**
```bash
# Testar conexão
docker compose exec backend pg_isready -h postgres -p 5432 -U postgres

# Verificar logs do PostgreSQL
docker compose logs postgres
```

#### **3. Redis não disponível**
```bash
# Testar Redis
docker compose exec backend redis-cli -h redis ping

# Verificar logs
docker compose logs redis
```

#### **4. Tasks Celery não processam**
```bash
# Verificar workers
docker compose exec celery-worker celery -A app.worker.celery_app inspect active

# Verificar fila
docker compose exec celery-worker celery -A app.worker.celery_app inspect reserved
```

### **Comandos de Debug**
```bash
# Entrar no container
docker compose exec backend bash

# Verificar variáveis de ambiente
docker compose exec backend printenv

# Testar conectividade
docker compose exec backend curl -f http://localhost:8000/health
```

---

## 📈 **ESCALABILIDADE**

### **Horizontal Scaling**
```yaml
# Adicionar replicas no docker compose
backend:
  deploy:
    replicas: 3
    
celery-worker:
  deploy:
    replicas: 5
```

### **Kubernetes Ready**
- Health checks configurados
- Resource limits definidos
- ConfigMaps para configuração
- Secrets para dados sensíveis

---

## 🔄 **VERSIONAMENTO E RELEASES**

### **Semantic Versioning**
- **Major**: Mudanças quebradoras (v2.0.0)
- **Minor**: Novas funcionalidades (v2.1.0)
- **Patch**: Bug fixes (v2.1.1)

### **Processo de Release**
1. Criar branch `release/v2.x.x`
2. Atualizar `VERSION` no código
3. Fazer merge para `main`
4. Criar tag `git tag v2.x.x`
5. Push da tag `git push origin v2.x.x`
6. CI/CD automaticamente deploya

---

## 📚 **DOCUMENTAÇÃO ADICIONAL**

- **API Docs**: `/docs` (Swagger UI)
- **Health Checks**: `/health/detailed`
- **Métricas**: `/metrics` (Prometheus format)
- **Logs Admin**: `/admin/logs/*` (apenas admins)

---

## 🆘 **SUPORTE E CONTATO**

- **Logs de Error**: Verificar `/app/logs/error.log`
- **Alertas**: Configurados no Slack/Discord
- **Rollback**: Sempre disponível com `--rollback`
- **Backup**: Automático a cada deploy

**🎯 Deploy realizado com sucesso quando todos os health checks passarem e métricas estiverem normais!**