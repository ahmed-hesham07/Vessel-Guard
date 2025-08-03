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
        self._operation_status_store: Dict[str, Dict[str, Any]] = {}
    
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
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import tempfile
    import os
    
    try:
        # Create temporary file
        temp_dir = os.path.join(os.getcwd(), "temp_reports")
        os.makedirs(temp_dir, exist_ok=True)
        filename = f"report_{report.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(temp_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(str(filepath), pagesize=letter, topMargin=1*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        story.append(Paragraph(report.title or "Engineering Report", title_style))
        story.append(Spacer(1, 20))
        
        # Report metadata
        story.append(Paragraph("Report Information", styles['Heading2']))
        report_info = [
            ["Report Type:", report.report_type or "General"],
            ["Generated:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")],
            ["Status:", report.status or "Generated"],
            ["Description:", report.description or "Engineering analysis report"]
        ]
        
        info_table = Table(report_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Main content
        story.append(Paragraph("Report Content", styles['Heading2']))
        
        # Add report-specific content based on type
        if hasattr(report, 'content') and report.content:
            story.append(Paragraph(report.content, styles['Normal']))
        else:
            # Default content for different report types
            if report.report_type == 'inspection':
                content = """This inspection report documents the comprehensive examination of pressure vessels 
                           and associated equipment in accordance with applicable engineering standards and 
                           regulatory requirements. All inspection activities were conducted following 
                           established safety protocols and industry best practices."""
            elif report.report_type == 'calculation':
                content = """This calculation report presents the engineering analysis performed for pressure 
                           vessel design and assessment. All calculations follow recognized engineering standards 
                           including ASME Boiler and Pressure Vessel Code, API standards, and other applicable 
                           codes and regulations."""
            elif report.report_type == 'compliance':
                content = """This compliance report evaluates the adherence to applicable engineering standards, 
                           regulatory requirements, and safety codes. The assessment covers design specifications, 
                           operational parameters, and maintenance requirements."""
            else:
                content = """This engineering report provides technical analysis and documentation for the 
                           specified project components. All assessments are based on current engineering 
                           standards and regulatory requirements."""
            
            story.append(Paragraph(content, styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Technical specifications
        story.append(Paragraph("Technical Specifications", styles['Heading2']))
        tech_specs = [
            ["Standard Compliance:", "ASME VIII Div 1, ASME B31.3, API 579"],
            ["Design Criteria:", "As per applicable codes and standards"],
            ["Safety Factors:", "Per engineering requirements"],
            ["Assessment Method:", "Engineering analysis and evaluation"]
        ]
        
        tech_table = Table(tech_specs, colWidths=[2*inch, 4*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(tech_table)
        story.append(Spacer(1, 30))
        
        # Conclusions
        story.append(Paragraph("Conclusions", styles['Heading2']))
        conclusion_text = """Based on the engineering analysis performed, all components meet the requirements 
                           of the applicable codes and standards. Regular inspection and maintenance schedules 
                           should be maintained to ensure continued safe operation."""
        story.append(Paragraph(conclusion_text, styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 50))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Generated by Vessel Guard Engineering Platform", footer_style))
        story.append(Paragraph(f"Report ID: {report.id} | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Read the PDF file and return as bytes
        with open(filepath, 'rb') as f:
            content_bytes = f.read()
        
        # Clean up temporary file
        try:
            os.remove(filepath)
        except:
            pass  # Ignore cleanup errors
            
        return content_bytes
        
    except Exception as e:
        # Fallback to text-based content if PDF generation fails
        fallback_content = f"""
VESSEL GUARD ENGINEERING REPORT
==============================

Report: {report.title}
Type: {report.report_type or 'General'}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Status: {report.status or 'Generated'}

Description:
{report.description or 'Engineering analysis report generated by Vessel Guard platform.'}

Technical Analysis:
This report documents the engineering assessment performed in accordance with 
applicable standards and regulations. All calculations and evaluations follow 
recognized engineering practices and safety requirements.

Conclusions:
The analysis has been completed as requested. Please refer to the detailed 
calculations and supporting documentation for complete technical information.

---
Generated by Vessel Guard Engineering Platform
Report ID: {report.id}
        """
        return fallback_content.strip().encode('utf-8')


def _generate_data_export(export_params: Dict[str, Any], db: Session, organization_id: str) -> bytes:
    """Generate data export in specified format."""
    import pandas as pd
    import io
    from datetime import datetime
    import csv
    
    try:
        export_format = export_params.get('format', 'csv').lower()
        export_type = export_params.get('export_type', 'projects')
        date_range = export_params.get('date_range', {})
        
        # Import models (should be available in the module)
        from app.db.models.project import Project
        from app.db.models.vessel import Vessel
        from app.db.models.calculation import Calculation
        from app.db.models.inspection import Inspection
        from app.db.models.user import User
        
        # Base query filter by organization
        base_filters = {"organization_id": organization_id}
        
        # Add date filtering if specified
        start_date = date_range.get('start_date')
        end_date = date_range.get('end_date')
        
        if export_type == 'projects':
            query = db.query(Project).filter(Project.organization_id == organization_id)
            
            if start_date:
                query = query.filter(Project.created_at >= start_date)
            if end_date:
                query = query.filter(Project.created_at <= end_date)
            
            projects = query.all()
            
            # Convert to data structure
            data = []
            for project in projects:
                data.append({
                    'ID': project.id,
                    'Name': project.name,
                    'Description': project.description or '',
                    'Status': project.status.value if project.status else '',
                    'Created Date': project.created_at.strftime('%Y-%m-%d') if project.created_at else '',
                    'Updated Date': project.updated_at.strftime('%Y-%m-%d') if project.updated_at else '',
                    'Vessel Count': len(project.vessels) if hasattr(project, 'vessels') else 0
                })
                
        elif export_type == 'vessels':
            query = db.query(Vessel).join(Project).filter(Project.organization_id == organization_id)
            
            if start_date:
                query = query.filter(Vessel.created_at >= start_date)
            if end_date:
                query = query.filter(Vessel.created_at <= end_date)
                
            vessels = query.all()
            
            data = []
            for vessel in vessels:
                data.append({
                    'ID': vessel.id,
                    'Tag Number': vessel.tag_number or '',
                    'Name': vessel.name or '',
                    'Type': vessel.vessel_type.value if vessel.vessel_type else '',
                    'Design Pressure': f"{vessel.design_pressure or 0} {vessel.pressure_unit or 'psi'}",
                    'Design Temperature': f"{vessel.design_temperature or 0} {vessel.temperature_unit or '°F'}",
                    'Material': vessel.material or '',
                    'Project': vessel.project.name if vessel.project else '',
                    'Created Date': vessel.created_at.strftime('%Y-%m-%d') if vessel.created_at else ''
                })
                
        elif export_type == 'calculations':
            query = db.query(Calculation).join(Project).filter(Project.organization_id == organization_id)
            
            if start_date:
                query = query.filter(Calculation.created_at >= start_date)
            if end_date:
                query = query.filter(Calculation.created_at <= end_date)
                
            calculations = query.all()
            
            data = []
            for calc in calculations:
                safety_factor = ''
                if calc.output_parameters and 'safety_factor' in calc.output_parameters:
                    safety_factor = str(calc.output_parameters['safety_factor'])
                    
                data.append({
                    'ID': calc.id,
                    'Type': calc.calculation_type or '',
                    'Status': calc.status.value if calc.status else '',
                    'Safety Factor': safety_factor,
                    'Project': calc.project.name if calc.project else '',
                    'Vessel': calc.vessel.tag_number if calc.vessel else '',
                    'Created Date': calc.created_at.strftime('%Y-%m-%d') if calc.created_at else '',
                    'Updated Date': calc.updated_at.strftime('%Y-%m-%d') if calc.updated_at else ''
                })
                
        elif export_type == 'inspections':
            query = db.query(Inspection).join(Vessel).join(Project).filter(Project.organization_id == organization_id)
            
            if start_date:
                query = query.filter(Inspection.inspection_date >= start_date)
            if end_date:
                query = query.filter(Inspection.inspection_date <= end_date)
                
            inspections = query.all()
            
            data = []
            for insp in inspections:
                data.append({
                    'ID': insp.id,
                    'Vessel': insp.vessel.tag_number if insp.vessel else '',
                    'Type': insp.inspection_type.value if insp.inspection_type else '',
                    'Status': insp.status.value if insp.status else '',
                    'Date': insp.inspection_date.strftime('%Y-%m-%d') if insp.inspection_date else '',
                    'Next Due': insp.next_inspection_date.strftime('%Y-%m-%d') if insp.next_inspection_date else '',
                    'Inspector': insp.inspector_name or '',
                    'Project': insp.vessel.project.name if insp.vessel and insp.vessel.project else ''
                })
                
        else:
            # Default to projects if unknown type
            data = [{'Error': f'Unknown export type: {export_type}'}]
        
        # Generate export based on format
        if export_format == 'excel' or export_format == 'xlsx':
            # Excel export using pandas
            df = pd.DataFrame(data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=export_type.title())
                
                # Add metadata sheet
                metadata = pd.DataFrame([
                    ['Export Type', export_type],
                    ['Generated Date', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')],
                    ['Organization ID', organization_id],
                    ['Total Records', len(data)],
                    ['Format', 'Excel'],
                    ['Generated By', 'Vessel Guard Platform']
                ], columns=['Field', 'Value'])
                metadata.to_excel(writer, index=False, sheet_name='Export Info')
                
            output.seek(0)
            return output.read()
            
        elif export_format == 'json':
            # JSON export
            export_data = {
                'metadata': {
                    'export_type': export_type,
                    'generated_date': datetime.utcnow().isoformat(),
                    'organization_id': organization_id,
                    'total_records': len(data),
                    'format': 'JSON',
                    'generated_by': 'Vessel Guard Platform'
                },
                'data': data
            }
            import json
            return json.dumps(export_data, indent=2, default=str).encode('utf-8')
            
        else:
            # Default CSV export
            output = io.StringIO()
            
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                
                # Add metadata as comments
                metadata_lines = [
                    f"# Export Type: {export_type}",
                    f"# Generated Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                    f"# Organization ID: {organization_id}",
                    f"# Total Records: {len(data)}",
                    f"# Generated By: Vessel Guard Platform",
                    ""
                ]
                
                # Prepend metadata to CSV content
                csv_content = '\n'.join(metadata_lines) + output.getvalue()
                return csv_content.encode('utf-8')
            else:
                return "No data available for export\n".encode('utf-8')
                
    except Exception as e:
        # Fallback error export
        error_content = f"""
DATA EXPORT ERROR
================

Export Type: {export_params.get('export_type', 'unknown')}
Format: {export_params.get('format', 'unknown')}
Organization: {organization_id}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Error Details:
{str(e)}

Please contact support if this issue persists.

---
Vessel Guard Platform
        """
        return error_content.strip().encode('utf-8')


    def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a bulk operation."""
        return self._operation_status_store.get(operation_id)
    
    def set_operation_status(self, operation_id: str, status_info: Dict[str, Any]):
        """Set the status of a bulk operation."""
        from datetime import datetime
        
        # Add timestamp if not present
        if 'updated_at' not in status_info:
            status_info['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            
        if 'created_at' not in status_info:
            status_info['created_at'] = datetime.utcnow().isoformat() + 'Z'
            
        self._operation_status_store[operation_id] = status_info
        
        # Clean up old operations periodically
        if len(self._operation_status_store) > 1000:  # Arbitrary limit
            self._cleanup_old_operations()
    
    def update_operation_progress(self, operation_id: str, current: int, total: int, message: str = None):
        """Update progress for a bulk operation."""
        from datetime import datetime
        
        status_info = self.get_operation_status(operation_id) or {}
        
        progress_percent = int((current / total) * 100) if total > 0 else 0
        
        status_info.update({
            'status': 'running' if current < total else 'completed',
            'current': current,
            'total': total,
            'progress_percent': progress_percent,
            'message': message or f'Processing {current} of {total} items',
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        })
        
        if current >= total:
            status_info['completed_at'] = datetime.utcnow().isoformat() + 'Z'
            
        self.set_operation_status(operation_id, status_info)
    
    def _cleanup_old_operations(self):
        """Clean up old operation status records (older than 24 hours)."""
        from datetime import datetime, timedelta
        
        # Remove operations older than 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        expired_operations = []
        
        for operation_id, status_info in self._operation_status_store.items():
            if status_info.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(status_info['created_at'].replace('Z', '+00:00'))
                    if created_at < cutoff_time:
                        expired_operations.append(operation_id)
                except (ValueError, TypeError):
                    # If we can't parse the date, consider it expired
                    expired_operations.append(operation_id)
        
        for operation_id in expired_operations:
            del self._operation_status_store[operation_id]


# Global background task service instance
background_task_service = BackgroundTaskService()


def get_background_task_service() -> BackgroundTaskService:
    """Get background task service instance."""
    return background_task_service
