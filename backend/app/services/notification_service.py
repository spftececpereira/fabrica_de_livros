"""
Notification Service for managing real-time notifications
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.services.email_service import email_service # Import the email service
from app.models.user import User # Import User model to get email address

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class NotificationService:
    """Service for handling application notifications"""
    
    def __init__(self):
        self.connection_manager = None  # Will be set from websocket module
    
    def set_connection_manager(self, manager):
        """Set the WebSocket connection manager"""
        self.connection_manager = manager
    
    async def _send_websocket_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType,
        action_url: Optional[str] = None
    ):
        """Helper to send a generic WebSocket notification."""
        if self.connection_manager:
            await self.connection_manager.send_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                action_url=action_url
            )

    async def _send_email_notification(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_plain: Optional[str] = None,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """Helper to send an email notification."""
        if not email_service.email_enabled:
            logger.info(f"Email service disabled. Not sending email to {to_email}.")
            return False
        
        # Prefer HTML body, fallback to plain
        body = body_html if body_html else body_plain
        
        return await email_service.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            subtype="html" if body_html else "plain",
            attachments=attachments
        )
            
    async def notify_book_generation_started(
        self, 
        user: User, # Changed to User object to get email
        book_id: int, 
        task_id: str,
        book_title: str
    ):
        """Notify user that book generation has started"""
        # Send WebSocket Notification
        await self._send_websocket_notification(
            user_id=user.id,
            title="Geração Iniciada",
            message=f"A geração do livro '{book_title}' foi iniciada!",
            notification_type=NotificationType.INFO
        )
        
        # Send WebSocket Book Update
        if self.connection_manager:
            await self.connection_manager.send_book_generation_update(
                user_id=user.id,
                book_id=book_id,
                task_id=task_id,
                status="processing",
                progress=0,
                message=f"Iniciando geração do livro '{book_title}'...",
                current_step="Preparando geração"
            )
        
        # Send Email Notification (Optional, maybe for critical steps or as a summary)
        # Not sending email for start for now to avoid spam.
    
    async def notify_book_generation_progress(
        self,
        user_id: int,
        book_id: int,
        task_id: str,
        progress: int,
        current_step: str,
        message: str = None
    ):
        """Notify user of book generation progress"""
        if self.connection_manager:
            await self.connection_manager.send_book_generation_update(
                user_id=user_id,
                book_id=book_id,
                task_id=task_id,
                status="processing",
                progress=progress,
                message=message or f"Progresso: {progress}%",
                current_step=current_step
            )
    
    async def notify_book_generation_completed(
        self,
        user: User, # Changed to User object to get email
        book_id: int,
        task_id: str,
        book_title: str,
        pdf_url: Optional[str] = None
    ):
        """Notify user that book generation is complete"""
        # Send WebSocket Notification
        await self._send_websocket_notification(
            user_id=user.id,
            title="Livro Concluído! 🎉",
            message=f"Seu livro '{book_title}' está pronto para leitura e download!",
            notification_type=NotificationType.SUCCESS,
            action_url=f"/dashboard/books/{book_id}"
        )
        
        # Send WebSocket Book Update
        if self.connection_manager:
            await self.connection_manager.send_book_generation_update(
                user_id=user.id,
                book_id=book_id,
                task_id=task_id,
                status="completed",
                progress=100,
                message=f"Livro '{book_title}' gerado com sucesso!",
                current_step="Concluído"
            )
            
        # Send Email Notification
        subject = f"Seu Livro '{book_title}' Está Pronto!"
        body_html = f"""
        <p>Olá {user.full_name},</p>
        <p>Seu livro <b>'{book_title}'</b> foi gerado com sucesso e está pronto!</p>
        <p>Você pode visualizá-lo e fazer o download <a href="{settings.FRONTEND_URL}/dashboard/books/{book_id}">aqui</a>.</p>
        <p>Aproveite a leitura!</p>
        <p>Atenciosamente,</p>
        <p>Equipe Fábrica de Livros</p>
        """
        await self._send_email_notification(user.email, subject, body_html)
    
    async def notify_book_generation_failed(
        self,
        user: User, # Changed to User object to get email
        book_id: int,
        task_id: str,
        book_title: str,
        error_message: str = None
    ):
        """Notify user that book generation failed"""
        # Send WebSocket Notification
        await self._send_websocket_notification(
            user_id=user.id,
            title="Erro na Geração",
            message=error_message or f"Houve um problema ao gerar o livro '{book_title}'. Tente novamente.",
            notification_type=NotificationType.ERROR,
            action_url=f"/dashboard/books/{book_id}"
        )
        
        # Send WebSocket Book Update
        if self.connection_manager:
            await self.connection_manager.send_book_generation_update(
                user_id=user.id,
                book_id=book_id,
                task_id=task_id,
                status="failed",
                progress=0,
                message=error_message or f"Falha na geração do livro '{book_title}'",
                current_step="Erro"
            )
        
        # Send Email Notification
        subject = f"Falha na Geração do Livro '{book_title}'"
        body_html = f"""
        <p>Olá {user.full_name},</p>
        <p>Houve um problema ao gerar o seu livro <b>'{book_title}'</b>.</p>
        <p>Mensagem de erro: {error_message or 'Erro desconhecido.'}</p>
        <p>Por favor, tente novamente mais tarde ou entre em contato com o suporte.</p>
        <p>Atenciosamente,</p>
        <p>Equipe Fábrica de Livros</p>
        """
        await self._send_email_notification(user.email, subject, body_html)
    
    async def notify_pdf_generation_completed(
        self,
        user: User, # Changed to User object to get email
        book_id: int,
        book_title: str,
        pdf_url: str
    ):
        """Notify user that PDF generation is complete"""
        # Send WebSocket Notification
        await self._send_websocket_notification(
            user_id=user.id,
            title="PDF Pronto! 📄",
            message=f"O PDF do livro '{book_title}' foi gerado e está pronto para download!",
            notification_type=NotificationType.SUCCESS,
            action_url=f"/dashboard/books/{book_id}"
        )
        
        # Send Email Notification (with PDF attachment placeholder)
        subject = f"PDF do seu Livro '{book_title}' está pronto!"
        body_html = f"""
        <p>Olá {user.full_name},</p>
        <p>O PDF do seu livro <b>'{book_title}'</b> foi gerado com sucesso!</p>
        <p>Você pode fazer o download <a href="{settings.FRONTEND_URL}{pdf_url}">aqui</a>.</p>
        <p>Atenciosamente,</p>
        <p>Equipe Fábrica de Livros</p>
        """
        # NOTE: For now, we're sending a link. Attaching the PDF would require
        # fetching its content here, which might be too heavy for NotificationService.
        # This will be a follow-up if needed.
        await self._send_email_notification(user.email, subject, body_html)
    
    async def notify_book_limit_reached(self, user_id: int, current_plan: str):
        """Notify user they've reached their book limit"""
        await self._send_websocket_notification(
            user_id=user_id,
            title="Limite Atingido",
            message="Você atingiu o limite de livros do seu plano atual." + (
                " Faça upgrade para Premium e crie livros ilimitados!" if current_plan == "free" else ""
            ),
            notification_type=NotificationType.WARNING,
            action_url="/dashboard/upgrade" if current_plan == "free" else None
        )
    
    async def notify_new_badge_earned(
        self,
        user_id: int,
        badge_name: str,
        badge_description: str
    ):
        """Notify user they earned a new badge"""
        await self._send_websocket_notification(
            user_id=user_id,
            title="Nova Conquista! 🏆",
            message=f"Parabéns! Você conquistou o badge '{badge_name}': {badge_description}",
            notification_type=NotificationType.SUCCESS,
            action_url="/dashboard/achievements"
        )
    
    async def notify_system_maintenance(
        self,
        message: str,
        scheduled_time: Optional[datetime] = None
    ):
        """Send system-wide maintenance notification"""
        if self.connection_manager:
            maintenance_message = message
            if scheduled_time:
                maintenance_message += f" Agendada para {scheduled_time.strftime('%d/%m/%Y às %H:%M')}"
            
            await self.connection_manager.broadcast_to_all({
                "type": "system_notification",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "id": f"maintenance_{datetime.now().timestamp()}",
                    "title": "Manutenção Programada",
                    "message": maintenance_message,
                    "type": NotificationType.WARNING,
                    "scheduled_time": scheduled_time.isoformat() if scheduled_time else None
                }
            })
    
    async def notify_welcome_new_user(self, user: User): # Changed to User object
        """Send welcome notification to new user"""
        # Send WebSocket Notification
        await self._send_websocket_notification(
            user_id=user.id,
            title=f"Bem-vindo, {user.full_name or user.email}! 👋",
            message="Seja bem-vindo à Fábrica de Livros! Comece criando seu primeiro livro personalizado.",
            notification_type=NotificationType.INFO,
            action_url="/dashboard/books/create"
        )
        
        # Send Email Notification
        subject = "Bem-vindo à Fábrica de Livros!"
        body_html = f"""
        <p>Olá {user.full_name or user.email},</p>
        <p>Seja muito bem-vindo à nossa plataforma! Estamos empolgados para que você comece a criar livros infantis incríveis com a ajuda da IA.</p>
        <p>Comece sua jornada <a href="{settings.FRONTEND_URL}/dashboard/books/create">aqui</a>.</p>
        <p>Se precisar de ajuda, entre em contato.</p>
        <p>Atenciosamente,</p>
        <p>Equipe Fábrica de Livros</p>
        """
        await self._send_email_notification(user.email, subject, body_html)
        
    async def notify_password_reset(self, user: User, reset_token: str): # New method for password reset
        """Send password reset email to user"""
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        subject = "Redefinição de Senha para Fábrica de Livros"
        body_html = f"""
        <p>Olá {user.full_name or user.email},</p>
        <p>Recebemos uma solicitação para redefinir sua senha na Fábrica de Livros.</p>
        <p>Clique no link abaixo para redefinir sua senha:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>Este link expirará em {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutos.</p>
        <p>Se você não solicitou a redefinição de senha, por favor, ignore este email.</p>
        <p>Atenciosamente,</p>
        <p>Equipe Fábrica de Livros</p>
        """
        await self._send_email_notification(user.email, subject, body_html)


# Global instance
notification_service = NotificationService()