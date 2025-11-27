from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List, Union
import os
from enum import Enum


class Environment(str, Enum):
    """Ambientes de execução da aplicação."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """Configurações da aplicação com suporte a CORS dinâmico."""
    
    # Application Info
    PROJECT_NAME: str = "Fábrica de Livros"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    CORS_ORIGINS: str = "*"  # Comma-separated list or "*" for all
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS,PATCH"
    CORS_ALLOW_HEADERS: str = "*"
    CORS_MAX_AGE: int = 3600
    
    # Multi-tenant CORS (para domínios personalizados)
    ENABLE_DYNAMIC_CORS: bool = False
    TENANT_DOMAIN_PATTERN: str = "*.fabrica-livros.com"
    ALLOWED_SUBDOMAINS: str = ""  # Comma-separated list of allowed subdomains
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = True
    HSTS_MAX_AGE: int = 31536000  # 1 year
    CONTENT_SECURITY_POLICY: str = "default-src 'self'"
    
    # AI Providers
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_UPLOAD_EXTENSIONS: str = "jpg,jpeg,png,pdf"
    
    # Email (for notifications)
    EMAIL_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção."""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Verifica se está em ambiente de testes."""
        return self.ENVIRONMENT == Environment.TESTING
    
    def get_cors_origins(self) -> Union[List[str], str]:
        """
        Retorna lista de origins permitidas para CORS.
        
        Returns:
            Lista de origins ou "*" para permitir todos
        """
        if self.CORS_ORIGINS == "*":
            return "*"
        
        # Parse comma-separated origins
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        
        # Add default development origins if in dev mode
        if self.is_development:
            dev_origins = [
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000"
            ]
            origins.extend([origin for origin in dev_origins if origin not in origins])
        
        return origins
    
    def get_cors_methods(self) -> List[str]:
        """
        Retorna lista de métodos HTTP permitidos.
        
        Returns:
            Lista de métodos HTTP
        """
        return [method.strip().upper() for method in self.CORS_ALLOW_METHODS.split(",")]
    
    def get_cors_headers(self) -> Union[List[str], str]:
        """
        Retorna headers permitidos para CORS.
        
        Returns:
            Lista de headers ou "*" para permitir todos
        """
        if self.CORS_ALLOW_HEADERS == "*":
            return "*"
        
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",")]
    
    def is_origin_allowed(self, origin: str) -> bool:
        """
        Verifica se uma origin está permitida.
        
        Args:
            origin: Origin para verificar
            
        Returns:
            True se permitida, False caso contrário
        """
        allowed_origins = self.get_cors_origins()
        
        # Se permite todos
        if allowed_origins == "*":
            return True
        
        # Verificação exata
        if origin in allowed_origins:
            return True
        
        # Se CORS dinâmico está habilitado, verificar padrões
        if self.ENABLE_DYNAMIC_CORS:
            return self._check_dynamic_cors(origin)
        
        return False
    
    def _check_dynamic_cors(self, origin: str) -> bool:
        """
        Verifica CORS dinâmico para domínios personalizados.
        
        Args:
            origin: Origin para verificar
            
        Returns:
            True se corresponde ao padrão permitido
        """
        import re
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(origin)
            domain = parsed.netloc.lower()
            
            # Verificar padrão de tenant
            if self.TENANT_DOMAIN_PATTERN:
                # Converter wildcard pattern para regex
                pattern = self.TENANT_DOMAIN_PATTERN.replace("*", r"[\w\-]+")
                if re.match(f"^{pattern}$", domain):
                    return True
            
            # Verificar subdomínios permitidos
            if self.ALLOWED_SUBDOMAINS:
                allowed_subs = [sub.strip() for sub in self.ALLOWED_SUBDOMAINS.split(",")]
                for sub in allowed_subs:
                    if domain == f"{sub}.fabrica-livros.com":
                        return True
            
            return False
            
        except Exception:
            # Em caso de erro no parsing, rejeitar
            return False
    
    def get_security_headers(self) -> dict:
        """
        Retorna headers de segurança configurados.
        
        Returns:
            Dict com headers de segurança
        """
        headers = {}
        
        if not self.SECURITY_HEADERS_ENABLED:
            return headers
        
        headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Permitted-Cross-Domain-Policies": "none"
        })
        
        # HSTS apenas em produção com HTTPS
        if self.is_production:
            headers["Strict-Transport-Security"] = f"max-age={self.HSTS_MAX_AGE}; includeSubDomains"
        
        # CSP se configurado
        if self.CONTENT_SECURITY_POLICY:
            headers["Content-Security-Policy"] = self.CONTENT_SECURITY_POLICY
        
        return headers
    
    def get_allowed_upload_extensions(self) -> List[str]:
        """
        Retorna extensões permitidas para upload.
        
        Returns:
            Lista de extensões
        """
        return [ext.strip().lower() for ext in self.ALLOWED_UPLOAD_EXTENSIONS.split(",")]

settings = Settings()
