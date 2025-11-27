from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.book import BookStatus

class PageBase(BaseModel):
    page_number: int
    text_content: Optional[str] = None
    image_url: Optional[str] = None

class PageCreate(PageBase):
    pass

class Page(PageBase):
    id: int
    book_id: int

    model_config = ConfigDict(from_attributes=True)

class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    pages_count: int
    style: str

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    pages_count: Optional[int] = None
    style: Optional[str] = None

class BookResponse(BookBase):
    id: int
    status: str
    user_id: int
    cover_image: Optional[str] = None
    pdf_file: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    pages: List[Page] = []

    model_config = ConfigDict(from_attributes=True)

# Alias para compatibilidade
Book = BookResponse
