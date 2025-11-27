"""
Validadores customizados para regras de negócio.
"""

import re
from typing import List, Optional, Union
from app.exceptions.base_exceptions import ValidationError, InvalidBookPagesError


def validate_email_format(email: str) -> str:
    """
    Valida e normaliza formato de email.
    
    Args:
        email: Email para validar
        
    Returns:
        Email normalizado
        
    Raises:
        ValidationError: Se formato for inválido
    """
    if not email:
        raise ValidationError(
            message="Email é obrigatório",
            field="email"
        )
    
    # Normalizar
    email = email.strip().lower()
    
    # Validar formato
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_regex.match(email):
        raise ValidationError(
            message="Formato de email inválido",
            field="email",
            value=email
        )
    
    return email


def validate_password_strength(password: str) -> None:
    """
    Valida força da senha conforme regras de segurança.
    
    Args:
        password: Senha para validar
        
    Raises:
        ValidationError: Se senha não atender critérios
    """
    errors = []
    
    if len(password) < 8:
        errors.append("deve ter pelo menos 8 caracteres")
    
    if len(password) > 128:
        errors.append("deve ter no máximo 128 caracteres")
    
    if not re.search(r'[a-z]', password):
        errors.append("deve conter pelo menos uma letra minúscula")
    
    if not re.search(r'[A-Z]', password):
        errors.append("deve conter pelo menos uma letra maiúscula")
    
    if not re.search(r'\d', password):
        errors.append("deve conter pelo menos um número")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("deve conter pelo menos um caractere especial")
    
    # Verificar padrões comuns fracos
    weak_patterns = [
        r'123456',
        r'password',
        r'qwerty',
        r'abc123',
        r'admin123'
    ]
    
    for pattern in weak_patterns:
        if re.search(pattern, password.lower()):
            errors.append("não deve conter padrões comuns fracos")
            break
    
    if errors:
        raise ValidationError(
            message=f"Senha {', '.join(errors)}",
            field="password",
            details={"requirements": errors}
        )


def validate_book_pages(pages_count: int) -> None:
    """
    Valida número de páginas do livro (regra crítica: 5-20 páginas).
    
    Args:
        pages_count: Número de páginas
        
    Raises:
        InvalidBookPagesError: Se número for inválido
    """
    if not isinstance(pages_count, int):
        raise ValidationError(
            message="Número de páginas deve ser um número inteiro",
            field="pages_count",
            value=pages_count
        )
    
    if pages_count < 5 or pages_count > 20:
        raise InvalidBookPagesError(pages_count)


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> None:
    """
    Valida extensão de arquivo.
    
    Args:
        filename: Nome do arquivo
        allowed_extensions: Lista de extensões permitidas
        
    Raises:
        ValidationError: Se extensão não for permitida
    """
    if not filename:
        raise ValidationError(
            message="Nome do arquivo é obrigatório",
            field="filename"
        )
    
    # Extrair extensão
    if '.' not in filename:
        raise ValidationError(
            message="Arquivo deve ter uma extensão",
            field="filename",
            value=filename
        )
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension not in allowed_extensions:
        raise ValidationError(
            message=f"Extensão '{extension}' não permitida. Permitidas: {', '.join(allowed_extensions)}",
            field="filename",
            value=filename,
            details={"allowed_extensions": allowed_extensions}
        )


def validate_url_format(url: str) -> str:
    """
    Valida formato de URL.
    
    Args:
        url: URL para validar
        
    Returns:
        URL validada
        
    Raises:
        ValidationError: Se URL for inválida
    """
    if not url:
        raise ValidationError(
            message="URL é obrigatória",
            field="url"
        )
    
    url = url.strip()
    
    # Validação básica de URL
    url_regex = re.compile(
        r'^https?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domínio
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # porta opcional
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_regex.match(url):
        raise ValidationError(
            message="Formato de URL inválido",
            field="url",
            value=url
        )
    
    return url


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitiza texto removendo caracteres perigosos.
    
    Args:
        text: Texto para sanitizar
        max_length: Comprimento máximo (opcional)
        
    Returns:
        Texto sanitizado
        
    Raises:
        ValidationError: Se texto exceder limite
    """
    if not text:
        return ""
    
    # Remover caracteres de controle
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Normalizar espaços em branco
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Verificar comprimento se especificado
    if max_length and len(sanitized) > max_length:
        raise ValidationError(
            message=f"Texto deve ter no máximo {max_length} caracteres",
            field="text",
            value=f"{sanitized[:50]}..." if len(sanitized) > 50 else sanitized
        )
    
    return sanitized


def validate_book_style(style: str) -> None:
    """
    Valida estilo do livro.
    
    Args:
        style: Estilo para validar
        
    Raises:
        ValidationError: Se estilo for inválido
    """
    valid_styles = ["cartoon", "realistic", "manga", "classic"]
    
    if style not in valid_styles:
        raise ValidationError(
            message=f"Estilo deve ser um dos: {', '.join(valid_styles)}",
            field="style",
            value=style
        )


def validate_book_status_transition(current_status: str, new_status: str) -> None:
    """
    Valida transição de status do livro.
    
    Args:
        current_status: Status atual
        new_status: Novo status
        
    Raises:
        ValidationError: Se transição for inválida
    """
    valid_transitions = {
        "draft": ["processing", "failed"],
        "processing": ["completed", "failed", "draft"],
        "completed": ["processing"],
        "failed": ["draft", "processing"]
    }
    
    allowed = valid_transitions.get(current_status, [])
    
    if new_status not in allowed:
        raise ValidationError(
            message=f"Transição de status inválida: {current_status} -> {new_status}",
            field="status",
            details={
                "current_status": current_status,
                "new_status": new_status,
                "allowed_transitions": allowed
            }
        )


def validate_user_role_permissions(user_role: str, required_role: str) -> None:
    """
    Valida se usuário tem permissão baseada em role.
    
    Args:
        user_role: Role do usuário
        required_role: Role requerida
        
    Raises:
        ValidationError: Se não tiver permissão
    """
    role_hierarchy = {
        "user": 1,
        "premium": 2,
        "admin": 3
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 999)
    
    if user_level < required_level:
        raise ValidationError(
            message=f"Permissão insuficiente. Requer role '{required_role}' ou superior",
            field="role",
            details={
                "user_role": user_role,
                "required_role": required_role
            }
        )