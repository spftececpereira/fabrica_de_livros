"""
Módulo de exceções customizadas para a aplicação.

Este módulo contém todas as exceções customizadas e handlers
para tratamento robusto de erros na aplicação.
"""

from .base_exceptions import (
    AppException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    BusinessRuleError,
    ExternalServiceError
)

from .http_exceptions import (
    HTTPExceptionHandler,
    ValidationExceptionHandler,
    DatabaseExceptionHandler,
    CeleryExceptionHandler
)

__all__ = [
    # Base exceptions
    "AppException",
    "ValidationError", 
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "BusinessRuleError",
    "ExternalServiceError",
    
    # HTTP exception handlers
    "HTTPExceptionHandler",
    "ValidationExceptionHandler", 
    "DatabaseExceptionHandler",
    "CeleryExceptionHandler",
]