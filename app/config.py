#!/usr/bin/env python3
"""
Configuration module for the test mail server
"""

import os
import secrets
from typing import Optional
from pathlib import Path


class Config:
    """Configuration settings for the mail server"""

    # Server ports
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', 25))
    API_PORT: int = int(os.getenv('API_PORT', 3000))

    # Email settings
    DOMAIN: str = os.getenv('MAIL_DOMAIN', 'test-mail.example.com')
    RETENTION_HOURS: int = int(os.getenv('RETENTION_HOURS', 4))
    MAX_EMAILS_PER_ADDRESS: int = int(os.getenv('MAX_EMAILS_PER_ADDRESS', 100))

    # Authentication
    API_KEY: Optional[str] = os.getenv('API_KEY', None)

    # Server settings
    HOST: str = os.getenv('HOST', '0.0.0.0')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'

    # Cleanup settings
    CLEANUP_INTERVAL_MINUTES: int = int(
        os.getenv('CLEANUP_INTERVAL_MINUTES', 30))

    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE: Optional[str] = os.getenv('LOG_FILE', None)

    # Application paths
    APP_DIR: Path = Path(__file__).parent
    PROJECT_DIR: Path = APP_DIR.parent
    LOGS_DIR: Path = PROJECT_DIR / "logs"

    @classmethod
    def generate_api_key(cls) -> str:
        """Generate a new API key if not provided"""
        if not cls.API_KEY:
            cls.API_KEY = secrets.token_urlsafe(32)
        return cls.API_KEY

    @classmethod
    def get_cleanup_interval_seconds(cls) -> int:
        """Get cleanup interval in seconds"""
        return cls.CLEANUP_INTERVAL_MINUTES * 60

    @classmethod
    def get_retention_seconds(cls) -> int:
        """Get retention time in seconds"""
        return cls.RETENTION_HOURS * 3600

    @classmethod
    def setup_logging_directory(cls) -> None:
        """Create logs directory if it doesn't exist"""
        cls.LOGS_DIR.mkdir(exist_ok=True)

    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors"""
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
    def display_config(cls) -> dict[str, any]:
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
            'api_key_set': bool(cls.API_KEY),
            'app_dir': str(cls.APP_DIR),
            'logs_dir': str(cls.LOGS_DIR)
        }


# Development configuration
class DevelopmentConfig(Config):
    """Development specific configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    RETENTION_HOURS = 1
    CLEANUP_INTERVAL_MINUTES = 5


# Production configuration
class ProductionConfig(Config):
    """Production specific configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"


# Testing configuration
class TestingConfig(Config):
    """Testing specific configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    RETENTION_HOURS = 1
    MAX_EMAILS_PER_ADDRESS = 10
    SMTP_PORT = 2525  # Different port for testing
    API_PORT = 8000


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv('APP_ENV', 'development').lower()

    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Global config instance
config = get_config()
