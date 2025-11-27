"""
Sistema de logging estruturado para observabilidade completa.
"""

import logging
import logging.config
import json
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, List
from pathlib import Path
from contextvars import ContextVar
try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    jsonlogger = None

from app.core.config import settings

# Context variables para tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[int] = ContextVar('user_id', default=0)
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')


class StructuredFormatter(logging.Formatter):
    """
    Formatter customizado para logs estruturados em JSON.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        if jsonlogger:
            return self._json_format(record)
        else:
            return self._text_format(record)
    
    def _json_format(self, record: logging.LogRecord) -> str:
        """Format as JSON using jsonlogger if available."""
        log_record = {}
        self.add_fields(log_record, record, {})
        return json.dumps(log_record, ensure_ascii=False)
    
    def _text_format(self, record: logging.LogRecord) -> str:
        """Fallback text format."""
        return f"{datetime.utcnow().isoformat()}Z - {record.levelname} - {record.name} - {record.getMessage()}"
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """
        Adiciona campos customizados ao log record.
        
        Args:
            log_record: Dicionário do log record
            record: Record original do logging
            message_dict: Dicionário da mensagem
        """
        # Set the message first
        log_record['message'] = record.getMessage()
        
        # Timestamp ISO 8601
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Informações do ambiente
        log_record['environment'] = settings.ENVIRONMENT
        log_record['service'] = 'fabrica-livros-api'
        log_record['version'] = settings.VERSION
        
        # Context variables
        log_record['request_id'] = request_id_var.get('')
        log_record['user_id'] = user_id_var.get(0) or None
        log_record['correlation_id'] = correlation_id_var.get('')
        
        # Informações do log
        log_record['level'] = record.levelname
        log_record['logger_name'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Thread info para debugging
        if hasattr(record, 'thread'):
            log_record['thread_id'] = record.thread
            log_record['thread_name'] = record.threadName
        
        # Remover campos desnecessários
        log_record.pop('color_message', None)
        log_record.pop('asctime', None)


class ConsoleFormatter(logging.Formatter):
    """
    Formatter para output colorido no console (desenvolvimento).
    """
    
    # Cores ANSI
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata log record para console com cores.
        
        Args:
            record: Record do logging
            
        Returns:
            String formatada com cores
        """
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format básico
        formatted = super().format(record)
        
        # Adicionar context info se disponível
        request_id = request_id_var.get('')
        user_id = user_id_var.get(0)
        
        context_info = []
        if request_id:
            context_info.append(f"req:{request_id[:8]}")
        if user_id:
            context_info.append(f"user:{user_id}")
        
        context_str = f"[{' '.join(context_info)}] " if context_info else ""
        
        return f"{color}{record.levelname:<8}{reset} {context_str}{formatted}"


class MetricsLogger:
    """
    Logger específico para métricas de performance e negócio.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('metrics')
    
    def log_request_metrics(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[int] = None,
        **extra_fields
    ) -> None:
        """
        Log de métricas de requisição.
        
        Args:
            method: Método HTTP
            path: Path da requisição
            status_code: Código de status HTTP
            duration_ms: Duração em milissegundos
            user_id: ID do usuário (opcional)
            **extra_fields: Campos adicionais
        """
        self.logger.info(
            "Request completed",
            extra={
                'metric_type': 'request',
                'http_method': method,
                'http_path': path,
                'http_status_code': status_code,
                'duration_ms': round(duration_ms, 2),
                'user_id': user_id,
                **extra_fields
            }
        )
    
    def log_business_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = 'count',
        tags: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log de métrica de negócio.
        
        Args:
            metric_name: Nome da métrica
            value: Valor da métrica
            unit: Unidade da métrica
            tags: Tags adicionais
        """
        self.logger.info(
            f"Business metric: {metric_name}",
            extra={
                'metric_type': 'business',
                'metric_name': metric_name,
                'metric_value': value,
                'metric_unit': unit,
                'tags': tags or {}
            }
        )
    
    def log_performance_metric(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        **extra_fields
    ) -> None:
        """
        Log de métrica de performance.
        
        Args:
            operation: Nome da operação
            duration_ms: Duração em milissegundos
            success: Se operação foi bem-sucedida
            **extra_fields: Campos adicionais
        """
        self.logger.info(
            f"Operation performance: {operation}",
            extra={
                'metric_type': 'performance',
                'operation': operation,
                'duration_ms': round(duration_ms, 2),
                'success': success,
                **extra_fields
            }
        )


class SecurityLogger:
    """
    Logger específico para eventos de segurança.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_authentication_attempt(
        self,
        email: str,
        success: bool,
        reason: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Log de tentativa de autenticação.
        
        Args:
            email: Email do usuário
            success: Se autenticação foi bem-sucedida
            reason: Motivo da falha (se houver)
            client_ip: IP do cliente
            user_agent: User agent do cliente
        """
        level = logging.INFO if success else logging.WARNING
        
        self.logger.log(
            level,
            f"Authentication {'succeeded' if success else 'failed'} for {email}",
            extra={
                'event_type': 'authentication',
                'email': email,
                'success': success,
                'failure_reason': reason,
                'client_ip': client_ip,
                'user_agent': user_agent
            }
        )
    
    def log_authorization_failure(
        self,
        user_id: int,
        resource: str,
        action: str,
        reason: str
    ) -> None:
        """
        Log de falha de autorização.
        
        Args:
            user_id: ID do usuário
            resource: Recurso acessado
            action: Ação tentada
            reason: Motivo da negação
        """
        self.logger.warning(
            f"Authorization denied for user {user_id}",
            extra={
                'event_type': 'authorization_failure',
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'denial_reason': reason
            }
        )
    
    def log_suspicious_activity(
        self,
        activity_type: str,
        details: Dict[str, Any],
        severity: str = 'medium'
    ) -> None:
        """
        Log de atividade suspeita.
        
        Args:
            activity_type: Tipo da atividade
            details: Detalhes da atividade
            severity: Severidade (low, medium, high, critical)
        """
        level_map = {
            'low': logging.INFO,
            'medium': logging.WARNING,
            'high': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        self.logger.log(
            level_map.get(severity, logging.WARNING),
            f"Suspicious activity detected: {activity_type}",
            extra={
                'event_type': 'suspicious_activity',
                'activity_type': activity_type,
                'severity': severity,
                'details': details
            }
        )


class AuditLogger:
    """
    Logger para auditoria de ações dos usuários.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_user_action(
        self,
        user_id: int,
        action: str,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        client_ip: Optional[str] = None,
        **extra_fields
    ) -> None:
        """
        Log de ação do usuário para auditoria.
        
        Args:
            user_id: ID do usuário
            action: Ação realizada
            resource: Recurso afetado
            resource_id: ID do recurso
            old_values: Valores antigos (para updates)
            new_values: Valores novos (para updates)
            client_ip: IP do cliente
            **extra_fields: Campos adicionais
        """
        self.logger.info(
            f"User action: {action}",
            extra={
                'event_type': 'user_action',
                'user_id': user_id,
                'action': action,
                'resource': resource,
                'resource_id': resource_id,
                'old_values': old_values,
                'new_values': new_values,
                'client_ip': client_ip,
                **extra_fields
            }
        )
    
    def log_data_change(
        self,
        table: str,
        operation: str,
        record_id: Any,
        changed_fields: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> None:
        """
        Log de mudança de dados.
        
        Args:
            table: Tabela afetada
            operation: Operação (INSERT, UPDATE, DELETE)
            record_id: ID do registro
            changed_fields: Campos alterados
            user_id: ID do usuário responsável
        """
        self.logger.info(
            f"Data change: {operation} on {table}",
            extra={
                'event_type': 'data_change',
                'table': table,
                'operation': operation,
                'record_id': str(record_id),
                'changed_fields': changed_fields,
                'user_id': user_id
            }
        )


def setup_logging() -> None:
    """
    Configura o sistema de logging da aplicação.
    """
    # Criar diretório de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configuração baseada no ambiente
    if settings.is_development:
        log_level = logging.DEBUG
        console_format = ConsoleFormatter()
        enable_file_logging = False
    elif settings.is_testing:
        log_level = logging.WARNING
        console_format = ConsoleFormatter()
        enable_file_logging = False
    else:  # Production
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        console_format = StructuredFormatter() if settings.LOG_FORMAT == 'json' else ConsoleFormatter()
        enable_file_logging = True
    
    # Handlers
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'console',
            'stream': sys.stdout
        }
    }
    
    # File handlers para produção
    if enable_file_logging:
        handlers.update({
            'file_all': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.INFO,
                'formatter': 'structured',
                'filename': 'logs/application.log',
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5
            },
            'file_error': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.ERROR,
                'formatter': 'structured',
                'filename': 'logs/error.log',
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 10
            },
            'file_security': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.INFO,
                'formatter': 'structured',
                'filename': 'logs/security.log',
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 20
            },
            'file_audit': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.INFO,
                'formatter': 'structured',
                'filename': 'logs/audit.log',
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 30
            },
            'file_metrics': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.INFO,
                'formatter': 'structured',
                'filename': 'logs/metrics.log',
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 15
            }
        })
    
    # Configuração completa
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'structured': {
                '()': StructuredFormatter,
                'format': '%(message)s'
            },
            'console': {
                '()': ConsoleFormatter,
                'format': '%(asctime)s - %(name)s - %(message)s',
                'datefmt': '%H:%M:%S'
            }
        },
        'handlers': handlers,
        'loggers': {
            # Root logger
            '': {
                'level': log_level,
                'handlers': ['console'] + (['file_all', 'file_error'] if enable_file_logging else [])
            },
            # Application logger
            'app': {
                'level': log_level,
                'handlers': ['console'] + (['file_all'] if enable_file_logging else []),
                'propagate': False
            },
            # Security events
            'security': {
                'level': logging.INFO,
                'handlers': ['console'] + (['file_security'] if enable_file_logging else []),
                'propagate': False
            },
            # Audit trail
            'audit': {
                'level': logging.INFO,
                'handlers': ['console'] + (['file_audit'] if enable_file_logging else []),
                'propagate': False
            },
            # Metrics
            'metrics': {
                'level': logging.INFO,
                'handlers': ['console'] + (['file_metrics'] if enable_file_logging else []),
                'propagate': False
            },
            # Suppress noisy third-party loggers
            'uvicorn.access': {
                'level': logging.WARNING,
                'propagate': False
            },
            'sqlalchemy': {
                'level': logging.WARNING if not settings.is_development else logging.INFO,
                'propagate': False
            }
        }
    }
    
    # Aplicar configuração
    logging.config.dictConfig(logging_config)


def get_logger(name: str = None) -> logging.Logger:
    """
    Retorna logger configurado.
    
    Args:
        name: Nome do logger (opcional)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name or 'app')


def set_request_context(request_id: str, user_id: Optional[int] = None, correlation_id: Optional[str] = None) -> None:
    """
    Define contexto da requisição para logs.
    
    Args:
        request_id: ID único da requisição
        user_id: ID do usuário (opcional)
        correlation_id: ID de correlação (opcional)
    """
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if correlation_id:
        correlation_id_var.set(correlation_id)


def clear_request_context() -> None:
    """
    Limpa contexto da requisição.
    """
    request_id_var.set('')
    user_id_var.set(0)
    correlation_id_var.set('')


# Instâncias globais dos loggers especializados
metrics_logger = MetricsLogger()
security_logger = SecurityLogger()
audit_logger = AuditLogger()

# Configurar logging na importação
setup_logging()