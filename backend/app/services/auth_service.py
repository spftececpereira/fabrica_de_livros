"""
Service de autenticação com validações de segurança.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.services.notification_service import notification_service # Import notification service
import secrets # For generating reset token


class AuthService:
    """Service para operações de autenticação e autorização."""
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa o service com dependências.
        
        Args:
            db: Sessão async do banco de dados
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Autentica usuário por email e senha.
        
        Args:
            email: Email do usuário
            password: Senha em texto plano
            
        Returns:
            Usuário autenticado ou None se credenciais inválidas
            
        Raises:
            HTTPException: Se usuário estiver inativo
        """
        # Buscar usuário por email
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            return None
        
        # Verificar se usuário está ativo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        
        # Verificar senha
        if not verify_password(password, user.password_hash):
            return None
        
        # Atualizar último login
        await self.user_repo.update_last_login(user.id)
        await self.db.commit()
        
        return user
    
    async def create_access_token_for_user(self, user: User) -> Dict[str, Any]:
        """
        Cria token de acesso para usuário.
        
        Args:
            user: Usuário para criar token
            
        Returns:
            Dict com token de acesso e informações
        """
        # Dados para incluir no token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "full_name": user.full_name
        }
        
        # Criar token
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active
            }
        }
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Processo completo de login.
        
        Args:
            email: Email do usuário
            password: Senha em texto plano
            
        Returns:
            Token de acesso e dados do usuário
            
        Raises:
            HTTPException: Se credenciais forem inválidas
        """
        # Validar email format
        if not self._is_valid_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de email inválido"
            )
        
        # Tentar autenticar
        user = await self.authenticate_user(email, password)
        
        if not user:
            # Log da tentativa de login falhou (sem expor detalhes)
            await self._log_failed_login_attempt(email)
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Log de login bem-sucedido
        await self._log_successful_login(user.id)
        
        # Criar e retornar token
        return await self.create_access_token_for_user(user)
    
    async def register(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Registra novo usuário.
        
        Args:
            user_data: Dados do usuário para criação
            
        Returns:
            Token de acesso e dados do usuário criado
            
        Raises:
            HTTPException: Se email já existir ou dados forem inválidos
        """
        # Validar se email já existe
        if await self.user_repo.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Validar força da senha
        self._validate_password_strength(user_data.password)
        
        # Criar hash da senha
        password_hash = get_password_hash(user_data.password)
        
        # Criar usuário
        new_user = await self.user_repo.create(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=password_hash,
            is_active=True
        )
        
        await self.db.commit()
        
        # Log de registro bem-sucedido
        await self._log_user_registration(new_user.id)
        
        # Criar e retornar token
        return await self.create_access_token_for_user(new_user)
    
    async def refresh_token(self, current_user: User) -> Dict[str, Any]:
        """
        Renova token de acesso.
        
        Args:
            current_user: Usuário atual autenticado
            
        Returns:
            Novo token de acesso
            
        Raises:
            HTTPException: Se usuário não estiver ativo
        """
        # Verificar se usuário ainda está ativo
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        
        # Criar novo token
        return await self.create_access_token_for_user(current_user)
    
    async def change_password(
        self, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Altera senha do usuário.
        
        Args:
            user_id: ID do usuário
            current_password: Senha atual
            new_password: Nova senha
            
        Returns:
            True se alteração foi bem-sucedida
            
        Raises:
            HTTPException: Se senha atual estiver incorreta ou nova senha for inválida
        """
        # Buscar usuário
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar senha atual
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Validar nova senha
        self._validate_password_strength(new_password)
        
        # Atualizar senha
        new_password_hash = get_password_hash(new_password)
        await self.user_repo.update(user_id, password_hash=new_password_hash)
        await self.db.commit()
        
        # Log da alteração de senha
        await self._log_password_change(user_id)
        
        return True
    
    async def request_password_reset(self, email: str) -> bool:
        """
        Inicia o processo de redefinição de senha para o email fornecido.
        
        Args:
            email: Email do usuário que solicitou a redefinição.
            
        Returns:
            True se o email foi enviado com sucesso (ou se o usuário não foi encontrado, 
            para evitar enumeração de usuários).
            
        Raises:
            HTTPException: Se o email for inválido.
        """
        if not self._is_valid_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de email inválido"
            )
            
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Para evitar enumeração de usuários, sempre retornamos sucesso
            # mesmo se o usuário não for encontrado.
            print(f"Password reset requested for non-existent or inactive email: {email}")
            return True # Retorna True para não dar dica ao atacante
            
        # Gerar um token de redefinição. Por simplicidade, usaremos um token JWT
        # com expiração. Em um cenário real, este token seria armazenado no DB.
        reset_token = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Enviar email de redefinição
        await notification_service.notify_password_reset(user, reset_token)
        
        print(f"Password reset email sent to {user.email}")
        return True
        
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Redefine a senha do usuário usando um token válido.
        
        Args:
            token: Token de redefinição de senha.
            new_password: Nova senha.
            
        Returns:
            True se a senha foi redefinida com sucesso.
            
        Raises:
            HTTPException: Se o token for inválido, expirado ou a nova senha fraca.
        """
        try:
            from jose import jwt, JWTError
            # Decodificar o token para obter o user_id
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token de redefinição inválido"
                )
            user = await self.user_repo.get(int(user_id))
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado"
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de redefinição inválido ou expirado"
            )

        # Validar força da nova senha
        self._validate_password_strength(new_password)

        # Atualizar a senha do usuário
        new_password_hash = get_password_hash(new_password)
        await self.user_repo.update(user.id, password_hash=new_password_hash)
        await self.db.commit()
        
        print(f"Password reset successfully for user_id: {user.id}")
        return True

    def _validate_password_strength(self, password: str) -> None:
        """
        Valida força da senha.
        
        Args:
            password: Senha para validar
            
        Raises:
            HTTPException: Se senha não atender critérios mínimos
        """
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve ter pelo menos 8 caracteres"
            )
        
        # Verificar se tem pelo menos um número
        if not any(char.isdigit() for char in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve conter pelo menos um número"
            )
        
        # Verificar se tem pelo menos uma letra
        if not any(char.isalpha() for char in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve conter pelo menos uma letra"
            )
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Valida formato básico do email.
        
        Args:
            email: Email para validar
            
        Returns:
            True se formato for válido
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    async def _log_failed_login_attempt(self, email: str) -> None:
        """
        Log de tentativa de login falhada.
        
        Args:
            email: Email da tentativa
        """
        # TODO: Implementar sistema de logging
        # Por enquanto apenas placeholder
        print(f"Failed login attempt for email: {email}")
    
    async def _log_successful_login(self, user_id: int) -> None:
        """
        Log de login bem-sucedido.
        
        Args:
            user_id: ID do usuário
        """
        # TODO: Implementar sistema de logging
        # Por enquanto apenas placeholder
        print(f"Successful login for user_id: {user_id}")
    
    async def _log_user_registration(self, user_id: int) -> None:
        """
        Log de registro de usuário.
        
        Args:
            user_id: ID do usuário registrado
        """
        # TODO: Implementar sistema de logging
        # Por enquanto apenas placeholder
        print(f"User registered with id: {user_id}")
    
    async def _log_password_change(self, user_id: int) -> None:
        """
        Log de alteração de senha.
        
        Args:
            user_id: ID do usuário
        """
        # TODO: Implementar sistema de logging
        # Por enquanto apenas placeholder
        print(f"Password changed for user_id: {user_id}")