#!/usr/bin/env python3
"""
FastAPI Test Mail Server
Modern replacement for deprecated Python `smtpd` module
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import config
from .models import ErrorResponse
from .services import smtp_service, cleanup_service
from .routers import auth_router, emails_router, health_router
from . import __version__, __description__


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        *([logging.FileHandler(config.LOG_FILE)] if config.LOG_FILE else [])
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""

    # Startup
    logger.info(f"Starting Test Mail Server v{__version__}")

    # Validate configuration
    config_errors = config.validate()
    if config_errors:
        logger.error("Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        sys.exit(1)

    # Setup logging directory
    config.setup_logging_directory()

    # Start services
    logger.info("Starting services...")

    # Start SMTP server
    if not smtp_service.start():
        logger.error("Failed to start SMTP server")
        sys.exit(1)

    # Start cleanup service
    if not await cleanup_service.start():
        logger.error("Failed to start cleanup service")
        smtp_service.stop()
        sys.exit(1)

    # Generate and log API key
    api_key = config.generate_api_key()
    logger.info(f"API Key: {api_key}")

    logger.info(
        f"Server ready - SMTP: {config.HOST}:{config.SMTP_PORT}, API: {config.HOST}:{config.API_PORT}")

    yield

    # Shutdown
    logger.info("Shutting down services...")

    # Stop services
    await cleanup_service.stop()
    smtp_service.stop()

    logger.info("Test Mail Server stopped")


# Create FastAPI application
app = FastAPI(
    title="Test Mail Server",
    description=__description__,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    from fastapi.responses import JSONResponse
    error_response = ErrorResponse(
        error="HTTP Error",
        message=str(exc.detail),
        detail=f"Status: {exc.status_code}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    from fastapi.responses import JSONResponse
    error_response = ErrorResponse(
        error="Validation Error",
        message="Request validation failed",
        detail=str(exc.errors())
    )
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    from fastapi.responses import JSONResponse
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    error_response = ErrorResponse(
        error="Internal Server Error",
        message="An unexpected error occurred",
        detail=str(exc) if config.DEBUG else "Enable debug mode for details"
    )
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(emails_router)


# Root redirect
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")


# Legacy API compatibility (redirect old endpoints)
@app.get("/api/v1/addresses", include_in_schema=False)
async def legacy_addresses_redirect():
    """Legacy redirect"""
    return RedirectResponse(url="/api/v1/addresses")


# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    # FastAPI will handle the shutdown through lifespan


if __name__ == "__main__":
    import uvicorn

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the server
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )
