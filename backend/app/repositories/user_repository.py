"""
Repository específico para operações com usuários.
"""

from typing import Optional, List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository para operações específicas com usuários."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Busca usuário por email.
        
        Args:
            email: Email do usuário
            
        Returns:
            Usuário encontrado ou None
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica se email já existe na base.
        
        Args:
            email: Email para verificar
            exclude_id: ID para excluir da verificação (útil para updates)
            
        Returns:
            True se email existe, False caso contrário
        """
        query = select(User.id).where(User.email == email)
        
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await self.db.execute(query.limit(1))
        return result.scalar_one_or_none() is not None
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Busca usuários ativos com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Limite de registros por página
            
        Returns:
            Lista de usuários ativos
        """
        result = await self.db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def search_by_name_or_email(self, search_term: str, limit: int = 50) -> List[User]:
        """
        Busca usuários por nome ou email (busca parcial).
        
        Args:
            search_term: Termo de busca
            limit: Limite de resultados
            
        Returns:
            Lista de usuários que correspondem ao termo
        """
        search_pattern = f"%{search_term.lower()}%"
        
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    User.is_active == True,
                    or_(
                        User.email.ilike(search_pattern),
                        User.full_name.ilike(search_pattern)
                    )
                )
            )
            .limit(limit)
            .order_by(User.full_name)
        )
        return list(result.scalars().all())
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Desativa um usuário (soft delete).
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se desativado com sucesso, False se não encontrado
        """
        user = await self.get(user_id)
        if not user:
            return False
        
        user.is_active = False
        await self.db.flush()
        return True
    
    async def activate_user(self, user_id: int) -> bool:
        """
        Reativa um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se ativado com sucesso, False se não encontrado
        """
        user = await self.get(user_id)
        if not user:
            return False
        
        user.is_active = True
        await self.db.flush()
        return True
    
    async def update_last_login(self, user_id: int) -> Optional[User]:
        """
        Atualiza timestamp do último login.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Usuário atualizado ou None se não encontrado
        """
        from datetime import datetime
        
        return await self.update(user_id, last_login=datetime.utcnow())
    
    async def get_users_stats(self) -> dict:
        """
        Retorna estatísticas dos usuários.
        
        Returns:
            Dict com estatísticas: total, ativos, inativos
        """
        from sqlalchemy import func, case
        
        result = await self.db.execute(
            select(
                func.count(User.id).label('total'),
                func.sum(case((User.is_active == True, 1), else_=0)).label('active'),
                func.sum(case((User.is_active == False, 1), else_=0)).label('inactive')
            )
        )
        
        stats = result.first()
        return {
            'total': stats.total or 0,
            'active': stats.active or 0, 
            'inactive': stats.inactive or 0
        }