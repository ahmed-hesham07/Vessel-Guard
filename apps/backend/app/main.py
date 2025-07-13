"""
Vessel Guard API - Main Application Entry Point

A comprehensive SaaS platform for pressure vessel integrity analysis
and compliance with engineering standards.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.api.v1.api import api_router
from app.db.init_db import init_db
from app.middleware.rate_limiting import RateLimitMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.security import SecurityMiddleware
from app.middleware.performance import PerformanceMiddleware, performance_middleware_instance

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Vessel Guard API...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down Vessel Guard API...")


# Create FastAPI application
app = FastAPI(
    title="Vessel Guard API",
    description="Pressure Vessel Integrity Analysis and Compliance Platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware (order matters - they execute in reverse order of addition)

# Performance monitoring (should be first to measure everything)
performance_middleware = PerformanceMiddleware(app)
app.add_middleware(PerformanceMiddleware)

# Security middleware
app.add_middleware(SecurityMiddleware)

# Rate limiting
redis_url = getattr(settings, 'REDIS_URL', None)
app.add_middleware(RateLimitMiddleware, redis_url=redis_url)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, 'CORS_ORIGINS', ['*']),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=getattr(settings, 'ALLOWED_HOSTS', ['*']),
)

# Store performance middleware instance globally
import app.middleware.performance as perf_module
perf_module.performance_middleware_instance = performance_middleware


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Vessel Guard API",
        "version": "1.0.0",
        "description": "Pressure Vessel Integrity Analysis and Compliance Platform",
        "docs_url": "/docs",
        "health_check": "/api/v1/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
