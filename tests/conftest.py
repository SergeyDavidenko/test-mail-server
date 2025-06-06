#!/usr/bin/env python3
"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.config import TestingConfig, config
from app.services import email_storage_service, smtp_service, cleanup_service


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_config():
    """Test configuration fixture"""
    # Use testing configuration
    original_config = config.__class__
    config.__class__ = TestingConfig
    yield config
    config.__class__ = original_config


@pytest.fixture(scope="function")
def clean_storage():
    """Clean email storage before each test"""
    email_storage_service.clear_all()
    yield email_storage_service
    email_storage_service.clear_all()


@pytest.fixture(scope="function")
def test_client(test_config, clean_storage):
    """Test client fixture"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
async def async_client(test_config, clean_storage):
    """Async test client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
def api_key(test_config):
    """API key fixture"""
    return test_config.generate_api_key()


@pytest.fixture(scope="function")
def auth_headers(api_key):
    """Authentication headers fixture"""
    return {"Authorization": f"Bearer {api_key}"}


@pytest.fixture(scope="function")
def sample_email():
    """Sample email data fixture"""
    return {
        'id': 'test-email-1',
        'from': 'sender@example.com',
        'to': 'test@test-mail.example.com',
        'subject': 'Test Email',
        'body': 'This is a test email body.',
        'headers': {
            'From': 'sender@example.com',
            'To': 'test@test-mail.example.com',
            'Subject': 'Test Email',
            'Date': 'Mon, 01 Jan 2024 12:00:00 +0000'
        },
        'received': '2024-01-01T12:00:00',
        'timestamp': 1704110400.0
    }


@pytest.fixture(scope="function")
def multiple_emails():
    """Multiple sample emails fixture"""
    return [
        {
            'id': f'test-email-{i}',
            'from': f'sender{i}@example.com',
            'to': 'test@test-mail.example.com',
            'subject': f'Test Email {i}',
            'body': f'This is test email body {i}.',
            'headers': {
                'From': f'sender{i}@example.com',
                'To': 'test@test-mail.example.com',
                'Subject': f'Test Email {i}',
                'Date': 'Mon, 01 Jan 2024 12:00:00 +0000'
            },
            'received': '2024-01-01T12:00:00',
            'timestamp': 1704110400.0 + i
        }
        for i in range(1, 6)
    ]


@pytest.fixture(scope="session", autouse=True)
async def setup_test_environment():
    """Setup test environment"""
    # Ensure we're using test configuration
    import os
    os.environ['APP_ENV'] = 'testing'
    
    yield
    
    # Cleanup after all tests
    if smtp_service.is_running:
        smtp_service.stop()
    
    if cleanup_service.is_running:
        await cleanup_service.stop() 