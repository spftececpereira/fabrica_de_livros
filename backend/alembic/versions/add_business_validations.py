"""add business validations

Revision ID: add_business_validations
Revises: e9885fb5c55d
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_business_validations'
down_revision = 'e9885fb5c55d'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database schema with business validations."""
    
    # Modificar tabela books
    op.alter_column('books', 'title', type_=sa.String(200), nullable=False)
    op.add_column('books', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('books', sa.Column('pages_count', sa.Integer(), nullable=False, server_default='8'))
    op.add_column('books', sa.Column('cover_image', sa.String(), nullable=True))
    op.add_column('books', sa.Column('pdf_file', sa.String(), nullable=True))
    op.alter_column('books', 'style', type_=sa.String(20), nullable=False)
    op.alter_column('books', 'status', type_=sa.String(20), nullable=False)
    
    # Renomear coluna owner_id para user_id se existir
    op.execute("ALTER TABLE books RENAME COLUMN owner_id TO user_id")
    
    # Remover coluna theme se existir
    op.execute("ALTER TABLE books DROP COLUMN IF EXISTS theme")
    
    # Adicionar constraints para books
    op.create_check_constraint(
        'valid_pages_count',
        'books',
        'pages_count >= 5 AND pages_count <= 20'
    )
    op.create_check_constraint(
        'valid_status',
        'books',
        "status IN ('draft', 'processing', 'completed', 'failed')"
    )
    op.create_check_constraint(
        'valid_style',
        'books',
        "style IN ('cartoon', 'realistic', 'manga', 'classic')"
    )
    op.create_check_constraint(
        'title_min_length',
        'books',
        'LENGTH(title) >= 3'
    )
    
    # Adicionar índices para books
    op.create_index('idx_user_status', 'books', ['user_id', 'status'])
    op.create_index('idx_created_status', 'books', ['created_at', 'status'])
    
    # Modificar tabela users
    op.alter_column('users', 'email', type_=sa.String(255), nullable=False)
    op.alter_column('users', 'full_name', type_=sa.String(100), nullable=False)
    op.add_column('users', sa.Column('role', sa.String(20), nullable=False, server_default='user'))
    op.add_column('users', sa.Column('status', sa.String(20), nullable=False, server_default='active'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    
    # Renomear coluna hashed_password para password_hash se existir
    op.execute("ALTER TABLE users RENAME COLUMN hashed_password TO password_hash")
    op.alter_column('users', 'password_hash', type_=sa.String(255), nullable=False)
    
    # Remover coluna is_superuser se existir
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS is_superuser")
    
    # Adicionar constraints para users
    op.create_check_constraint(
        'valid_email_format',
        'users',
        "email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
    )
    op.create_check_constraint(
        'full_name_min_length',
        'users',
        'LENGTH(full_name) >= 2'
    )
    op.create_check_constraint(
        'valid_role',
        'users',
        "role IN ('user', 'premium', 'admin')"
    )
    op.create_check_constraint(
        'valid_status',
        'users',
        "status IN ('active', 'inactive', 'suspended', 'pending')"
    )
    
    # Adicionar índices para users
    op.create_index('idx_email_status', 'users', ['email', 'status'])
    op.create_index('idx_role_active', 'users', ['role', 'is_active'])
    op.create_index('idx_created_at', 'users', ['created_at'])
    
    # Modificar tabela pages
    op.add_column('pages', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('pages', sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True))
    
    # Adicionar constraints para pages
    op.create_check_constraint(
        'page_number_positive',
        'pages',
        'page_number > 0'
    )
    op.create_check_constraint(
        'text_content_max_length',
        'pages',
        'LENGTH(text_content) <= 2000'
    )
    op.create_check_constraint(
        'image_prompt_max_length',
        'pages',
        'LENGTH(image_prompt) <= 1000'
    )
    
    # Adicionar índices para pages
    op.create_index('idx_book_page_unique', 'pages', ['book_id', 'page_number'], unique=True)
    op.create_index('idx_book_page_order', 'pages', ['book_id', 'page_number'])


def downgrade():
    """Downgrade database schema."""
    
    # Remover índices
    op.drop_index('idx_book_page_order', 'pages')
    op.drop_index('idx_book_page_unique', 'pages')
    op.drop_index('idx_created_at', 'users')
    op.drop_index('idx_role_active', 'users')
    op.drop_index('idx_email_status', 'users')
    op.drop_index('idx_created_status', 'books')
    op.drop_index('idx_user_status', 'books')
    
    # Remover constraints
    op.drop_constraint('image_prompt_max_length', 'pages')
    op.drop_constraint('text_content_max_length', 'pages')
    op.drop_constraint('page_number_positive', 'pages')
    op.drop_constraint('valid_status', 'users')
    op.drop_constraint('valid_role', 'users')
    op.drop_constraint('full_name_min_length', 'users')
    op.drop_constraint('valid_email_format', 'users')
    op.drop_constraint('title_min_length', 'books')
    op.drop_constraint('valid_style', 'books')
    op.drop_constraint('valid_status', 'books')
    op.drop_constraint('valid_pages_count', 'books')
    
    # Reverter alterações nas colunas e tabelas
    op.drop_column('pages', 'updated_at')
    op.drop_column('pages', 'created_at')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'status')
    op.drop_column('users', 'role')
    op.drop_column('books', 'pdf_file')
    op.drop_column('books', 'cover_image')
    op.drop_column('books', 'pages_count')
    op.drop_column('books', 'description')
    
    # Renomear colunas de volta
    op.execute("ALTER TABLE users RENAME COLUMN password_hash TO hashed_password")
    op.execute("ALTER TABLE books RENAME COLUMN user_id TO owner_id")