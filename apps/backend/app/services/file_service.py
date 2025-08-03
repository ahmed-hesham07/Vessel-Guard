"""
File upload and management service for documents and drawings.

This service provides comprehensive file management capabilities including
document upload, drawing management, version control, and file organization.
"""

import os
import uuid
import magic
from datetime import datetime
from typing import Dict, Any, List, Optional, BinaryIO
from pathlib import Path
import shutil
from PIL import Image
import fitz  # PyMuPDF for PDF processing

from sqlalchemy.orm import Session
from app.db.models.file import File
from app.db.models.user import User
from app.core.config import settings
from app.core.exceptions import ValidationError, NotFoundError


class FileService:
    """Service for file upload and management operations."""
    
    ALLOWED_EXTENSIONS = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'drawings': ['.dwg', '.dxf', '.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'],
        'images': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'],
        'spreadsheets': ['.xls', '.xlsx', '.csv'],
        'presentations': ['.ppt', '.pptx']
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path(settings.STATIC_FILES_DIR) / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        file_type: str,
        project_id: int,
        vessel_id: Optional[int] = None,
        uploaded_by_id: int = None,
        organization_id: int = None,
        description: str = None,
        tags: List[str] = None
    ) -> File:
        """Upload and process a file."""
        # Validate file
        self._validate_file(file, filename)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix.lower()
        unique_filename = f"{file_id}{file_extension}"
        
        # Create directory structure
        year_month = datetime.now().strftime("%Y/%m")
        file_dir = self.upload_dir / year_month
        file_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = file_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file, buffer)
        
        # Get file metadata
        file_size = os.path.getsize(file_path)
        mime_type = magic.from_file(str(file_path), mime=True)
        
        # Process file based on type
        metadata = self._process_file(file_path, mime_type, file_type)
        
        # Create file record
        file_record = File(
            filename=filename,
            unique_filename=unique_filename,
            file_path=str(file_path.relative_to(self.upload_dir)),
            file_size=file_size,
            mime_type=mime_type,
            file_type=file_type,
            project_id=project_id,
            vessel_id=vessel_id,
            uploaded_by_id=uploaded_by_id,
            organization_id=organization_id,
            description=description,
            tags=tags or [],
            metadata=metadata
        )
        
        self.db.add(file_record)
        self.db.commit()
        self.db.refresh(file_record)
        
        return file_record
    
    def get_project_files(self, project_id: int, file_type: Optional[str] = None) -> List[File]:
        """Get all files for a project."""
        query = self.db.query(File).filter(File.project_id == project_id)
        
        if file_type:
            query = query.filter(File.file_type == file_type)
        
        return query.order_by(File.created_at.desc()).all()
    
    def get_vessel_files(self, vessel_id: int, file_type: Optional[str] = None) -> List[File]:
        """Get all files for a vessel."""
        query = self.db.query(File).filter(File.vessel_id == vessel_id)
        
        if file_type:
            query = query.filter(File.file_type == file_type)
        
        return query.order_by(File.created_at.desc()).all()
    
    def search_files(
        self,
        organization_id: int,
        search_term: str = None,
        file_type: str = None,
        tags: List[str] = None
    ) -> List[File]:
        """Search files by various criteria."""
        query = self.db.query(File).filter(File.organization_id == organization_id)
        
        if search_term:
            query = query.filter(
                (File.filename.ilike(f"%{search_term}%")) |
                (File.description.ilike(f"%{search_term}%"))
            )
        
        if file_type:
            query = query.filter(File.file_type == file_type)
        
        if tags:
            for tag in tags:
                query = query.filter(File.tags.contains([tag]))
        
        return query.order_by(File.created_at.desc()).all()
    
    def delete_file(self, file_id: int, user_id: int) -> bool:
        """Delete a file."""
        file_record = self.db.query(File).filter(File.id == file_id).first()
        
        if not file_record:
            raise NotFoundError("File not found")
        
        # Check permissions (simplified)
        if file_record.uploaded_by_id != user_id:
            raise ValidationError("Permission denied")
        
        # Delete physical file
        file_path = self.upload_dir / file_record.file_path
        if file_path.exists():
            file_path.unlink()
        
        # Delete record
        self.db.delete(file_record)
        self.db.commit()
        
        return True
    
    def update_file_metadata(
        self,
        file_id: int,
        description: str = None,
        tags: List[str] = None,
        vessel_id: int = None
    ) -> File:
        """Update file metadata."""
        file_record = self.db.query(File).filter(File.id == file_id).first()
        
        if not file_record:
            raise NotFoundError("File not found")
        
        if description is not None:
            file_record.description = description
        
        if tags is not None:
            file_record.tags = tags
        
        if vessel_id is not None:
            file_record.vessel_id = vessel_id
        
        self.db.commit()
        self.db.refresh(file_record)
        
        return file_record
    
    def get_file_download_path(self, file_id: int) -> str:
        """Get the download path for a file."""
        file_record = self.db.query(File).filter(File.id == file_id).first()
        
        if not file_record:
            raise NotFoundError("File not found")
        
        return str(self.upload_dir / file_record.file_path)
    
    def _validate_file(self, file: BinaryIO, filename: str) -> None:
        """Validate uploaded file."""
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > self.MAX_FILE_SIZE:
            raise ValidationError(f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024)}MB")
        
        # Check file extension
        file_extension = Path(filename).suffix.lower()
        allowed_extensions = []
        for extensions in self.ALLOWED_EXTENSIONS.values():
            allowed_extensions.extend(extensions)
        
        if file_extension not in allowed_extensions:
            raise ValidationError(f"File type {file_extension} is not allowed")
    
    def _process_file(self, file_path: Path, mime_type: str, file_type: str) -> Dict[str, Any]:
        """Process file and extract metadata."""
        metadata = {
            "processed_at": datetime.now().isoformat(),
            "file_type": file_type,
            "mime_type": mime_type
        }
        
        try:
            if mime_type.startswith('image/'):
                # Process image files
                with Image.open(file_path) as img:
                    metadata.update({
                        "width": img.width,
                        "height": img.height,
                        "mode": img.mode,
                        "format": img.format
                    })
            
            elif mime_type == 'application/pdf':
                # Process PDF files
                doc = fitz.open(str(file_path))
                metadata.update({
                    "page_count": len(doc),
                    "title": doc.metadata.get("title", ""),
                    "author": doc.metadata.get("author", ""),
                    "subject": doc.metadata.get("subject", "")
                })
                doc.close()
            
            elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                             'application/msword']:
                # Process Word documents (basic metadata)
                metadata.update({
                    "document_type": "Word Document"
                })
            
            elif mime_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             'application/vnd.ms-excel']:
                # Process Excel documents (basic metadata)
                metadata.update({
                    "document_type": "Spreadsheet"
                })
            
        except Exception as e:
            metadata["processing_error"] = str(e)
        
        return metadata
    
    def create_file_version(self, file_id: int, new_file: BinaryIO, version_notes: str = None) -> File:
        """Create a new version of an existing file."""
        original_file = self.db.query(File).filter(File.id == file_id).first()
        
        if not original_file:
            raise NotFoundError("Original file not found")
        
        # Create new version
        new_version = self.upload_file(
            file=new_file,
            filename=original_file.filename,
            file_type=original_file.file_type,
            project_id=original_file.project_id,
            vessel_id=original_file.vessel_id,
            uploaded_by_id=original_file.uploaded_by_id,
            organization_id=original_file.organization_id,
            description=f"Version update: {version_notes}" if version_notes else "New version",
            tags=original_file.tags
        )
        
        # Link to original file
        new_version.parent_file_id = file_id
        new_version.version_notes = version_notes
        
        self.db.commit()
        self.db.refresh(new_version)
        
        return new_version
    
    def get_file_versions(self, file_id: int) -> List[File]:
        """Get all versions of a file."""
        return self.db.query(File).filter(
            (File.id == file_id) | (File.parent_file_id == file_id)
        ).order_by(File.created_at.desc()).all()
    
    def generate_file_preview(self, file_id: int) -> Optional[str]:
        """Generate a preview for supported file types."""
        file_record = self.db.query(File).filter(File.id == file_id).first()
        
        if not file_record:
            return None
        
        file_path = self.upload_dir / file_record.file_path
        
        if not file_path.exists():
            return None
        
        try:
            if file_record.mime_type.startswith('image/'):
                # Generate thumbnail for images
                return self._generate_image_thumbnail(file_path)
            
            elif file_record.mime_type == 'application/pdf':
                # Generate PDF preview
                return self._generate_pdf_preview(file_path)
            
        except Exception as e:
            print(f"Error generating preview: {e}")
            return None
        
        return None
    
    def _generate_image_thumbnail(self, file_path: Path) -> str:
        """Generate thumbnail for image files."""
        thumbnail_dir = self.upload_dir / "thumbnails"
        thumbnail_dir.mkdir(exist_ok=True)
        
        thumbnail_path = thumbnail_dir / f"{file_path.stem}_thumb.jpg"
        
        with Image.open(file_path) as img:
            img.thumbnail((200, 200))
            img.save(thumbnail_path, "JPEG", quality=85)
        
        return str(thumbnail_path.relative_to(self.upload_dir))
    
    def _generate_pdf_preview(self, file_path: Path) -> str:
        """Generate preview for PDF files."""
        preview_dir = self.upload_dir / "previews"
        preview_dir.mkdir(exist_ok=True)
        
        preview_path = preview_dir / f"{file_path.stem}_preview.jpg"
        
        doc = fitz.open(str(file_path))
        page = doc[0]  # First page
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
        pix.save(str(preview_path))
        doc.close()
        
        return str(preview_path.relative_to(self.upload_dir))
