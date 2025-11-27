from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import TokenPayload
from app.exceptions.base_exceptions import AuthenticationError, ErrorCode
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency para obter usuário atual do token JWT.
    
    Agora usa exceções customizadas e UserRepository.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        raise AuthenticationError(
            message="Token inválido ou expirado",
            error_code=ErrorCode.TOKEN_INVALID,
            details={"error": str(e)}
        )
    
    # Usar UserRepository ao invés de query direta
    user_repo = UserRepository(db)
    user = await user_repo.get(token_data.sub)
    
    if not user:
        raise AuthenticationError(
            message="Usuário não encontrado",
            error_code=ErrorCode.USER_NOT_FOUND
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency para obter usuário ativo atual.
    
    Usa exceções customizadas.
    """
    if not current_user.is_active:
        raise AuthenticationError(
            message="Usuário inativo",
            error_code=ErrorCode.USER_INACTIVE
        )
    
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency para obter usuário admin atual.
    """
    if not current_user.is_admin:
        raise AuthenticationError(
            message="Operação requer privilégios de administrador",
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS
        )
    
    return current_user

async def get_current_premium_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency para obter usuário premium ou admin.
    """
    if not current_user.is_premium:
        raise AuthenticationError(
            message="Operação requer plano premium",
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS
        )
    
    return current_user

def validate_pagination_params(
    skip: int = 0,
    limit: int = 100
) -> tuple[int, int]:
    """
    Valida parâmetros de paginação.
    """
    if skip < 0:
        raise HTTPException(
            status_code=400,
            detail="Skip deve ser maior ou igual a 0"
        )
    
    if limit <= 0 or limit > 1000:
        raise HTTPException(
            status_code=400,
            detail="Limit deve ser entre 1 e 1000"
        )
    
    return skip, limit
