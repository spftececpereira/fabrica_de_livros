"""
Tasks assíncronas para processamento de livros com gestão robusta de sessões.
"""

from celery import Task
from celery.exceptions import Retry, MaxRetriesExceededError
from app.worker.celery_app import celery_app, sync_run_async_task, get_async_session
from app.services.ai.factory import AIServiceFactory
from app.repositories.book_repository import BookRepository
from app.repositories.user_repository import UserRepository
from app.models.book import Book
from app.exceptions.base_exceptions import (
    BookNotFoundError,
    ExternalServiceError,
    ErrorCode
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class BaseTask(Task):
    """Task base com tratamento robusto de exceções."""
    
    abstract = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Callback executado quando task falha."""
        logger.error(
            f"Task {self.name} failed",
            extra={
                "task_id": task_id,
                "exception": str(exc),
                "args": args,
                "kwargs": kwargs,
                "traceback": str(einfo)
            }
        )
        # Enviar notificação de falha via WebSocket
        notification_service.send_ws_message(
            user_id=kwargs.get('user_id'), # Assumindo que user_id é passado como kwargs
            message_type="book_generation_update",
            data={
                "task_id": task_id,
                "book_id": kwargs.get('book_id'),
                "status": "failed",
                "message": f"Geração do livro falhou: {str(exc)}",
                "progress": 100
            }
        )
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Callback executado quando task é retentada."""
        logger.warning(
            f"Task {self.name} retrying",
            extra={
                "task_id": task_id,
                "exception": str(exc),
                "retry_count": self.request.retries,
                "max_retries": self.max_retries
            }
        )
        # Enviar notificação de retry via WebSocket
        notification_service.send_ws_message(
            user_id=kwargs.get('user_id'),
            message_type="book_generation_update",
            data={
                "task_id": task_id,
                "book_id": kwargs.get('book_id'),
                "status": "retrying",
                "message": f"Geração do livro falhou, tentando novamente ({self.request.retries}/{self.max_retries})",
                "progress": (self.request.retries / self.max_retries) * 100
            }
        )
    
    def on_success(self, retval, task_id, args, kwargs):
        """Callback executado quando task é bem-sucedida."""
        logger.info(
            f"Task {self.name} completed successfully",
            extra={
                "task_id": task_id,
                "result": str(retval)[:200]  # Limitar tamanho do log
            }
        )
        # Enviar notificação de sucesso via WebSocket
        notification_service.send_ws_message(
            user_id=kwargs.get('user_id'),
            message_type="book_generation_update",
            data={
                "task_id": task_id,
                "book_id": kwargs.get('book_id'),
                "status": "completed",
                "message": "Livro gerado com sucesso!",
                "progress": 100
            }
        )


async def _generate_book_content_async(
    book_id: int,
    user_id: int, # Adicionado user_id para notificações
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Lógica assíncrona para geração de conteúdo do livro.
    
    Args:
        book_id: ID do livro
        user_id: ID do usuário proprietário do livro para notificações
        progress_callback: Callback para reportar progresso
        
    Returns:
        Dict com resultado da geração
        
    Raises:
        BookNotFoundError: Se livro não for encontrado
        ExternalServiceError: Se serviço de IA falhar
    """
    async with get_async_session() as session:
        book_repo = BookRepository(session)
        user_repo = UserRepository(session) # Instantiate UserRepo
        
        try:
            # 1. Buscar livro e usuário
            book = await book_repo.get(book_id)
            if not book:
                raise BookNotFoundError(book_id)
            user = await user_repo.get(user_id) # Fetch User object
            if not user:
                logger.error(f"User {user_id} not found for book {book_id}. Cannot send notifications.")
                # Continue without user-specific notifications if user is missing
            
            if progress_callback:
                progress_callback({
                    "current": 1, 
                    "total": 5, 
                    "status": "Carregando livro",
                    "book_id": book_id,
                    "user_id": user_id
                })
            if user: # Only send WS if user is found
                notification_service.send_ws_message(
                    user_id=user_id,
                    message_type="book_generation_update",
                    data={
                        "book_id": book_id,
                        "status": "processing",
                        "progress": 20,
                        "message": "Iniciando geração do livro..."
                    }
                )
            
            # 2. Atualizar status para processamento
            await book_repo.update_status(book_id, "processing")
            await session.commit()
            
            if progress_callback:
                progress_callback({
                    "current": 2, 
                    "total": 5, 
                    "status": "Gerando história",
                    "book_id": book_id,
                    "user_id": user_id
                })
            if user: # Only send WS if user is found
                notification_service.send_ws_message(
                    user_id=user_id,
                    message_type="book_generation_update",
                    data={
                        "book_id": book_id,
                        "status": "processing",
                        "progress": 40,
                        "message": "Gerando história e conteúdo da página..."
                    }
                )
            
            # 3. Gerar história com IA
            ai_service = AIServiceFactory.create_ai_service()
            
            story_prompt = _build_story_prompt(book)
            story_text = await ai_service.generate_text(story_prompt)
            
            if progress_callback:
                progress_callback({
                    "current": 3, 
                    "total": 5, 
                    "status": "Processando páginas",
                    "book_id": book_id,
                    "user_id": user_id
                })
            if user: # Only send WS if user is found
                notification_service.send_ws_message(
                    user_id=user_id,
                    message_type="book_generation_update",
                    data={
                        "book_id": book_id,
                        "status": "processing",
                        "progress": 60,
                        "message": "Processando páginas e prompts de imagem..."
                    }
                )
            
            # 4. Processar e salvar páginas
            pages_data = _parse_story_into_pages(story_text, book.pages_count)
            
            if progress_callback:
                progress_callback({
                    "current": 4, 
                    "total": 5, 
                    "status": "Gerando imagens",
                    "book_id": book_id,
                    "user_id": user_id
                })
            if user: # Only send WS if user is found
                notification_service.send_ws_message(
                    user_id=user_id,
                    message_type="book_generation_update",
                    data={
                        "book_id": book_id,
                        "status": "processing",
                        "progress": 80,
                        "message": "Gerando imagens para cada página..."
                    }
                )
            
            # 5. Gerar imagens para cada página
            images_generated = 0
            total_pages = len(pages_data)
            
            from app.services.storage.factory import StorageServiceFactory
            storage_provider = StorageServiceFactory.create_storage()
            
            for page_idx, page_data in enumerate(pages_data):
                try:
                    image_prompt = _build_image_prompt(page_data["text"], book.style)
                    image_bytes = await ai_service.generate_image(image_prompt, book.style)
                    
                    # Salvar imagem usando Storage Service
                    import io
                    file_data = io.BytesIO(image_bytes)
                    filename = f"book_{book_id}_page_{page_idx+1}_{datetime.utcnow().timestamp()}.png"
                    image_url = await storage_provider.upload(file_data, filename, content_type="image/png")
                    
                    page_data["image_url"] = image_url
                    images_generated += 1
                    
                    # Notificação de progresso da imagem
                    if user: # Only send WS if user is found
                        await notification_service.send_ws_message(
                            user_id=user_id,
                            message_type="book_generation_update",
                            data={
                                "book_id": book_id,
                                "status": "processing",
                                "progress": 80 + (20 * (page_idx + 1) / total_pages), # Progress entre 80-100
                                "message": f"Gerando imagem para página {page_idx + 1} de {total_pages}",
                                "current_step": "generating_images"
                            }
                        )
                        
                except Exception as e:
                    logger.warning(f"Failed to generate image for page {page_idx + 1}: {e}")
                    page_data["image_url"] = None
                    if user: # Only send WS if user is found
                        await notification_service.send_ws_message(
                            user_id=user_id,
                            message_type="book_generation_update",
                            data={
                                "book_id": book_id,
                                "status": "processing",
                                "message": f"Falha ao gerar imagem para página {page_idx + 1}. Prosseguindo...",
                                "current_step": "generating_images_error"
                            }
                        )
            
            # 6. Salvar dados no banco
            await _save_book_pages(session, book_id, pages_data)
            
            # 7. Atualizar status final
            await book_repo.update_status(book_id, "completed")
            await session.commit()
            
            if progress_callback:
                progress_callback({
                    "current": 5, 
                    "total": 5, 
                    "status": "Concluído",
                    "book_id": book_id,
                    "user_id": user_id
                })
            if user: # Only send WS if user is found
                await notification_service.send_ws_message(
                    user_id=user_id,
                    message_type="book_generation_update",
                    data={
                        "book_id": book_id,
                        "status": "completed",
                        "progress": 100,
                        "message": "Livro gerado e pronto!"
                    }
                )
                await notification_service.notify_book_generation_completed(
                    user=user,
                    book_id=book_id,
                    task_id=self.request.id,
                    book_title=book.title
                )
            
            return {
                "status": "success",
                "book_id": book_id,
                "pages_generated": len(pages_data),
                "images_generated": images_generated,
                "message": f"Livro {book_id} gerado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Error generating book content for book {book_id}: {e}", exc_info=True)
            
            # Marcar livro como falhado
            try:
                await book_repo.update_status(book_id, "failed")
                await session.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update book status to failed for book {book_id}: {commit_error}")
            
            # Send failure notification
            if user: # Only send if user is found
                await notification_service.notify_book_generation_failed(
                    user=user,
                    book_id=book_id,
                    task_id=self.request.id,
                    book_title=book.title,
                    error_message=f"Falha na geração: {str(e)}"
                )
            
            # Re-lançar exceção apropriada
            if isinstance(e, (BookNotFoundError, ExternalServiceError)):
                raise
            else:
                raise ExternalServiceError(
                    message=f"Falha na geração do livro: {str(e)}",
                    service="book_generation",
                    original_error=e
                )


@celery_app.task(bind=True, base=BaseTask, max_retries=3, default_retry_delay=60)
def generate_book_content(self, book_id: int, user_id: int) -> Dict[str, Any]: # Adicionado user_id aqui
    """
    Task para gerar conteúdo completo do livro.
    
    Args:
        book_id: ID do livro para gerar
        user_id: ID do usuário proprietário do livro
        
    Returns:
        Dict com resultado da operação
    """
    try:
        # Callback para reportar progresso
        def progress_callback(progress_info: Dict[str, Any]):
            self.update_state(
                state="PROGRESS",
                meta=progress_info
            )
        
        # Executar geração assíncrona
        result = sync_run_async_task(_generate_book_content_async, book_id, user_id, progress_callback)
        
        # Enviar notificação final se a task não falhou antes
        if self.request.state != "FAILED":
            notification_service.send_ws_message(
                user_id=user_id,
                message_type="book_generation_update",
                data={
                    "book_id": book_id,
                    "task_id": self.request.id,
                    "status": "completed",
                    "progress": 100,
                    "message": "Geração do livro finalizada!"
                }
            )
        return result
        
    except (BookNotFoundError, ExternalServiceError) as e:
        # Erros que não devem ser retentados
        logger.error(f"Non-retryable error in book generation: {e}")
        # A notificação de falha já foi enviada no on_failure da BaseTask
        raise
        
    except Exception as e:
        # Outros erros podem ser retentados
        logger.error(f"Retryable error in book generation: {e}")
        try:
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for book {book_id}")
            # A notificação de falha já foi enviada no on_failure da BaseTask
            raise ExternalServiceError(
                message="Falha na geração após múltiplas tentativas",
                service="book_generation",
                original_error=e
            )


@celery_app.task(bind=True, base=BaseTask, max_retries=2)
def generate_book_pdf(self, book_id: int, user_id: int) -> Dict[str, Any]:
    """
    Task para gerar PDF do livro.
    
    Args:
        book_id: ID do livro
        user_id: ID do usuário proprietário do livro
        
    Returns:
        Dict com resultado da geração de PDF
    """
    async def _generate_book_pdf_wrapper():
        async with get_async_session() as session:
            user_repo = UserRepository(session)
            book_repo = BookRepository(session)
            
            book = await book_repo.get(book_id)
            user = await user_repo.get(user_id)
            
            if not book:
                raise BookNotFoundError(book_id)
            if not user:
                logger.error(f"User {user_id} not found for book {book_id}. Cannot send PDF notifications.")
                # Decide here if to proceed without user or raise. For now, proceed.

            pdf_path = None
            try:
                pdf_path = await _generate_book_pdf_async(book_id) # This now returns pdf path
                
                if user:
                    # WebSocket message for general update
                    await notification_service.send_ws_message(
                        user_id=user_id,
                        message_type="book_pdf_generation_update",
                        data={
                            "book_id": book_id,
                            "task_id": self.request.id,
                            "status": "completed",
                            "message": "PDF do livro gerado com sucesso!",
                            "pdf_path": pdf_path
                        }
                    )
                    # Email notification for completion
                    await notification_service.notify_pdf_generation_completed(
                        user=user,
                        book_id=book_id,
                        book_title=book.title,
                        pdf_url=pdf_path
                    )
                return {"status": "success", "pdf_path": pdf_path}
            except Exception as e:
                logger.error(f"Error in PDF generation for book {book_id}: {e}", exc_info=True)
                if user:
                    # WebSocket message for failure
                    await notification_service.send_ws_message(
                        user_id=user_id,
                        message_type="book_pdf_generation_update",
                        data={
                            "book_id": book_id,
                            "task_id": self.request.id,
                            "status": "failed",
                            "message": f"Falha ao gerar PDF: {str(e)}"
                        }
                    )
                    # Email notification for failure
                    # Since notify_pdf_generation_completed implies success, we'll send a direct email here for failure
                    await notification_service._send_email_notification(
                        to_email=user.email,
                        subject=f"Falha na Geração do PDF do Livro '{book.title}'",
                        body_html=f"""
                        <p>Olá {user.full_name},</p>
                        <p>Houve um problema ao gerar o PDF do seu livro <b>'{book.title}'</b>.</p>
                        <p>Mensagem de erro: {str(e)}</p>
                        <p>Por favor, tente novamente mais tarde ou entre em contato com o suporte.</p>
                        <p>Atenciosamente,</p>
                        <p>Equipe Fábrica de Livros</p>
                        """
                    )
                raise # Re-raise to trigger retry/failure handling
    
    try:
        return sync_run_async_task(_generate_book_pdf_wrapper)
        
    except Exception as e:
        logger.error(f"Error in PDF generation: {e}")
        try:
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            raise ExternalServiceError(
                message="Falha na geração de PDF após múltiplas tentativas",
                service="pdf_generation",
                original_error=e
            )


@celery_app.task(bind=True, base=BaseTask)
def cleanup_failed_books(self) -> Dict[str, int]:
    """
    Task periódica para limpeza de livros com falha há muito tempo.
    
    Returns:
        Dict com estatísticas da limpeza
    """
    async def _cleanup_async():
        async with get_async_session() as session:
            book_repo = BookRepository(session)
            from app.models.book import Book # Import Book model here for filtering
            from datetime import timedelta
            
            # Use the StorageService to delete files
            from app.services.storage.factory import StorageServiceFactory
            storage_provider = StorageServiceFactory.create_storage()

            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Query for books with status 'failed' that are older than cutoff_time
            # Assuming BookRepository has a method to get books by status and created_at
            # Or we can use SQLAlchemy directly for a more complex query
            failed_books_query = await session.execute(
                select(Book).where(
                    Book.status == "failed",
                    Book.created_at < cutoff_time
                )
            )
            failed_books = failed_books_query.scalars().all()
            
            cleaned_count = 0
            for book in failed_books:
                # Delete associated image files (if any and if we have page details)
                # This assumes pages are still linked to the book for their image_url
                # For simplicity, we'll try to delete book's cover_image and pdf_file directly.
                # A more robust solution would iterate through pages if they were still available.
                
                if book.cover_image:
                    await storage_provider.delete(book.cover_image)
                if book.pdf_file:
                    await storage_provider.delete(book.pdf_file)
                
                # Delete the book record itself
                await book_repo.delete(book.id)
                cleaned_count += 1
                logger.info(f"Cleaned up failed book {book.id} (title: {book.title})")
            
            await session.commit()
            
            logger.info(f"Cleanup task executed. Cleaned {cleaned_count} failed books.")
            
            return {"cleaned": cleaned_count, "checked": len(failed_books)}
    
    try:
        result = sync_run_async_task(_cleanup_async)
        logger.info(f"Cleanup completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        raise


@celery_app.task(bind=True, base=BaseTask)
def health_check(self) -> Dict[str, Any]:
    """
    Task de health check para monitoramento.
    
    Returns:
        Status do worker
    """
    import time
    start_time = time.time()
    
    # Test básico de funcionamento
    test_data = {"timestamp": datetime.utcnow().isoformat(), "worker_id": self.request.id}
    
    processing_time = time.time() - start_time
    
    return {
        "status": "healthy",
        "processing_time_ms": round(processing_time * 1000, 2),
        "test_data": test_data
    }
