"""
Service de livros com validação de negócio e integração com IA.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.book_repository import BookRepository
from app.repositories.user_repository import UserRepository
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.services.notification_service import notification_service
from app.services.ai.factory import AIServiceFactory
# from app.worker.tasks import generate_book_content, generate_book_pdf  # Circular import - import dinamicamente
from celery.result import AsyncResult


class BookService:
    """Service para operações relacionadas a livros."""
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa o service com dependências.
        
        Args:
            db: Sessão async do banco de dados
        """
        self.db = db
        self.book_repo = BookRepository(db)
        self.user_repo = UserRepository(db)
        self.ai_service = AIServiceFactory.create_ai_service()
    
    async def create_book(self, book_data: BookCreate, current_user: User) -> Book:
        """
        Cria novo livro com validações de negócio.
        
        Args:
            book_data: Dados do livro
            current_user: Usuário que está criando o livro
            
        Returns:
            Livro criado
            
        Raises:
            HTTPException: Se dados forem inválidos ou limites excedidos
        """
        # Validar dados de entrada
        self._validate_book_data(book_data)
        
        # Verificar limite de livros por usuário (regra de negócio)
        await self._check_user_book_limit(current_user.id)
        
        # Criar livro
        new_book = await self.book_repo.create(
            title=book_data.title,
            description=book_data.description,
            pages_count=book_data.pages_count,
            style=book_data.style,
            status="draft",
            user_id=current_user.id
        )
        
        await self.db.commit()
        return new_book
    
    async def start_book_generation(self, book_id: int, current_user: User) -> Dict[str, Any]:
        """
        Inicia geração assíncrona do conteúdo do livro.
        
        Args:
            book_id: ID do livro
            current_user: Usuário que está solicitando a geração
            
        Returns:
            Informações sobre a task de geração
            
        Raises:
            HTTPException: Se livro não for encontrado ou não pertencer ao usuário
        """
        # Verificar se livro existe e pertence ao usuário
        book = await self._get_user_book(book_id, current_user.id)
        
        # Verificar se livro está em status adequado
        if book.status not in ["draft", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Livro não pode ser gerado no status '{book.status}'"
            )
        
        # Atualizar status para processamento
        await self.book_repo.update_status(book_id, "processing")
        await self.db.commit()
        
        # Importação dinâmica para evitar circular import
        from app.worker.tasks import generate_book_content
        
        # Iniciar task assíncrona de geração
        task = generate_book_content.delay(book_id, user_id, book.title)
        
        return {
            "message": "Geração do livro iniciada",
            "task_id": task.id,
            "book_id": book_id,
            "status": "processing"
        }
    
    async def get_book_generation_status(
        self, 
        task_id: str, 
        current_user: User
    ) -> Dict[str, Any]:
        """
        Verifica status da geração do livro.
        
        Args:
            task_id: ID da task Celery
            current_user: Usuário que está verificando o status
            
        Returns:
            Status da geração
        """
        # Verificar status da task
        result = AsyncResult(task_id)
        
        status_info = {
            "task_id": task_id,
            "status": result.status,
            "current": getattr(result, 'current', 0),
            "total": getattr(result, 'total', 1)
        }
        
        if result.successful():
            status_info["result"] = result.result
        elif result.failed():
            status_info["error"] = str(result.info)
        
        return status_info
    
    async def generate_pdf(self, book_id: int, current_user: User) -> Dict[str, Any]:
        """
        Inicia geração do PDF do livro.
        
        Args:
            book_id: ID do livro
            current_user: Usuário que está solicitando a geração
            
        Returns:
            Informações sobre a task de geração do PDF
            
        Raises:
            HTTPException: Se livro não estiver completo ou não pertencer ao usuário
        """
        # Verificar se livro existe e pertence ao usuário
        book = await self._get_user_book(book_id, current_user.id)
        
        # Verificar se livro está completo
        if book.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Livro deve estar completo para gerar PDF"
            )
        
        # Iniciar task assíncrona de geração do PDF
        task = generate_book_pdf.delay(book_id)
        
        return {
            "message": "Geração do PDF iniciada",
            "task_id": task.id,
            "book_id": book_id
        }
    
    async def get_user_books(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[str] = None,
        current_user: User = None
    ) -> List[Book]:
        """
        Lista livros do usuário.
        
        Args:
            user_id: ID do usuário
            skip: Número de registros para pular
            limit: Limite de registros por página
            status_filter: Filtro por status (opcional)
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            Lista de livros
            
        Raises:
            HTTPException: Se não tiver permissão
        """
        # Verificar permissões
        if current_user.id != user_id and not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para ver livros deste usuário"
            )
        
        # Validar parâmetros
        if skip < 0 or limit <= 0 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parâmetros de paginação inválidos"
            )
        
        if status_filter:
            return await self.book_repo.get_by_status(status_filter, skip, limit)
        else:
            return await self.book_repo.get_by_user(user_id, skip, limit)
    
    async def get_book_details(self, book_id: int, current_user: User) -> Book:
        """
        Retorna detalhes completos do livro.
        
        Args:
            book_id: ID do livro
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            Livro com detalhes completos
            
        Raises:
            HTTPException: Se livro não for encontrado ou não tiver permissão
        """
        # Buscar livro com dados do usuário
        book = await self.book_repo.get_with_user(book_id)
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado"
            )
        
        # Verificar permissões
        if book.user_id != current_user.id and not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para ver este livro"
            )
        
        return book
    
    async def update_book(
        self, 
        book_id: int, 
        book_data: BookUpdate, 
        current_user: User
    ) -> Book:
        """
        Atualiza dados do livro.
        
        Args:
            book_id: ID do livro
            book_data: Novos dados do livro
            current_user: Usuário que está fazendo a atualização
            
        Returns:
            Livro atualizado
            
        Raises:
            HTTPException: Se livro não for encontrado ou não tiver permissão
        """
        # Verificar se livro existe e pertence ao usuário
        book = await self._get_user_book(book_id, current_user.id)
        
        # Verificar se livro pode ser editado
        if book.status not in ["draft", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Livro não pode ser editado no status '{book.status}'"
            )
        
        # Preparar dados para atualização
        update_data = {}
        
        if book_data.title:
            update_data["title"] = book_data.title
        
        if book_data.description is not None:
            update_data["description"] = book_data.description
        
        if book_data.pages_count:
            # Validar nova quantidade de páginas
            self._validate_pages_count(book_data.pages_count)
            update_data["pages_count"] = book_data.pages_count
        
        if book_data.style:
            self._validate_style(book_data.style)
            update_data["style"] = book_data.style
        
        # Atualizar livro
        updated_book = await self.book_repo.update(book_id, **update_data)
        await self.db.commit()
        
        return updated_book
    
    async def delete_book(self, book_id: int, current_user: User) -> bool:
        """
        Remove livro.
        
        Args:
            book_id: ID do livro
            current_user: Usuário que está removendo
            
        Returns:
            True se removido com sucesso
            
        Raises:
            HTTPException: Se livro não for encontrado ou não tiver permissão
        """
        # Verificar se livro existe e pertence ao usuário
        book = await self._get_user_book(book_id, current_user.id)
        
        # Verificar se livro pode ser removido
        if book.status == "processing":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover livro em processamento"
            )
        
        # Remover livro
        result = await self.book_repo.delete(book_id)
        await self.db.commit()
        
        return result
    
    async def search_books(
        self, 
        search_term: str, 
        user_id: Optional[int] = None,
        limit: int = 50,
        current_user: User = None
    ) -> List[Book]:
        """
        Busca livros por termo.
        
        Args:
            search_term: Termo de busca
            user_id: ID do usuário (opcional, para buscar apenas seus livros)
            limit: Limite de resultados
            current_user: Usuário que está fazendo a busca
            
        Returns:
            Lista de livros encontrados
        """
        # Validar termo de busca
        if not search_term or len(search_term.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Termo de busca deve ter pelo menos 3 caracteres"
            )
        
        # Se user_id especificado, verificar permissões
        if user_id and current_user.id != user_id and not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para buscar livros deste usuário"
            )
        
        return await self.book_repo.search_books(
            search_term.strip(), user_id, limit
        )
    
    async def get_books_statistics(
        self, 
        user_id: Optional[int] = None,
        current_user: User = None
    ) -> Dict[str, Any]:
        """
        Retorna estatísticas dos livros.
        
        Args:
            user_id: ID do usuário (opcional, para stats específicas)
            current_user: Usuário que está fazendo a requisição
            
        Returns:
            Dict com estatísticas
        """
        # Verificar permissões
        if user_id and current_user.id != user_id and not self._is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para ver estatísticas deste usuário"
            )
        
        return await self.book_repo.get_books_stats(user_id)
    
    async def _get_user_book(self, book_id: int, user_id: int) -> Book:
        """
        Busca livro e verifica se pertence ao usuário.
        
        Args:
            book_id: ID do livro
            user_id: ID do usuário
            
        Returns:
            Livro encontrado
            
        Raises:
            HTTPException: Se livro não for encontrado ou não pertencer ao usuário
        """
        book = await self.book_repo.get(book_id)
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado"
            )
        
        if book.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Livro não pertence a este usuário"
            )
        
        return book
    
    async def _check_user_book_limit(self, user_id: int) -> None:
        """
        Verifica limite de livros por usuário.
        
        Args:
            user_id: ID do usuário
            
        Raises:
            HTTPException: Se limite foi excedido
        """
        user = await self.user_repo.get(user_id)
        if not user:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        # Contar livros ativos do usuário
        book_count = await self.book_repo.count_by_user(user_id)
        
        # Usar limite definido no modelo do usuário
        max_books = user.max_books_allowed
        
        if book_count >= max_books:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limite de {max_books} livros por usuário excedido. Faça upgrade para Premium para criar mais livros."
            )
    
    def _validate_book_data(self, book_data: BookCreate) -> None:
        """
        Valida dados do livro.
        
        Args:
            book_data: Dados para validar
            
        Raises:
            HTTPException: Se dados forem inválidos
        """
        # Validar título
        if not book_data.title or len(book_data.title.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Título deve ter pelo menos 3 caracteres"
            )
        
        if len(book_data.title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Título deve ter no máximo 200 caracteres"
            )
        
        # Validar descrição
        if book_data.description and len(book_data.description) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Descrição deve ter no máximo 1000 caracteres"
            )
        
        # Validar quantidade de páginas (regra de negócio: 5-20 páginas)
        self._validate_pages_count(book_data.pages_count)
        
        # Validar estilo
        self._validate_style(book_data.style)
    
    def _validate_pages_count(self, pages_count: int) -> None:
        """
        Valida quantidade de páginas.
        
        Args:
            pages_count: Número de páginas
            
        Raises:
            HTTPException: Se quantidade for inválida
        """
        if pages_count < 5 or pages_count > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Livro deve ter entre 5 e 20 páginas"
            )
    
    def _validate_style(self, style: str) -> None:
        """
        Valida estilo do livro.
        
        Args:
            style: Estilo para validar
            
        Raises:
            HTTPException: Se estilo for inválido
        """
        valid_styles = ["cartoon", "realistic", "manga", "classic"]
        
        if style not in valid_styles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estilo deve ser um dos: {', '.join(valid_styles)}"
            )
    
    def _is_admin(self, user: User) -> bool:
        """
        Verifica se usuário é administrador.
        
        Args:
            user: Usuário para verificar
            
        Returns:
            True se for administrador
        """
        # Verifica se o objeto user tem a propriedade is_admin (hybrid_property)
        # ou verifica o role diretamente se for um objeto simples
        if hasattr(user, 'is_admin'):
            return user.is_admin
            
        from app.models.user import UserRole
        return getattr(user, 'role', '') == UserRole.ADMIN