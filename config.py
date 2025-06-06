#!/usr/bin/env python3
"""
Configuration file for the test mail server
"""

import os
import secrets


class Config:
    """Configuration settings for the mail server"""

    # Server ports
    SMTP_PORT = int(os.getenv('SMTP_PORT', 25))
    API_PORT = int(os.getenv('API_PORT', 3000))

    # Email settings
    DOMAIN = os.getenv('MAIL_DOMAIN', 'test-mail.example.com')
    RETENTION_HOURS = int(os.getenv('RETENTION_HOURS', 4))
    MAX_EMAILS_PER_ADDRESS = int(os.getenv('MAX_EMAILS_PER_ADDRESS', 100))

    # Authentication
    API_KEY = os.getenv('API_KEY', None)

    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

    # Cleanup settings
    CLEANUP_INTERVAL_MINUTES = int(os.getenv('CLEANUP_INTERVAL_MINUTES', 30))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

    @classmethod
    def generate_api_key(cls):
        """Generate a new API key if not provided"""
        if not cls.API_KEY:
            cls.API_KEY = secrets.token_urlsafe(32)
        return cls.API_KEY

    @classmethod
    def get_cleanup_interval_seconds(cls):
        """Get cleanup interval in seconds"""
        return cls.CLEANUP_INTERVAL_MINUTES * 60

    @classmethod
    def get_retention_seconds(cls):
        """Get retention time in seconds"""
        return cls.RETENTION_HOURS * 3600

    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []

        if cls.SMTP_PORT < 1 or cls.SMTP_PORT > 65535:
            errors.append(f"Invalid SMTP_PORT: {cls.SMTP_PORT}")

        if cls.API_PORT < 1 or cls.API_PORT > 65535:
            errors.append(f"Invalid API_PORT: {cls.API_PORT}")

        if not cls.DOMAIN:
            errors.append("DOMAIN cannot be empty")

        if cls.RETENTION_HOURS < 1:
            errors.append(
                f"RETENTION_HOURS must be >= 1: {cls.RETENTION_HOURS}")

        if cls.MAX_EMAILS_PER_ADDRESS < 1:
            errors.append(
                f"MAX_EMAILS_PER_ADDRESS must be >= 1: {cls.MAX_EMAILS_PER_ADDRESS}")

        return errors

    @classmethod
    def display_config(cls):
        """Display current configuration"""
        return {
            'smtp_port': cls.SMTP_PORT,
            'api_port': cls.API_PORT,
            'domain': cls.DOMAIN,
            'retention_hours': cls.RETENTION_HOURS,
            'max_emails_per_address': cls.MAX_EMAILS_PER_ADDRESS,
            'host': cls.HOST,
            'debug': cls.DEBUG,
            'cleanup_interval_minutes': cls.CLEANUP_INTERVAL_MINUTES,
            'log_level': cls.LOG_LEVEL,
            'api_key_set': bool(cls.API_KEY)
        }
