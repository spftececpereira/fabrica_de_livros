from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_celery_db_session():
    """
    Cria uma nova sessão de banco para uso em tasks Celery.
    
    Esta função é específica para tasks assíncronas do Celery e garante
    que as sessões sejam adequadamente gerenciadas em contexto de workers.
    
    Returns:
        AsyncSession: Sessão de banco configurada para Celery
    """
    return AsyncSessionLocal()


class CeleryDatabaseManager:
    """
    Gerenciador de sessões de banco específico para tasks Celery.
    """
    
    def __init__(self):
        self._session_pool = {}
    
    async def get_session(self, task_id: str = None) -> AsyncSession:
        """
        Obtém sessão de banco para task.
        
        Args:
            task_id: ID da task (para cache de sessão)
            
        Returns:
            AsyncSession: Sessão de banco
        """
        if task_id and task_id in self._session_pool:
            session = self._session_pool[task_id]
            if not session.is_active:
                # Session inativa, criar nova
                await session.close()
                del self._session_pool[task_id]
                session = AsyncSessionLocal()
                self._session_pool[task_id] = session
        else:
            session = AsyncSessionLocal()
            if task_id:
                self._session_pool[task_id] = session
        
        return session
    
    async def close_session(self, task_id: str = None):
        """
        Fecha sessão de banco para task.
        
        Args:
            task_id: ID da task
        """
        if task_id and task_id in self._session_pool:
            session = self._session_pool[task_id]
            await session.close()
            del self._session_pool[task_id]
    
    async def cleanup_sessions(self):
        """Fecha todas as sessões ativas."""
        for task_id, session in self._session_pool.items():
            try:
                await session.close()
            except Exception as e:
                # Log mas não falhe
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error closing session for task {task_id}: {e}")
        
        self._session_pool.clear()


# Instância global do gerenciador para Celery
celery_db_manager = CeleryDatabaseManager()


async def commit_with_retry(session: AsyncSession, max_retries: int = 3):
    """
    Faz commit com retry automático para lidar com deadlocks.
    
    Args:
        session: Sessão de banco
        max_retries: Número máximo de tentativas
        
    Raises:
        Exception: Se todas as tentativas falharem
    """
    import asyncio
    from sqlalchemy.exc import OperationalError
    
    for attempt in range(max_retries):
        try:
            await session.commit()
            return
        except OperationalError as e:
            if "deadlock" in str(e).lower() and attempt < max_retries - 1:
                # Aguardar um pouco antes da próxima tentativa
                await asyncio.sleep(0.1 * (attempt + 1))
                await session.rollback()
                continue
            else:
                await session.rollback()
                raise
        except Exception:
            await session.rollback()
            raise


async def safe_session_operation(operation_func, *args, **kwargs):
    """
    Executa operação de banco com gestão segura de sessão.
    
    Args:
        operation_func: Função async que recebe session como primeiro argumento
        *args: Argumentos para a função
        **kwargs: Argumentos nomeados para a função
        
    Returns:
        Resultado da operação
        
    Raises:
        Exception: Se a operação falhar
    """
    async with AsyncSessionLocal() as session:
        try:
            result = await operation_func(session, *args, **kwargs)
            await commit_with_retry(session)
            return result
        except Exception:
            await session.rollback()
            raise
