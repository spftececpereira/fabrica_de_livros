from sqlalchemy import Column, Integer, String, Boolean, DateTime, CheckConstraint, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.database import Base
from app.exceptions.base_exceptions import ValidationError, ErrorCode
from typing import Optional
import re
import enum


class UserRole(str, enum.Enum):
    """Roles disponíveis para usuários."""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """Status do usuário."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """
    Modelo de usuário com validações de negócio e segurança.
    
    Regras implementadas:
    - Email deve ter formato válido e ser único
    - Nome completo deve ter pelo menos 2 caracteres
    - Password hash é obrigatório
    - Controle de roles e status
    - Auditoria de criação e atualização
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default=UserRole.USER)
    status = Column(String(20), default=UserStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    books = relationship("Book", back_populates="user", cascade="all, delete-orphan")

    # Constraints no banco
    __table_args__ = (
        CheckConstraint(
            "email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name='valid_email_format'
        ),
        CheckConstraint(
            'LENGTH(full_name) >= 2',
            name='full_name_min_length'
        ),
        CheckConstraint(
            "role IN ('user', 'premium', 'admin')",
            name='valid_role'
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended', 'pending')",
            name='valid_status'
        ),
        Index('idx_email_status', 'email', 'status'),
        Index('idx_role_active', 'role', 'is_active'),
        Index('idx_created_at', 'created_at'),
    )

    @validates('email')
    def validate_email(self, key, email: str) -> str:
        """
        Valida formato do email.
        
        Args:
            key: Nome do campo
            email: Email a validar
            
        Returns:
            Email validado e normalizado
            
        Raises:
            ValidationError: Se email for inválido
        """
        if not email:
            raise ValidationError(
                message="Email é obrigatório",
                field="email"
            )
        
        # Normalizar email (lowercase, strip)
        email = email.strip().lower()
        
        # Validar formato
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(email):
            raise ValidationError(
                message="Formato de email inválido",
                field="email",
                value=email
            )
        
        # Verificar comprimento
        if len(email) > 255:
            raise ValidationError(
                message="Email deve ter no máximo 255 caracteres",
                field="email",
                value=email
            )
        
        # Validações de segurança básicas
        forbidden_domains = ['tempmail.', 'guerrillamail.', '10minutemail.']
        for forbidden in forbidden_domains:
            if forbidden in email:
                raise ValidationError(
                    message="Domínio de email temporário não permitido",
                    field="email",
                    value=email
                )
        
        return email

    @validates('full_name')
    def validate_full_name(self, key, full_name: str) -> str:
        """
        Valida nome completo do usuário.
        
        Args:
            key: Nome do campo
            full_name: Nome a validar
            
        Returns:
            Nome validado
            
        Raises:
            ValidationError: Se nome for inválido
        """
        if not full_name:
            raise ValidationError(
                message="Nome completo é obrigatório",
                field="full_name"
            )
        
        full_name = full_name.strip()
        
        if len(full_name) < 2:
            raise ValidationError(
                message="Nome deve ter pelo menos 2 caracteres",
                field="full_name",
                value=full_name
            )
        
        if len(full_name) > 100:
            raise ValidationError(
                message="Nome deve ter no máximo 100 caracteres",
                field="full_name",
                value=full_name
            )
        
        # Verificar se contém apenas caracteres válidos
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\.\']+$', full_name):
            raise ValidationError(
                message="Nome contém caracteres inválidos",
                field="full_name",
                value=full_name
            )
        
        return full_name

    @validates('role')
    def validate_role(self, key, role: str) -> str:
        """
        Valida role do usuário.
        
        Args:
            key: Nome do campo
            role: Role a validar
            
        Returns:
            Role validado
            
        Raises:
            ValidationError: Se role for inválido
        """
        valid_roles = [r.value for r in UserRole]
        
        if role not in valid_roles:
            raise ValidationError(
                message=f"Role deve ser um dos: {', '.join(valid_roles)}",
                field="role",
                value=role
            )
        
        return role

    @validates('status')
    def validate_status(self, key, status: str) -> str:
        """
        Valida status do usuário.
        
        Args:
            key: Nome do campo
            status: Status a validar
            
        Returns:
            Status validado
            
        Raises:
            ValidationError: Se status for inválido
        """
        valid_statuses = [s.value for s in UserStatus]
        
        if status not in valid_statuses:
            raise ValidationError(
                message=f"Status deve ser um dos: {', '.join(valid_statuses)}",
                field="status",
                value=status
            )
        
        # Sincronizar com is_active
        if status == UserStatus.ACTIVE and not self.is_active:
            self.is_active = True
        elif status in [UserStatus.INACTIVE, UserStatus.SUSPENDED] and self.is_active:
            self.is_active = False
        
        return status

    @validates('password_hash')
    def validate_password_hash(self, key, password_hash: str) -> str:
        """
        Valida hash da senha.
        
        Args:
            key: Nome do campo
            password_hash: Hash da senha
            
        Returns:
            Hash validado
            
        Raises:
            ValidationError: Se hash for inválido
        """
        if not password_hash:
            raise ValidationError(
                message="Hash da senha é obrigatório",
                field="password_hash"
            )
        
        # Verificar se parece com um hash (formato básico)
        if len(password_hash) < 50:  # Hashes bcrypt têm ~60 chars
            raise ValidationError(
                message="Hash da senha parece inválido",
                field="password_hash"
            )
        
        return password_hash

    @hybrid_property
    def is_admin(self) -> bool:
        """
        Verifica se usuário é administrador.
        
        Returns:
            True se for admin
        """
        return self.role == UserRole.ADMIN

    @hybrid_property
    def is_premium(self) -> bool:
        """
        Verifica se usuário tem plano premium.
        
        Returns:
            True se for premium ou admin
        """
        return self.role in [UserRole.PREMIUM, UserRole.ADMIN]

    @hybrid_property
    def can_create_books(self) -> bool:
        """
        Verifica se usuário pode criar livros.
        
        Returns:
            True se puder criar livros
        """
        return self.is_active and self.status == UserStatus.ACTIVE

    @hybrid_property
    def max_books_allowed(self) -> int:
        """
        Retorna número máximo de livros permitidos.
        
        Returns:
            Limite de livros baseado no role
        """
        limits = {
            UserRole.USER: 5,
            UserRole.PREMIUM: 50,
            UserRole.ADMIN: 999999
        }
        
        return limits.get(self.role, 5)

    @hybrid_property
    def books_count(self) -> int:
        """
        Retorna número atual de livros do usuário.
        
        Returns:
            Quantidade de livros
        """
        return len(self.books) if self.books else 0

    @hybrid_property
    def can_create_more_books(self) -> bool:
        """
        Verifica se usuário pode criar mais livros.
        
        Returns:
            True se não atingiu o limite
        """
        return self.books_count < self.max_books_allowed

    def validate_business_rules(self) -> None:
        """
        Valida regras de negócio do usuário.
        
        Raises:
            ValidationError: Se regras forem violadas
        """
        # Verificar se usuário suspenso não está ativo
        if self.status == UserStatus.SUSPENDED and self.is_active:
            raise ValidationError(
                message="Usuário suspenso não pode estar ativo",
                field="status",
                details={
                    "status": self.status,
                    "is_active": self.is_active
                }
            )

    def can_perform_action(self, action: str) -> bool:
        """
        Verifica se usuário pode executar uma ação.
        
        Args:
            action: Ação a verificar (create_book, edit_book, etc)
            
        Returns:
            True se puder executar a ação
        """
        if not self.is_active or self.status != UserStatus.ACTIVE:
            return False
        
        action_permissions = {
            'create_book': self.can_create_books and self.can_create_more_books,
            'edit_book': self.can_create_books,
            'delete_book': self.can_create_books,
            'generate_pdf': True,
            'admin_actions': self.is_admin,
            'premium_features': self.is_premium
        }
        
        return action_permissions.get(action, False)

    def update_last_login(self) -> None:
        """Atualiza timestamp do último login."""
        from datetime import datetime
        self.last_login = datetime.utcnow()

    def activate(self) -> None:
        """Ativa o usuário."""
        self.is_active = True
        self.status = UserStatus.ACTIVE

    def deactivate(self, reason: str = "inactive") -> None:
        """
        Desativa o usuário.
        
        Args:
            reason: Motivo da desativação
        """
        self.is_active = False
        if reason == "suspended":
            self.status = UserStatus.SUSPENDED
        else:
            self.status = UserStatus.INACTIVE

    def get_validation_errors(self) -> list[str]:
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
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', status='{self.status}')>"
