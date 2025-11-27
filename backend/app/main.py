from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware # Import GZipMiddleware
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.middleware.exception_middleware import ExceptionMiddleware, RequestMiddleware
from app.middleware.logging_middleware import LoggingMiddleware, AuditMiddleware
from app.middleware.security_middleware import SecurityMiddleware
from app.exceptions.base_exceptions import AppException
from app.exceptions.http_exceptions import (
    HTTPExceptionHandler,
    ValidationExceptionHandler,
    DatabaseExceptionHandler,
    GeneralExceptionHandler
)
from app.core.logging import setup_logging, get_logger
from app.core.config import settings

# Configurar logging antes de criar a aplicação
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Fábrica de Livros API",
    description="API para geração de livros infantis com IA com sistema completo de observabilidade",
    version=settings.VERSION,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# Middleware stack temporariamente desabilitado para resolver problemas

# 1. Logging middleware (primeiro para capturar tudo)
app.add_middleware(LoggingMiddleware)

# 2. Auditoria middleware (para ações de modificação)
app.add_middleware(AuditMiddleware)

# 3. Exception middleware (captura erros globalmente)
app.add_middleware(ExceptionMiddleware)

# 4. Security middleware (rate limiting, security headers)
app.add_middleware(SecurityMiddleware)

# 5. Request middleware (headers padrão)
app.add_middleware(RequestMiddleware)

# 6. GZip Compression (Otimização)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS Configuration - Dinâmico baseado em configurações
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.get_cors_methods(),
    allow_headers=settings.get_cors_headers(),
    max_age=settings.CORS_MAX_AGE,
)

# Registrar handlers de exceção específicos
app.add_exception_handler(AppException, HTTPExceptionHandler.app_exception_handler)
app.add_exception_handler(HTTPException, HTTPExceptionHandler.http_exception_handler)
app.add_exception_handler(ValidationError, ValidationExceptionHandler.pydantic_validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, DatabaseExceptionHandler.sqlalchemy_exception_handler)
app.add_exception_handler(Exception, GeneralExceptionHandler.general_exception_handler)

from app.api.v1.api import api_router

app.include_router(api_router, prefix=settings.API_V1_STR)

# Include health and monitoring endpoints
from app.api.v1.endpoints import health, logs
app.include_router(health.router, prefix="/health", tags=["Health"])
if not settings.is_production:  # Logs endpoints apenas em dev/staging
    app.include_router(logs.router, prefix="/admin/logs", tags=["Logs"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Fábrica de Livros API v2",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not settings.is_production else "disabled in production"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Evento de inicialização da aplicação."""
    logger.info(
        f"Starting {settings.PROJECT_NAME} v{settings.VERSION}",
        extra={
            "event_type": "application_startup",
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de finalização da aplicação."""
    logger.info(
        "Shutting down application",
        extra={"event_type": "application_shutdown"}
    )
