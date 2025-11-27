"""
Middleware global para captura e tratamento de exceções.
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError as PydanticValidationError
from celery.exceptions import CeleryError

from app.exceptions.base_exceptions import AppException
from app.exceptions.http_exceptions import (
    HTTPExceptionHandler,
    ValidationExceptionHandler,
    DatabaseExceptionHandler,
    CeleryExceptionHandler,
    GeneralExceptionHandler
)
from app.core.logging import get_logger, set_request_context, clear_request_context

logger = logging.getLogger(__name__)


class ExceptionMiddleware:
    """
    Middleware para tratamento global de exceções.
    
    Este middleware captura todas as exceções não tratadas e as converte
    em respostas JSON padronizadas.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Processa requisição com tratamento de exceções.
        
        Args:
            request: Request do FastAPI
            call_next: Próximo middleware/handler
            
        Returns:
            Response processada ou resposta de erro
        """
        # Gerar ID único para a requisição
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Configurar contexto de logging estruturado
        set_request_context(request_id)
        
        # Log da requisição recebida
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "event_type": "request_start",
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": self._get_client_ip(request)
            }
        )
        
        try:
            # Processar requisição
            response = await call_next(request)
            
            # Log de sucesso
            process_time = time.time() - start_time
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "event_type": "request_complete",
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2)
                }
            )
            
            # Adicionar headers de resposta
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            
            return response
            
        except AppException as exc:
            # Exceções customizadas da aplicação
            process_time = time.time() - start_time
            logger.warning(
                f"App exception: {exc.error_code.value}",
                extra={
                    "request_id": request_id,
                    "error_code": exc.error_code.value,
                    "process_time": round(process_time, 3)
                }
            )
            
            response = await HTTPExceptionHandler.app_exception_handler(request, exc)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            return response
            
        except PydanticValidationError as exc:
            # Erros de validação do Pydantic
            process_time = time.time() - start_time
            logger.warning(
                f"Validation error on {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "process_time": round(process_time, 3)
                }
            )
            
            response = await ValidationExceptionHandler.pydantic_validation_exception_handler(request, exc)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            return response
            
        except SQLAlchemyError as exc:
            # Erros de banco de dados
            process_time = time.time() - start_time
            logger.error(
                f"Database error on {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "process_time": round(process_time, 3)
                },
                exc_info=True
            )
            
            response = await DatabaseExceptionHandler.sqlalchemy_exception_handler(request, exc)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            return response
            
        except CeleryError as exc:
            # Erros do Celery
            process_time = time.time() - start_time
            logger.error(
                f"Celery error on {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "process_time": round(process_time, 3)
                },
                exc_info=True
            )
            
            response = await CeleryExceptionHandler.celery_exception_handler(request, exc)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            return response
            
        except Exception as exc:
            # Outras exceções não tratadas
            process_time = time.time() - start_time
            logger.error(
                f"Unhandled exception on {request.method} {request.url.path}: {type(exc).__name__}",
                extra={
                    "event_type": "request_error",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "process_time_ms": round(process_time * 1000, 2)
                },
                exc_info=True
            )
            
            response = await GeneralExceptionHandler.general_exception_handler(request, exc)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            return response
            
        finally:
            # Limpar contexto de logging
            clear_request_context()
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extrai IP real do cliente considerando proxies.
        
        Args:
            request: Request do FastAPI
            
        Returns:
            IP do cliente
        """
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Pegar o primeiro IP da lista (cliente original)
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback para IP direto
        return request.client.host if request.client else "unknown"


class RequestMiddleware(BaseHTTPMiddleware):
    """
    Middleware para processamento de requisições.
    
    Adiciona funcionalidades como logging, métricas e headers padrão.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Processa requisição com funcionalidades adicionais.
        
        Args:
            request: Request do FastAPI
            call_next: Próximo middleware/handler
            
        Returns:
            Response processada
        """
        # Adicionar timestamp de início
        request.state.start_time = time.time()
        
        # Processar requisição
        response = await call_next(request)
        
        # Adicionar headers de segurança padrão
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Headers de API
        response.headers["X-API-Version"] = "2.0"
        response.headers["X-Powered-By"] = "FastAPI"
        
        return response


# Funcionalidades auxiliares para uso nos endpoints

def get_request_id(request: Request) -> str:
    """
    Retorna ID da requisição atual.
    
    Args:
        request: Request do FastAPI
        
    Returns:
        ID da requisição ou string vazia
    """
    return getattr(request.state, 'request_id', '')


def log_user_action(
    request: Request,
    user_id: int,
    action: str,
    resource: str = None,
    resource_id: str = None,
    details: dict = None
):
    """
    Log de ação do usuário para auditoria.
    
    Args:
        request: Request do FastAPI
        user_id: ID do usuário
        action: Ação realizada
        resource: Recurso afetado
        resource_id: ID do recurso
        details: Detalhes adicionais
    """
    request_id = get_request_id(request)
    
    log_data = {
        "request_id": request_id,
        "user_id": user_id,
        "action": action,
        "path": request.url.path,
        "method": request.method,
        "client_ip": request.client.host if request.client else "unknown"
    }
    
    if resource:
        log_data["resource"] = resource
    
    if resource_id:
        log_data["resource_id"] = resource_id
    
    if details:
        log_data["details"] = details
    
    logger.info(f"User action: {action}", extra=log_data)