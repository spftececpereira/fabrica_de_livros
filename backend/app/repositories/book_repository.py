"""
Repository específico para operações com livros.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Repository para operações específicas com livros."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Book, db)
    
    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Book]:
        """
        Busca livros de um usuário específico.
        
        Args:
            user_id: ID do usuário
            skip: Número de registros para pular
            limit: Limite de registros por página
            
        Returns:
            Lista de livros do usuário
        """
        result = await self.db.execute(
            select(Book)
            .where(Book.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Book.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Book]:
        """
        Busca livros por status.
        
        Args:
            status: Status do livro (draft, processing, completed, failed)
            skip: Número de registros para pular
            limit: Limite de registros por página
            
        Returns:
            Lista de livros com o status especificado
        """
        result = await self.db.execute(
            select(Book)
            .where(Book.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(Book.updated_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_style(self, style: str, skip: int = 0, limit: int = 100) -> List[Book]:
        """
        Busca livros por estilo.
        
        Args:
            style: Estilo do livro (cartoon, realistic, manga, classic)
            skip: Número de registros para pular
            limit: Limite de registros por página
            
        Returns:
            Lista de livros com o estilo especificado
        """
        result = await self.db.execute(
            select(Book)
            .where(Book.style == style)
            .offset(skip)
            .limit(limit)
            .order_by(Book.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def search_books(
        self, 
        search_term: str, 
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Book]:
        """
        Busca livros por título ou descrição.
        
        Args:
            search_term: Termo de busca
            user_id: ID do usuário (opcional, para buscar apenas seus livros)
            limit: Limite de resultados
            
        Returns:
            Lista de livros que correspondem ao termo
        """
        search_pattern = f"%{search_term.lower()}%"
        
        conditions = [
            or_(
                Book.title.ilike(search_pattern),
                Book.description.ilike(search_pattern)
            )
        ]
        
        if user_id:
            conditions.append(Book.user_id == user_id)
        
        result = await self.db.execute(
            select(Book)
            .where(and_(*conditions))
            .limit(limit)
            .order_by(Book.title)
        )
        return list(result.scalars().all())
    
    async def get_with_user(self, book_id: int) -> Optional[Book]:
        """
        Busca livro com informações do usuário carregadas.
        
        Args:
            book_id: ID do livro
            
        Returns:
            Livro com dados do usuário ou None
        """
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.user))
            .where(Book.id == book_id)
        )
        return result.scalar_one_or_none()
    
    async def get_completed_books(
        self, 
        user_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Book]:
        """
        Busca livros completos (com PDF gerado).
        
        Args:
            user_id: ID do usuário (opcional)
            skip: Número de registros para pular
            limit: Limite de registros por página
            
        Returns:
            Lista de livros completos
        """
        conditions = [
            Book.status == "completed",
            Book.pdf_file.isnot(None)
        ]
        
        if user_id:
            conditions.append(Book.user_id == user_id)
        
        result = await self.db.execute(
            select(Book)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(Book.updated_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_status(self, book_id: int, status: str) -> Optional[Book]:
        """
        Atualiza apenas o status do livro.
        
        Args:
            book_id: ID do livro
            status: Novo status
            
        Returns:
            Livro atualizado ou None se não encontrado
        """
        return await self.update(book_id, status=status)
    
    async def get_books_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Retorna estatísticas dos livros.
        
        Args:
            user_id: ID do usuário (opcional, para stats específicas)
            
        Returns:
            Dict com estatísticas: total, por status, por estilo, etc
        """
        from sqlalchemy import case
        
        conditions = []
        if user_id:
            conditions.append(Book.user_id == user_id)
        
        base_query = select(Book.id)
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Estatísticas por status
        status_query = select(
            Book.status,
            func.count(Book.id).label('count')
        ).group_by(Book.status)
        
        if conditions:
            status_query = status_query.where(and_(*conditions))
        
        # Estatísticas por estilo  
        style_query = select(
            Book.style,
            func.count(Book.id).label('count')
        ).group_by(Book.style)
        
        if conditions:
            style_query = style_query.where(and_(*conditions))
        
        # Executar queries
        total_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        
        status_result = await self.db.execute(status_query)
        style_result = await self.db.execute(style_query)
        
        # Processar resultados
        total = total_result.scalar_one()
        
        status_stats = {row.status: row.count for row in status_result.fetchall()}
        style_stats = {row.style: row.count for row in style_result.fetchall()}
        
        return {
            'total': total,
            'by_status': status_stats,
            'by_style': style_stats
        }
    
    async def get_recent_books(self, days: int = 7, limit: int = 10) -> List[Book]:
        """
        Busca livros criados recentemente.
        
        Args:
            days: Número de dias para considerar como recente
            limit: Limite de resultados
            
        Returns:
            Lista de livros recentes
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(Book)
            .where(Book.created_at >= cutoff_date)
            .limit(limit)
            .order_by(Book.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def count_by_user(self, user_id: int) -> int:
        """
        Conta livros de um usuário específico.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Número total de livros do usuário
        """
        return await self.count(user_id=user_id)