#!/usr/bin/env python3
"""
Pydantic models for the Test Mail Server API
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model with common fields"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )


class EmailModel(BaseModel):
    """Model for individual email representation"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    id: str = Field(..., description="Unique email identifier")
    from_address: str = Field(alias="from", description="Sender email address")
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    headers: Dict[str, str] = Field(..., description="Email headers")
    received: str = Field(...,
                          description="Email received timestamp (ISO format)")


class EmailListResponse(BaseResponse):
    """Response model for email list endpoint"""
    address: str = Field(..., description="Email address")
    count: int = Field(..., description="Number of emails", ge=0)
    emails: List[EmailModel] = Field(..., description="List of emails")


class AddressInfo(BaseModel):
    """Model for address information"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    address: str = Field(..., description="Email address")
    emailCount: int = Field(...,
                            description="Number of emails for this address", ge=0)


class AddressListResponse(BaseResponse):
    """Response model for address list endpoint"""
    count: int = Field(..., description="Total number of addresses", ge=0)
    addresses: List[AddressInfo] = Field(...,
                                         description="List of email addresses")


class StatusResponse(BaseResponse):
    """Response model for server status endpoint"""
    status: str = Field(..., description="Server status")
    domain: str = Field(..., description="Mail domain")
    smtpPort: int = Field(..., description="SMTP port", ge=1, le=65535)
    apiPort: int = Field(..., description="API port", ge=1, le=65535)
    totalAddresses: int = Field(..., description="Total email addresses", ge=0)
    totalEmails: int = Field(..., description="Total emails stored", ge=0)
    retentionHours: int = Field(..., description="Email retention hours", ge=1)
    authRequired: bool = Field(...,
                               description="Whether authentication is required")
    uptime: Optional[str] = Field(None, description="Server uptime")


class MessageResponse(BaseResponse):
    """Generic message response model"""
    message: str = Field(..., description="Response message")
    timestamp: Optional[str] = Field(None, description="Response timestamp")


class AuthInfo(BaseResponse):
    """Response model for authentication info endpoint"""
    message: str = Field(..., description="Authentication info message")
    methods: List[str] = Field(...,
                               description="Available authentication methods")
    note: str = Field(..., description="Additional notes")


class ConfigResponse(BaseResponse):
    """Response model for configuration endpoint"""
    config: Dict[str, Any] = Field(..., description="Server configuration")


class ErrorResponse(BaseResponse):
    """Response model for error responses"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(
        None, description="Detailed error information")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class HealthResponse(BaseResponse):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = Field(..., description="Application version")
    services: Dict[str, str] = Field(..., description="Service statuses")


class SMTPStatus(BaseModel):
    """SMTP server status model"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    running: bool = Field(..., description="Whether SMTP server is running")
    port: int = Field(..., description="SMTP port", ge=1, le=65535)
    host: str = Field(..., description="SMTP host")
    connections: int = Field(default=0, description="Active connections", ge=0)


class APIStatus(BaseModel):
    """API server status model"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    running: bool = Field(..., description="Whether API server is running")
    port: int = Field(..., description="API port", ge=1, le=65535)
    host: str = Field(..., description="API host")
    requests_count: int = Field(
        default=0, description="Total requests processed", ge=0)
