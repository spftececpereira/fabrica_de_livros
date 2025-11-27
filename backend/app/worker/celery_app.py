from celery import Celery
from celery.signals import worker_init, worker_shutdown, task_prerun, task_postrun
from app.core.config import settings
import logging
import asyncio
from typing import Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar instância do Celery
celery_app = Celery(
    "fabrica_livros_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"]
)

# Configurações básicas
celery_app.conf.update(
    # Serialização
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.worker.tasks.generate_book_content": {"queue": "book_generation"},
        "app.worker.tasks.generate_book_pdf": {"queue": "pdf_generation"},
        "app.worker.tasks.generate_book_images": {"queue": "image_generation"},
        "app.worker.tasks.*": {"queue": "default"}
    },
    
    # Worker configuration
    worker_concurrency=2,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # Task execution
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    result_expires=3600,  # 1 hour
    
    # Retry configuration
    task_retry_jitter=True,
    task_retry_jitter_max=0.1,
    task_max_retries=3,
    task_default_retry_delay=60,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Beat configuration (para tasks periódicas)
    beat_schedule={
        "cleanup-failed-tasks": {
            "task": "app.worker.tasks.cleanup_failed_books",
            "schedule": 3600.0,  # Every hour
        },
    }
)


@worker_init.connect
def worker_init_handler(sender=None, **kwargs):
    """Inicialização do worker."""
    logger.info("Celery worker initialized")
    
    # Verificar se há um loop de eventos ativo
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Event loop is closed")
    except RuntimeError:
        # Criar novo loop para o worker
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.info("Created new event loop for worker")


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Limpeza no shutdown do worker."""
    logger.info("Celery worker shutting down")
    
    # Fechar loop de eventos se existir
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            # Cancelar tasks pendentes
            pending_tasks = asyncio.all_tasks(loop)
            for task in pending_tasks:
                task.cancel()
            
            # Aguardar finalização das tasks canceladas
            if pending_tasks:
                loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
            
            loop.close()
            logger.info("Event loop closed")
    except Exception as e:
        logger.error(f"Error closing event loop: {e}")


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handler executado antes de cada task."""
    logger.info(f"Starting task {task.name} with ID {task_id}")


@task_postrun.connect  
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **kwds):
    """Handler executado após cada task."""
    if state == "SUCCESS":
        logger.info(f"Task {task.name} completed successfully with ID {task_id}")
    elif state == "FAILURE":
        logger.error(f"Task {task.name} failed with ID {task_id}")
    elif state == "RETRY":
        logger.warning(f"Task {task.name} is retrying with ID {task_id}")


def get_async_session():
    """
    Cria uma nova sessão async para uso em tasks.
    
    Returns:
        AsyncSession: Sessão de banco configurada para tasks
    """
    from app.core.database import AsyncSessionLocal
    return AsyncSessionLocal()


async def run_async_task(coro_func, *args, **kwargs) -> Any:
    """
    Helper para executar funções async em tasks Celery.
    
    Args:
        coro_func: Função async para executar
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
        
    Returns:
        Resultado da função async
    """
    try:
        # Verificar se há loop de eventos
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Event loop is closed")
    except RuntimeError:
        # Criar novo loop se necessário
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        # Executar função async
        result = await coro_func(*args, **kwargs)
        return result
    except Exception as e:
        logger.error(f"Error in async task: {e}", exc_info=True)
        raise
    finally:
        # Cleanup de tasks pendentes
        pending_tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
        if pending_tasks:
            logger.warning(f"Cleaning up {len(pending_tasks)} pending tasks")
            for task in pending_tasks:
                task.cancel()
            
            # Aguardar cancelamento
            try:
                await asyncio.gather(*pending_tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"Error cleaning up tasks: {e}")


def sync_run_async_task(coro_func, *args, **kwargs) -> Any:
    """
    Wrapper síncrono para executar funções async em tasks Celery.
    
    Args:
        coro_func: Função async para executar
        *args: Argumentos posicionais  
        **kwargs: Argumentos nomeados
        
    Returns:
        Resultado da função async
    """
    try:
        # Verificar se há loop de eventos ativo
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Se o loop está rodando, criar task
            return loop.create_task(run_async_task(coro_func, *args, **kwargs))
    except RuntimeError:
        pass
    
    # Criar novo loop e executar
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(run_async_task(coro_func, *args, **kwargs))
    finally:
        # Cleanup do loop
        try:
            # Cancelar tasks pendentes
            pending_tasks = asyncio.all_tasks(loop)
            for task in pending_tasks:
                task.cancel()
            
            if pending_tasks:
                loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
        except Exception as e:
            logger.error(f"Error during loop cleanup: {e}")
        finally:
            loop.close()


# Configurações específicas por ambiente
if settings.is_development:
    celery_app.conf.update(
        task_always_eager=False,  # Para desenvolvimento real com Redis
        worker_log_level="INFO"
    )
elif settings.is_production:
    celery_app.conf.update(
        worker_log_level="WARNING",
        worker_concurrency=4,  # Mais workers em produção
        task_soft_time_limit=300,  # 5 minutes
        task_time_limit=600,  # 10 minutes hard limit
    )
elif settings.is_testing:
    celery_app.conf.update(
        task_always_eager=True,  # Executar tarefas sincronamente em testes
        task_eager_propagates=True
    )
