"""
Endpoints de health check e monitoramento.
"""

import time
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis # Import redis.asyncio

from app.api import deps
from app.core.database import get_db
from app.core.config import settings
from app.core.logging import get_logger, metrics_logger
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.book_repository import BookRepository

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check básico da aplicação.
    
    Returns:
        Status da aplicação
    """
    logger.info("Health check endpoint accessed", extra={"endpoint": "/health"})
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/health/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Health check detalhado com verificação de dependências.
    
    Returns:
        Status detalhado de todos os componentes
    """
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    # Check 1: Database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        db_result = result.scalar()
        
        if db_result == 1:
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        else:
            raise Exception("Unexpected database response")
            
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check 2: Redis connectivity
    try:
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy", # Changed to unhealthy as Redis is critical
            "message": f"Redis connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy" # If Redis is down, app is unhealthy
    
    # Check 3: Memory usage
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent < 80:
            status = "healthy"
        elif memory_percent < 90:
            status = "degraded"
        else:
            status = "unhealthy"
            
        health_status["checks"]["memory"] = {
            "status": status,
            "usage_percent": memory_percent,
            "available_gb": round(memory.available / (1024**3), 2)
        }
        
        if status == "unhealthy":
            health_status["status"] = "unhealthy"
        elif status == "degraded" and health_status["status"] == "healthy":
            health_status["status"] = "degraded"
            
    except ImportError:
        health_status["checks"]["memory"] = {
            "status": "unknown",
            "message": "psutil not available"
        }
    except Exception as e:
        health_status["checks"]["memory"] = {
            "status": "unknown",
            "message": f"Memory check failed: {str(e)}"
        }
    
    # Check 4: Disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        disk_percent = (used / total) * 100
        
        if disk_percent < 80:
            status = "healthy"
        elif disk_percent < 90:
            status = "degraded"
        else:
            status = "unhealthy"
            
        health_status["checks"]["disk"] = {
            "status": status,
            "usage_percent": round(disk_percent, 2),
            "free_gb": round(free / (1024**3), 2)
        }
        
        if status == "unhealthy":
            health_status["status"] = "unhealthy"
        elif status == "degraded" and health_status["status"] in ["healthy", "degraded"]:
            health_status["status"] = "degraded"
            
    except Exception as e:
        health_status["checks"]["disk"] = {
            "status": "unknown",
            "message": f"Disk check failed: {str(e)}"
        }
    
    # Check 5: Application metrics
    try:
        user_repo = UserRepository(db)
        book_repo = BookRepository(db)
        
        # Contar usuários ativos
        active_users = await user_repo.count(is_active=True)
        
        # Contar livros por status
        draft_books = await book_repo.count(status="draft")
        processing_books = await book_repo.count(status="processing")
        completed_books = await book_repo.count(status="completed")
        
        health_status["checks"]["application_metrics"] = {
            "status": "healthy",
            "active_users": active_users,
            "books": {
                "draft": draft_books,
                "processing": processing_books,
                "completed": completed_books
            }
        }
        
    except Exception as e:
        health_status["checks"]["application_metrics"] = {
            "status": "degraded",
            "message": f"Metrics collection failed: {str(e)}"
        }
    
    # Adicionar tempo total de verificação
    health_status["check_duration_ms"] = round((time.time() - start_time) * 1000, 2)
    
    # Log métricas de health check
    metrics_logger.log_performance_metric(
        operation="health_check",
        duration_ms=health_status["check_duration_ms"],
        success=health_status["status"] in ["healthy", "degraded"]
    )
    
    return health_status


@router.get("/health/readiness")
async def readiness_check(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Readiness check para Kubernetes/Docker.
    
    Verifica se a aplicação está pronta para receber tráfego.
    
    Returns:
        Status de readiness
    """
    try:
        # Verificar conectividade básica do banco
        await db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "reason": "Database connectivity issue",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/health/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check para Kubernetes/Docker.
    
    Verifica se a aplicação está executando corretamente.
    
    Returns:
        Status de liveness
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - getattr(sys.modules[__name__], '_start_time', time.time())
    }


@router.get("/metrics")
async def application_metrics(
    current_user: User = Depends(deps.get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Métricas detalhadas da aplicação (apenas admins).
    
    Returns:
        Métricas completas da aplicação
    """
    start_time = time.time()
    
    try:
        user_repo = UserRepository(db)
        book_repo = BookRepository(db)
        
        # Métricas de usuários
        user_stats = await user_repo.get_users_stats()
        
        # Métricas de livros
        book_stats = await book_repo.get_books_stats()
        
        # Métricas de performance do sistema
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memória
        memory = psutil.virtual_memory()
        
        # Processos
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # Estatísticas de rede (se disponível)
        try:
            network = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        except:
            network_stats = None
        
        # Últimas 24 horas de atividade
        yesterday = datetime.utcnow() - timedelta(hours=24)
        recent_users = await user_repo.count(created_at__gte=yesterday)
        recent_books = await book_repo.count(created_at__gte=yesterday)
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "collection_time_ms": round((time.time() - start_time) * 1000, 2),
            
            # Métricas de negócio
            "business_metrics": {
                "users": user_stats,
                "books": book_stats,
                "recent_activity": {
                    "new_users_24h": recent_users,
                    "new_books_24h": recent_books
                }
            },
            
            # Métricas de sistema
            "system_metrics": {
                "cpu_usage_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "process": {
                    "memory_rss_mb": round(process_memory.rss / (1024**2), 2),
                    "memory_vms_mb": round(process_memory.vms / (1024**2), 2)
                }
            },
            
            # Métricas de aplicação
            "application_metrics": {
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "python_version": sys.version.split()[0],
                "uptime_seconds": round(time.time() - getattr(sys.modules[__name__], '_start_time', time.time()))
            }
        }
        
        # Adicionar métricas de rede se disponíveis
        if network_stats:
            metrics["system_metrics"]["network"] = network_stats
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect metrics: {str(e)}"
        )


@router.get("/metrics/summary")
async def metrics_summary(
    current_user: User = Depends(deps.get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Resumo das métricas principais (apenas admins).
    
    Returns:
        Resumo das métricas mais importantes
    """
    try:
        user_repo = UserRepository(db)
        book_repo = BookRepository(db)
        
        # Métricas básicas
        total_users = await user_repo.count()
        active_users = await user_repo.count(is_active=True)
        
        total_books = await book_repo.count()
        completed_books = await book_repo.count(status="completed")
        
        # Taxa de conversão
        conversion_rate = (completed_books / total_books * 100) if total_books > 0 else 0
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "activation_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 2)
                },
                "books": {
                    "total": total_books,
                    "completed": completed_books,
                    "completion_rate": round(conversion_rate, 2)
                },
                "health_status": "healthy"  # Simplificado
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to collect metrics summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect metrics summary: {str(e)}"
        )


@router.get("/version")
async def version_info() -> Dict[str, Any]:
    """
    Informações de versão da aplicação.
    
    Returns:
        Informações de versão e build
    """
    return {
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "api_version": "v1",
        "python_version": sys.version.split()[0],
        "timestamp": datetime.utcnow().isoformat()
    }


# Armazenar tempo de início do módulo
setattr(sys.modules[__name__], '_start_time', time.time())