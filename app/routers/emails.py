#!/usr/bin/env python3
"""
Email management router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

from ..models import EmailListResponse, AddressListResponse, MessageResponse, ErrorResponse
from ..services import email_storage_service
from .auth import verify_api_key


router = APIRouter(prefix="/api/v1", tags=["Email Management"])


@router.get(
    "/addresses",
    response_model=AddressListResponse,
    responses={
        200: {"description": "List of email addresses"},
        401: {"model": ErrorResponse, "description": "API key required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"}
    },
    summary="Get all email addresses",
    description="Get list of all email addresses that have received emails"
)
async def get_addresses(verified: bool = Depends(verify_api_key)):
    """Get all email addresses"""

    addresses = email_storage_service.get_all_addresses()

    return AddressListResponse(
        count=len(addresses),
        addresses=addresses
    )


@router.get(
    "/email/{address}",
    response_model=EmailListResponse,
    responses={
        200: {"description": "Emails for the address"},
        401: {"model": ErrorResponse, "description": "API key required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        404: {"model": ErrorResponse, "description": "Address not found"}
    },
    summary="Get emails for address",
    description="Get all emails for a specific email address"
)
async def get_emails_for_address(
    address: str,
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of emails to return"),
    verified: bool = Depends(verify_api_key)
):
    """Get emails for a specific address"""

    emails = email_storage_service.get_emails(address, limit)

    if not emails and address.lower() not in [addr.lower() for addr in email_storage_service.email_storage.keys()]:
        raise HTTPException(
            status_code=404,
            detail=f"No emails found for address: {address}"
        )

    # Convert to response format
    email_models = []
    for email in emails:
        email_models.append({
            'id': email['id'],
            'from': email['from'],
            'to': email['to'],
            'subject': email['subject'],
            'body': email['body'],
            'headers': email['headers'],
            'received': email['received']
        })

    return EmailListResponse(
        address=address,
        count=len(email_models),
        emails=email_models
    )


@router.delete(
    "/email/{address}",
    response_model=MessageResponse,
    responses={
        200: {"description": "Emails deleted successfully"},
        401: {"model": ErrorResponse, "description": "API key required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        404: {"model": ErrorResponse, "description": "Address not found"}
    },
    summary="Delete emails for address",
    description="Delete all emails for a specific email address"
)
async def delete_emails_for_address(
    address: str,
    verified: bool = Depends(verify_api_key)
):
    """Delete all emails for a specific address"""

    success = email_storage_service.delete_emails(address)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"No emails found for address: {address}"
        )

    return MessageResponse(
        message=f"All emails deleted for address: {address}"
    )


@router.post(
    "/cleanup",
    response_model=MessageResponse,
    responses={
        200: {"description": "Cleanup completed"},
        401: {"model": ErrorResponse, "description": "API key required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"}
    },
    summary="Force cleanup",
    description="Force immediate cleanup of old emails"
)
async def force_cleanup(verified: bool = Depends(verify_api_key)):
    """Force immediate cleanup of old emails"""

    result = email_storage_service.cleanup_old_emails()

    return MessageResponse(
        message=f"Cleanup completed: {result['cleaned_emails']} emails cleaned, "
        f"{result['removed_addresses']} addresses removed, "
        f"{result['active_addresses']} addresses remaining"
    )


@router.get(
    "/stats",
    responses={
        200: {"description": "Email storage statistics"},
        401: {"model": ErrorResponse, "description": "API key required"},
        403: {"model": ErrorResponse, "description": "Invalid API key"}
    },
    summary="Get storage statistics",
    description="Get detailed statistics about email storage"
)
async def get_storage_stats(verified: bool = Depends(verify_api_key)):
    """Get storage statistics"""

    stats = email_storage_service.get_statistics()

    return {
        "statistics": stats,
        "configuration": {
            "max_emails_per_address": email_storage_service.email_storage.__class__.__name__,
            "retention_hours": "Configured in settings"
        }
    }
