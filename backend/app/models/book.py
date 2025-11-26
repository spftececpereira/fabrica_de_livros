from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class BookStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    theme = Column(String, nullable=False) # e.g., "Space Adventure"
    style = Column(String, nullable=False) # e.g., "Cartoon", "Realistic"
    status = Column(String, default=BookStatus.DRAFT)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="books")
    pages = relationship("Page", back_populates="book", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    page_number = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=True)
    image_url = Column(String, nullable=True) # URL to S3 or local storage
    image_prompt = Column(Text, nullable=True) # The prompt used to generate the image
    
    book = relationship("Book", back_populates="pages")
