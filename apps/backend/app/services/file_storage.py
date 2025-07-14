"""
File storage service for Vessel Guard application.

Handles file uploads, downloads, and storage management for reports,
documents, certificates, and other engineering files.
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
import magic
from PIL import Image
import logging
from datetime import datetime

from fastapi import UploadFile, HTTPException
from pydantic import BaseModel

from app.core.config import settings


logger = logging.getLogger(__name__)


class FileInfo(BaseModel):
    """File information model."""
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    content_type: str
    upload_date: datetime
    organization_id: str
    uploaded_by: str


class StorageConfig:
    """Storage configuration."""
    
    def __init__(self):
        self.base_path = Path(getattr(settings, 'UPLOAD_DIR', './uploads'))
        self.max_file_size = getattr(settings, 'MAX_FILE_SIZE', 50 * 1024 * 1024)  # 50MB
        self.allowed_extensions = getattr(settings, 'ALLOWED_EXTENSIONS', {
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'spreadsheets': ['.xls', '.xlsx', '.csv'],
            'cad': ['.dwg', '.dxf', '.step', '.stp', '.iges', '.igs'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
        })
        self.thumbnail_size = (200, 200)
        
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)


class FileStorageService:
    """Service for handling file storage operations."""
    
    def __init__(self):
        self.config = StorageConfig()
    
    def upload_file(
        self,
        file: UploadFile,
        organization_id: str,
        user_id: str,
        category: str = "documents",
        subfolder: Optional[str] = None
    ) -> FileInfo:
        """
        Upload a file to storage.
        
        Args:
            file: Uploaded file
            organization_id: Organization ID
            user_id: User ID who uploaded the file
            category: File category (documents, images, etc.)
            subfolder: Optional subfolder within category
            
        Returns:
            FileInfo object with file details
        """
        try:
            # Validate file
            self._validate_file(file, category)
            
            # Generate unique filename
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create directory structure
            storage_path = self._get_storage_path(
                organization_id, category, subfolder
            )
            storage_path.mkdir(parents=True, exist_ok=True)
            
            # Full file path
            file_path = storage_path / unique_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file size and content type
            file_size = file_path.stat().st_size
            content_type = self._detect_content_type(file_path)
            
            # Create thumbnail for images
            if category == "images":
                self._create_thumbnail(file_path)
            
            # Create file info
            file_info = FileInfo(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                content_type=content_type,
                upload_date=datetime.utcnow(),
                organization_id=organization_id,
                uploaded_by=user_id
            )
            
            logger.info(f"File uploaded successfully: {file.filename} -> {unique_filename}")
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to upload file {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    def get_file_path(
        self,
        filename: str,
        organization_id: str,
        category: str = "documents",
        subfolder: Optional[str] = None
    ) -> Path:
        """Get full path to a file."""
        storage_path = self._get_storage_path(organization_id, category, subfolder)
        return storage_path / filename
    
    def delete_file(
        self,
        filename: str,
        organization_id: str,
        category: str = "documents",
        subfolder: Optional[str] = None
    ) -> bool:
        """
        Delete a file from storage.
        
        Args:
            filename: Name of file to delete
            organization_id: Organization ID
            category: File category
            subfolder: Optional subfolder
            
        Returns:
            True if file deleted successfully
        """
        try:
            file_path = self.get_file_path(filename, organization_id, category, subfolder)
            
            if file_path.exists():
                file_path.unlink()
                
                # Delete thumbnail if it exists
                thumbnail_path = file_path.parent / "thumbnails" / f"thumb_{filename}"
                if thumbnail_path.exists():
                    thumbnail_path.unlink()
                
                logger.info(f"File deleted: {filename}")
                return True
            else:
                logger.warning(f"File not found for deletion: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file {filename}: {e}")
            return False
    
    def list_files(
        self,
        organization_id: str,
        category: str = "documents",
        subfolder: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in a directory.
        
        Args:
            organization_id: Organization ID
            category: File category
            subfolder: Optional subfolder
            
        Returns:
            List of file information dictionaries
        """
        try:
            storage_path = self._get_storage_path(organization_id, category, subfolder)
            
            if not storage_path.exists():
                return []
            
            files = []
            for file_path in storage_path.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "file_size": stat.st_size,
                        "content_type": self._detect_content_type(file_path),
                        "modified_date": datetime.fromtimestamp(stat.st_mtime),
                        "category": category,
                        "subfolder": subfolder
                    })
            
            return sorted(files, key=lambda x: x["modified_date"], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def get_file_info(
        self,
        filename: str,
        organization_id: str,
        category: str = "documents",
        subfolder: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get information about a specific file."""
        try:
            file_path = self.get_file_path(filename, organization_id, category, subfolder)
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            return {
                "filename": file_path.name,
                "file_size": stat.st_size,
                "content_type": self._detect_content_type(file_path),
                "created_date": datetime.fromtimestamp(stat.st_ctime),
                "modified_date": datetime.fromtimestamp(stat.st_mtime),
                "category": category,
                "subfolder": subfolder,
                "file_path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {filename}: {e}")
            return None
    
    def create_directory(
        self,
        organization_id: str,
        category: str,
        directory_name: str
    ) -> bool:
        """Create a new directory."""
        try:
            directory_path = self._get_storage_path(organization_id, category, directory_name)
            directory_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {directory_name}: {e}")
            return False
    
    def get_storage_usage(self, organization_id: str) -> Dict[str, Any]:
        """Get storage usage statistics for an organization."""
        try:
            org_path = self.config.base_path / organization_id
            
            if not org_path.exists():
                return {"total_size": 0, "file_count": 0, "categories": {}}
            
            total_size = 0
            file_count = 0
            categories = {}
            
            for category_path in org_path.iterdir():
                if category_path.is_dir():
                    category_size = 0
                    category_files = 0
                    
                    for file_path in category_path.rglob("*"):
                        if file_path.is_file():
                            size = file_path.stat().st_size
                            category_size += size
                            category_files += 1
                    
                    categories[category_path.name] = {
                        "size": category_size,
                        "file_count": category_files
                    }
                    
                    total_size += category_size
                    file_count += category_files
            
            return {
                "total_size": total_size,
                "file_count": file_count,
                "categories": categories,
                "max_allowed_size": self.config.max_file_size
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage usage: {e}")
            return {"total_size": 0, "file_count": 0, "categories": {}}
    
    def _validate_file(self, file: UploadFile, category: str) -> None:
        """Validate uploaded file."""
        # Check file size
        if file.size > self.config.max_file_size:
            raise ValueError(f"File size exceeds maximum allowed size of {self.config.max_file_size} bytes")
        
        # Check file extension
        if category in self.config.allowed_extensions:
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in self.config.allowed_extensions[category]:
                raise ValueError(f"File type {file_extension} not allowed for category {category}")
        
        # Additional security checks could be added here
        # (e.g., virus scanning, content validation)
    
    def _get_storage_path(
        self,
        organization_id: str,
        category: str,
        subfolder: Optional[str] = None
    ) -> Path:
        """Get storage path for a file."""
        path = self.config.base_path / organization_id / category
        
        if subfolder:
            path = path / subfolder
        
        return path
    
    def _detect_content_type(self, file_path: Path) -> str:
        """Detect content type of a file."""
        try:
            return magic.from_file(str(file_path), mime=True)
        except:
            # Fallback to extension-based detection
            extension = file_path.suffix.lower()
            content_types = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xls': 'application/vnd.ms-excel',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.txt': 'text/plain',
                '.csv': 'text/csv'
            }
            return content_types.get(extension, 'application/octet-stream')
    
    def _create_thumbnail(self, image_path: Path) -> None:
        """Create thumbnail for image files."""
        try:
            # Create thumbnails directory
            thumb_dir = image_path.parent / "thumbnails"
            thumb_dir.mkdir(exist_ok=True)
            
            # Create thumbnail
            with Image.open(image_path) as img:
                img.thumbnail(self.config.thumbnail_size, Image.LANCZOS)
                thumb_path = thumb_dir / f"thumb_{image_path.name}"
                img.save(thumb_path, optimize=True, quality=85)
                
        except Exception as e:
            logger.warning(f"Failed to create thumbnail for {image_path}: {e}")


# Global file storage service instance
file_storage_service = FileStorageService()


def get_file_storage_service() -> FileStorageService:
    """Get file storage service instance."""
    return file_storage_service
