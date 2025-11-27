"""
Middleware de segurança com rate limiting e headers de segurança.
"""

import time
import asyncio
from typing import Callable, Dict, Any, Optional
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.exceptions.base_exceptions import ErrorCode
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter usando sliding window counter.
    """
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        """
        Inicializa rate limiter.
        
        Args:
            max_requests: Máximo de requests por janela
            window_seconds: Tamanho da janela em segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self._cleanup_interval = 60  # Cleanup a cada 60 segundos
        self._last_cleanup = time.time()
    
    def is_allowed(self, identifier: str) -> tuple[bool, Dict[str, Any]]:
        """
        Verifica se request é permitida.
        
        Args:
            identifier: Identificador único (IP, user_id, etc)
            
        Returns:
            Tuple (is_allowed, rate_limit_info)
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Cleanup periódico para evitar memory leak
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_entries(now)
        
        # Obter requests do identificador
        user_requests = self.requests[identifier]
        
        # Remover requests antigas da janela
        while user_requests and user_requests[0] < window_start:
            user_requests.popleft()
        
        # Verificar se pode fazer nova request
        request_count = len(user_requests)
        is_allowed = request_count < self.max_requests
        
        # Se permitido, adicionar timestamp atual
        if is_allowed:
            user_requests.append(now)
        
        # Calcular informações de rate limit
        remaining = max(0, self.max_requests - request_count - (1 if is_allowed else 0))
        reset_time = int(window_start + self.window_seconds) if user_requests else int(now + self.window_seconds)
        
        rate_limit_info = {
            "limit": self.max_requests,
            "remaining": remaining,
            "reset": reset_time,
            "window": self.window_seconds
        }
        
        return is_allowed, rate_limit_info
    
    def _cleanup_old_entries(self, now: float):
        """Remove entradas antigas para liberar memória."""
        cutoff = now - (self.window_seconds * 2)  # Keep extra buffer
        
        keys_to_remove = []
        for identifier, requests in self.requests.items():
            # Remover requests antigas
            while requests and requests[0] < cutoff:
                requests.popleft()
            
            # Se não há requests recentes, remover entrada
            if not requests:
                keys_to_remove.append(identifier)
        
        for key in keys_to_remove:
            del self.requests[key]
        
        self._last_cleanup = now


class SecurityMiddleware:
    """
    Middleware de segurança com rate limiting e headers.
    """
    
    def __init__(self, app):
        self.app = app
        self.rate_limiter = None
        
        # Inicializar rate limiter se habilitado
        if settings.RATE_LIMIT_ENABLED:
            self.rate_limiter = RateLimiter(
                max_requests=settings.RATE_LIMIT_PER_MINUTE,
                window_seconds=60
            )
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Processa requisição com segurança.
        
        Args:
            request: Request do FastAPI
            call_next: Próximo middleware/handler
            
        Returns:
            Response processada
        """
        # Aplicar rate limiting se habilitado
        if self.rate_limiter and not self._is_excluded_from_rate_limit(request):
            rate_limit_response = await self._apply_rate_limiting(request)
            if rate_limit_response:
                return rate_limit_response
        
        # Verificar origin se CORS dinâmico habilitado
        if settings.ENABLE_DYNAMIC_CORS:
            origin_check = self._check_origin_security(request)
            if origin_check:
                return origin_check
        
        # Processar request
        response = await call_next(request)
        
        # Adicionar headers de segurança
        self._add_security_headers(response)
        
        return response
    
    async def _apply_rate_limiting(self, request: Request) -> Optional[JSONResponse]:
        """
        Aplica rate limiting na requisição.
        
        Args:
            request: Request do FastAPI
            
        Returns:
            JSONResponse se rate limit excedido, None caso contrário
        """
        # Identificador para rate limiting (IP + User se autenticado)
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.state, 'user_id', None)
        
        if user_id:
            identifier = f"user:{user_id}"
        else:
            identifier = f"ip:{client_ip}"
        
        # Verificar rate limit
        is_allowed, rate_info = self.rate_limiter.is_allowed(identifier)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {identifier}",
                extra={
                    "identifier": identifier,
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "method": request.method,
                    "rate_limit_info": rate_info
                }
            )
            
            # Criar resposta de rate limit
            response = JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": "Rate limit excedido. Tente novamente mais tarde.",
                        "code": ErrorCode.VALIDATION_ERROR.value,
                        "status_code": 429,
                        "details": {
                            "rate_limit": {
                                "limit": rate_info["limit"],
                                "window_seconds": rate_info["window"],
                                "reset_at": rate_info["reset"]
                            }
                        }
                    }
                }
            )
            
            # Headers de rate limit
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
            response.headers["Retry-After"] = str(rate_info["window"])
            
            return response
        
        # Request permitida - adicionar headers informativos
        request.state.rate_limit_info = rate_info
        return None
    
    def _check_origin_security(self, request: Request) -> Optional[JSONResponse]:
        """
        Verifica segurança da origin para CORS dinâmico.
        
        Args:
            request: Request do FastAPI
            
        Returns:
            JSONResponse se origin não permitida, None caso contrário
        """
        origin = request.headers.get("origin")
        
        # Se não há origin header, permitir (requests diretos)
        if not origin:
            return None
        
        # Verificar se origin é permitida
        if not settings.is_origin_allowed(origin):
            logger.warning(
                f"Origin not allowed: {origin}",
                extra={
                    "origin": origin,
                    "client_ip": self._get_client_ip(request),
                    "path": request.url.path,
                    "method": request.method
                }
            )
            
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "message": "Origin não permitida",
                        "code": ErrorCode.ACCESS_DENIED.value,
                        "status_code": 403
                    }
                }
            )
        
        return None
    
    def _add_security_headers(self, response: Response) -> None:
        """
        Adiciona headers de segurança à resposta.
        
        Args:
            response: Response do FastAPI
        """
        # Headers de segurança configurados
        security_headers = settings.get_security_headers()
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Headers de rate limit se disponíveis
        if hasattr(response, 'state') and hasattr(response.state, 'rate_limit_info'):
            rate_info = response.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
    
    def _is_excluded_from_rate_limit(self, request: Request) -> bool:
        """
        Verifica se path está excluído do rate limiting.
        
        Args:
            request: Request do FastAPI
            
        Returns:
            True se deve ser excluído
        """
        excluded_paths = [
            "/health",
            "/metrics",
            "/favicon.ico",
            "/robots.txt"
        ]
        
        return request.url.path in excluded_paths
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extrai IP real do cliente.
        
        Args:
            request: Request do FastAPI
            
        Returns:
            IP do cliente
        """
        # Verificar headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        return request.client.host if request.client else "unknown"


class CORSSecurityMiddleware:
    """
    Middleware específico para CORS com suporte a domínios dinâmicos.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Processa CORS com verificações de segurança.
        
        Args:
            request: Request do FastAPI
            call_next: Próximo middleware/handler
            
        Returns:
            Response com headers CORS apropriados
        """
        origin = request.headers.get("origin")
        
        # Para requests OPTIONS (preflight)
        if request.method == "OPTIONS":
            return self._handle_preflight(origin)
        
        # Processar request normal
        response = await call_next(request)
        
        # Adicionar headers CORS apropriados
        self._add_cors_headers(response, origin)
        
        return response
    
    def _handle_preflight(self, origin: Optional[str]) -> JSONResponse:
        """
        Processa request preflight OPTIONS.
        
        Args:
            origin: Origin da requisição
            
        Returns:
            Response para preflight
        """
        headers = {}
        
        # Verificar se origin é permitida
        if origin and settings.is_origin_allowed(origin):
            headers["Access-Control-Allow-Origin"] = origin
            
            if settings.CORS_ALLOW_CREDENTIALS:
                headers["Access-Control-Allow-Credentials"] = "true"
        
        # Methods e headers permitidos
        headers["Access-Control-Allow-Methods"] = settings.CORS_ALLOW_METHODS
        headers["Access-Control-Allow-Headers"] = settings.CORS_ALLOW_HEADERS
        headers["Access-Control-Max-Age"] = str(settings.CORS_MAX_AGE)
        
        return JSONResponse(
            status_code=200,
            content={},
            headers=headers
        )
    
    def _add_cors_headers(self, response: Response, origin: Optional[str]) -> None:
        """
        Adiciona headers CORS à resposta.
        
        Args:
            response: Response do FastAPI
            origin: Origin da requisição
        """
        if origin and settings.is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            
            if settings.CORS_ALLOW_CREDENTIALS:
                response.headers["Access-Control-Allow-Credentials"] = "true"
        
        # Headers expostos para o cliente
        response.headers["Access-Control-Expose-Headers"] = "X-Request-ID, X-Process-Time, X-RateLimit-Remaining"


# Helpers para configuração dinâmica

def configure_cors_for_tenant(subdomain: str) -> str:
    """
    Configura CORS para um tenant específico.
    
    Args:
        subdomain: Subdomínio do tenant
        
    Returns:
        Origin configurada para o tenant
    """
    if settings.is_production:
        return f"https://{subdomain}.fabrica-livros.com"
    else:
        return f"http://{subdomain}.localhost:3000"


def add_tenant_origin(subdomain: str) -> None:
    """
    Adiciona origin de tenant às origens permitidas.
    
    Args:
        subdomain: Subdomínio do tenant
    """
    tenant_origin = configure_cors_for_tenant(subdomain)
    
    current_origins = settings.get_cors_origins()
    if isinstance(current_origins, list) and tenant_origin not in current_origins:
        # Adicionar à lista de subdomínios permitidos
        current_subs = settings.ALLOWED_SUBDOMAINS
        if current_subs:
            settings.ALLOWED_SUBDOMAINS = f"{current_subs},{subdomain}"
        else:
            settings.ALLOWED_SUBDOMAINS = subdomain
        
        logger.info(f"Added tenant origin: {tenant_origin}")


def validate_custom_domain(domain: str) -> bool:
    """
    Valida se um domínio customizado é seguro.
    
    Args:
        domain: Domínio para validar
        
    Returns:
        True se válido e seguro
    """
    import re
    
    # Verificações básicas de segurança
    if not domain or len(domain) > 253:
        return False
    
    # Não permitir IPs
    if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
        return False
    
    # Verificar formato básico de domínio
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    if not re.match(domain_pattern, domain):
        return False
    
    # Lista de domínios proibidos por segurança
    forbidden_domains = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        'example.com',
        'test.com'
    ]
    
    if domain.lower() in forbidden_domains:
        return False
    
    return True