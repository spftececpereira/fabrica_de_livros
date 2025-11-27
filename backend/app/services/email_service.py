import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.email_enabled = settings.EMAIL_ENABLED

        # Basic validation for essential settings if email is enabled
        if self.email_enabled and not all([self.smtp_host, self.smtp_username, self.smtp_password]):
            logger.warning("Email service is enabled but SMTP credentials are incomplete. Emails will not be sent.")
            self.email_enabled = False

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        subtype: str = "plain", # "plain" or "html"
        attachments: Optional[List[dict]] = None # [{"filename": "...", "content": b"...", "mimetype": "..."}]
    ) -> bool:
        if not self.email_enabled:
            logger.info(f"Email service disabled. Not sending email to {to_email} with subject '{subject}'.")
            return False

        msg = MIMEMultipart()
        msg["From"] = self.smtp_username
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, subtype))

        if attachments:
            for attachment in attachments:
                part = MIMEApplication(attachment["content"], Name=attachment["filename"])
                part["Content-Disposition"] = f'attachment; filename="{attachment["filename"]}"'
                msg.attach(part)

        try:
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.smtp_use_tls,
                username=self.smtp_username,
                password=self.smtp_password,
                timeout=settings.EMAIL_TIMEOUT_SECONDS # Assuming EMAIL_TIMEOUT_SECONDS exists in settings
            ) as client:
                await client.login()
                await client.send_message(msg)
            logger.info(f"Email sent successfully to {to_email} with subject '{subject}'.")
            return True
        except aiosmtplib.SMTPException as e:
            logger.error(f"Failed to send email to {to_email} with subject '{subject}': {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending email to {to_email}: {e}")
            return False

# Global instance
email_service = EmailService()
