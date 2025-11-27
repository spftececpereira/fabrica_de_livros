"""
Handlers de exceções HTTP para FastAPI.
"""

import logging
from typing import Dict, Any, Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError as PydanticValidationError
from celery.exceptions import CeleryError

from app.exceptions.base_exceptions import AppException, ErrorCode


logger = logging.getLogger(__name__)


class HTTPExceptionHandler:
    """Handler base para exceções HTTP."""
    
    @staticmethod
    def create_error_response(
        status_code: int,
        message: str,
        error_code: str,
        details: Dict[str, Any] = None,
        request_id: str = None
    ) -> JSONResponse:
        """
        Cria resposta de erro padronizada.
        
        Args:
            status_code: Código HTTP de status
            message: Mensagem de erro
            error_code: Código de erro interno
            details: Detalhes adicionais
            request_id: ID da requisição
            
        Returns:
            JSONResponse com erro padronizado
        """
        error_data = {
            "error": {
                "message": message,
                "code": error_code,
                "status_code": status_code
            }
        }
        
        if details:
            error_data["error"]["details"] = details
            
        if request_id:
            error_data["error"]["request_id"] = request_id
            
        return JSONResponse(
            status_code=status_code,
            content=error_data
        )
    
    @staticmethod
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """
        Handler para exceções customizadas da aplicação.
        
        Args:
            request: Request do FastAPI
            exc: Exceção da aplicação
            
        Returns:
            JSONResponse com erro formatado
        """
        request_id = getattr(request.state, 'request_id', None)
        
        # Log da exceção
        logger.warning(
            f"AppException: {exc.error_code.value} - {exc.message}",
            extra={
                "error_code": exc.error_code.value,
                "status_code": exc.status_code,
                "details": exc.details,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return HTTPExceptionHandler.create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code.value,
            details=exc.details,
            request_id=request_id
        )
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handler para HTTPExceptions do FastAPI.
        
        Args:
            request: Request do FastAPI
            exc: HTTPException
            
        Returns:
            JSONResponse com erro formatado
        """
        request_id = getattr(request.state, 'request_id', None)
        
        # Mapear status codes para error codes
        error_code_map = {
            400: ErrorCode.VALIDATION_ERROR.value,
            401: ErrorCode.INVALID_CREDENTIALS.value,
            403: ErrorCode.INSUFFICIENT_PERMISSIONS.value,
            404: ErrorCode.RESOURCE_NOT_FOUND.value,
            409: ErrorCode.RESOURCE_ALREADY_EXISTS.value,
            422: ErrorCode.VALIDATION_ERROR.value,
            500: ErrorCode.INTERNAL_SERVER_ERROR.value
        }
        
        error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR.value)
        
        # Log da exceção
        logger.warning(
            f"HTTPException: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return HTTPExceptionHandler.create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_code=error_code,
            request_id=request_id
        )


class ValidationExceptionHandler:
    """Handler para erros de validação Pydantic."""
    
    @staticmethod
    async def pydantic_validation_exception_handler(
        request: Request, 
        exc: PydanticValidationError
    ) -> JSONResponse:
        """
        Handler para erros de validação do Pydantic.
        
        Args:
            request: Request do FastAPI
            exc: Erro de validação do Pydantic
            
        Returns:
            JSONResponse com erros de validação formatados
        """
        request_id = getattr(request.state, 'request_id', None)
        
        # Processar erros de validação
        validation_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            validation_errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        # Log da exceção
        logger.warning(
            f"Validation error on {request.method} {request.url.path}",
            extra={
                "errors": validation_errors,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return HTTPExceptionHandler.create_error_response(
            status_code=422,
            message="Dados de entrada inválidos",
            error_code=ErrorCode.VALIDATION_ERROR.value,
            details={"validation_errors": validation_errors},
            request_id=request_id
        )


class DatabaseExceptionHandler:
    """Handler para erros de banco de dados."""
    
    @staticmethod
    async def sqlalchemy_exception_handler(
        request: Request, 
        exc: SQLAlchemyError
    ) -> JSONResponse:
        """
        Handler para erros do SQLAlchemy.
        
        Args:
            request: Request do FastAPI
            exc: Erro do SQLAlchemy
            
        Returns:
            JSONResponse com erro formatado
        """
        request_id = getattr(request.state, 'request_id', None)
        
        # Log completo do erro
        logger.error(
            f"Database error: {type(exc).__name__}",
            extra={
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )
        
        # Diferentes tratamentos para diferentes tipos de erro
        if isinstance(exc, IntegrityError):
            # Erro de integridade (chave duplicada, etc)
            return HTTPExceptionHandler.create_error_response(
                status_code=409,
                message="Conflito de dados detectado",
                error_code=ErrorCode.RESOURCE_ALREADY_EXISTS.value,
                details={"database_error": "Violação de integridade"},
                request_id=request_id
            )
        else:
            # Outros erros de banco
            return HTTPExceptionHandler.create_error_response(
                status_code=500,
                message="Erro interno do servidor",
                error_code=ErrorCode.DATABASE_ERROR.value,
                details={"database_error": "Erro de acesso aos dados"},
                request_id=request_id
            )


class CeleryExceptionHandler:
    """Handler para erros do Celery."""
    
    @staticmethod
    async def celery_exception_handler(
        request: Request, 
        exc: CeleryError
    ) -> JSONResponse:
        """
        Handler para erros do Celery.
        
        Args:
            request: Request do FastAPI
            exc: Erro do Celery
            
        Returns:
            JSONResponse com erro formatado
        """
        request_id = getattr(request.state, 'request_id', None)
        
        # Log do erro
        logger.error(
            f"Celery error: {type(exc).__name__}",
            extra={
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )
        
        return HTTPExceptionHandler.create_error_response(
            status_code=502,
            message="Erro no processamento assíncrono",
            error_code=ErrorCode.CELERY_TASK_ERROR.value,
            details={"task_error": "Falha na execução da tarefa"},
            request_id=request_id
        )


class GeneralExceptionHandler:
    """Handler para exceções gerais não capturadas."""
    
    @staticmethod
    async def general_exception_handler(
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """
        Handler para exceções não tratadas.
        
        Args:
            request: Request do FastAPI
            exc: Exceção não tratada
            
        Returns:
            JSONResponse com erro genérico
        """
        request_id = getattr(request.state, 'request_id', None)
        
        # Log completo do erro
        logger.error(
            f"Unhandled exception: {type(exc).__name__}",
            extra={
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )
        
        return HTTPExceptionHandler.create_error_response(
            status_code=500,
            message="Erro interno do servidor",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
            details={"error_type": type(exc).__name__} if request.app.debug else None,
            request_id=request_id
        )


# Helpers para facilitar uso nos services

def raise_not_found(resource: str, resource_id: Union[int, str] = None) -> None:
    """
    Facilita lançamento de exceção de recurso não encontrado.
    
    Args:
        resource: Tipo de recurso
        resource_id: ID do recurso
    """
    from app.exceptions.base_exceptions import NotFoundError
    
    if resource == "user":
        from app.exceptions.base_exceptions import UserNotFoundError
        raise UserNotFoundError(resource_id)
    elif resource == "book":
        from app.exceptions.base_exceptions import BookNotFoundError
        raise BookNotFoundError(resource_id)
    else:
        raise NotFoundError(
            message=f"{resource.title()} não encontrado",
            resource=resource,
            resource_id=resource_id
        )


def raise_validation_error(field: str, message: str, value: Any = None) -> None:
    """
    Facilita lançamento de erro de validação.
    
    Args:
        field: Campo que falhou na validação
        message: Mensagem de erro
        value: Valor que causou o erro
    """
    from app.exceptions.base_exceptions import ValidationError
    
    raise ValidationError(
        message=message,
        field=field,
        value=value
    )


def raise_authorization_error(resource: str = None, permission: str = None) -> None:
    """
    Facilita lançamento de erro de autorização.
    
    Args:
        resource: Recurso que requer autorização
        permission: Permissão necessária
    """
    from app.exceptions.base_exceptions import AuthorizationError
    
    raise AuthorizationError(
        resource=resource,
        required_permission=permission
    )


def raise_business_rule_error(rule: str, message: str, error_code: ErrorCode) -> None:
    """
    Facilita lançamento de erro de regra de negócio.
    
    Args:
        rule: Regra violada
        message: Mensagem de erro
        error_code: Código de erro
    """
    from app.exceptions.base_exceptions import BusinessRuleError
    
    raise BusinessRuleError(
        message=message,
        rule=rule,
        error_code=error_code
    )