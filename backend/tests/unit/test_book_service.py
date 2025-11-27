import pytest
from unittest.mock import AsyncMock, MagicMock, PropertyMock
from fastapi import HTTPException
from app.services.book_service import BookService
from app.models.user import User, UserRole
from app.models.book import Book
from app.schemas.book import BookCreate

class TestBookService:
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
        
    @pytest.fixture
    def mock_user_repo(self):
        return AsyncMock()
        
    @pytest.fixture
    def mock_book_repo(self):
        return AsyncMock()
        
    @pytest.fixture
    def book_service(self, mock_db, mock_user_repo, mock_book_repo):
        service = BookService(mock_db)
        service.user_repo = mock_user_repo
        service.book_repo = mock_book_repo
        # Mock AI service to avoid real instantiation
        service.ai_service = MagicMock()
        return service

    @pytest.mark.asyncio
    async def test_check_user_book_limit_success(self, book_service, mock_user_repo, mock_book_repo):
        """Test that user within limit can create book."""
        user_id = 1
        # Mock user with regular role
        user = MagicMock(spec=User)
        user.id = user_id
        user.role = UserRole.USER
        # Mock max_books_allowed property
        type(user).max_books_allowed = PropertyMock(return_value=5)
        
        mock_user_repo.get.return_value = user
        mock_book_repo.count_by_user.return_value = 3 # Under limit of 5
        
        # Should not raise exception
        await book_service._check_user_book_limit(user_id)
        
        mock_book_repo.count_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_check_user_book_limit_exceeded(self, book_service, mock_user_repo, mock_book_repo):
        """Test that user exceeding limit raises exception."""
        user_id = 1
        user = MagicMock(spec=User)
        user.id = user_id
        user.role = UserRole.USER
        type(user).max_books_allowed = PropertyMock(return_value=5)
        
        mock_user_repo.get.return_value = user
        mock_book_repo.count_by_user.return_value = 5 # Reached limit
        
        with pytest.raises(HTTPException) as exc:
            await book_service._check_user_book_limit(user_id)
            
        assert exc.value.status_code == 400
        assert "Limite de 5 livros" in exc.value.detail

    @pytest.mark.asyncio
    async def test_check_premium_user_limit(self, book_service, mock_user_repo, mock_book_repo):
        """Test that premium user has higher limit."""
        user_id = 2
        user = MagicMock(spec=User)
        user.id = user_id
        user.role = UserRole.PREMIUM
        type(user).max_books_allowed = PropertyMock(return_value=50)
        
        mock_user_repo.get.return_value = user
        mock_book_repo.count_by_user.return_value = 10 # Over regular limit but under premium
        
        # Should not raise exception
        await book_service._check_user_book_limit(user_id)

    def test_is_admin_check(self, book_service):
        """Test admin check logic."""
        # User is admin
        admin_user = MagicMock(spec=User)
        admin_user.is_admin = True
        assert book_service._is_admin(admin_user) is True
        
        # User is not admin
        regular_user = MagicMock(spec=User)
        regular_user.is_admin = False
        assert book_service._is_admin(regular_user) is False
        
    @pytest.mark.asyncio
    async def test_create_book_full_flow(self, book_service, mock_user_repo, mock_book_repo, mock_db):
        """Test validation and creation flow."""
        user = MagicMock(spec=User)
        user.id = 1
        user.role = UserRole.USER
        type(user).max_books_allowed = PropertyMock(return_value=5)
        
        book_data = BookCreate(
            title="Test Book",
            description="A test description",
            pages_count=10,
            style="cartoon"
        )
        
        mock_user_repo.get.return_value = user
        mock_book_repo.count_by_user.return_value = 0
        mock_book_repo.create.return_value = Book(
            id=1, 
            title=book_data.title,
            user_id=user.id,
            status="draft"
        )
        
        result = await book_service.create_book(book_data, user)
        
        assert result.title == "Test Book"
        mock_book_repo.create.assert_called_once()
        mock_db.commit.assert_called_once()
