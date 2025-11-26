# Product Requirements Document (PRD)
## Fábrica de Livros - Plataforma de Geração de Livros Infantis com IA

**Versão:** 2.0  
**Data:** Novembro 2025  
**Status:** In Progress  
**Escopo:** Redevelopment com Backend Python + PostgreSQL e Frontend Moderno

---

## 1. Visão Geral Executiva

### 1.1 Objetivo do Produto

Recrear e melhorar a plataforma "Fábrica de Livros" como um sistema moderno, escalável e robusto para geração de livros de colorir personalizados utilizando inteligência artificial. A plataforma permitirá que usuários criem livros únicos com histórias educativas, múltiplos estilos artísticos e funcionalidades gamificadas.

### 1.2 Problema

- Plataforma atual construída em Next.js com backend Node.js/TypeScript
- Necessidade de migração para stack mais robusta: Python (FastAPI) + PostgreSQL
- Integração simplificada com múltiplos provedores de IA (Gemini, OpenRouter)
- Facilidade de troca entre diferentes modelos e plataformas de IA
- Arquitetura não otimizada para processamento assíncrono de geração de imagens e textos

### 1.3 Solução Proposta

Desenvolver uma plataforma completa com:
- **Backend:** Python 3.12+ com FastAPI, SQLAlchemy ORM, PostgreSQL
- **Frontend:** Next.js 15+ com React 19, TypeScript, Tailwind CSS (baseado em referências modernas)
- **IA Integration:** Camada abstrata para Gemini API e OpenRouter
- **Processamento:** Celery + Redis para processamento assíncrono de jobs
- **Infraestrutura:** Docker, Kubernetes-ready, CI/CD com GitHub Actions
- **Observabilidade:** OpenTelemetry, logging estruturado, monitoring

---

## 2. Escopo do Produto

### 2.1 Funcionalidades Principais

#### 2.1.1 Autenticação e Gerenciamento de Usuários
- Login com Google OAuth (Supabase Auth ou Auth.js)
- Registro de usuários (social e manual)
- Perfil de usuário com preferências
- Integração com PostgreSQL para persistência
- Rate limiting por usuário
- Sessions com JWT refresh tokens

#### 2.1.2 Criação de Livros
- **Seleção de Estilo Artístico:** Cartoon, Mangá, Realista, Clássico (expansível)
- **Configuração de Tamanho:** 5 a 20 páginas (configurável)
- **Narrativa:** Upload ou geração automática de histórias educativas
- **Geração Inteligente:**
  - Geração de texto com Gemini ou OpenRouter
  - Geração de imagens com base na narrativa
  - Processamento assíncrono com feedback em tempo real
- **Validação:** Validação de entrada, limits de recursos por usuário tier

#### 2.1.3 Biblioteca Pessoal
- Galeria de livros criados pelo usuário
- Busca e filtros (por estilo, data, status)
- Visualização detalhada de cada livro
- Edição de livros existentes
- Deleção com soft delete (retenção de dados para auditoria)

#### 2.1.4 Gamificação
- **Sistema de Badges:** 10+ tipos de conquistas
- **Pontos de Experiência:** Acumulação baseada em ações
- **Leaderboards:** Rankings globais e amigos
- **Desafios:** Missions diárias/semanais
- **Progresso em Tempo Real:** Dashboard com métricas

#### 2.1.5 Exportação e Download
- **Formato PDF:** Alta qualidade para impressão
- **Formato Digital:** Para leitura em telas
- **Compressão Inteligente:** Otimização de tamanho
- **Cache de Downloads:** Reuso de PDFs já gerados

#### 2.1.6 Administração
- Dashboard administrativo
- Monitoramento de jobs de IA
- Gerenciamento de quotas e limites
- Analytics de uso
- Logs de auditoria

### 2.2 Funcionalidades Secundárias

- Compartilhamento de livros (links públicos com expiração)
- Impressão direta (integração com serviços de print-on-demand)
- API pública para integrações
- Webhooks para eventos importantes
- Exportação de dados do usuário (GDPR compliance)

### 2.3 Restrições e Limites

| Aspecto | Limite |
|--------|--------|
| Páginas por livro | 5-20 |
| Tamanho máximo da história | 10,000 caracteres |
| Tamanho máximo de upload | 50 MB |
| Tempo máximo de geração | 5 minutos (com retry) |
| Livros simultâneos por usuário | 3 (tier padrão) |
| Requests por dia | 50 (tier padrão, escalável) |
| Tamanho do PDF final | 100 MB máximo |

---

## 3. Arquitetura Técnica

### 3.1 Stack Tecnológico Recomendado

#### Backend
```
- Runtime: Python 3.12.x
- Framework: FastAPI 0.115+
- ORM: SQLAlchemy 2.x com Async support
- Driver DB: asyncpg (PostgreSQL async)
- Migrations: Alembic
- Task Queue: Celery 5.x
- Message Broker: Redis 7.x
- Validation: Pydantic v2 (built-in FastAPI)
- API Documentation: Swagger/OpenAPI (built-in)
- Authentication: python-jose, bcrypt, PyJWT
- HTTP Client: httpx (async/await support)
```

#### Banco de Dados
```
- PostgreSQL 15+
- PostGIS (opcional, para geolocalização)
- Connection Pooling: pgBouncer ou built-in SQLAlchemy
- Backups: pg_dump automated, S3 storage
- Monitoring: pg_stat_statements
```

#### Frontend
```
- Framework: Next.js 15+ (App Router)
- Library: React 19+
- Language: TypeScript 5.x
- Styling: Tailwind CSS 4+
- Components: shadcn/ui ou Headless UI
- State Management: TanStack Query (React Query) + Zustand
- Forms: React Hook Form + Zod
- HTTP Client: axios ou fetch com interceptors
- Real-time: Socket.io (opcional, para notificações)
```

#### Infraestrutura
```
- Containerização: Docker 25.x
- Orquestração: Kubernetes 1.28+ ou Docker Swarm
- CI/CD: GitHub Actions
- Container Registry: Docker Hub / ECR / GCR
- Reverse Proxy: Nginx 1.25+
- Load Balancer: AWS ALB / GCP LB
- DNS: Route 53 / CloudFlare
- Storage: S3 / GCS (PDFs, imagens)
- Secrets Management: Vault / AWS Secrets Manager
```

#### Observabilidade
```
- Logging: Structured JSON (ELK / Datadog / New Relic)
- Tracing: OpenTelemetry (Jaeger / Tempo)
- Metrics: Prometheus + Grafana
- Monitoring: Sentry para error tracking
- Uptime: StatusPage / Better Uptime
```

### 3.2 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Browser/Client (React + TypeScript + Tailwind)       │  │
│  │ - Server Components for Data Fetching                │  │
│  │ - Client Components for Interactivity                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/gRPC
     ┌───────────────┴───────────────┐
     │                               │
┌────▼──────────────┐    ┌──────────▼────────┐
│  API Gateway      │    │   WebSocket       │
│  (Nginx)          │    │   Server          │
│  - Rate Limiting  │    │   (Socket.io)     │
│  - Auth Check     │    └──────────────────┘
│  - CORS Policy    │
└────┬──────────────┘
     │
┌────▼─────────────────────────────────────────────────────────┐
│                Backend (Python/FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ FastAPI Application                                   │   │
│  │ - Dependency Injection System                        │   │
│  │ - Middleware (Auth, CORS, Logging)                   │   │
│  │ - Route Handlers (sync + async)                      │   │
│  │ - Exception Handlers                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Auth     │  │ Books    │  │ Users    │  │ Admin    │    │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ AI Integration Layer (Abstraction)                    │   │
│  │ - Gemini Adapter                                     │   │
│  │ - OpenRouter Adapter                                 │   │
│  │ - Provider Router (fallback strategy)                │   │
│  │ - Request/Response Normalization                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ PDF Generation Service                                │   │
│  │ - ReportLab / weasyprint                              │   │
│  │ - Caching Strategy                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└────┬──────────────────────────────────────────────────────────┘
     │
   ┌─┴─────────────────────────────────────────────────┐
   │                                                   │
┌──▼──────────┐  ┌────────────────┐  ┌──────────────┐│
│ PostgreSQL  │  │ Redis          │  │ S3 Storage   ││
│ - Users     │  │ - Caching      │  │ - PDFs       ││
│ - Books     │  │ - Sessions     │  │ - Images     ││
│ - Badges    │  │ - Pub/Sub      │  │ - Backups    ││
│ - Analytics │  │ - Task Queue   │  │              ││
└─────────────┘  └────────────────┘  └──────────────┘│
                                                     │
   ┌─────────────────────────────────────────────────┘
   │
┌──▼────────────────────────────────┐
│ Task Queue (Celery Workers)        │
│ - Image Generation Tasks           │
│ - Text Generation Tasks            │
│ - PDF Generation Jobs              │
│ - Email Tasks                      │
│ - Cleanup Tasks                    │
│ - Analytics Aggregation            │
└────────────────────────────────────┘
   │
   ├──► Gemini API
   ├──► OpenRouter API
   └──► External Services
```

### 3.3 Padrões e Best Practices de Arquitetura

#### 3.3.1 Backend Architecture Patterns

**Layered Architecture:**
```
┌─────────────────────────────────────┐
│   API Layer (Route Handlers)         │
├─────────────────────────────────────┤
│   Service Layer (Business Logic)     │
├─────────────────────────────────────┤
│   Repository Layer (Data Access)     │
├─────────────────────────────────────┤
│   Database Layer (Models)            │
└─────────────────────────────────────┘
```

**Separation of Concerns:**
- Controllers/Routes: HTTP request/response handling
- Services: Business logic, orchestration
- Repositories: Database operations with abstraction
- Models: Data definitions (Pydantic + SQLAlchemy)
- Middleware: Cross-cutting concerns (auth, logging)

**Dependency Injection:**
```python
# FastAPI's built-in DI system
from fastapi import Depends

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.get("/books")
async def list_books(db: AsyncSession = Depends(get_db)):
    ...
```

**Async/Await Throughout:**
- Async route handlers
- Async database queries with asyncpg
- Async HTTP calls with httpx
- Non-blocking I/O operations

#### 3.3.2 AI Provider Integration - Abstraction Layer

**Objetivo:** Desacoplar a aplicação de provedores específicos de IA

```python
# Adapter Pattern
from abc import ABC, abstractmethod
from typing import Optional

class AIProvider(ABC):
    """Base class para todos os provedores de IA"""
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        description: str,
        style: str,
        model: Optional[str] = None,
        **kwargs
    ) -> bytes:
        pass

class GeminiProvider(AIProvider):
    """Implementação específica do Gemini"""
    def __init__(self, api_key: str):
        self.client = genai.GenerativeModel(...)
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        # Implementação Gemini
        pass

class OpenRouterProvider(AIProvider):
    """Implementação específica do OpenRouter"""
    def __init__(self, api_key: str):
        self.client = OpenRouter(api_key=api_key)
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        # Implementação OpenRouter
        pass

class AIProviderFactory:
    """Factory para instanciar providers"""
    
    _providers: Dict[str, Type[AIProvider]] = {
        "gemini": GeminiProvider,
        "openrouter": OpenRouterProvider,
    }
    
    @classmethod
    def create(cls, provider: str, config: dict) -> AIProvider:
        if provider not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}")
        return cls._providers[provider](**config)

class AIProviderRouter:
    """Roteador inteligente com fallback strategy"""
    
    def __init__(self, providers: List[AIProvider], config: dict):
        self.providers = providers
        self.config = config
        self.current_index = 0
    
    async def generate_text_with_fallback(
        self, 
        prompt: str,
        **kwargs
    ) -> str:
        """Tenta com múltiplos providers em caso de falha"""
        for i, provider in enumerate(self.providers):
            try:
                return await provider.generate_text(prompt, **kwargs)
            except Exception as e:
                if i == len(self.providers) - 1:
                    raise
                continue
```

**Configuração Dinâmica:**
```python
# config.py
AI_CONFIG = {
    "primary": {
        "provider": "gemini",
        "model": "gemini-2.0-flash",
        "api_key": settings.GEMINI_API_KEY,
    },
    "fallback": [
        {
            "provider": "openrouter",
            "model": "google/gemini-pro",
            "api_key": settings.OPENROUTER_API_KEY,
        }
    ],
    "models": {
        "text_generation": {
            "primary": "gemini-2.0-flash",
            "fallback": "openrouter/google/gemini-pro"
        },
        "image_generation": {
            "primary": "gemini-2.0-vision",
            "fallback": "openrouter/..."
        }
    }
}

# Uso na aplicação
router = AIProviderRouter.from_config(AI_CONFIG)
```

#### 3.3.3 Task Queue Pattern (Celery + Redis)

**Arquitetura de Jobs:**
```python
from celery import Celery, Task
from typing import Optional

celery_app = Celery(
    'fabrica_livros',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=5 * 60,  # 5 min hard limit
    task_soft_time_limit=4 * 60,  # 4 min soft limit
)

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def generate_book_pages(
    self,
    book_id: str,
    prompts: List[str],
    style: str
) -> dict:
    """Task para gerar páginas do livro"""
    try:
        # Implementação
        pass
    except Exception as exc:
        # Retry com backoff exponencial
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery_app.task
def generate_pdf(book_id: str) -> dict:
    """Task para gerar PDF"""
    try:
        # Implementação
        pass
    except Exception as exc:
        logger.error(f"PDF generation failed: {exc}")
        raise

# Monitoramento de tasks
@celery_app.task
def cleanup_expired_jobs():
    """Cleanup periódico de jobs expirados"""
    pass
```

**Monitoramento com Celery Flower:**
```bash
# Dashboard em tempo real
celery -A app.celery_app flower --port=5555
```

#### 3.3.4 Caching Strategy

```python
from functools import wraps
import hashlib

class CacheManager:
    """Manager centralizado de cache"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = {
            "user": 3600,  # 1 hora
            "book": 7200,  # 2 horas
            "pdf": 86400,  # 24 horas
            "generated_image": 86400,
        }
    
    async def get(self, key: str):
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: dict, ttl: Optional[int] = None):
        ttl = ttl or self.ttl.get("default", 3600)
        await self.redis.setex(key, ttl, json.dumps(value))
    
    def cache_key(self, *args, **kwargs) -> str:
        """Gera chave consistente para cache"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = ":".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()

# Decorator para cache automático
def cached(ttl: int = 3600, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{cache_manager.cache_key(*args, **kwargs)}"
            
            # Tentar cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value:
                return cached_value
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Salvar no cache
            await cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
```

#### 3.3.5 Error Handling e Resiliência

```python
from typing import Callable, Any
import asyncio

class AppException(Exception):
    """Base exception para a aplicação"""
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class AIGenerationException(AppException):
    """Erro durante geração de IA"""
    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"AI Generation failed ({provider}): {message}",
            code="AI_GENERATION_ERROR",
            status_code=502
        )

class RateLimitException(AppException):
    """Rate limit excedido"""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(
            message="Rate limit exceeded",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429
        )

# Exception handlers no FastAPI
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

# Circuit Breaker Pattern
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failures = 0
        self.state = "closed"
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = "open"
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
        )

# Retry com backoff exponencial
async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: int = 1,
    backoff_factor: float = 2.0,
    **kwargs
) -> Any:
    for attempt in range(max_retries):
        try:
            return await func(**kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (backoff_factor ** attempt)
            await asyncio.sleep(delay)
```

### 3.4 Segurança

#### 3.4.1 Autenticação e Autorização

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

# OAuth2 com JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Dependency para validar JWT e retornar usuário"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_admin_user(
    current_user: User = Security(get_current_user)
) -> User:
    """Dependency para validar admin"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/books")
@limiter.limit("100/minute")
async def list_books(request: Request, current_user: User = Depends(get_current_user)):
    ...

# RBAC (Role-Based Access Control)
class Permission(str, Enum):
    CREATE_BOOK = "create:book"
    READ_BOOK = "read:book"
    UPDATE_BOOK = "update:book"
    DELETE_BOOK = "delete:book"
    ADMIN_ACCESS = "admin:access"

def require_permission(permission: Permission):
    async def check_permission(current_user: User = Depends(get_current_user)):
        if permission not in current_user.permissions:
            raise HTTPException(status_code=403, detail="Permission denied")
        return current_user
    return check_permission
```

#### 3.4.2 Proteção de Dados

```python
from cryptography.fernet import Fernet
from passlib.context import CryptContext

# Hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Criptografia de dados sensíveis
class EncryptionManager:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# SQL Injection Prevention (SQLAlchemy handles automatically)
# CSRF Protection
from fastapi.middleware.csrf import CSRFProtection

# CORS Configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Headers de Segurança
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

#### 3.4.3 Secrets Management

```python
# .env (com rotação periódica)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
OPENROUTER_API_KEY=...
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=...
REDIS_URL=redis://...

# Acesso via Pydantic Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Básico
    APP_NAME: str = "Fábrica de Livros"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Banco de Dados
    DATABASE_URL: str
    
    # IA APIs
    GEMINI_API_KEY: str
    OPENROUTER_API_KEY: str
    
    # Redis
    REDIS_URL: str
    
    # Segurança
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    
    # Storage
    S3_BUCKET: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Alternativa: AWS Secrets Manager / Vault
import boto3

def get_secret(secret_name: str):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])
```

---

## 4. Banco de Dados

### 4.1 Modelo de Dados

```sql
-- Usuários
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    tier VARCHAR(50) DEFAULT 'free',
    daily_credits INT DEFAULT 50,
    monthly_credits INT DEFAULT 500,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Livros
CREATE TABLE books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    style VARCHAR(50) NOT NULL,
    num_pages INT NOT NULL CHECK (num_pages >= 5 AND num_pages <= 20),
    narrative TEXT,
    cover_image_url TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    -- draft, generating, generated, published, archived
    progress INT DEFAULT 0,
    total_steps INT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    UNIQUE(id, user_id)
);

-- Páginas do livro
CREATE TABLE book_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    page_number INT NOT NULL,
    prompt TEXT NOT NULL,
    image_url TEXT,
    image_hash VARCHAR(64),
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    generation_time_ms INT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gerações de PDF
CREATE TABLE pdf_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    pdf_url TEXT NOT NULL,
    pdf_hash VARCHAR(64),
    file_size_bytes INT,
    quality VARCHAR(50) DEFAULT 'high',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    download_count INT DEFAULT 0,
    last_downloaded_at TIMESTAMP
);

-- Badges e conquistas
CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon_url TEXT,
    category VARCHAR(50),
    requirements JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Badges de usuários
CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_id)
);

-- Experiência e pontos
CREATE TABLE user_experience (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_xp INT DEFAULT 0,
    level INT DEFAULT 1,
    books_created INT DEFAULT 0,
    pages_generated INT DEFAULT 0,
    pdfs_downloaded INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Leaderboard (atualizado periodicamente)
CREATE MATERIALIZED VIEW leaderboard AS
SELECT 
    ue.user_id,
    u.username,
    u.avatar_url,
    ue.total_xp,
    ue.level,
    ue.books_created,
    ROW_NUMBER() OVER (ORDER BY ue.total_xp DESC) as rank
FROM user_experience ue
JOIN users u ON ue.user_id = u.id
WHERE u.is_active = TRUE
ORDER BY ue.total_xp DESC;

-- Jobs de processamento
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(100) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    book_id UUID REFERENCES books(id),
    status VARCHAR(50) DEFAULT 'pending',
    -- pending, running, completed, failed
    result JSONB,
    error_details JSONB,
    celery_task_id VARCHAR(255),
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days')
);

-- Auditoria
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_resource (resource_type, resource_id)
);

-- Analytics
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_name VARCHAR(100) NOT NULL,
    event_data JSONB,
    session_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_created (event_name, created_at)
);
```

### 4.2 Índices e Performance

```sql
-- Índices para queries frequentes
CREATE INDEX idx_books_user_created ON books(user_id, created_at DESC) WHERE is_deleted = FALSE;
CREATE INDEX idx_book_pages_book_id ON book_pages(book_id, page_number);
CREATE INDEX idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status, created_at);
CREATE INDEX idx_users_email ON users(email);

-- Full-text search
CREATE INDEX idx_books_title_fts ON books USING GIN(to_tsvector('portuguese', title));

-- Particionamento (para tabelas grandes)
CREATE TABLE analytics_events_2025_11 PARTITION OF analytics_events
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

### 4.3 Migrations com Alembic

```bash
# Inicializar
alembic init alembic

# Criar migration
alembic revision --autogenerate -m "Create initial schema"

# Aplicar migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

```python
# alembic/env.py exemplo
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.models import Base

def run_migrations_online():
    configuration = context.config.get_section(context.config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    
    engine = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata
        )
        
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## 5. Frontend (Next.js/React)

### 5.1 Estrutura de Pastas

```
frontend/
├── public/
│   ├── images/
│   ├── fonts/
│   └── icons/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx
│   │   │   ├── books/page.tsx
│   │   │   ├── books/[id]/page.tsx
│   │   │   ├── create/page.tsx
│   │   │   └── profile/page.tsx
│   │   └── api/
│   │       ├── auth/[...nextauth]/route.ts
│   │       └── webhooks/route.ts
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Modal.tsx
│   │   ├── layouts/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── features/
│   │   │   ├── BookCard.tsx
│   │   │   ├── BookCreator.tsx
│   │   │   ├── BookGallery.tsx
│   │   │   └── GenerationProgress.tsx
│   │   └── common/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       └── Toast.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useBooks.ts
│   │   ├── useGenerationStatus.ts
│   │   └── useLocalStorage.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── constants.ts
│   │   ├── utils.ts
│   │   └── types.ts
│   ├── services/
│   │   ├── api/
│   │   │   ├── bookService.ts
│   │   │   ├── userService.ts
│   │   │   └── authService.ts
│   │   └── websocket.ts
│   ├── store/
│   │   ├── authStore.ts
│   │   ├── booksStore.ts
│   │   └── uiStore.ts
│   └── styles/
│       ├── globals.css
│       ├── variables.css
│       └── animations.css
├── .env.local.example
├── next.config.ts
├── tsconfig.json
├── tailwind.config.ts
└── package.json
```

### 5.2 Patterns e Best Practices Frontend

#### 5.2.1 Server Components vs Client Components

```typescript
// app/books/page.tsx (Server Component)
import { BookGallery } from '@/components/features/BookGallery'
import { getBooks } from '@/services/api/bookService'

export default async function BooksPage() {
  const books = await getBooks() // Fetch no servidor
  
  return (
    <div>
      <h1>Meus Livros</h1>
      <BookGallery initialBooks={books} /> {/* Client component */}
    </div>
  )
}

// components/features/BookGallery.tsx (Client Component)
'use client'

import { useState, useEffect } from 'react'
import { useInfiniteQuery } from '@tanstack/react-query'
import { BookCard } from '@/components/features/BookCard'

export function BookGallery({ initialBooks }) {
  const [searchTerm, setSearchTerm] = useState('')
  
  const { data, fetchNextPage, hasNextPage, isLoading } = useInfiniteQuery({
    queryKey: ['books', searchTerm],
    queryFn: async ({ pageParam = 0 }) => {
      const response = await fetch(
        `/api/books?skip=${pageParam}&search=${searchTerm}`
      )
      return response.json()
    },
    initialData: { pages: [initialBooks] },
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  })
  
  return (
    <div>
      <input
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Buscar livros..."
      />
      <div className="grid grid-cols-3 gap-4">
        {data?.pages.flatMap((page) => page.items).map((book) => (
          <BookCard key={book.id} book={book} />
        ))}
      </div>
    </div>
  )
}
```

#### 5.2.2 Estado Global com Zustand

```typescript
// store/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isLoading: false,
      error: null,
      login: async (email, password) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/auth/login', { email, password })
          set({ user: response.data.user, error: null })
        } catch (error) {
          set({ error: error.message })
        } finally {
          set({ isLoading: false })
        }
      },
      logout: () => set({ user: null }),
      setUser: (user) => set({ user }),
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ user: state.user }),
    }
  )
)
```

#### 5.2.3 Data Fetching com React Query

```typescript
// hooks/useBooks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as bookService from '@/services/api/bookService'

export function useBooks() {
  return useQuery({
    queryKey: ['books'],
    queryFn: () => bookService.getBooks(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000, // 10 minutos (antigo cacheTime)
  })
}

export function useCreateBook() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (newBook: CreateBookDTO) =>
      bookService.createBook(newBook),
    onSuccess: (newBook) => {
      // Atualizar cache otimisticamente
      queryClient.setQueryData(['books'], (old: Book[]) => [
        ...old,
        newBook,
      ])
    },
    onError: (error) => {
      console.error('Failed to create book:', error)
    },
  })
}
```

#### 5.2.4 Real-time Updates com WebSocket

```typescript
// services/websocket.ts
import { useEffect, useState } from 'react'

export function useWebSocket(url: string) {
  const [data, setData] = useState<any>(null)
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting')
  
  useEffect(() => {
    const ws = new WebSocket(url)
    
    ws.onopen = () => setStatus('connected')
    ws.onmessage = (event) => setData(JSON.parse(event.data))
    ws.onerror = () => setStatus('disconnected')
    ws.onclose = () => setStatus('disconnected')
    
    return () => ws.close()
  }, [url])
  
  return { data, status }
}

// Uso em componente
export function GenerationProgress({ bookId }: { bookId: string }) {
  const { data: progress } = useWebSocket(`ws://localhost:8000/ws/books/${bookId}/progress`)
  
  return (
    <div>
      <progress value={progress?.percentage} max="100" />
      <p>{progress?.status}</p>
    </div>
  )
}
```

---

## 6. Processamento e Geração de IA

### 6.1 Fluxo de Geração de Livro

```
1. Usuário inicia criação de livro
   ↓
2. Validação de entrada (título, estilo, num páginas)
   ↓
3. Verificação de quotas e rate limits
   ↓
4. Criação de registro no banco (status: "generating")
   ↓
5. Envio de tasks para fila Celery:
   - generate_narrative_text (se não fornecido)
   - generate_page_images (x N páginas, em paralelo)
   ↓
6. Cada task:
   - Chama IA Provider (com fallback)
   - Armazena resultado no S3
   - Atualiza banco de dados
   - Notifica cliente via WebSocket
   ↓
7. Quando todos os pages estão prontos:
   - generate_pdf task
   ↓
8. Atualização final (status: "generated")
   ↓
9. Notificação ao cliente
```

### 6.2 Task de Geração de Texto

```python
# tasks/text_generation.py
from celery import shared_task
from app.services.ai import AIProviderRouter
from app.db import AsyncSession
from app.models import Book
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
async def generate_narrative_text(
    self,
    book_id: str,
    num_pages: int,
    style: str,
    keywords: List[str]
) -> dict:
    """Generate narrative text for a book"""
    
    try:
        db = AsyncSession()
        book = await db.get(Book, book_id)
        
        if not book:
            raise ValueError(f"Book {book_id} not found")
        
        # AI Provider Router com fallback
        ai_router = AIProviderRouter.from_config(settings.AI_CONFIG)
        
        # Criar prompt para geração de narrativa
        prompt = f"""
        Crie uma história educativa infantil para um livro de colorir com {num_pages} páginas.
        Estilo: {style}
        Palavras-chave: {', '.join(keywords)}
        
        Forneça a narrativa em formato JSON com a seguinte estrutura:
        {{
            "title": "...",
            "pages": [
                {{"number": 1, "text": "..."}},
                ...
            ]
        }}
        """
        
        # Gerar com retry automático
        narrative_json = await ai_router.generate_text_with_fallback(
            prompt,
            model="text_generation"
        )
        
        # Parsear e validar resposta
        narrative_data = json.loads(narrative_json)
        
        # Salvar no banco
        book.narrative = json.dumps(narrative_data)
        book.save()
        
        return {
            "success": True,
            "book_id": book_id,
            "narrative": narrative_data
        }
        
    except Exception as exc:
        logger.error(f"Error generating narrative: {exc}")
        # Retry com backoff exponencial
        raise self.retry(
            exc=exc,
            countdown=60 * (2 ** self.request.retries)
        )
```

### 6.3 Task de Geração de Imagens

```python
# tasks/image_generation.py
from celery import shared_task, group
import aiohttp
from app.services.storage import S3Manager
from app.db import AsyncSession
from app.models import BookPage

@shared_task(bind=True, max_retries=3)
async def generate_page_image(
    self,
    book_id: str,
    page_number: int,
    prompt: str,
    style: str
) -> dict:
    """Generate image for a specific page"""
    
    try:
        ai_router = AIProviderRouter.from_config(settings.AI_CONFIG)
        s3_manager = S3Manager()
        
        # Adaptar prompt com estilo
        full_prompt = f"{prompt}\nArtistic style: {style}\nColoring book page"
        
        # Gerar imagem
        image_bytes = await ai_router.generate_image_with_fallback(
            full_prompt,
            style=style,
            model="image_generation"
        )
        
        # Upload para S3
        image_key = f"books/{book_id}/pages/{page_number:02d}.png"
        image_url = await s3_manager.upload(image_key, image_bytes)
        
        # Salvar no banco
        db = AsyncSession()
        page = BookPage(
            book_id=book_id,
            page_number=page_number,
            image_url=image_url,
            status="completed"
        )
        db.add(page)
        await db.commit()
        
        return {
            "success": True,
            "page_number": page_number,
            "image_url": image_url
        }
        
    except Exception as exc:
        logger.error(f"Error generating image: {exc}")
        raise self.retry(
            exc=exc,
            countdown=60 * (2 ** self.request.retries)
        )

@shared_task
def generate_all_pages(book_id: str, num_pages: int, style: str):
    """Coordenador: gera todas as páginas em paralelo"""
    
    db = AsyncSession()
    book = db.get(Book, book_id)
    narrative = json.loads(book.narrative)
    
    # Criar grupo de tasks paralelas
    jobs = group([
        generate_page_image.s(
            book_id,
            page['number'],
            page['text'],
            style
        )
        for page in narrative['pages']
    ])
    
    # Callback quando todos forem concluídos
    jobs.link(generate_pdf_task.s(book_id))
    
    return jobs.apply_async()
```

### 6.4 Task de Geração de PDF

```python
# tasks/pdf_generation.py
from celery import shared_task
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image
import io
from app.services.storage import S3Manager

@shared_task(bind=True, max_retries=2)
async def generate_pdf(self, book_id: str) -> dict:
    """Generate PDF from book pages"""
    
    try:
        db = AsyncSession()
        book = await db.get(Book, book_id)
        pages = await db.query(BookPage).filter_by(book_id=book_id).all()
        
        # Criar PDF com ReportLab ou Weasyprint
        pdf_buffer = io.BytesIO()
        
        # ReportLab approach
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4
        
        for page in pages:
            # Download imagem do S3
            image_data = await s3_manager.download(page.image_url)
            img = Image.open(io.BytesIO(image_data))
            
            # Adicionar ao PDF
            c.drawImage(
                ImageReader(io.BytesIO(image_data)),
                0, 0,
                width=width,
                height=height
            )
            c.showPage()
        
        c.save()
        pdf_buffer.seek(0)
        
        # Upload PDF
        s3_manager = S3Manager()
        pdf_key = f"books/{book_id}/output.pdf"
        pdf_url = await s3_manager.upload(pdf_key, pdf_buffer.getvalue())
        
        # Salvar metadados
        pdf_gen = PDFGeneration(
            book_id=book_id,
            pdf_url=pdf_url,
            file_size_bytes=len(pdf_buffer.getvalue())
        )
        db.add(pdf_gen)
        
        # Atualizar status do livro
        book.status = "generated"
        book.updated_at = datetime.now()
        await db.commit()
        
        return {
            "success": True,
            "book_id": book_id,
            "pdf_url": pdf_url
        }
        
    except Exception as exc:
        logger.error(f"PDF generation failed: {exc}")
        raise self.retry(exc=exc, countdown=300)
```

---

## 7. Observabilidade e Monitoramento

### 7.1 Logging Estruturado

```python
# lib/logging.py
import json
import logging
from pythonjsonlogger import jsonlogger
from opentelemetry import trace

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # JSON formatter
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_event(
        self,
        event: str,
        level: str = "INFO",
        user_id: str = None,
        **kwargs
    ):
        """Log estruturado com contexto"""
        trace_id = trace.get_current_span().get_span_context().trace_id
        
        log_entry = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "user_id": user_id,
            **kwargs
        }
        
        getattr(self.logger, level.lower())(json.dumps(log_entry))

# Middleware para logging automático
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.log_event(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=process_time * 1000
        )
        
        return response
```

### 7.2 Tracing com OpenTelemetry

```python
# lib/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def setup_tracing():
    # Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.JAEGER_HOST,
        agent_port=settings.JAEGER_PORT,
    )
    
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    # Auto-instrumentation
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine)
    RedisInstrumentor().instrument(redis_client=redis_client)

# Uso manual em funções críticas
tracer = trace.get_tracer(__name__)

async def critical_operation(book_id: str):
    with tracer.start_as_current_span("critical_operation") as span:
        span.set_attribute("book_id", book_id)
        # Operação aqui
```

### 7.3 Métricas com Prometheus

```python
# lib/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Métricas
books_created = Counter(
    'books_created_total',
    'Total livros criados',
    ['user_tier']
)

generation_duration = Histogram(
    'book_generation_duration_seconds',
    'Tempo de geração de livro',
    buckets=(1, 5, 10, 30, 60, 300)
)

active_generations = Gauge(
    'active_generations',
    'Gerações em andamento'
)

api_requests = Counter(
    'api_requests_total',
    'Total requisições API',
    ['method', 'endpoint', 'status']
)

# Middleware para métricas
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Uso
@app.post("/books")
async def create_book(request: CreateBookRequest):
    with generation_duration.time():
        active_generations.inc()
        try:
            # Criar livro
            books_created.labels(user_tier=user.tier).inc()
        finally:
            active_generations.dec()
```

---

## 8. Deployment e DevOps

### 8.1 Containerização

#### Dockerfile - Backend

```dockerfile
# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Instalar build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Criar virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Criar usuário não-root
RUN useradd -m -u 1000 appuser

# Copiar venv do builder
COPY --from=builder /opt/venv /opt/venv

# Copiar código
COPY --chown=appuser:appuser . .

# Variáveis de ambiente
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Trocar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile - Frontend

```dockerfile
# Build stage
FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build otimizado
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

RUN npm install -g pm2

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["pm2-runtime", "next", "start"]
```

### 8.2 Docker Compose (Development)

```yaml
version: '3.9'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
      ENVIRONMENT: development
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: celery -A app.celery_app worker --loglevel=info

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: celery -A app.celery_app beat --loglevel=info

volumes:
  postgres_data:
```

### 8.3 Kubernetes Manifests

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: docker.io/user/fabrica-livros-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 5

---
# k8s/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: default
spec:
  selector:
    app: backend
  type: ClusterIP
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000

---
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: docker.io/user/fabrica-livros-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.fabrica-livros.com"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### 8.4 GitHub Actions CI/CD

```yaml
# .github/workflows/ci-cd.yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        cache: 'pip'

    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt

    - name: Run migrations
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
      run: |
        alembic upgrade head

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
        REDIS_URL: redis://localhost:6379/0
      run: |
        pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Node
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run linting
      run: npm run lint

    - name: Run tests
      run: npm test

    - name: Build
      run: npm run build

  build-and-push:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push backend
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/fabrica-livros-backend:latest
          ${{ secrets.DOCKER_USERNAME }}/fabrica-livros-backend:${{ github.sha }}

    - name: Build and push frontend
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/fabrica-livros-frontend:latest
          ${{ secrets.DOCKER_USERNAME }}/fabrica-livros-frontend:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Deploy to Kubernetes
      env:
        KUBECONFIG: ${{ secrets.KUBE_CONFIG }}
      run: |
        kubectl set image deployment/backend \
          backend=${{ secrets.DOCKER_USERNAME }}/fabrica-livros-backend:${{ github.sha }}
        kubectl set image deployment/frontend \
          frontend=${{ secrets.DOCKER_USERNAME }}/fabrica-livros-frontend:${{ github.sha }}
        kubectl rollout status deployment/backend
        kubectl rollout status deployment/frontend
```

---

## 9. Plano de Implementação

### Fase 1: Fundação (4-6 semanas)

- Setup inicial do projeto
- Configuração de banco de dados e migrations
- Implementação da autenticação (JWT + OAuth)
- CRUD básico de usuários e livros
- Estrutura de pastas e patterns (backend e frontend)
- Pipeline CI/CD básico

### Fase 2: IA Integration (4-5 semanas)

- Implementação da camada abstrata de IA (Adapter pattern)
- Integração com Gemini API
- Integração com OpenRouter
- Sistema de fallback e retry
- Task queue (Celery + Redis)

### Fase 3: Geração de Conteúdo (5-6 semanas)

- Geração de narrativas com IA
- Geração de imagens com IA
- Geração de PDFs
- Caching e otimizações
- Monitoramento de jobs

### Fase 4: Gamificação (3-4 semanas)

- Sistema de badges
- Pontos de experiência
- Leaderboards
- Desafios e missions

### Fase 5: Frontend Avançado (4-5 semanas)

- UI/UX completa (baseado em referências)
- Real-time updates (WebSocket)
- Progressive enhancement
- Performance optimization

### Fase 6: Observabilidade e Deploy (3-4 semanas)

- Logging estruturado
- Tracing com OpenTelemetry
- Monitoring e alertas
- Deployment em Kubernetes
- Documentação final

---

## 10. Métricas de Sucesso

| Métrica | Target |
|---------|--------|
| Uptime | 99.9% |
| Latência P95 | < 500ms |
| Tempo de geração de livro | < 3 min |
| Taxa de erro | < 0.5% |
| Cobertura de testes | > 80% |
| Performance Lighthouse | > 90 |
| Deploy time | < 10 min |
| MTTR (Mean Time To Recovery) | < 15 min |

---

## 11. Tecnologias Alternativas (Optional)

### Para certas funcionalidades:

- **Cache:** Memcached (se preferir ao Redis)
- **Search:** Elasticsearch (para full-text search avançado)
- **File Storage:** Google Cloud Storage / Azure Blob (alternativas ao S3)
- **Message Queue:** RabbitMQ (alternativa ao Redis Celery)
- **Monitoring:** Datadog / New Relic (alternativas ao Prometheus)
- **PDF Generation:** Weasyprint / Puppeteer (alternativas ao ReportLab)
- **Image Generation:** Stable Diffusion API (alternativa ao Gemini)

---

## 12. Documentação Necessária

- API documentation (Swagger/OpenAPI)
- Architecture Decision Records (ADRs)
- Database schema documentation
- Deployment runbooks
- Troubleshooting guides
- Contributing guidelines
- Security policies
- Privacy policy (GDPR compliance)

---

## Conclusão

Este PRD fornece uma base sólida para o desenvolvimento da plataforma Fábrica de Livros v2.0 com stack moderno e escalável. A arquitetura proposta segue as melhores práticas de 2025 para Python/FastAPI + PostgreSQL + Next.js, com ênfase em observabilidade, segurança e manutenibilidade.

A separação clara entre camadas, o uso de padrões comprovados e a automação de CI/CD garantem um produto robusto, escalável e fácil de manter.