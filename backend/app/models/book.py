from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, CheckConstraint, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.database import Base
from app.exceptions.base_exceptions import (
    ValidationError,
    InvalidBookPagesError,
    ErrorCode
)
import enum
from typing import List, Optional
import re

class BookStatus(str, enum.Enum):
    """Status do livro durante seu ciclo de vida."""
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BookStyle(str, enum.Enum):
    """Estilos disponíveis para livros de colorir."""
    CARTOON = "cartoon"
    REALISTIC = "realistic"
    MANGA = "manga"
    CLASSIC = "classic"


class Book(Base):
    """
    Modelo de livro com validações de negócio baseadas no PRD.
    
    Regras implementadas:
    - Livros devem ter entre 5 e 20 páginas
    - Título deve ter entre 3 e 200 caracteres
    - Descrição limitada a 1000 caracteres
    - Estilos pré-definidos
    - Status controlado com transições válidas
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    pages_count = Column(Integer, nullable=False)
    style = Column(String(20), nullable=False)
    status = Column(String(20), default=BookStatus.DRAFT)
    cover_image = Column(String)
    pdf_file = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="books")
    pages = relationship("Page", back_populates="book", cascade="all, delete-orphan")

    # Constraints no banco
    __table_args__ = (
        CheckConstraint(
            'pages_count >= 5 AND pages_count <= 20',
            name='valid_pages_count'
        ),
        CheckConstraint(
            "status IN ('draft', 'processing', 'completed', 'failed')",
            name='valid_status'
        ),
        CheckConstraint(
            "style IN ('cartoon', 'realistic', 'manga', 'classic')",
            name='valid_style'
        ),
        CheckConstraint(
            'LENGTH(title) >= 3',
            name='title_min_length'
        ),
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_created_status', 'created_at', 'status'),
    )

    @validates('title')
    def validate_title(self, key, title: str) -> str:
        """
        Valida título do livro.
        
        Args:
            key: Nome do campo
            title: Título a validar
            
        Returns:
            Título validado
            
        Raises:
            ValidationError: Se título for inválido
        """
        if not title or not title.strip():
            raise ValidationError(
                message="Título é obrigatório",
                field="title"
            )
        
        title = title.strip()
        
        if len(title) < 3:
            raise ValidationError(
                message="Título deve ter pelo menos 3 caracteres",
                field="title",
                value=title
            )
        
        if len(title) > 200:
            raise ValidationError(
                message="Título deve ter no máximo 200 caracteres",
                field="title",
                value=title
            )
        
        return title

    @validates('description')
    def validate_description(self, key, description: Optional[str]) -> Optional[str]:
        """
        Valida descrição do livro.
        
        Args:
            key: Nome do campo
            description: Descrição a validar
            
        Returns:
            Descrição validada
            
        Raises:
            ValidationError: Se descrição for inválida
        """
        if description is None:
            return None
        
        description = description.strip() if description else ""
        
        if len(description) > 1000:
            raise ValidationError(
                message="Descrição deve ter no máximo 1000 caracteres",
                field="description",
                value=description
            )
        
        return description if description else None

    @validates('pages_count')
    def validate_pages_count(self, key, pages_count: int) -> int:
        """
        Valida quantidade de páginas (regra crítica do PRD: 5-20 páginas).
        
        Args:
            key: Nome do campo
            pages_count: Número de páginas
            
        Returns:
            Número de páginas validado
            
        Raises:
            InvalidBookPagesError: Se quantidade for inválida
        """
        if not isinstance(pages_count, int):
            raise ValidationError(
                message="Número de páginas deve ser um número inteiro",
                field="pages_count",
                value=pages_count
            )
        
        if pages_count < 5 or pages_count > 20:
            raise InvalidBookPagesError(pages_count)
        
        return pages_count

    @validates('style')
    def validate_style(self, key, style: str) -> str:
        """
        Valida estilo do livro.
        
        Args:
            key: Nome do campo
            style: Estilo a validar
            
        Returns:
            Estilo validado
            
        Raises:
            ValidationError: Se estilo for inválido
        """
        if not style:
            raise ValidationError(
                message="Estilo é obrigatório",
                field="style"
            )
        
        valid_styles = [s.value for s in BookStyle]
        
        if style not in valid_styles:
            raise ValidationError(
                message=f"Estilo deve ser um dos: {', '.join(valid_styles)}",
                field="style",
                value=style
            )
        
        return style

    @validates('status')
    def validate_status(self, key, status: str) -> str:
        """
        Valida mudanças de status.
        
        Args:
            key: Nome do campo
            status: Novo status
            
        Returns:
            Status validado
            
        Raises:
            ValidationError: Se transição de status for inválida
        """
        valid_statuses = [s.value for s in BookStatus]
        
        if status not in valid_statuses:
            raise ValidationError(
                message=f"Status deve ser um dos: {', '.join(valid_statuses)}",
                field="status",
                value=status
            )
        
        # Validar transições de status
        if hasattr(self, 'status') and self.status:
            current_status = self.status
            if not self._is_valid_status_transition(current_status, status):
                raise ValidationError(
                    message=f"Transição de status inválida: {current_status} -> {status}",
                    field="status",
                    details={
                        "current_status": current_status,
                        "new_status": status,
                        "allowed_transitions": self._get_allowed_transitions(current_status)
                    }
                )
        
        return status

    def _is_valid_status_transition(self, current: str, new: str) -> bool:
        """
        Verifica se transição de status é válida.
        
        Args:
            current: Status atual
            new: Novo status
            
        Returns:
            True se transição for válida
        """
        # Definir transições válidas
        valid_transitions = {
            BookStatus.DRAFT: [BookStatus.PROCESSING, BookStatus.FAILED],
            BookStatus.PROCESSING: [BookStatus.COMPLETED, BookStatus.FAILED, BookStatus.DRAFT],
            BookStatus.COMPLETED: [BookStatus.PROCESSING],  # Reprocessar se necessário
            BookStatus.FAILED: [BookStatus.DRAFT, BookStatus.PROCESSING]
        }
        
        return new in valid_transitions.get(current, [])

    def _get_allowed_transitions(self, current_status: str) -> List[str]:
        """
        Retorna transições permitidas para status atual.
        
        Args:
            current_status: Status atual
            
        Returns:
            Lista de status permitidos
        """
        valid_transitions = {
            BookStatus.DRAFT: [BookStatus.PROCESSING, BookStatus.FAILED],
            BookStatus.PROCESSING: [BookStatus.COMPLETED, BookStatus.FAILED, BookStatus.DRAFT],
            BookStatus.COMPLETED: [BookStatus.PROCESSING],
            BookStatus.FAILED: [BookStatus.DRAFT, BookStatus.PROCESSING]
        }
        
        return valid_transitions.get(current_status, [])

    @hybrid_property
    def is_editable(self) -> bool:
        """
        Verifica se livro pode ser editado.
        
        Returns:
            True se livro puder ser editado
        """
        return self.status in [BookStatus.DRAFT, BookStatus.FAILED]

    @hybrid_property
    def is_processing(self) -> bool:
        """
        Verifica se livro está sendo processado.
        
        Returns:
            True se livro estiver em processamento
        """
        return self.status == BookStatus.PROCESSING

    @hybrid_property
    def is_completed(self) -> bool:
        """
        Verifica se livro está completo.
        
        Returns:
            True se livro estiver completo
        """
        return self.status == BookStatus.COMPLETED

    @hybrid_property
    def can_generate_pdf(self) -> bool:
        """
        Verifica se pode gerar PDF do livro.
        
        Returns:
            True se PDF puder ser gerado
        """
        return self.status == BookStatus.COMPLETED and len(self.pages) == self.pages_count

    def validate_business_rules(self) -> None:
        """
        Valida todas as regras de negócio do livro.
        
        Raises:
            ValidationError: Se alguma regra for violada
        """
        # Validar se número de páginas criadas corresponde ao esperado
        if len(self.pages) > 0 and len(self.pages) != self.pages_count:
            raise ValidationError(
                message=f"Número de páginas criadas ({len(self.pages)}) não corresponde ao esperado ({self.pages_count})",
                field="pages",
                details={
                    "expected_pages": self.pages_count,
                    "actual_pages": len(self.pages)
                }
            )

    def can_transition_to(self, new_status: str) -> bool:
        """
        Verifica se pode fazer transição para novo status.
        
        Args:
            new_status: Status desejado
            
        Returns:
            True se transição for possível
        """
        return self._is_valid_status_transition(self.status, new_status)

    def get_validation_errors(self) -> List[str]:
        """
        Retorna lista de erros de validação atuais.
        
        Returns:
            Lista de mensagens de erro
        """
        errors = []
        
        try:
            self.validate_business_rules()
        except ValidationError as e:
            errors.append(e.message)
        
        return errors

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title='{self.title}', status='{self.status}', pages={self.pages_count})>"

class Page(Base):
    """
    Modelo de página do livro com validações de conteúdo.
    
    Regras implementadas:
    - Número de página deve ser positivo
    - Conteúdo de texto limitado a 2000 caracteres
    - Prompt de imagem limitado a 1000 caracteres
    - Páginas devem estar em sequência dentro do livro
    """
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    text_content = Column(Text)
    image_url = Column(String)
    image_prompt = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    book = relationship("Book", back_populates="pages")

    # Constraints no banco
    __table_args__ = (
        CheckConstraint(
            'page_number > 0',
            name='page_number_positive'
        ),
        CheckConstraint(
            'LENGTH(text_content) <= 2000',
            name='text_content_max_length'
        ),
        CheckConstraint(
            'LENGTH(image_prompt) <= 1000',
            name='image_prompt_max_length'
        ),
        # Constraint de unicidade: uma página por número por livro
        Index('idx_book_page_unique', 'book_id', 'page_number', unique=True),
        Index('idx_book_page_order', 'book_id', 'page_number'),
    )

    @validates('page_number')
    def validate_page_number(self, key, page_number: int) -> int:
        """
        Valida número da página.
        
        Args:
            key: Nome do campo
            page_number: Número da página
            
        Returns:
            Número validado
            
        Raises:
            ValidationError: Se número for inválido
        """
        if not isinstance(page_number, int):
            raise ValidationError(
                message="Número da página deve ser um número inteiro",
                field="page_number",
                value=page_number
            )
        
        if page_number <= 0:
            raise ValidationError(
                message="Número da página deve ser positivo",
                field="page_number",
                value=page_number
            )
        
        # Se temos acesso ao livro, validar se página está no range válido
        if hasattr(self, 'book') and self.book and self.book.pages_count:
            if page_number > self.book.pages_count:
                raise ValidationError(
                    message=f"Página {page_number} excede o total de páginas do livro ({self.book.pages_count})",
                    field="page_number",
                    value=page_number
                )
        
        return page_number

    @validates('text_content')
    def validate_text_content(self, key, text_content: Optional[str]) -> Optional[str]:
        """
        Valida conteúdo de texto da página.
        
        Args:
            key: Nome do campo
            text_content: Conteúdo de texto
            
        Returns:
            Conteúdo validado
            
        Raises:
            ValidationError: Se conteúdo for inválido
        """
        if text_content is None:
            return None
        
        text_content = text_content.strip() if text_content else ""
        
        if len(text_content) > 2000:
            raise ValidationError(
                message="Conteúdo da página deve ter no máximo 2000 caracteres",
                field="text_content",
                value=f"{text_content[:50]}..." if len(text_content) > 50 else text_content
            )
        
        return text_content if text_content else None

    @validates('image_prompt')
    def validate_image_prompt(self, key, image_prompt: Optional[str]) -> Optional[str]:
        """
        Valida prompt de geração de imagem.
        
        Args:
            key: Nome do campo
            image_prompt: Prompt para IA
            
        Returns:
            Prompt validado
            
        Raises:
            ValidationError: Se prompt for inválido
        """
        if image_prompt is None:
            return None
        
        image_prompt = image_prompt.strip() if image_prompt else ""
        
        if len(image_prompt) > 1000:
            raise ValidationError(
                message="Prompt de imagem deve ter no máximo 1000 caracteres",
                field="image_prompt",
                value=f"{image_prompt[:50]}..." if len(image_prompt) > 50 else image_prompt
            )
        
        return image_prompt if image_prompt else None

    @validates('image_url')
    def validate_image_url(self, key, image_url: Optional[str]) -> Optional[str]:
        """
        Valida URL da imagem.
        
        Args:
            key: Nome do campo
            image_url: URL da imagem
            
        Returns:
            URL validada
            
        Raises:
            ValidationError: Se URL for inválida
        """
        if image_url is None:
            return None
        
        image_url = image_url.strip() if image_url else ""
        
        if not image_url:
            return None
        
        # Validação básica de URL
        if not re.match(r'^https?://.+', image_url):
            raise ValidationError(
                message="URL da imagem deve começar com http:// ou https://",
                field="image_url",
                value=image_url
            )
        
        return image_url

    @hybrid_property
    def has_content(self) -> bool:
        """
        Verifica se página tem conteúdo.
        
        Returns:
            True se página tiver texto ou imagem
        """
        return bool(self.text_content) or bool(self.image_url)

    @hybrid_property
    def is_complete(self) -> bool:
        """
        Verifica se página está completa (tem texto e imagem).
        
        Returns:
            True se página estiver completa
        """
        return bool(self.text_content) and bool(self.image_url)

    def validate_content_rules(self) -> None:
        """
        Valida regras de conteúdo da página.
        
        Raises:
            ValidationError: Se regras forem violadas
        """
        # Página deve ter pelo menos texto ou imagem
        if not self.has_content:
            raise ValidationError(
                message="Página deve ter pelo menos texto ou imagem",
                field="content",
                details={
                    "has_text": bool(self.text_content),
                    "has_image": bool(self.image_url)
                }
            )

    def __repr__(self) -> str:
        return f"<Page(id={self.id}, book_id={self.book_id}, page_number={self.page_number})>"
