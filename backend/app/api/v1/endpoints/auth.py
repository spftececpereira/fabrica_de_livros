from typing import Any, Dict
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.services.auth_service import AuthService
from app.schemas.user import TokenResponse, UserCreate, UserResponse, PasswordResetRequest, PasswordReset
from app.middleware.exception_middleware import log_user_action

router = APIRouter()


def get_auth_service(db: AsyncSession = Depends(deps.get_db)) -> AuthService:
    """Dependency para injetar AuthService."""
    return AuthService(db)


@router.post("/login", response_model=TokenResponse)
async def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Agora usa AuthService com todas as validações e tratamento de exceções.
    """
    # AuthService já trata todas as validações e exceções
    result = await auth_service.login(
        email=form_data.username,
        password=form_data.password
    )
    
    # Log da ação para auditoria
    log_user_action(
        request=request,
        user_id=result["user"]["id"],
        action="login",
        details={"method": "password"}
    )
    
    return result


@router.post("/register", response_model=TokenResponse)
async def register_user(
    request: Request,
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Registra novo usuário e retorna token de acesso.
    
    Aplica todas as validações de negócio implementadas.
    """
    # AuthService já aplica validações de email, senha, etc.
    result = await auth_service.register(user_data)
    
    # Log da ação para auditoria  
    log_user_action(
        request=request,
        user_id=result["user"]["id"],
        action="register",
        details={"email": user_data.email}
    )
    
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    current_user = Depends(deps.get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Renova token de acesso do usuário atual.
    """
    # Verificar se usuário ainda está ativo
    result = await auth_service.refresh_token(current_user)
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="refresh_token"
    )
    
    return result


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str,
    new_password: str,
    current_user = Depends(deps.get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """
    Altera senha do usuário atual.
    
    Aplica validações de senha forte implementadas.
    """
    # AuthService já valida força da nova senha
    await auth_service.change_password(
        user_id=current_user.id,
        current_password=current_password,
        new_password=new_password
    )
    
    # Log da ação para auditoria
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="change_password"
    )
    
    return {"message": "Senha alterada com sucesso"}


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    password_reset_request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """
    Inicia o processo de redefinição de senha, enviando um email com um token.
    Sempre retorna sucesso para evitar enumeração de usuários.
    """
    await auth_service.request_password_reset(password_reset_request.email)
    
    log_user_action(
        request=request,
        user_id=None, # User ID is unknown at this point
        action="forgot_password_request",
        details={"email": password_reset_request.email}
    )
    
    return {"message": "Se o email estiver registrado, um link para redefinição de senha será enviado."}


@router.post("/reset-password")
async def reset_password(
    request: Request,
    password_reset: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """
    Redefine a senha do usuário usando um token de redefinição.
    """
    await auth_service.reset_password(password_reset.token, password_reset.new_password)
    
    # TODO: Fetch user_id from token payload for logging if possible and safe
    log_user_action(
        request=request,
        user_id=None, # User ID needs to be extracted from token for accurate logging
        action="password_reset_confirm"
    )
    
    return {"message": "Sua senha foi redefinida com sucesso."}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(deps.get_current_active_user)
) -> UserResponse:
    """
    Retorna informações do usuário atual.
    """
    return current_user

