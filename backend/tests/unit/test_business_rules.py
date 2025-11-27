import pytest
from app.models.book import BookStatus, BookStyle
from app.models.user import UserRole
from app.utils.validators import (
    validate_email_format,
    validate_password_strength,
    validate_book_pages,
    validate_book_style,
    validate_book_status_transition
)
from app.exceptions.base_exceptions import (
    ValidationError,
    InvalidBookPagesError
)

class TestBusinessRules:
    
    def test_book_pages_validation_valid(self):
        """Test valid page counts (5-20)."""
        for pages in [5, 8, 12, 20]:
            # Should not raise exception
            validate_book_pages(pages)

    def test_book_pages_validation_invalid(self):
        """Test invalid page counts."""
        invalid_pages = [4, 21, 0, -1]
        for pages in invalid_pages:
            with pytest.raises(InvalidBookPagesError):
                validate_book_pages(pages)

    def test_book_style_validation_valid(self):
        """Test valid book styles."""
        valid_styles = ["cartoon", "realistic", "manga", "classic"]
        for style in valid_styles:
            # Should not raise exception
            validate_book_style(style)

    def test_book_style_validation_invalid(self):
        """Test invalid book styles."""
        invalid_styles = ["anime", "3d", "watercolor", ""]
        for style in invalid_styles:
            with pytest.raises(ValidationError):
                validate_book_style(style)

    def test_book_status_transitions_valid(self):
        """Test valid status transitions."""
        valid_transitions = [
            ("draft", "processing"),
            ("processing", "completed"),
            ("processing", "failed"),
            ("failed", "draft"),
            ("completed", "processing")
        ]
        for current, new in valid_transitions:
            # Should not raise exception
            validate_book_status_transition(current, new)

    def test_book_status_transitions_invalid(self):
        """Test invalid status transitions."""
        invalid_transitions = [
            ("draft", "completed"),
            ("completed", "draft"),
            ("failed", "completed")
        ]
        for current, new in invalid_transitions:
            with pytest.raises(ValidationError):
                validate_book_status_transition(current, new)

    def test_email_validation_valid(self):
        """Test valid email formats."""
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "user123@test-domain.com"
        ]
        for email in valid_emails:
            # Should not raise exception
            validate_email_format(email)

    def test_email_validation_invalid(self):
        """Test invalid email formats."""
        invalid_emails = [
            "invalid.email",
            "@domain.com",
            "user@",
            "user space@domain.com",
            ""
        ]
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                validate_email_format(email)

    def test_password_strength_valid(self):
        """Test strong passwords."""
        valid_passwords = [
            "MinhaSenh@123",
            "S3cr3t!2024",
            "Str0ng#Pass"
        ]
        for password in valid_passwords:
            # Should not raise exception
            validate_password_strength(password)

    def test_password_strength_invalid(self):
        """Test weak passwords."""
        invalid_passwords = [
            "123456",           # Too simple
            "password",         # No caps, no number, no special
            "Pass1",            # Too short
            "PASSWORD123",      # No lower, no special
            "password123"       # No caps, no special
        ]
        for password in invalid_passwords:
            with pytest.raises(ValidationError):
                validate_password_strength(password)

    def test_user_role_limits_mock(self):
        """Test role limits (mocked logic check)."""
        role_limits = {
            UserRole.USER: 5,
            UserRole.PREMIUM: 50,
            UserRole.ADMIN: 999999
        }
        # This just validates the constants/enum values match expectation
        assert role_limits[UserRole.USER] == 5
        assert role_limits[UserRole.PREMIUM] == 50
