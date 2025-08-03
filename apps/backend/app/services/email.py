"""
Email notification service for Vessel Guard application.

Provides email notifications for various events like inspection
reminders, report generation completion, system alerts, etc.
"""

import smtplib
import ssl
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, Template
from pydantic import BaseModel, EmailStr

from app.core.config import settings


logger = logging.getLogger(__name__)


class EmailRecipient(BaseModel):
    """Email recipient model."""
    email: EmailStr
    name: Optional[str] = None


class EmailAttachment(BaseModel):
    """Email attachment model."""
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


class EmailTemplate(BaseModel):
    """Email template model."""
    subject: str
    body_text: str
    body_html: Optional[str] = None


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.smtp_use_tls = getattr(settings, 'SMTP_USE_TLS', True)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@vessel-guard.com')
        self.from_name = getattr(settings, 'FROM_NAME', 'Vessel Guard')
        
        # Initialize Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        if template_dir.exists():
            self.template_env = Environment(loader=FileSystemLoader(str(template_dir)))
        else:
            self.template_env = None
            logger.warning(f"Email template directory not found: {template_dir}")
    
    def send_email(
        self,
        recipients: List[EmailRecipient],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        attachments: Optional[List[EmailAttachment]] = None,
        cc_recipients: Optional[List[EmailRecipient]] = None,
        bcc_recipients: Optional[List[EmailRecipient]] = None
    ) -> bool:
        """
        Send an email to specified recipients.
        
        Args:
            recipients: List of email recipients
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body (optional)
            attachments: List of attachments (optional)
            cc_recipients: CC recipients (optional)
            bcc_recipients: BCC recipients (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MimeMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = ", ".join([f"{r.name} <{r.email}>" if r.name else str(r.email) for r in recipients])
            
            if cc_recipients:
                msg["Cc"] = ", ".join([f"{r.name} <{r.email}>" if r.name else str(r.email) for r in cc_recipients])
            
            # Add text part
            text_part = MimeText(body_text, "plain")
            msg.attach(text_part)
            
            # Add HTML part if provided
            if body_html:
                html_part = MimeText(body_html, "html")
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    part = MimeBase("application", "octet-stream")
                    part.set_payload(attachment.content)
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment.filename}"
                    )
                    msg.attach(part)
            
            # Combine all recipients
            all_recipients = [r.email for r in recipients]
            if cc_recipients:
                all_recipients.extend([r.email for r in cc_recipients])
            if bcc_recipients:
                all_recipients.extend([r.email for r in bcc_recipients])
            
            # Send email
            if self.smtp_use_tls:
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=context)
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.from_email, all_recipients, msg.as_string())
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.from_email, all_recipients, msg.as_string())
            
            logger.info(f"Email sent successfully to {len(all_recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_template_email(
        self,
        recipients: List[EmailRecipient],
        template_name: str,
        template_data: Dict[str, Any],
        attachments: Optional[List[EmailAttachment]] = None
    ) -> bool:
        """
        Send an email using a template.
        
        Args:
            recipients: List of email recipients
            template_name: Name of the email template
            template_data: Data to populate the template
            attachments: List of attachments (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.template_env:
            logger.error("Template environment not initialized")
            return False
        
        try:
            # Load template
            template = self.template_env.get_template(f"{template_name}.html")
            body_html = template.render(**template_data)
            
            # Try to load text version
            try:
                text_template = self.template_env.get_template(f"{template_name}.txt")
                body_text = text_template.render(**template_data)
            except:
                # Fallback to plain text version of HTML
                body_text = self._html_to_text(body_html)
            
            # Extract subject from template data or use default
            subject = template_data.get("subject", "Vessel Guard Notification")
            
            return self.send_email(
                recipients=recipients,
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                attachments=attachments
            )
            
        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            return False
    
    def send_inspection_reminder(
        self,
        recipients: List[EmailRecipient],
        inspection_data: Dict[str, Any]
    ) -> bool:
        """Send inspection reminder notification."""
        template_data = {
            "subject": f"Inspection Reminder: {inspection_data.get('vessel_name', 'Vessel')}",
            "vessel_name": inspection_data.get("vessel_name"),
            "inspection_type": inspection_data.get("inspection_type"),
            "due_date": inspection_data.get("due_date"),
            "inspector": inspection_data.get("inspector"),
            "location": inspection_data.get("location"),
            "notes": inspection_data.get("notes"),
            "dashboard_url": f"{getattr(settings, 'FRONTEND_URL', '')}/inspections"
        }
        
        return self.send_template_email(
            recipients=recipients,
            template_name="inspection_reminder",
            template_data=template_data
        )
    
    def send_report_ready_notification(
        self,
        recipients: List[EmailRecipient],
        report_data: Dict[str, Any],
        report_file: Optional[bytes] = None
    ) -> bool:
        """Send notification when report is ready for download."""
        template_data = {
            "subject": f"Report Ready: {report_data.get('title', 'Engineering Report')}",
            "report_title": report_data.get("title"),
            "report_type": report_data.get("report_type"),
            "generated_by": report_data.get("generated_by"),
            "generated_at": report_data.get("generated_at"),
            "download_url": report_data.get("download_url"),
            "dashboard_url": f"{getattr(settings, 'FRONTEND_URL', '')}/reports"
        }
        
        attachments = None
        if report_file and report_data.get("filename"):
            attachments = [EmailAttachment(
                filename=report_data["filename"],
                content=report_file,
                content_type="application/pdf"
            )]
        
        return self.send_template_email(
            recipients=recipients,
            template_name="report_ready",
            template_data=template_data,
            attachments=attachments
        )
    
    def send_overdue_inspection_alert(
        self,
        recipients: List[EmailRecipient],
        overdue_inspections: List[Dict[str, Any]]
    ) -> bool:
        """Send alert for overdue inspections."""
        template_data = {
            "subject": f"URGENT: {len(overdue_inspections)} Overdue Inspections",
            "overdue_count": len(overdue_inspections),
            "inspections": overdue_inspections,
            "dashboard_url": f"{getattr(settings, 'FRONTEND_URL', '')}/inspections?filter=overdue"
        }
        
        return self.send_template_email(
            recipients=recipients,
            template_name="overdue_inspections",
            template_data=template_data
        )
    
    def send_calculation_completion_notification(
        self,
        recipients: List[EmailRecipient],
        calculation_data: Dict[str, Any]
    ) -> bool:
        """Send notification when calculation is completed."""
        template_data = {
            "subject": f"Calculation Complete: {calculation_data.get('calculation_type', 'Engineering Calculation')}",
            "calculation_type": calculation_data.get("calculation_type"),
            "vessel_name": calculation_data.get("vessel_name"),
            "calculated_by": calculation_data.get("calculated_by"),
            "completion_time": calculation_data.get("completion_time"),
            "results_summary": calculation_data.get("results_summary"),
            "dashboard_url": f"{getattr(settings, 'FRONTEND_URL', '')}/calculations"
        }
        
        return self.send_template_email(
            recipients=recipients,
            template_name="calculation_complete",
            template_data=template_data
        )
    
    def send_inspection_report_notification(
        self,
        recipients: List[EmailRecipient],
        inspection_data: Dict[str, Any]
    ) -> bool:
        """Send notification when inspection report is generated."""
        template_data = {
            "subject": f"Technical Inspection Report Ready: {inspection_data.get('inspection_number', 'Inspection')}",
            "inspection_number": inspection_data.get("inspection_number"),
            "inspection_type": inspection_data.get("inspection_type"),
            "vessel_tag": inspection_data.get("vessel_tag"),
            "vessel_name": inspection_data.get("vessel_name"),
            "inspector_name": inspection_data.get("inspector_name"),
            "report_title": inspection_data.get("report_title"),
            "report_download_url": inspection_data.get("report_download_url"),
            "generated_at": inspection_data.get("generated_at"),
            "dashboard_url": f"{getattr(settings, 'FRONTEND_URL', '')}/reports"
        }
        
        return self.send_template_email(
            recipients=recipients,
            template_name="inspection_report_ready",
            template_data=template_data
        )
    
    def send_welcome_email(
        self,
        recipient: EmailRecipient,
        user_data: Dict[str, Any]
    ) -> bool:
        """Send welcome email to new user."""
        template_data = {
            "subject": "Welcome to Vessel Guard",
            "user_name": user_data.get("full_name", recipient.name),
            "organization_name": user_data.get("organization_name"),
            "login_url": f"{getattr(settings, 'FRONTEND_URL', '')}/login",
            "dashboard_url": f"{getattr(settings, 'FRONTEND_URL', '')}/dashboard",
            "support_email": getattr(settings, 'SUPPORT_EMAIL', 'support@vessel-guard.com')
        }
        
        return self.send_template_email(
            recipients=[recipient],
            template_name="welcome",
            template_data=template_data
        )
    
    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text (basic implementation)."""
        # This is a basic implementation. For production,
        # consider using libraries like html2text or BeautifulSoup
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text


# Global email service instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get email service instance."""
    return email_service
