#!/usr/bin/env python3
"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import email_storage_service


class TestAPI:
    """Test API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def api_key(self):
        """Get API key for testing"""
        from app.config import config
        return config.generate_api_key()

    @pytest.fixture
    def auth_headers(self, api_key):
        """Authentication headers"""
        return {"Authorization": f"Bearer {api_key}"}

    @pytest.fixture
    def sample_email_data(self):
        """Sample email for testing"""
        import time
        from datetime import datetime
        
        timestamp = datetime.now()
        return {
            'id': 'test-email-1',
            'from': 'sender@example.com',
            'to': 'test@test-mail.example.com',
            'subject': 'Test Email',
            'body': 'This is a test email body.',
            'headers': {
                'From': 'sender@example.com',
                'To': 'test@test-mail.example.com',
                'Subject': 'Test Email'
            },
            'received': timestamp.isoformat(),
            'timestamp': timestamp.timestamp()
        }

    def test_root_redirect(self, client):
        """Test root endpoint redirects to docs"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/docs" in response.headers["location"]

    def test_health_check_no_auth(self, client):
        """Test health check endpoint (no auth required)"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_status_requires_auth(self, client):
        """Test status endpoint requires authentication"""
        response = client.get("/api/v1/status")
        assert response.status_code == 401

    def test_status_with_auth(self, client, auth_headers):
        """Test status endpoint with authentication"""
        response = client.get("/api/v1/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "domain" in data
        assert "smtpPort" in data
        assert "apiPort" in data

    def test_addresses_empty(self, client, auth_headers):
        """Test addresses endpoint with no emails"""
        # Clear storage first
        email_storage_service.clear_all()
        
        response = client.get("/api/v1/addresses", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["addresses"] == []

    def test_addresses_with_emails(self, client, auth_headers, sample_email_data):
        """Test addresses endpoint with emails"""
        # Clear and add test email
        email_storage_service.clear_all()
        email_storage_service.add_email(sample_email_data)
        
        response = client.get("/api/v1/addresses", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["addresses"]) == 1
        assert data["addresses"][0]["address"] == "test@test-mail.example.com"
        assert data["addresses"][0]["emailCount"] == 1

    def test_get_emails_for_address(self, client, auth_headers, sample_email_data):
        """Test getting emails for specific address"""
        # Clear and add test email
        email_storage_service.clear_all()
        email_storage_service.add_email(sample_email_data)
        
        response = client.get(
            "/api/v1/email/test@test-mail.example.com", 
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["address"] == "test@test-mail.example.com"
        assert data["count"] == 1
        assert len(data["emails"]) == 1
        assert data["emails"][0]["subject"] == "Test Email"

    def test_get_emails_not_found(self, client, auth_headers):
        """Test getting emails for non-existent address"""
        email_storage_service.clear_all()
        
        response = client.get(
            "/api/v1/email/nonexistent@example.com", 
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_emails_for_address(self, client, auth_headers, sample_email_data):
        """Test deleting emails for address"""
        # Clear and add test email
        email_storage_service.clear_all()
        email_storage_service.add_email(sample_email_data)
        
        response = client.delete(
            "/api/v1/email/test@test-mail.example.com", 
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    def test_delete_emails_not_found(self, client, auth_headers):
        """Test deleting emails for non-existent address"""
        email_storage_service.clear_all()
        
        response = client.delete(
            "/api/v1/email/nonexistent@example.com", 
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_force_cleanup(self, client, auth_headers):
        """Test force cleanup endpoint"""
        response = client.post("/api/v1/cleanup", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "cleanup completed" in data["message"].lower()

    def test_storage_stats(self, client, auth_headers, sample_email_data):
        """Test storage statistics endpoint"""
        # Clear and add test email
        email_storage_service.clear_all()
        email_storage_service.add_email(sample_email_data)
        
        response = client.get("/api/v1/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "statistics" in data
        assert data["statistics"]["total_addresses"] == 1
        assert data["statistics"]["total_emails"] == 1

    def test_auth_info(self, client, auth_headers):
        """Test auth info endpoint"""
        response = client.get("/api/v1/auth/info", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "methods" in data
        assert isinstance(data["methods"], list)

    def test_config_endpoint(self, client, auth_headers):
        """Test config endpoint"""
        response = client.get("/api/v1/auth/config", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "config" in data
        assert isinstance(data["config"], dict)

    def test_services_status(self, client, auth_headers):
        """Test services status endpoint"""
        response = client.get("/api/v1/services", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "smtp_server" in data
        assert "cleanup_service" in data
        assert "email_storage" in data
        assert "api_server" in data

    def test_bearer_token_auth(self, client, api_key, sample_email_data):
        """Test Bearer token authentication"""
        headers = {"Authorization": f"Bearer {api_key}"}
        response = client.get("/api/v1/addresses", headers=headers)
        assert response.status_code == 200

    def test_query_param_auth(self, client, api_key):
        """Test query parameter authentication"""
        response = client.get(f"/api/v1/addresses?api_key={api_key}")
        assert response.status_code == 200

    def test_invalid_auth(self, client):
        """Test invalid authentication"""
        headers = {"Authorization": "Bearer invalid-key"}
        response = client.get("/api/v1/addresses", headers=headers)
        assert response.status_code == 403

    def test_missing_auth(self, client):
        """Test missing authentication"""
        response = client.get("/api/v1/addresses")
        assert response.status_code == 401

    def test_email_limit_parameter(self, client, auth_headers):
        """Test email limit query parameter"""
        # Add multiple emails
        email_storage_service.clear_all()
        for i in range(5):
            email_data = {
                'id': f'test-email-{i}',
                'from': f'sender{i}@example.com',
                'to': 'test@test-mail.example.com',
                'subject': f'Test Email {i}',
                'body': f'Body {i}',
                'headers': {},
                'received': '2024-01-01T12:00:00',
                'timestamp': 1704110400.0 + i
            }
            email_storage_service.add_email(email_data)
        
        response = client.get(
            "/api/v1/email/test@test-mail.example.com?limit=3", 
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3 