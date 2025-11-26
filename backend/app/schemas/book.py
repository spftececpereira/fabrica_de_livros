from typing import List, Optional
from pydantic import BaseModel
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

    class Config:
        from_attributes = True

class BookBase(BaseModel):
    title: str
    theme: str
    style: str

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None

class Book(BookBase):
    id: int
    status: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    pages: List[Page] = []

    class Config:
        from_attributes = True
