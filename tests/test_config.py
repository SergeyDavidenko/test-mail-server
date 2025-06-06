#!/usr/bin/env python3
"""
Tests for configuration module
"""

import pytest
import os
from app.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig


class TestConfig:
    """Test configuration classes"""

    def test_default_values(self):
        """Test default configuration values"""
        config = Config()
        
        assert config.SMTP_PORT == 25
        assert config.API_PORT == 3000
        assert config.DOMAIN == 'test-mail.example.com'
        assert config.RETENTION_HOURS == 4
        assert config.MAX_EMAILS_PER_ADDRESS == 100
        assert config.HOST == '0.0.0.0'
        assert config.DEBUG == False
        assert config.CLEANUP_INTERVAL_MINUTES == 30

    def test_environment_override(self, monkeypatch):
        """Test configuration from environment variables"""
        # Set environment variables
        monkeypatch.setenv('SMTP_PORT', '2525')
        monkeypatch.setenv('API_PORT', '8000')
        monkeypatch.setenv('MAIL_DOMAIN', 'test.example.com')
        monkeypatch.setenv('DEBUG', 'true')
        
        # Create new config class to re-read environment
        import os
        
        class TestConfig:
            SMTP_PORT: int = int(os.getenv('SMTP_PORT', 25))
            API_PORT: int = int(os.getenv('API_PORT', 3000))
            DOMAIN: str = os.getenv('MAIL_DOMAIN', 'test-mail.example.com')
            DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
        
        config = TestConfig()
        
        assert config.SMTP_PORT == 2525
        assert config.API_PORT == 8000
        assert config.DOMAIN == 'test.example.com'
        assert config.DEBUG == True

    def test_api_key_generation(self):
        """Test API key generation"""
        # Test class method
        api_key = Config.generate_api_key()
        
        assert api_key is not None
        assert len(api_key) > 0
        assert Config.API_KEY == api_key

    def test_validation_valid_config(self):
        """Test validation with valid configuration"""
        errors = Config.validate()
        
        assert errors == []

    def test_validation_invalid_config(self):
        """Test validation with invalid configuration"""
        # Create a test config class with invalid values
        class InvalidConfig(Config):
            SMTP_PORT = 0
            RETENTION_HOURS = 0
            MAX_EMAILS_PER_ADDRESS = 0
        
        errors = InvalidConfig.validate()
        
        assert len(errors) == 3
        assert any("Invalid SMTP_PORT" in error for error in errors)
        assert any("RETENTION_HOURS must be >= 1" in error for error in errors)
        assert any("MAX_EMAILS_PER_ADDRESS must be >= 1" in error for error in errors)

    def test_development_config(self):
        """Test development configuration"""
        config = DevelopmentConfig()
        
        assert config.DEBUG == True
        assert config.LOG_LEVEL == "DEBUG"
        assert config.RETENTION_HOURS == 1
        assert config.CLEANUP_INTERVAL_MINUTES == 5

    def test_production_config(self):
        """Test production configuration"""
        config = ProductionConfig()
        
        assert config.DEBUG == False
        assert config.LOG_LEVEL == "INFO"

    def test_testing_config(self):
        """Test testing configuration"""
        config = TestingConfig()
        
        assert config.DEBUG == True
        assert config.LOG_LEVEL == "DEBUG"
        assert config.RETENTION_HOURS == 1
        assert config.MAX_EMAILS_PER_ADDRESS == 10
        assert config.SMTP_PORT == 2525
        assert config.API_PORT == 8000

    def test_helper_methods(self):
        """Test helper methods"""
        cleanup_seconds = Config.get_cleanup_interval_seconds()
        retention_seconds = Config.get_retention_seconds()
        
        assert cleanup_seconds == Config.CLEANUP_INTERVAL_MINUTES * 60
        assert retention_seconds == Config.RETENTION_HOURS * 3600

    def test_display_config(self):
        """Test display configuration method"""
        display = Config.display_config()
        
        assert isinstance(display, dict)
        assert 'smtp_port' in display
        assert 'api_port' in display
        assert 'domain' in display
        assert 'debug' in display 