"""
Repository base genérico com operações CRUD usando SQLAlchemy async.
"""

from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repository base com operações CRUD genéricas."""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Inicializa o repository.
        
        Args:
            model: Classe do modelo SQLAlchemy
            db: Sessão async do banco de dados
        """
        self.model = model
        self.db = db
    
    async def get(self, id: int) -> Optional[ModelType]:
        """
        Busca um registro por ID.
        
        Args:
            id: ID do registro
            
        Returns:
            Instância do modelo ou None se não encontrado
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Busca múltiplos registros com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Limite de registros por página
            order_by: Campo para ordenação
            
        Returns:
            Lista de instâncias do modelo
        """
        query = select(self.model).offset(skip).limit(limit)
        
        if order_by:
            # Aplicar ordenação se especificada
            order_field = getattr(self.model, order_by, None)
            if order_field:
                query = query.order_by(order_field)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, **kwargs) -> ModelType:
        """
        Cria um novo registro.
        
        Args:
            **kwargs: Dados para criação do registro
            
        Returns:
            Instância criada do modelo
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        Atualiza um registro por ID.
        
        Args:
            id: ID do registro
            **kwargs: Dados para atualização
            
        Returns:
            Instância atualizada ou None se não encontrado
        """
        # Primeiro verificar se o registro existe
        instance = await self.get(id)
        if not instance:
            return None
        
        # Atualizar campos
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        await self.db.flush()
        await self.db.refresh(instance)
        return instance
    
    async def delete(self, id: int) -> bool:
        """
        Remove um registro por ID.
        
        Args:
            id: ID do registro
            
        Returns:
            True se removido com sucesso, False se não encontrado
        """
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0
    
    async def count(self, **filters) -> int:
        """
        Conta registros com filtros opcionais.
        
        Args:
            **filters: Filtros para aplicar na contagem
            
        Returns:
            Número total de registros
        """
        query = select(func.count(self.model.id))
        
        # Aplicar filtros se fornecidos
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def exists(self, **filters) -> bool:
        """
        Verifica se existe registro com filtros.
        
        Args:
            **filters: Filtros para verificação
            
        Returns:
            True se existe, False caso contrário
        """
        query = select(self.model.id)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        query = query.limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_by_filters(self, **filters) -> List[ModelType]:
        """
        Busca registros por filtros customizados.
        
        Args:
            **filters: Filtros para busca
            
        Returns:
            Lista de instâncias do modelo
        """
        query = select(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())