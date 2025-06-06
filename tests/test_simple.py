#!/usr/bin/env python3
"""
Simple working tests for demonstration
"""

import pytest
from app.config import config
from app.services.email_storage import EmailStorageService


def test_config_basic():
    """Test basic configuration access"""
    assert config.DOMAIN is not None
    assert config.SMTP_PORT > 0
    assert config.API_PORT > 0


def test_email_storage_basic():
    """Test basic email storage functionality"""
    storage = EmailStorageService()
    storage.clear_all()
    
    # Test empty state
    assert len(storage.email_storage) == 0
    
    # Add test email
    email_data = {
        'id': 'test-1',
        'from': 'sender@example.com',
        'to': 'test@example.com',
        'subject': 'Test',
        'body': 'Test body',
        'headers': {},
        'received': '2024-01-01T12:00:00',
        'timestamp': 1704110400.0
    }
    
    result = storage.add_email(email_data)
    assert result == True
    assert len(storage.email_storage) == 1
    
    # Get emails
    emails = storage.get_emails('test@example.com')
    assert len(emails) == 1
    assert emails[0]['subject'] == 'Test'


def test_api_key_generation():
    """Test API key generation"""
    api_key = config.generate_api_key()
    assert api_key is not None
    assert len(api_key) > 10  # Should be a reasonable length
    assert isinstance(api_key, str)


@pytest.mark.unit
def test_unit_example():
    """Example unit test"""
    assert 1 + 1 == 2


@pytest.mark.integration
def test_integration_example():
    """Example integration test"""
    storage = EmailStorageService()
    storage.clear_all()
    
    # This would be an integration test
    stats = storage.get_statistics()
    assert isinstance(stats, dict)
    assert 'total_addresses' in stats 