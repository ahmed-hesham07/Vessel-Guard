"""
Background task service for Vessel Guard application.

Handles asynchronous tasks like report generation, email notifications,
data export, and other long-running operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from celery import Celery
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.email import get_email_service
from app.services.file_storage import get_file_storage_service
from app.crud.report import report_crud
from app.crud.inspection import inspection_crud
from app.crud.user import user_crud
from app.schemas.report import ReportUpdate
from app.core.config import settings


logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Configure Celery for background tasks
celery_app = Celery(
    "vessel_guard",
    broker=getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=getattr(settings, 'CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_compression='gzip',
    result_compression='gzip'
)


class BackgroundTaskService:
    """Service for managing background tasks."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
    
    def schedule_task(
        self,
        task_name: str,
        task_func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: int = 0,
        retry_count: int = 3
    ) -> str:
        """
        Schedule a background task for execution.
        
        Args:
            task_name: Name of the task
            task_func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            priority: Task priority
            delay_seconds: Delay before execution
            retry_count: Number of retries on failure
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        kwargs = kwargs or {}
        
        # Store task information
        self.active_tasks[task_id] = {
            "task_name": task_name,
            "status": TaskStatus.PENDING,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "priority": priority,
            "retry_count": retry_count,
            "current_retry": 0,
            "result": None,
            "error": None
        }
        
        # Schedule task execution
        if delay_seconds > 0:
            # Use Celery for delayed tasks
            task_func.apply_async(
                args=args,
                kwargs=kwargs,
                task_id=task_id,
                countdown=delay_seconds
            )
        else:
            # Use thread pool for immediate execution
            future = self.executor.submit(self._execute_task, task_id, task_func, args, kwargs)
        
        logger.info(f"Task scheduled: {task_name} (ID: {task_id})")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a background task."""
        return self.active_tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        if task_id in self.active_tasks:
            task_info = self.active_tasks[task_id]
            if task_info["status"] in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                # Try to cancel with Celery
                celery_app.control.revoke(task_id, terminate=True)
                task_info["status"] = TaskStatus.FAILURE
                task_info["error"] = "Task cancelled by user"
                task_info["completed_at"] = datetime.utcnow()
                return True
        return False
    
    def _execute_task(
        self,
        task_id: str,
        task_func: Callable,
        args: tuple,
        kwargs: Dict[str, Any]
    ) -> None:
        """Execute a task and update its status."""
        task_info = self.active_tasks[task_id]
        
        try:
            task_info["status"] = TaskStatus.RUNNING
            task_info["started_at"] = datetime.utcnow()
            
            # Execute the task
            result = task_func(*args, **kwargs)
            
            # Update task status
            task_info["status"] = TaskStatus.SUCCESS
            task_info["result"] = result
            task_info["completed_at"] = datetime.utcnow()
            
            logger.info(f"Task completed successfully: {task_id}")
            
        except Exception as e:
            logger.error(f"Task failed: {task_id}, Error: {e}")
            
            task_info["error"] = str(e)
            task_info["current_retry"] += 1
            
            # Retry logic
            if task_info["current_retry"] < task_info["retry_count"]:
                task_info["status"] = TaskStatus.RETRY
                # Schedule retry with exponential backoff
                delay = 2 ** task_info["current_retry"] * 60  # 2, 4, 8 minutes
                asyncio.create_task(self._retry_task(task_id, task_func, args, kwargs, delay))
            else:
                task_info["status"] = TaskStatus.FAILURE
                task_info["completed_at"] = datetime.utcnow()
    
    async def _retry_task(
        self,
        task_id: str,
        task_func: Callable,
        args: tuple,
        kwargs: Dict[str, Any],
        delay: int
    ) -> None:
        """Retry a failed task after a delay."""
        await asyncio.sleep(delay)
        
        if task_id in self.active_tasks:
            task_info = self.active_tasks[task_id]
            if task_info["status"] == TaskStatus.RETRY:
                logger.info(f"Retrying task: {task_id} (attempt {task_info['current_retry']})")
                future = self.executor.submit(self._execute_task, task_id, task_func, args, kwargs)


# Celery tasks
@celery_app.task(bind=True)
def generate_report_task(self, report_id: str, organization_id: str):
    """Generate a report in the background."""
    try:
        db = SessionLocal()
        
        # Update report status to processing
        report = report_crud.get_by_id(db, id=report_id, organization_id=organization_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        report_crud.update(
            db=db,
            db_obj=report,
            obj_in=ReportUpdate(status="processing")
        )
        db.commit()
        
        # Generate report content (this would be implemented based on report type)
        report_content = _generate_report_content(report, db)
        
        # Save report file
        file_storage = get_file_storage_service()
        file_path = file_storage.get_file_path(
            f"report_{report_id}.pdf",
            organization_id,
            "reports"
        )
        
        # Save the generated content to file
        with open(file_path, "wb") as f:
            f.write(report_content)
        
        # Update report status to completed
        report_crud.update(
            db=db,
            db_obj=report,
            obj_in=ReportUpdate(
                status="completed",
                file_path=str(file_path),
                generated_at=datetime.utcnow()
            )
        )
        db.commit()
        
        # Send notification email
        email_service = get_email_service()
        user = user_crud.get(db, id=report.created_by)
        if user and user.email:
            email_service.send_report_ready_notification(
                recipients=[{"email": user.email, "name": user.full_name}],
                report_data={
                    "title": report.title,
                    "report_type": report.report_type,
                    "generated_by": user.full_name,
                    "generated_at": report.generated_at,
                    "download_url": f"/api/v1/reports/{report_id}/download"
                }
            )
        
        db.close()
        return {"status": "success", "report_id": report_id}
        
    except Exception as e:
        db = SessionLocal()
        try:
            report = report_crud.get_by_id(db, id=report_id, organization_id=organization_id)
            if report:
                report_crud.update(
                    db=db,
                    db_obj=report,
                    obj_in=ReportUpdate(status="failed", error_message=str(e))
                )
                db.commit()
        except:
            pass
        finally:
            db.close()
        
        logger.error(f"Report generation failed: {e}")
        raise


@celery_app.task
def send_inspection_reminders():
    """Send inspection reminder emails for upcoming inspections."""
    try:
        db = SessionLocal()
        
        # Get inspections due in the next 7 days
        upcoming_date = datetime.utcnow() + timedelta(days=7)
        upcoming_inspections = inspection_crud.get_upcoming_inspections(
            db=db,
            due_before=upcoming_date
        )
        
        email_service = get_email_service()
        
        for inspection in upcoming_inspections:
            # Get vessel and user information
            vessel = inspection.vessel
            user = user_crud.get(db, id=inspection.assigned_to)
            
            if user and user.email:
                email_service.send_inspection_reminder(
                    recipients=[{"email": user.email, "name": user.full_name}],
                    inspection_data={
                        "vessel_name": vessel.name if vessel else "Unknown",
                        "inspection_type": inspection.inspection_type,
                        "due_date": inspection.scheduled_date,
                        "inspector": user.full_name,
                        "location": vessel.location if vessel else "Unknown",
                        "notes": inspection.notes
                    }
                )
        
        db.close()
        return {"status": "success", "reminders_sent": len(upcoming_inspections)}
        
    except Exception as e:
        logger.error(f"Failed to send inspection reminders: {e}")
        raise


@celery_app.task
def cleanup_old_files():
    """Clean up old temporary files and reports."""
    try:
        file_storage = get_file_storage_service()
        
        # Clean up files older than 30 days in temp directory
        # This would be implemented based on your cleanup policy
        
        return {"status": "success", "message": "Cleanup completed"}
        
    except Exception as e:
        logger.error(f"File cleanup failed: {e}")
        raise


@celery_app.task
def export_data_task(user_id: str, organization_id: str, export_params: Dict[str, Any]):
    """Export data to various formats (CSV, Excel, PDF)."""
    try:
        db = SessionLocal()
        
        # Generate export based on parameters
        export_content = _generate_data_export(export_params, db, organization_id)
        
        # Save export file
        file_storage = get_file_storage_service()
        export_filename = f"export_{uuid.uuid4()}.{export_params.get('format', 'csv')}"
        file_path = file_storage.get_file_path(
            export_filename,
            organization_id,
            "exports"
        )
        
        with open(file_path, "wb") as f:
            f.write(export_content)
        
        # Send notification to user
        user = user_crud.get(db, id=user_id)
        if user and user.email:
            email_service = get_email_service()
            email_service.send_email(
                recipients=[{"email": user.email, "name": user.full_name}],
                subject="Data Export Ready",
                body_text=f"Your data export is ready for download: {export_filename}",
                body_html=f"<p>Your data export is ready for download: <strong>{export_filename}</strong></p>"
            )
        
        db.close()
        return {"status": "success", "export_file": export_filename}
        
    except Exception as e:
        logger.error(f"Data export failed: {e}")
        raise


def _generate_report_content(report, db: Session) -> bytes:
    """Generate report content based on report type."""
    # This is a placeholder implementation
    # In practice, this would generate PDF reports using libraries like reportlab
    content = f"Report: {report.title}\nGenerated at: {datetime.utcnow()}\n"
    return content.encode('utf-8')


def _generate_data_export(export_params: Dict[str, Any], db: Session, organization_id: str) -> bytes:
    """Generate data export in specified format."""
    # This is a placeholder implementation
    # In practice, this would query data and generate CSV/Excel/PDF files
    content = "Export data placeholder\n"
    return content.encode('utf-8')


# Global background task service instance
background_task_service = BackgroundTaskService()


def get_background_task_service() -> BackgroundTaskService:
    """Get background task service instance."""
    return background_task_service
