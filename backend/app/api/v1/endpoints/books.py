from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, Request, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.services.book_service import BookService
from app.models.user import User
from app.schemas.book import BookResponse, BookCreate, BookUpdate
from app.middleware.exception_middleware import log_user_action

router = APIRouter()


def get_book_service(db: AsyncSession = Depends(deps.get_db)) -> BookService:
    """Dependency para injetar BookService."""
    return BookService(db)


@router.get("/", response_model=List[BookResponse])
async def list_user_books(
    request: Request,
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros por página"),
    status_filter: Optional[str] = Query(None, description="Filtrar por status específico"),
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> List[BookResponse]:
    """
    Lista livros do usuário atual com paginação.
    
    Aplica filtros de status e paginação segura.
    """
    # BookService já valida parâmetros e permissões
    books = await book_service.get_user_books(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="list_books",
        details={"count": len(books), "status_filter": status_filter}
    )
    
    return books


@router.post("/", response_model=BookResponse)
async def create_book(
    request: Request,
    book_data: BookCreate,
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> BookResponse:
    """
    Cria novo livro aplicando todas as validações de negócio.
    
    Regras aplicadas:
    - 5-20 páginas (regra crítica PRD)
    - Estilos válidos (cartoon, realistic, manga, classic)
    - Limite por role de usuário (5/50/∞)
    - Validações de título e descrição
    """
    # BookService já aplica todas as validações de negócio
    new_book = await book_service.create_book(
        book_data=book_data,
        current_user=current_user
    )
    
    # Log da ação para auditoria
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="create_book",
        resource="book",
        resource_id=str(new_book.id),
        details={
            "title": book_data.title,
            "pages_count": book_data.pages_count,
            "style": book_data.style
        }
    )
    
    return new_book


@router.post("/{book_id}/generate")
async def start_book_generation(
    book_id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> Dict[str, Any]:
    """
    Inicia geração assíncrona do conteúdo do livro.
    
    Usa Celery para processamento em background com progress tracking.
    """
    # BookService já valida permissões e status do livro
    result = await book_service.start_book_generation(
        book_id=book_id,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="start_book_generation",
        resource="book",
        resource_id=str(book_id)
    )
    
    return result


@router.get("/{book_id}/generation-status/{task_id}")
async def get_generation_status(
    book_id: int,
    task_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> Dict[str, Any]:
    """
    Verifica status da geração do livro em tempo real.
    """
    # BookService já valida permissões
    status_info = await book_service.get_book_generation_status(
        task_id=task_id,
        current_user=current_user
    )
    
    return status_info


@router.get("/{book_id}", response_model=BookResponse)
async def get_book_details(
    book_id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> BookResponse:
    """
    Retorna detalhes completos do livro incluindo páginas.
    
    Verifica permissões de acesso ao livro.
    """
    # BookService já verifica se livro pertence ao usuário
    book = await book_service.get_book_details(
        book_id=book_id,
        current_user=current_user
    )
    
    # Log da ação se necessário (não loggar visualizações próprias frequentes)
    # Apenas se for admin vendo livro de outro usuário
    if hasattr(current_user, 'is_admin') and current_user.is_admin and book.user_id != current_user.id:
        log_user_action(
            request=request,
            user_id=current_user.id,
            action="view_book_details",
            resource="book",
            resource_id=str(book_id)
        )
    
    return book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    request: Request,
    book_data: BookUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> BookResponse:
    """
    Atualiza dados do livro aplicando validações.
    
    Permite edição apenas em status 'draft' ou 'failed'.
    """
    # BookService já valida permissões, status e dados
    updated_book = await book_service.update_book(
        book_id=book_id,
        book_data=book_data,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="update_book",
        resource="book",
        resource_id=str(book_id)
    )
    
    return updated_book


@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> Dict[str, str]:
    """
    Remove livro do usuário.
    
    Não permite remoção se livro estiver em processamento.
    """
    # BookService já valida permissões e status
    success = await book_service.delete_book(
        book_id=book_id,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="delete_book",
        resource="book",
        resource_id=str(book_id)
    )
    
    return {"message": "Livro removido com sucesso"}


@router.post("/{book_id}/generate-pdf")
async def generate_book_pdf(
    book_id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> Dict[str, Any]:
    """
    Inicia geração assíncrona do PDF do livro.
    
    Requer que livro esteja no status 'completed'.
    """
    # BookService já valida permissões e status
    result = await book_service.generate_pdf(
        book_id=book_id,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="generate_pdf",
        resource="book",
        resource_id=str(book_id)
    )
    
    return result


@router.get("/{book_id}/pdf")
async def download_book_pdf(
    book_id: int,
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> StreamingResponse:
    """
    Download do PDF do livro (se disponível).
    """
    # BookService já verifica permissões e se PDF existe
    book = await book_service.get_book_details(
        book_id=book_id,
        current_user=current_user
    )
    
    # Verificar se tem PDF gerado
    if not book.pdf_file:
        from app.exceptions.base_exceptions import ValidationError
        raise ValidationError(
            message="PDF ainda não foi gerado para este livro",
            field="pdf_file"
        )
    
    # Gerar/retornar PDF
    from app.services.pdf_service import PDFService
    pdf_service = PDFService()
    pdf_buffer = await pdf_service.get_book_pdf(book)
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="download_pdf",
        resource="book",
        resource_id=str(book_id)
    )
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={book.title.replace(' ', '_')}.pdf"
        }
    )


@router.get("/search/{search_term}", response_model=List[BookResponse])
async def search_books(
    search_term: str,
    request: Request,
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados"),
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> List[BookResponse]:
    """
    Busca livros por título ou descrição.
    """
    # BookService já valida termo de busca e permissões
    books = await book_service.search_books(
        search_term=search_term,
        user_id=current_user.id,
        limit=limit,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="search_books",
        details={"search_term": search_term, "results_count": len(books)}
    )
    
    return books


@router.get("/stats/overview")
async def get_book_statistics(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> Dict[str, Any]:
    """
    Retorna estatísticas dos livros do usuário.
    """
    # BookService retorna estatísticas do usuário
    stats = await book_service.get_books_statistics(
        user_id=current_user.id,
        current_user=current_user
    )
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="view_book_stats"
    )
    
    return stats


@router.get("/recent/list", response_model=List[BookResponse])
async def get_recent_books(
    request: Request,
    days: int = Query(7, ge=1, le=30, description="Número de dias para considerar recente"),
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados"),
    current_user: User = Depends(deps.get_current_active_user),
    book_service: BookService = Depends(get_book_service)
) -> List[BookResponse]:
    """
    Retorna livros criados recentemente pelo usuário.
    """
    # Usar repository diretamente para esta funcionalidade simples
    from app.repositories.book_repository import BookRepository
    from app.core.database import get_async_session
    
    async with get_async_session() as session:
        book_repo = BookRepository(session)
        books = await book_repo.get_recent_books(days=days, limit=limit)
        
        # Filtrar apenas livros do usuário
        user_books = [book for book in books if book.user_id == current_user.id]
    
    # Log da ação
    log_user_action(
        request=request,
        user_id=current_user.id,
        action="view_recent_books",
        details={"days": days, "count": len(user_books)}
    )
    
    return user_books
