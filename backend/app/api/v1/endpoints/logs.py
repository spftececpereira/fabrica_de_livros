"""
Endpoints para consulta de logs e auditoria (apenas admins).
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/logs/audit")
async def get_audit_logs(
    current_user: User = Depends(deps.get_current_admin_user),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    user_id: Optional[int] = Query(None, description="Filtrar por usuário"),
    action: Optional[str] = Query(None, description="Filtrar por ação"),
    resource: Optional[str] = Query(None, description="Filtrar por recurso"),
    hours: int = Query(24, ge=1, le=168, description="Últimas N horas")
) -> Dict[str, Any]:
    """
    Retorna logs de auditoria filtrados (apenas admins).
    
    Args:
        limit: Número máximo de logs
        user_id: Filtrar por ID do usuário
        action: Filtrar por tipo de ação
        resource: Filtrar por tipo de recurso
        hours: Número de horas para buscar
        
    Returns:
        Lista de logs de auditoria
    """
    try:
        audit_logs = await _read_log_file(
            'audit.log', 
            limit=limit,
            hours=hours,
            filters={
                'user_id': user_id,
                'action': action,
                'resource': resource
            }
        )
        
        return {
            "logs": audit_logs,
            "total": len(audit_logs),
            "filters_applied": {
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "hours": hours
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve audit logs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audit logs: {str(e)}"
        )


@router.get("/logs/security")
async def get_security_logs(
    current_user: User = Depends(deps.get_current_admin_user),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    severity: Optional[str] = Query(None, description="Filtrar por severidade"),
    event_type: Optional[str] = Query(None, description="Filtrar por tipo de evento"),
    hours: int = Query(24, ge=1, le=168, description="Últimas N horas")
) -> Dict[str, Any]:
    """
    Retorna logs de segurança filtrados (apenas admins).
    
    Args:
        limit: Número máximo de logs
        severity: Filtrar por severidade
        event_type: Filtrar por tipo de evento
        hours: Número de horas para buscar
        
    Returns:
        Lista de logs de segurança
    """
    try:
        security_logs = await _read_log_file(
            'security.log',
            limit=limit,
            hours=hours,
            filters={
                'severity': severity,
                'event_type': event_type
            }
        )
        
        return {
            "logs": security_logs,
            "total": len(security_logs),
            "filters_applied": {
                "severity": severity,
                "event_type": event_type,
                "hours": hours
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve security logs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve security logs: {str(e)}"
        )


@router.get("/logs/metrics")
async def get_metrics_logs(
    current_user: User = Depends(deps.get_current_admin_user),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    metric_type: Optional[str] = Query(None, description="Filtrar por tipo de métrica"),
    operation: Optional[str] = Query(None, description="Filtrar por operação"),
    hours: int = Query(24, ge=1, le=168, description="Últimas N horas")
) -> Dict[str, Any]:
    """
    Retorna logs de métricas filtrados (apenas admins).
    
    Args:
        limit: Número máximo de logs
        metric_type: Filtrar por tipo de métrica
        operation: Filtrar por operação
        hours: Número de horas para buscar
        
    Returns:
        Lista de logs de métricas
    """
    try:
        metrics_logs = await _read_log_file(
            'metrics.log',
            limit=limit,
            hours=hours,
            filters={
                'metric_type': metric_type,
                'operation': operation
            }
        )
        
        return {
            "logs": metrics_logs,
            "total": len(metrics_logs),
            "filters_applied": {
                "metric_type": metric_type,
                "operation": operation,
                "hours": hours
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve metrics logs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics logs: {str(e)}"
        )


@router.get("/logs/errors")
async def get_error_logs(
    current_user: User = Depends(deps.get_current_admin_user),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    level: str = Query("ERROR", description="Nível mínimo do log"),
    hours: int = Query(24, ge=1, le=168, description="Últimas N horas")
) -> Dict[str, Any]:
    """
    Retorna logs de erro filtrados (apenas admins).
    
    Args:
        limit: Número máximo de logs
        level: Nível mínimo do log
        hours: Número de horas para buscar
        
    Returns:
        Lista de logs de erro
    """
    try:
        error_logs = await _read_log_file(
            'error.log',
            limit=limit,
            hours=hours,
            filters={'level': level}
        )
        
        return {
            "logs": error_logs,
            "total": len(error_logs),
            "filters_applied": {
                "level": level,
                "hours": hours
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve error logs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve error logs: {str(e)}"
        )


@router.get("/logs/stats")
async def get_log_statistics(
    current_user: User = Depends(deps.get_current_admin_user),
    hours: int = Query(24, ge=1, le=168, description="Últimas N horas")
) -> Dict[str, Any]:
    """
    Retorna estatísticas dos logs (apenas admins).
    
    Args:
        hours: Número de horas para análise
        
    Returns:
        Estatísticas dos logs
    """
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        stats = {
            "period_hours": hours,
            "cutoff_time": cutoff_time.isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Estatísticas de auditoria
        audit_logs = await _read_log_file('audit.log', limit=10000, hours=hours)
        stats["audit"] = _analyze_logs(audit_logs, 'audit')
        
        # Estatísticas de segurança
        security_logs = await _read_log_file('security.log', limit=10000, hours=hours)
        stats["security"] = _analyze_logs(security_logs, 'security')
        
        # Estatísticas de métricas
        metrics_logs = await _read_log_file('metrics.log', limit=10000, hours=hours)
        stats["metrics"] = _analyze_logs(metrics_logs, 'metrics')
        
        # Estatísticas de erros
        error_logs = await _read_log_file('error.log', limit=10000, hours=hours)
        stats["errors"] = _analyze_logs(error_logs, 'errors')
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to generate log statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate log statistics: {str(e)}"
        )


async def _read_log_file(
    filename: str,
    limit: int = 100,
    hours: int = 24,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Lê e filtra arquivo de log.
    
    Args:
        filename: Nome do arquivo de log
        limit: Limite de registros
        hours: Horas para filtrar
        filters: Filtros adicionais
        
    Returns:
        Lista de entradas de log filtradas
    """
    log_file = Path("logs") / filename
    
    if not log_file.exists():
        return []
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    logs = []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Processar linhas mais recentes primeiro
        for line in reversed(lines[-limit*2:]):  # Pegar mais linhas para filtrar
            line = line.strip()
            if not line:
                continue
            
            try:
                log_entry = json.loads(line)
                
                # Filtrar por timestamp
                if 'timestamp' in log_entry:
                    log_time = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
                    if log_time < cutoff_time:
                        continue
                
                # Aplicar filtros
                if filters:
                    skip_entry = False
                    for key, value in filters.items():
                        if value is not None and log_entry.get(key) != value:
                            skip_entry = True
                            break
                    if skip_entry:
                        continue
                
                logs.append(log_entry)
                
                if len(logs) >= limit:
                    break
                    
            except json.JSONDecodeError:
                # Ignorar linhas que não são JSON válido
                continue
                
    except Exception as e:
        logger.error(f"Error reading log file {filename}: {e}")
        raise
    
    return logs


def _analyze_logs(logs: List[Dict[str, Any]], log_type: str) -> Dict[str, Any]:
    """
    Analisa logs e gera estatísticas.
    
    Args:
        logs: Lista de logs
        log_type: Tipo do log
        
    Returns:
        Estatísticas dos logs
    """
    total_entries = len(logs)
    
    if total_entries == 0:
        return {
            "total_entries": 0,
            "analysis": "No logs found for the specified period"
        }
    
    stats = {
        "total_entries": total_entries
    }
    
    if log_type == 'audit':
        # Análise de logs de auditoria
        actions = {}
        users = {}
        
        for log in logs:
            action = log.get('action', 'unknown')
            user_id = log.get('user_id', 'unknown')
            
            actions[action] = actions.get(action, 0) + 1
            users[str(user_id)] = users.get(str(user_id), 0) + 1
        
        stats.update({
            "top_actions": sorted(actions.items(), key=lambda x: x[1], reverse=True)[:10],
            "active_users": len([u for u in users.keys() if u != 'unknown']),
            "most_active_users": sorted(users.items(), key=lambda x: x[1], reverse=True)[:5]
        })
    
    elif log_type == 'security':
        # Análise de logs de segurança
        severities = {}
        event_types = {}
        
        for log in logs:
            severity = log.get('severity', 'unknown')
            event_type = log.get('event_type', 'unknown')
            
            severities[severity] = severities.get(severity, 0) + 1
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        stats.update({
            "by_severity": severities,
            "by_event_type": event_types,
            "critical_events": len([l for l in logs if l.get('severity') == 'critical'])
        })
    
    elif log_type == 'metrics':
        # Análise de logs de métricas
        metric_types = {}
        operations = {}
        
        for log in logs:
            metric_type = log.get('metric_type', 'unknown')
            operation = log.get('operation', 'unknown')
            
            metric_types[metric_type] = metric_types.get(metric_type, 0) + 1
            operations[operation] = operations.get(operation, 0) + 1
        
        stats.update({
            "by_metric_type": metric_types,
            "by_operation": operations
        })
    
    elif log_type == 'errors':
        # Análise de logs de erro
        levels = {}
        modules = {}
        
        for log in logs:
            level = log.get('level', 'unknown')
            module = log.get('module', 'unknown')
            
            levels[level] = levels.get(level, 0) + 1
            modules[module] = modules.get(module, 0) + 1
        
        stats.update({
            "by_level": levels,
            "by_module": modules,
            "critical_errors": len([l for l in logs if l.get('level') == 'CRITICAL'])
        })
    
    return stats