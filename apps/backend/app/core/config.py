"""
Core configuration for Vessel Guard API.

This module contains all configuration settings for the application,
including database connections, authentication, and service settings.
"""

import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Vessel Guard API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DESCRIPTION: str = "Pressure Vessel Integrity Analysis and Compliance Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "vessel_guard"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None
    
    # SSL Configuration for Aiven
    POSTGRES_SSL_MODE: str = "disable"  # Can be: disable, require, verify-ca, verify-full
    POSTGRES_SSL_CERT_PATH: Optional[str] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        # For PostgreSQL connections, build the URL
        if values.get("POSTGRES_SERVER") and values.get("POSTGRES_DB"):
            # Build base URL manually for better compatibility
            user = values.get("POSTGRES_USER", "postgres")
            password = values.get("POSTGRES_PASSWORD", "")
            host = values.get("POSTGRES_SERVER", "localhost")
            port = values.get("POSTGRES_PORT", "5432")
            database = values.get("POSTGRES_DB", "")
            
            # Build the connection string
            if password:
                base_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
            else:
                base_url = f"postgresql+psycopg2://{user}@{host}:{port}/{database}"
            
            # Add SSL parameters if required
            ssl_mode = values.get("POSTGRES_SSL_MODE", "disable")
            if ssl_mode != "disable":
                ssl_params = f"?sslmode={ssl_mode}"
                ssl_cert_path = values.get("POSTGRES_SSL_CERT_PATH")
                if ssl_cert_path:
                    ssl_params += f"&sslrootcert={ssl_cert_path}"
                base_url += ssl_params
            
            return base_url
        # For development with SQLite, return a simple string
        return "sqlite:///./vessel_guard_dev.db"
    
    # Redis for caching and sessions
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Azure Configuration
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_SUBSCRIPTION_ID: Optional[str] = None
    
    # Azure Storage
    AZURE_STORAGE_ACCOUNT_NAME: Optional[str] = None
    AZURE_STORAGE_CONTAINER_NAME: str = "reports"
    
    # Azure Key Vault
    AZURE_KEY_VAULT_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Email (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # New email service settings
    SMTP_SERVER: str = "localhost"
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: str = "noreply@vessel-guard.com"
    FROM_NAME: str = "Vessel Guard"
    SUPPORT_EMAIL: str = "support@vessel-guard.com"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: Dict[str, List[str]] = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'spreadsheets': ['.xls', '.xlsx', '.csv'],
        'cad': ['.dwg', '.dxf', '.step', '.stp', '.iges', '.igs'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
    }
    
    # Engineering Constants
    ENGINEERING_CODES: List[str] = [
        "ASME_B31_3",
        "API_579",
        "ASME_VIII_DIV_1",
        "ASME_VIII_DIV_2",
        "API_650",
        "API_653"
    ]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv"]
    
    # Monitoring and Health
    HEALTH_CHECK_TIMEOUT: int = 30
    
    # Celery (for background tasks)
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Testing
    TESTING: bool = False
    TEST_DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = "dev.env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in environment


# Global settings instance
settings = Settings()
