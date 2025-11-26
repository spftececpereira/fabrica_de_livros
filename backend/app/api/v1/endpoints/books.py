from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.book import Book, BookStatus
from app.models.user import User
from app.schemas.book import Book as BookSchema, BookCreate, BookUpdate
from app.worker.tasks import generate_story_task

router = APIRouter()

@router.get("/", response_model=List[BookSchema])
async def read_books(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve books.
    """
    # Use selectinload to fetch pages eagerly if needed, or just books
    result = await db.execute(
        select(Book)
        .where(Book.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Book.pages))
    )
    books = result.scalars().all()
    return books

@router.post("/", response_model=BookSchema)
async def create_book(
    *,
    db: AsyncSession = Depends(deps.get_db),
    book_in: BookCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new book.
    """
    book = Book(
        title=book_in.title,
        theme=book_in.theme,
        style=book_in.style,
        owner_id=current_user.id,
        status=BookStatus.GENERATING # Set initial status
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)
    
    # Trigger Async Task
    # Note: We pass the book ID and prompt (theme) to the task
    generate_story_task.delay(book_id=book.id, theme=book.theme, style=book.style)
    
    # Explicitly set pages to empty list to avoid lazy load error on serialization
    # because the relationship is not loaded and we are in async context
    # This is safe as it is a newly created book
    # We need to bypass SQLAlchemy instrumentation for this to work purely for Pydantic
    # or just rely on the fact that we can return a dict or similar.
    # But setting the attribute on the instance might trigger SQLAlchemy.
    # A safer way is to return a response model instance constructed manually if needed,
    # or just ensure Pydantic doesn't trigger the load.
    # However, simply accessing it might trigger it.
    # Let's try setting it to empty list, usually SQLAlchemy allows setting relationships.
    # If that fails, we can reload it with options.
    
    # Option 1: Reload with options (safest)
    # result = await db.execute(select(Book).where(Book.id == book.id).options(selectinload(Book.pages)))
    # book = result.scalars().first()
    
    # Option 2: Just return the object and hope Pydantic doesn't touch it? No, Pydantic reads all fields.
    
    # Let's go with Option 1: Reloading is clean.
    result = await db.execute(select(Book).where(Book.id == book.id).options(selectinload(Book.pages)))
    book = result.scalars().first()
    
    return book

@router.get("/{book_id}", response_model=BookSchema)
async def read_book(
    book_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get book by ID.
    """
    result = await db.execute(
        select(Book)
        .where(Book.id == book_id)
        .where(Book.owner_id == current_user.id)
        .options(selectinload(Book.pages))
    )
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

from fastapi.responses import StreamingResponse
from app.services.pdf_service import PDFService

@router.get("/{book_id}/pdf")
async def download_book_pdf(
    book_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate and download PDF for the book.
    """
    result = await db.execute(
        select(Book)
        .where(Book.id == book_id)
        .where(Book.owner_id == current_user.id)
        .options(selectinload(Book.pages))
    )
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    pdf_buffer = PDFService.generate_book_pdf(book)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=book_{book_id}.pdf"}
    )
