"""
Service de usuário com validações de negócio.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash
from app.services.notification_service import notification_service # Import notification service


class UserService:
    """Service para operações relacionadas a usuários."""
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa o service com dependências.
        
        Args:
            db: Sessão async do banco de dados
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Busca usuário por ID.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Usuário encontrado ou None
        """
        return await self.user_repo.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Busca usuário por email.
        
        Args:
            email: Email do usuário
            
        Returns:
            Usuário encontrado ou None
        """
        return await self.user_repo.get_by_email(email)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Cria novo usuário com validações.
        
        Args:
            user_data: Dados do usuário
            
        Returns:
            Usuário criado
            
        Raises:
            HTTPException: Se email já existir ou dados forem inválidos
        """
        # Validar se email já existe
        if await self.user_repo.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Validar dados de entrada
        self._validate_user_data(user_data)
        
        # Criar hash da senha
        password_hash = get_password_hash(user_data.password)
        
        # Criar usuário
        new_user = await self.user_repo.create(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=password_hash,
            is_active=True
        )
        
        await self.db.commit()
        
        # Enviar email de boas-vindas
        await notification_service.notify_welcome_new_user(new_user)
        
        return new_user
    
    async def update_user(
        self, 
        user_id: int, 
        user_data: UserUpdate, 
        current_user: User
    ) -> User:
        """
        Atualiza dados do usuário.
        
        Args:
            user_id: ID do usuário a ser atualizado
            user_data: Novos dados do usuário
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            Usuário atualizado
            
        Raises:
            HTTPException: Se usuário não for encontrado ou não tiver permissão
        """
        # Verificar se usuário existe
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar permissões (usuário só pode atualizar próprios dados)
        if current_user.id != user_id and not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para atualizar este usuário"
            )
        
        # Validar email se estiver sendo alterado
        if user_data.email and user_data.email != user.email:
            if await self.user_repo.email_exists(user_data.email, exclude_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já está em uso"
                )
        
        # Preparar dados para atualização
        update_data = {}
        
        if user_data.email:
            update_data["email"] = user_data.email
        
        if user_data.full_name:
            update_data["full_name"] = user_data.full_name
        
        if user_data.password:
            self._validate_password_strength(user_data.password)
            update_data["password_hash"] = get_password_hash(user_data.password)
        
        # Atualizar usuário
        updated_user = await self.user_repo.update(user_id, **update_data)
        await self.db.commit()
        
        return updated_user
    
    async def deactivate_user(self, user_id: int, current_user: User) -> bool:
        """
        Desativa usuário (soft delete).
        
        Args:
            user_id: ID do usuário
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            True se desativado com sucesso
            
        Raises:
            HTTPException: Se não tiver permissão ou usuário não existir
        """
        # Verificar se usuário existe
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar permissões (apenas admin pode desativar outros usuários)
        if current_user.id != user_id and not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para desativar este usuário"
            )
        
        # Não permitir auto-desativação de admin
        if self._is_admin(user) and current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administradores não podem se auto-desativar"
            )
        
        # Desativar usuário
        result = await self.user_repo.deactivate_user(user_id)
        await self.db.commit()
        
        return result
    
    async def activate_user(self, user_id: int, current_user: User) -> bool:
        """
        Reativa usuário.
        
        Args:
            user_id: ID do usuário
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            True se ativado com sucesso
            
        Raises:
            HTTPException: Se não tiver permissão
        """
        # Apenas admin pode ativar usuários
        if not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem ativar usuários"
            )
        
        # Ativar usuário
        result = await self.user_repo.activate_user(user_id)
        await self.db.commit()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return result
    
    async def get_users_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True,
        current_user: User = None
    ) -> List[User]:
        """
        Lista usuários com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Limite de registros por página
            active_only: Se deve retornar apenas usuários ativos
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            Lista de usuários
            
        Raises:
            HTTPException: Se não tiver permissão
        """
        # Verificar permissões (apenas admin pode listar usuários)
        if not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para listar usuários"
            )
        
        # Validar parâmetros de paginação
        if skip < 0 or limit <= 0 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parâmetros de paginação inválidos"
            )
        
        if active_only:
            return await self.user_repo.get_active_users(skip, limit)
        else:
            return await self.user_repo.get_multi(skip, limit, order_by="created_at")
    
    async def search_users(
        self, 
        search_term: str, 
        limit: int = 50,
        current_user: User = None
    ) -> List[User]:
        """
        Busca usuários por nome ou email.
        
        Args:
            search_term: Termo de busca
            limit: Limite de resultados
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            Lista de usuários encontrados
            
        Raises:
            HTTPException: Se não tiver permissão
        """
        # Verificar permissões (apenas admin pode buscar usuários)
        if not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para buscar usuários"
            )
        
        # Validar termo de busca
        if not search_term or len(search_term.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Termo de busca deve ter pelo menos 3 caracteres"
            )
        
        return await self.user_repo.search_by_name_or_email(
            search_term.strip(), limit
        )
    
    async def get_user_statistics(self, current_user: User) -> Dict[str, Any]:
        """
        Retorna estatísticas dos usuários.
        
        Args:
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            Dict com estatísticas
            
        Raises:
            HTTPException: Se não tiver permissão
        """
        # Verificar permissões (apenas admin pode ver estatísticas)
        if not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para ver estatísticas"
            )
        
        return await self.user_repo.get_users_stats()
    
    async def get_user_profile(self, user_id: int, current_user: User) -> User:
        """
        Retorna perfil completo do usuário.
        
        Args:
            user_id: ID do usuário
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            Dados do usuário
            
        Raises:
            HTTPException: Se não tiver permissão ou usuário não existir
        """
        # Verificar se usuário existe
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar permissões (usuário só pode ver próprio perfil, admin vê qualquer um)
        if current_user.id != user_id and not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para ver este perfil"
            )
        
        return user
    
    def _validate_user_data(self, user_data: UserCreate) -> None:
        """
        Valida dados do usuário.
        
        Args:
            user_data: Dados para validar
            
        Raises:
            HTTPException: Se dados forem inválidos
        """
        # Validar email
        if not self._is_valid_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de email inválido"
            )
        
        # Validar nome
        if not user_data.full_name or len(user_data.full_name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome deve ter pelo menos 2 caracteres"
            )
        
        # Validar senha
        self._validate_password_strength(user_data.password)
    
    def _validate_password_strength(self, password: str) -> None:
        """
        Valida força da senha.
        
        Args:
            password: Senha para validar
            
        Raises:
            HTTPException: Se senha não atender critérios
        """
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve ter pelo menos 8 caracteres"
            )
        
        if not any(char.isdigit() for char in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve conter pelo menos um número"
            )
        
        if not any(char.isalpha() for char in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve conter pelo menos uma letra"
            )
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Valida formato do email.
        
        Args:
            email: Email para validar
            
        Returns:
            True se formato for válido
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_admin(self, user: User) -> bool:
        """
        Verifica se usuário é administrador.
        
        Args:
            user: Usuário para verificar
            
        Returns:
            True se for administrador
        """
        # TODO: Implementar sistema de roles/permissions
        # Por enquanto, verificar se tem atributo is_admin ou similar
        return getattr(user, 'is_admin', False)