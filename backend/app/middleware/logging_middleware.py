"""
Middleware para logging automático de requisições e métricas.
"""

import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import (
    get_logger, 
    set_request_context, 
    clear_request_context,
    metrics_logger,
    security_logger,
    audit_logger
)

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging automático de requisições com métricas.
    """
    
    def __init__(self, app):
        self.app = app
        # Paths que não devem ser logados (health checks, etc)
        self.excluded_paths = {
            "/health",
            "/health/",
            "/metrics",
            "/metrics/",
            "/favicon.ico",
            "/robots.txt"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa requisição com logging completo.
        
        Args:
            request: Request do FastAPI
            call_next: Próximo middleware/handler
            
        Returns:
            Response processada
        """
        # Skip logging para paths excluídos
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Gerar ID único da requisição
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Extrair informações da requisição
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        
        # Configurar contexto de logging
        set_request_context(request_id)
        
        # Armazenar no state da requisição para uso posterior
        request.state.request_id = request_id
        request.state.start_time = start_time
        request.state.client_ip = client_ip
        
        # Log inicial da requisição
        logger.info(
            f"Request started: {method} {path}",
            extra={
                'event_type': 'request_start',
                'http_method': method,
                'http_path': path,
                'query_params': query_params,
                'client_ip': client_ip,
                'user_agent': user_agent,
                'content_length': request.headers.get('content-length'),
                'content_type': request.headers.get('content-type')
            }
        )
        
        # Detectar atividades suspeitas
        self._check_suspicious_activity(request)
        
        try:
            # Processar requisição
            response = await call_next(request)
            
            # Calcular tempo de processamento
            process_time = (time.time() - start_time) * 1000  # em ms
            
            # Atualizar contexto com user_id se disponível
            user_id = getattr(request.state, 'user_id', None)
            if user_id:
                set_request_context(request_id, user_id)
            
            # Log de sucesso
            logger.info(
                f"Request completed: {method} {path} - {response.status_code}",
                extra={
                    'event_type': 'request_complete',
                    'http_status_code': response.status_code,
                    'process_time_ms': round(process_time, 2),
                    'response_size': response.headers.get('content-length'),
                    'user_id': user_id
                }
            )
            
            # Log métricas de performance
            metrics_logger.log_request_metrics(
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=process_time,
                user_id=user_id,
                client_ip=client_ip
            )
            
            # Adicionar headers de resposta
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 2))
            
            # Log métricas de negócio específicas
            self._log_business_metrics(request, response, process_time)
            
            return response
            
        except Exception as exc:
            # Calcular tempo mesmo em caso de erro
            process_time = (time.time() - start_time) * 1000
            
            # Log de erro
            logger.error(
                f"Request failed: {method} {path} - {type(exc).__name__}",
                extra={
                    'event_type': 'request_error',
                    'exception_type': type(exc).__name__,
                    'exception_message': str(exc),
                    'process_time_ms': round(process_time, 2)
                },
                exc_info=True
            )
            
            # Log métricas de erro
            metrics_logger.log_request_metrics(
                method=method,
                path=path,
                status_code=500,
                duration_ms=process_time,
                error_type=type(exc).__name__
            )
            
            # Re-lançar exceção para tratamento normal
            raise
            
        finally:
            # Limpar contexto de logging
            clear_request_context()
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extrai IP real do cliente considerando proxies.
        
        Args:
            request: Request do FastAPI
            
        Returns:
            IP do cliente
        """
        # Headers de proxy comuns
        forwarded_headers = [
            "X-Forwarded-For",
            "X-Real-IP", 
            "X-Client-IP",
            "CF-Connecting-IP"  # Cloudflare
        ]
        
        for header in forwarded_headers:
            value = request.headers.get(header)
            if value:
                # X-Forwarded-For pode ter múltiplos IPs separados por vírgula
                return value.split(",")[0].strip()
        
        # Fallback para IP direto
        return request.client.host if request.client else "unknown"
    
    def _check_suspicious_activity(self, request: Request) -> None:
        """
        Verifica atividades suspeitas na requisição.
        
        Args:
            request: Request do FastAPI
        """
        # Lista de user agents suspeitos
        suspicious_user_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'nessus',
            'openvas', 'burp', 'w3af', 'skipfish', 'gobuster'
        ]
        
        user_agent = request.headers.get("user-agent", "").lower()
        
        # Verificar user agents suspeitos
        for suspicious in suspicious_user_agents:
            if suspicious in user_agent:
                security_logger.log_suspicious_activity(
                    activity_type='suspicious_user_agent',
                    details={
                        'user_agent': user_agent,
                        'client_ip': self._get_client_ip(request),
                        'path': request.url.path,
                        'method': request.method
                    },
                    severity='medium'
                )
                break
        
        # Verificar paths suspeitos
        suspicious_paths = [
            'wp-admin', 'wp-login', '.env', 'config.php', 'admin.php',
            'phpmyadmin', 'sql', '../', '..\\', 'etc/passwd'
        ]
        
        path = request.url.path.lower()
        for suspicious_path in suspicious_paths:
            if suspicious_path in path:
                security_logger.log_suspicious_activity(
                    activity_type='suspicious_path_access',
                    details={
                        'path': request.url.path,
                        'client_ip': self._get_client_ip(request),
                        'user_agent': user_agent
                    },
                    severity='high'
                )
                break
        
        # Verificar tentativas de SQL injection básicas
        query_string = str(request.query_params)
        sql_injection_patterns = [
            'union select', 'drop table', 'insert into', 'delete from',
            'update set', 'exec(', 'script>', '<script', 'javascript:',
            'or 1=1', "' or ''='"
        ]
        
        for pattern in sql_injection_patterns:
            if pattern in query_string.lower():
                security_logger.log_suspicious_activity(
                    activity_type='potential_sql_injection',
                    details={
                        'query_string': query_string,
                        'pattern_detected': pattern,
                        'client_ip': self._get_client_ip(request),
                        'path': request.url.path
                    },
                    severity='critical'
                )
                break
    
    def _log_business_metrics(self, request: Request, response: Response, process_time: float) -> None:
        """
        Log métricas específicas de negócio baseadas no endpoint.
        
        Args:
            request: Request do FastAPI
            response: Response do FastAPI
            process_time: Tempo de processamento em ms
        """
        path = request.url.path
        method = request.method
        status_code = response.status_code
        
        # Métricas de autenticação
        if '/auth/' in path:
            if 'login' in path and status_code == 200:
                metrics_logger.log_business_metric('user_login_success', 1)
            elif 'login' in path and status_code >= 400:
                metrics_logger.log_business_metric('user_login_failure', 1)
            elif 'register' in path and status_code == 200:
                metrics_logger.log_business_metric('user_registration', 1)
        
        # Métricas de livros
        elif '/books/' in path:
            if method == 'POST' and status_code == 201:
                metrics_logger.log_business_metric('book_created', 1)
            elif '/generate' in path and method == 'POST':
                metrics_logger.log_business_metric('book_generation_started', 1)
            elif '/pdf' in path and method == 'GET':
                metrics_logger.log_business_metric('pdf_downloaded', 1)
        
        # Métricas de performance por tipo de endpoint
        if '/books/' in path:
            metrics_logger.log_performance_metric(
                operation='book_endpoint',
                duration_ms=process_time,
                success=status_code < 400
            )
        elif '/auth/' in path:
            metrics_logger.log_performance_metric(
                operation='auth_endpoint',
                duration_ms=process_time,
                success=status_code < 400
            )
        elif '/users/' in path:
            metrics_logger.log_performance_metric(
                operation='user_endpoint',
                duration_ms=process_time,
                success=status_code < 400
            )


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware para auditoria automática de ações.
    """
    
    def __init__(self, app):
        self.app = app
        # Actions que devem ser auditadas
        self.auditable_methods = {'POST', 'PUT', 'PATCH', 'DELETE'}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa requisição com auditoria.
        
        Args:
            request: Request do FastAPI
            call_next: Próximo middleware/handler
            
        Returns:
            Response processada
        """
        # Só auditar métodos que modificam dados
        if request.method not in self.auditable_methods:
            return await call_next(request)
        
        # Armazenar dados da requisição para auditoria
        request_data = {
            'method': request.method,
            'path': request.url.path,
            'client_ip': self._get_client_ip(request)
        }
        
        # Processar requisição
        response = await call_next(request)
        
        # Log auditoria se ação foi bem-sucedida
        if response.status_code < 400:
            user_id = getattr(request.state, 'user_id', None)
            
            if user_id:
                action = self._determine_action(request.method, request.url.path)
                resource_type, resource_id = self._extract_resource_info(request.url.path)
                
                audit_logger.log_user_action(
                    user_id=user_id,
                    action=action,
                    resource=resource_type,
                    resource_id=resource_id,
                    client_ip=request_data['client_ip']
                )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrai IP do cliente."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _determine_action(self, method: str, path: str) -> str:
        """
        Determina ação baseada no método e path.
        
        Args:
            method: Método HTTP
            path: Path da requisição
            
        Returns:
            Nome da ação
        """
        method_map = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
        
        base_action = method_map.get(method, 'action')
        
        # Ações específicas baseadas no path
        if 'activate' in path:
            return 'activate'
        elif 'deactivate' in path:
            return 'deactivate'
        elif 'generate' in path:
            return 'generate'
        elif 'password' in path:
            return 'change_password'
        
        return base_action
    
    def _extract_resource_info(self, path: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extrai informações do recurso do path.
        
        Args:
            path: Path da requisição
            
        Returns:
            Tuple (resource_type, resource_id)
        """
        parts = path.strip('/').split('/')
        
        if 'books' in parts:
            resource_type = 'book'
            # Procurar por ID numérico
            for part in parts:
                if part.isdigit():
                    return resource_type, part
            return resource_type, None
        elif 'users' in parts:
            resource_type = 'user'
            for part in parts:
                if part.isdigit():
                    return resource_type, part
            return resource_type, None
        
        return None, None


# Helper functions para usar nos endpoints

def log_user_action_detailed(
    request: Request,
    user_id: int,
    action: str,
    resource: Optional[str] = None,
    resource_id: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    **extra_fields
) -> None:
    """
    Helper para log detalhado de ação do usuário.
    
    Args:
        request: Request do FastAPI
        user_id: ID do usuário
        action: Ação realizada
        resource: Recurso afetado
        resource_id: ID do recurso
        old_values: Valores antigos
        new_values: Valores novos
        **extra_fields: Campos extras
    """
    client_ip = request.state.client_ip if hasattr(request.state, 'client_ip') else 'unknown'
    
    audit_logger.log_user_action(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        client_ip=client_ip,
        **extra_fields
    )


def log_security_event(
    event_type: str,
    request: Request,
    details: dict,
    severity: str = 'medium'
) -> None:
    """
    Helper para log de evento de segurança.
    
    Args:
        event_type: Tipo do evento
        request: Request do FastAPI
        details: Detalhes do evento
        severity: Severidade do evento
    """
    client_ip = request.state.client_ip if hasattr(request.state, 'client_ip') else 'unknown'
    user_agent = request.headers.get('user-agent', 'unknown')
    
    details_with_context = {
        **details,
        'client_ip': client_ip,
        'user_agent': user_agent,
        'path': request.url.path,
        'method': request.method
    }
    
    security_logger.log_suspicious_activity(
        activity_type=event_type,
        details=details_with_context,
        severity=severity
    )


def log_business_event(
    event_name: str,
    value: float = 1.0,
    tags: Optional[dict] = None
) -> None:
    """
    Helper para log de evento de negócio.
    
    Args:
        event_name: Nome do evento
        value: Valor do evento
        tags: Tags adicionais
    """
    metrics_logger.log_business_metric(
        metric_name=event_name,
        value=value,
        tags=tags
    )