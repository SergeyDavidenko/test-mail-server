#!/usr/bin/env python3
"""
Health check and status router
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import time

from ..models import HealthResponse, StatusResponse, ErrorResponse
from ..config import config
from ..services import email_storage_service, smtp_service, cleanup_service
from .auth import verify_api_key
from .. import __version__


router = APIRouter(prefix="/api/v1", tags=["Health & Status"])

# Server start time for uptime calculation
_start_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        200: {"description": "Health check response"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    },
    summary="Health check",
    description="Health check endpoint for monitoring and load balancers (Kubernetes ready)"
)
async def health_check():
    """Health check endpoint"""

    # Check critical services
    services = {
        "smtp_server": "healthy" if smtp_service.is_running else "unhealthy",
        "email_storage": "healthy",  # Always healthy if responding
        "cleanup_service": "healthy" if cleanup_service.is_running else "degraded"
    }

    # Determine overall status
    if services["smtp_server"] == "unhealthy":
        status = "unhealthy"
    elif services["cleanup_service"] == "degraded":
        status = "degraded"
    else:
        status = "healthy"

    return HealthResponse(
        status=status,
        version=__version__,
        services=services
    )


@router.get(
    "/status",
    response_model=StatusResponse,
    responses={
        200: {"description": "Server status"},
        401: {"model": ErrorResponse, "description": "API key required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"}
    },
    summary="Get server status",
    description="Get detailed server status information"
)
async def get_status(verified: bool = Depends(verify_api_key)):
    """Get detailed server status"""

    # Get storage statistics
    stats = email_storage_service.get_statistics()

    # Calculate uptime
    uptime_seconds = int(time.time() - _start_time)
    uptime_str = _format_uptime(uptime_seconds)

    return StatusResponse(
        status="running",
        domain=config.DOMAIN,
        smtpPort=config.SMTP_PORT,
        apiPort=config.API_PORT,
        totalAddresses=stats['total_addresses'],
        totalEmails=stats['total_emails'],
        retentionHours=config.RETENTION_HOURS,
        authRequired=bool(config.API_KEY),
        uptime=uptime_str
    )


@router.get(
    "/services",
    responses={
        200: {"description": "Service status details"},
        401: {"model": ErrorResponse, "description": "API key required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"}
    },
    summary="Get service status",
    description="Get detailed status of all services"
)
async def get_services_status(verified: bool = Depends(verify_api_key)):
    """Get detailed service status"""

    smtp_status = smtp_service.get_status()
    cleanup_status = cleanup_service.get_status()
    storage_stats = email_storage_service.get_statistics()

    return {
        "smtp_server": {
            **smtp_status,
            "uptime_seconds": int(time.time() - _start_time)
        },
        "cleanup_service": {
            **cleanup_status,
            "next_cleanup_in_seconds": cleanup_service.get_next_cleanup_in_seconds()
        },
        "email_storage": {
            **storage_stats,
            "memory_usage": "In-memory storage"
        },
        "api_server": {
            "running": True,
            "port": config.API_PORT,
            "host": config.HOST,
            "version": __version__,
            "uptime_seconds": int(time.time() - _start_time)
        }
    }


def _format_uptime(seconds: int) -> str:
    """Format uptime in human readable format"""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)
