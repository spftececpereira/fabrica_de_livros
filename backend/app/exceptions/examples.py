"""
Exemplos de uso das exceções customizadas nos services.

Este arquivo demonstra como refatorar os services para usar
as novas exceções customizadas ao invés de HTTPException.
"""

# ANTES (usando HTTPException diretamente):
# from fastapi import HTTPException, status
# 
# if not user:
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="Usuário não encontrado"
#     )

# DEPOIS (usando exceções customizadas):
from app.exceptions.base_exceptions import (
    UserNotFoundError,
    BookNotFoundError, 
    EmailAlreadyExistsError,
    InvalidBookPagesError,
    InvalidPasswordError,
    AuthenticationError,
    AuthorizationError
)
from app.exceptions.http_exceptions import (
    raise_not_found,
    raise_validation_error,
    raise_authorization_error,
    raise_business_rule_error
)

# Exemplos de uso nos services:

class AuthServiceExamples:
    """Exemplos para AuthService."""
    
    async def authenticate_user_example(self, email: str, password: str):
        """Exemplo de autenticação com exceções customizadas."""
        
        # Buscar usuário
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            # Usar exceção específica para usuário não encontrado
            raise UserNotFoundError(email=email)
        
        if not user.is_active:
            # Usar exceção de autenticação
            raise AuthenticationError(
                message="Usuário inativo",
                error_code=ErrorCode.USER_INACTIVE
            )
        
        if not verify_password(password, user.password_hash):
            # Usar exceção de autenticação
            raise AuthenticationError(
                message="Credenciais inválidas"
            )
        
        return user
    
    async def register_example(self, user_data):
        """Exemplo de registro com validações."""
        
        # Verificar se email existe
        if await self.user_repo.email_exists(user_data.email):
            raise EmailAlreadyExistsError(user_data.email)
        
        # Validar senha
        try:
            self._validate_password_strength(user_data.password)
        except Exception:
            raise InvalidPasswordError("Senha deve ter pelo menos 8 caracteres")


class UserServiceExamples:
    """Exemplos para UserService."""
    
    async def get_user_profile_example(self, user_id: int, current_user):
        """Exemplo de busca de perfil."""
        
        # Verificar se usuário existe
        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        
        # Verificar permissões
        if current_user.id != user_id and not self._is_admin(current_user):
            raise AuthorizationError(
                resource="user_profile",
                required_permission="view_user"
            )
        
        return user
    
    async def update_user_example(self, user_id: int, user_data, current_user):
        """Exemplo de atualização de usuário."""
        
        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        
        # Verificar email se estiver sendo alterado
        if user_data.email and user_data.email != user.email:
            if await self.user_repo.email_exists(user_data.email, exclude_id=user_id):
                raise EmailAlreadyExistsError(user_data.email)


class BookServiceExamples:
    """Exemplos para BookService."""
    
    async def create_book_example(self, book_data, current_user):
        """Exemplo de criação de livro."""
        
        # Validar quantidade de páginas (regra de negócio)
        if book_data.pages_count < 5 or book_data.pages_count > 20:
            raise InvalidBookPagesError(book_data.pages_count)
        
        # Verificar limite de livros por usuário
        book_count = await self.book_repo.count_by_user(current_user.id)
        if book_count >= 10:
            raise UserBookLimitError(current_count=book_count, max_limit=10)
        
        # Criar livro
        return await self.book_repo.create(**book_data.model_dump())
    
    async def get_book_details_example(self, book_id: int, current_user):
        """Exemplo de busca de livro."""
        
        book = await self.book_repo.get(book_id)
        if not book:
            raise BookNotFoundError(book_id)
        
        # Verificar se livro pertence ao usuário
        if book.user_id != current_user.id and not self._is_admin(current_user):
            raise AuthorizationError(
                resource="book",
                required_permission="view_book"
            )
        
        return book
    
    async def update_book_example(self, book_id: int, book_data, current_user):
        """Exemplo de atualização de livro."""
        
        book = await self.book_repo.get(book_id)
        if not book:
            raise BookNotFoundError(book_id)
        
        # Verificar se livro pode ser editado
        if book.status not in ["draft", "failed"]:
            from app.exceptions.base_exceptions import InvalidBookStatusError
            raise InvalidBookStatusError(
                current_status=book.status,
                operation="editar",
                allowed_statuses=["draft", "failed"]
            )
        
        return await self.book_repo.update(book_id, **book_data.model_dump())


# Helpers para casos específicos:

def validate_book_ownership(book, user_id: int):
    """Valida se livro pertence ao usuário."""
    if book.user_id != user_id:
        raise AuthorizationError(
            message="Livro não pertence a este usuário",
            resource="book"
        )

def validate_admin_permission(user):
    """Valida se usuário é administrador."""
    if not getattr(user, 'is_admin', False):
        raise AuthorizationError(
            message="Operação requer privilégios de administrador",
            required_permission="admin"
        )

def validate_pages_count(pages: int):
    """Valida quantidade de páginas do livro."""
    if not 5 <= pages <= 20:
        raise InvalidBookPagesError(pages)

def validate_book_style(style: str):
    """Valida estilo do livro."""
    valid_styles = ["cartoon", "realistic", "manga", "classic"]
    if style not in valid_styles:
        raise ValidationError(
            message=f"Estilo deve ser um dos: {', '.join(valid_styles)}",
            field="style",
            value=style
        )


# Exemplo de uso em endpoint:

"""
@router.get("/books/{book_id}")
async def get_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    # As exceções serão automaticamente capturadas pelo middleware
    # e convertidas em respostas JSON padronizadas
    return await book_service.get_book_details(book_id, current_user)
"""