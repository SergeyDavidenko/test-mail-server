#!/usr/bin/env python3
"""
Authentication router for API key management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Union

from ..config import config
from ..models import AuthInfo, ConfigResponse, ErrorResponse


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    api_key: Optional[str] = Query(
        None, description="API key as query parameter")
) -> bool:
    """
    Verify API key from Bearer token or query parameter
    """
    # Generate API key if not set
    if not config.API_KEY:
        config.generate_api_key()

    provided_key = None

    # Check Bearer token first
    if credentials:
        provided_key = credentials.credentials
    # Then check query parameter
    elif api_key:
        provided_key = api_key

    if not provided_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide via Authorization header or api_key parameter."
        )

    if provided_key != config.API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )

    return True


@router.get(
    "/info",
    response_model=AuthInfo,
    responses={
        200: {"description": "Authentication information"},
        401: {"model": ErrorResponse, "description": "API key required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"}
    },
    summary="Get authentication information",
    description="Get information about authentication methods and requirements"
)
async def get_auth_info(verified: bool = Depends(verify_api_key)):
    """Get authentication information"""

    return AuthInfo(
        message="Authentication successful",
        methods=["Bearer Token", "Query Parameter"],
        note="Use Authorization: Bearer <api_key> header or ?api_key=<api_key> parameter"
    )


@router.get(
    "/config",
    response_model=ConfigResponse,
    responses={
        200: {"description": "Server configuration"},
        401: {"model": ErrorResponse, "description": "API key required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"}
    },
    summary="Get server configuration",
    description="Get current server configuration settings"
)
async def get_config(verified: bool = Depends(verify_api_key)):
    """Get server configuration"""

    return ConfigResponse(
        config=config.display_config()
    )


# Public endpoint to get API key (for development/testing)
@router.get(
    "/key",
    summary="Get API key",
    description="Get the current API key (development only)",
    include_in_schema=config.DEBUG  # Only show in schema if debug mode
)
async def get_api_key():
    """Get API key (development only)"""

    if not config.DEBUG:
        raise HTTPException(
            status_code=404,
            detail="Endpoint not available in production"
        )

    api_key = config.generate_api_key()

    return {
        "api_key": api_key,
        "usage": {
            "bearer_token": f"Authorization: Bearer {api_key}",
            "query_parameter": f"?api_key={api_key}"
        },
        "note": "This endpoint is only available in debug mode"
    }
