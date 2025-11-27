from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.middleware.exception_middleware import log_user_action

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(deps.get_db)) -> UserService:
    """Dependency para injetar UserService."""
    return UserService(db)


@router.get("/", response_model=List[UserResponse])
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros por página"),
    active_only: bool = Query(True, description="Se deve retornar apenas usuários ativos"),
    current_user: User = Depends(deps.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    """
    Lista usuários com paginação (apenas admins).
    
    Aplica validações de permissão e paginação segura.
    """
    # UserService já verifica se usuário é admin
    users = await user_service.get_users_list(
        skip=skip,
        limit=limit,
        active_only=active_only,
        current_user=current_user
    )
    
    # Log da ação para auditoria
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="list_users",
        details={"count": len(users), "active_only": active_only}
    )
    
    return users


@router.post("/", response_model=UserResponse)
async def create_user(
    request: Request,
    user_data: UserCreate,
    current_user: User = Depends(deps.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Cria novo usuário (apenas admins).
    
    Aplica todas as validações de negócio implementadas.
    """
    # UserService já verifica permissões e validações
    new_user = await user_service.create_user(user_data)
    
    # Log da ação para auditoria
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="create_user",
        resource="user",
        resource_id=str(new_user.id),
        details={"email": user_data.email, "role": getattr(user_data, 'role', 'user')}
    )
    
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(deps.get_current_active_user)
) -> UserResponse:
    """
    Retorna informações do usuário atual.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: Request,
    user_data: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Atualiza informações do usuário atual.
    
    Aplica validações de email único e outros campos.
    """
    # UserService já valida dados e permissões
    updated_user = await user_service.update_user(
        user_id=current_user.id,
        user_data=user_data,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="update_profile"
    )
    
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Busca usuário por ID.
    
    Usuários podem ver apenas próprio perfil, admins veem qualquer um.
    """
    # UserService já verifica permissões
    user = await user_service.get_user_profile(
        user_id=user_id,
        current_user=current_user
    )
    
    # Log da ação se for diferente do usuário atual
    if user_id != current_user.id:
        log_user_action(
            request=request,
            user_id=current_user.id,
            action="view_user_profile",
            resource="user",
            resource_id=str(user_id)
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: int,
    request: Request,
    user_data: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Atualiza usuário por ID (apenas próprio perfil ou admin).
    
    Aplica validações de permissão e dados.
    """
    # UserService já verifica todas as permissões e validações
    updated_user = await user_service.update_user(
        user_id=user_id,
        user_data=user_data,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="update_user",
        resource="user",
        resource_id=str(user_id)
    )
    
    return updated_user


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, str]:
    """
    Desativa usuário (soft delete).
    
    Usuários podem se auto-desativar, admins podem desativar outros.
    """
    # UserService já valida permissões e regras de negócio
    success = await user_service.deactivate_user(
        user_id=user_id,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="deactivate_user",
        resource="user",
        resource_id=str(user_id)
    )
    
    return {"message": "Usuário desativado com sucesso"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, str]:
    """
    Reativa usuário (apenas admins).
    """
    # UserService já verifica se usuário é admin
    success = await user_service.activate_user(
        user_id=user_id,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="activate_user",
        resource="user",
        resource_id=str(user_id)
    )
    
    return {"message": "Usuário ativado com sucesso"}


@router.get("/search/{search_term}", response_model=List[UserResponse])
async def search_users(
    search_term: str,
    request: Request,
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados"),
    current_user: User = Depends(deps.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    """
    Busca usuários por nome ou email (apenas admins).
    """
    # UserService já valida permissões
    users = await user_service.search_users(
        search_term=search_term,
        limit=limit,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="search_users",
        details={"search_term": search_term, "results_count": len(users)}
    )
    
    return users


@router.get("/stats/overview")
async def get_user_statistics(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    Retorna estatísticas dos usuários (apenas admins).
    """
    # UserService já verifica se é admin
    stats = await user_service.get_user_statistics(current_user)
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="view_user_stats"
    )
    
    return stats


@router.get("/me/activity", response_model=List[Dict[str, Any]])
async def get_my_recent_activity(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Retorna uma lista de atividades recentes para o usuário atual.
    
    TODO: Substituir por dados reais de um sistema de auditoria/logs.
    """
    # Mock data para permitir o frontend consumir
    mock_activities = [
        {
            "id": "1",
            "type": "book_completed",
            "title": "Livro concluído",
            "description": "Seu livro 'Aventuras na Floresta Mágica' foi gerado com sucesso",
            "timestamp": "2025-11-27T10:00:00Z",
            "metadata": {"book_id": 1}
        },
        {
            "id": "2",
            "type": "book_created",
            "title": "Novo livro criado",
            "description": "Você criou o livro 'Animais do Oceano'",
            "timestamp": "2025-11-27T08:30:00Z",
            "metadata": {"book_id": 2}
        },
        {
            "id": "3",
            "type": "pdf_downloaded",
            "title": "PDF baixado",
            "description": "Você fez download do PDF 'Contos de Fadas'",
            "timestamp": "2025-11-26T16:00:00Z",
            "metadata": {"book_id": 1, "pdf_url": "/uploads/book_1.pdf"}
        },
    ]
    
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="view_recent_activity"
    )
    
    return mock_activities
