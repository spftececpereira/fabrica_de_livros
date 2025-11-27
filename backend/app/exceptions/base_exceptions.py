"""
Exceções base customizadas para a aplicação.
"""

from typing import Any, Dict, Optional, List
from enum import Enum


class ErrorCode(str, Enum):
    """Códigos de erro padronizados."""
    
    # Validação
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_VALUE = "INVALID_VALUE"
    
    # Autenticação
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    USER_INACTIVE = "USER_INACTIVE"
    
    # Autorização
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ACCESS_DENIED = "ACCESS_DENIED"
    RESOURCE_FORBIDDEN = "RESOURCE_FORBIDDEN"
    
    # Recursos não encontrados
    USER_NOT_FOUND = "USER_NOT_FOUND"
    BOOK_NOT_FOUND = "BOOK_NOT_FOUND"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    
    # Conflitos
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    CONCURRENT_MODIFICATION = "CONCURRENT_MODIFICATION"
    
    # Regras de negócio
    BOOK_PAGES_LIMIT_EXCEEDED = "BOOK_PAGES_LIMIT_EXCEEDED"
    USER_BOOK_LIMIT_EXCEEDED = "USER_BOOK_LIMIT_EXCEEDED"
    INVALID_BOOK_STATUS = "INVALID_BOOK_STATUS"
    INVALID_STYLE = "INVALID_STYLE"
    
    # Serviços externos
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    PDF_GENERATION_ERROR = "PDF_GENERATION_ERROR"
    EMAIL_SERVICE_ERROR = "EMAIL_SERVICE_ERROR"
    
    # Sistema
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    CELERY_TASK_ERROR = "CELERY_TASK_ERROR"


class AppException(Exception):
    """Exceção base da aplicação."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        """
        Inicializa exceção da aplicação.
        
        Args:
            message: Mensagem de erro para o usuário
            error_code: Código de erro padronizado
            details: Detalhes adicionais do erro
            status_code: Código HTTP de resposta
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte exceção para dicionário.
        
        Returns:
            Dict com dados da exceção
        """
        return {
            "error": {
                "message": self.message,
                "code": self.error_code.value,
                "details": self.details,
                "status_code": self.status_code
            }
        }


class ValidationError(AppException):
    """Erro de validação de dados."""
    
    def __init__(
        self,
        message: str = "Dados de entrada inválidos",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        
        if field:
            error_details["field"] = field
        
        if value is not None:
            error_details["provided_value"] = str(value)
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details=error_details,
            status_code=400
        )


class AuthenticationError(AppException):
    """Erro de autenticação."""
    
    def __init__(
        self,
        message: str = "Falha na autenticação",
        error_code: ErrorCode = ErrorCode.INVALID_CREDENTIALS,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=401
        )


class AuthorizationError(AppException):
    """Erro de autorização/permissões."""
    
    def __init__(
        self,
        message: str = "Sem permissão para acessar este recurso",
        resource: Optional[str] = None,
        required_permission: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        
        if resource:
            error_details["resource"] = resource
            
        if required_permission:
            error_details["required_permission"] = required_permission
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            details=error_details,
            status_code=403
        )


class NotFoundError(AppException):
    """Erro de recurso não encontrado."""
    
    def __init__(
        self,
        message: str = "Recurso não encontrado",
        resource: Optional[str] = None,
        resource_id: Optional[Any] = None,
        error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        
        if resource:
            error_details["resource"] = resource
            
        if resource_id is not None:
            error_details["resource_id"] = str(resource_id)
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=error_details,
            status_code=404
        )


class ConflictError(AppException):
    """Erro de conflito de dados."""
    
    def __init__(
        self,
        message: str = "Conflito de dados detectado",
        conflicting_field: Optional[str] = None,
        conflicting_value: Optional[Any] = None,
        error_code: ErrorCode = ErrorCode.RESOURCE_ALREADY_EXISTS,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        
        if conflicting_field:
            error_details["conflicting_field"] = conflicting_field
            
        if conflicting_value is not None:
            error_details["conflicting_value"] = str(conflicting_value)
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=error_details,
            status_code=409
        )


class BusinessRuleError(AppException):
    """Erro de violação de regra de negócio."""
    
    def __init__(
        self,
        message: str,
        rule: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details["violated_rule"] = rule
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=error_details,
            status_code=422
        )


class ExternalServiceError(AppException):
    """Erro em serviço externo."""
    
    def __init__(
        self,
        message: str = "Erro em serviço externo",
        service: str = "unknown",
        error_code: ErrorCode = ErrorCode.AI_SERVICE_ERROR,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details["service"] = service
        
        if original_error:
            error_details["original_error"] = str(original_error)
            error_details["original_error_type"] = type(original_error).__name__
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=error_details,
            status_code=502
        )


# Exceções específicas para facilitar uso

class UserNotFoundError(NotFoundError):
    """Usuário não encontrado."""
    
    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        if user_id:
            super().__init__(
                message="Usuário não encontrado",
                resource="user",
                resource_id=user_id,
                error_code=ErrorCode.USER_NOT_FOUND
            )
        elif email:
            super().__init__(
                message="Usuário não encontrado",
                resource="user",
                error_code=ErrorCode.USER_NOT_FOUND,
                details={"email": email}
            )
        else:
            super().__init__(
                message="Usuário não encontrado",
                resource="user",
                error_code=ErrorCode.USER_NOT_FOUND
            )


class BookNotFoundError(NotFoundError):
    """Livro não encontrado."""
    
    def __init__(self, book_id: int):
        super().__init__(
            message="Livro não encontrado",
            resource="book",
            resource_id=book_id,
            error_code=ErrorCode.BOOK_NOT_FOUND
        )


class EmailAlreadyExistsError(ConflictError):
    """Email já existe na base."""
    
    def __init__(self, email: str):
        super().__init__(
            message="Email já está em uso",
            conflicting_field="email",
            conflicting_value=email,
            error_code=ErrorCode.EMAIL_ALREADY_EXISTS
        )


class InvalidBookPagesError(BusinessRuleError):
    """Número de páginas inválido."""
    
    def __init__(self, pages_count: int):
        super().__init__(
            message="Livro deve ter entre 5 e 20 páginas",
            rule="book_pages_limit",
            error_code=ErrorCode.BOOK_PAGES_LIMIT_EXCEEDED,
            details={"provided_pages": pages_count, "min_pages": 5, "max_pages": 20}
        )


class UserBookLimitError(BusinessRuleError):
    """Limite de livros por usuário excedido."""
    
    def __init__(self, current_count: int, max_limit: int):
        super().__init__(
            message=f"Limite de {max_limit} livros por usuário excedido",
            rule="user_book_limit",
            error_code=ErrorCode.USER_BOOK_LIMIT_EXCEEDED,
            details={"current_count": current_count, "max_limit": max_limit}
        )


class InvalidPasswordError(ValidationError):
    """Senha inválida."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Senha inválida: {reason}",
            field="password"
        )


class InvalidBookStatusError(BusinessRuleError):
    """Status de livro inválido para operação."""
    
    def __init__(self, current_status: str, operation: str, allowed_statuses: List[str]):
        super().__init__(
            message=f"Não é possível {operation} livro no status '{current_status}'",
            rule="book_status_validation",
            error_code=ErrorCode.INVALID_BOOK_STATUS,
            details={
                "current_status": current_status,
                "operation": operation,
                "allowed_statuses": allowed_statuses
            }
        )