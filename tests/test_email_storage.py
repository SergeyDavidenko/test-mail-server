#!/usr/bin/env python3
"""
Tests for email storage service
"""

import pytest
import time
from datetime import datetime
from app.services.email_storage import EmailStorageService


class TestEmailStorageService:
    """Test email storage service"""

    @pytest.fixture
    def storage_service(self):
        """Create a fresh storage service for each test"""
        service = EmailStorageService()
        service.clear_all()
        return service

    @pytest.fixture
    def sample_email(self):
        """Sample email data"""
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

    def test_add_email_success(self, storage_service, sample_email):
        """Test successful email addition"""
        result = storage_service.add_email(sample_email)
        
        assert result == True
        assert len(storage_service.email_storage) == 1
        assert 'test@test-mail.example.com' in storage_service.email_storage

    def test_add_email_case_insensitive(self, storage_service, sample_email):
        """Test email addresses are stored in lowercase"""
        sample_email['to'] = 'TEST@test-mail.example.com'
        
        storage_service.add_email(sample_email)
        
        assert 'test@test-mail.example.com' in storage_service.email_storage
        assert 'TEST@test-mail.example.com' not in storage_service.email_storage

    def test_get_emails(self, storage_service, sample_email):
        """Test getting emails for an address"""
        storage_service.add_email(sample_email)
        
        emails = storage_service.get_emails('test@test-mail.example.com')
        
        assert len(emails) == 1
        assert emails[0]['subject'] == 'Test Email'
        assert 'timestamp' not in emails[0]  # Should be removed

    def test_get_emails_case_insensitive(self, storage_service, sample_email):
        """Test getting emails is case insensitive"""
        storage_service.add_email(sample_email)
        
        emails = storage_service.get_emails('TEST@test-mail.example.com')
        
        assert len(emails) == 1

    def test_get_emails_empty(self, storage_service):
        """Test getting emails for non-existent address"""
        emails = storage_service.get_emails('nonexistent@example.com')
        
        assert emails == []

    def test_get_emails_limit(self, storage_service):
        """Test email limit functionality"""
        # Add multiple emails
        for i in range(15):
            email = {
                'id': f'test-email-{i}',
                'from': f'sender{i}@example.com',
                'to': 'test@test-mail.example.com',
                'subject': f'Test Email {i}',
                'body': f'Body {i}',
                'headers': {},
                'received': datetime.now().isoformat(),
                'timestamp': time.time() + i
            }
            storage_service.add_email(email)
        
        # Get with limit
        emails = storage_service.get_emails('test@test-mail.example.com', limit=5)
        
        assert len(emails) == 5
        # Should be newest first (highest timestamp)
        assert emails[0]['subject'] == 'Test Email 14'

    def test_get_all_addresses(self, storage_service, sample_email):
        """Test getting all addresses"""
        # Add emails for multiple addresses
        storage_service.add_email(sample_email)
        
        sample_email2 = sample_email.copy()
        sample_email2['to'] = 'user2@test-mail.example.com'
        storage_service.add_email(sample_email2)
        
        addresses = storage_service.get_all_addresses()
        
        assert len(addresses) == 2
        assert any(addr['address'] == 'test@test-mail.example.com' for addr in addresses)
        assert any(addr['address'] == 'user2@test-mail.example.com' for addr in addresses)
        assert all(addr['emailCount'] == 1 for addr in addresses)

    def test_delete_emails(self, storage_service, sample_email):
        """Test deleting emails for an address"""
        storage_service.add_email(sample_email)
        
        result = storage_service.delete_emails('test@test-mail.example.com')
        
        assert result == True
        assert len(storage_service.email_storage) == 0

    def test_delete_emails_case_insensitive(self, storage_service, sample_email):
        """Test deleting emails is case insensitive"""
        storage_service.add_email(sample_email)
        
        result = storage_service.delete_emails('TEST@test-mail.example.com')
        
        assert result == True
        assert len(storage_service.email_storage) == 0

    def test_delete_emails_not_found(self, storage_service):
        """Test deleting emails for non-existent address"""
        result = storage_service.delete_emails('nonexistent@example.com')
        
        assert result == False

    def test_cleanup_old_emails(self, storage_service):
        """Test cleanup of old emails"""
        # Add old email
        old_email = {
            'id': 'old-email',
            'from': 'sender@example.com',
            'to': 'test@test-mail.example.com',
            'subject': 'Old Email',
            'body': 'Old body',
            'headers': {},
            'received': datetime.now().isoformat(),
            'timestamp': time.time() - 10000  # Very old
        }
        storage_service.add_email(old_email)
        
        # Add recent email
        recent_email = {
            'id': 'recent-email',
            'from': 'sender@example.com',
            'to': 'test@test-mail.example.com',
            'subject': 'Recent Email',
            'body': 'Recent body',
            'headers': {},
            'received': datetime.now().isoformat(),
            'timestamp': time.time()  # Now
        }
        storage_service.add_email(recent_email)
        
        # Cleanup (assuming retention is less than 10000 seconds)
        result = storage_service.cleanup_old_emails()
        
        assert result['cleaned_emails'] >= 1
        
        # Check that recent email is still there
        emails = storage_service.get_emails('test@test-mail.example.com')
        assert len(emails) == 1
        assert emails[0]['subject'] == 'Recent Email'

    def test_get_statistics(self, storage_service, sample_email):
        """Test getting storage statistics"""
        storage_service.add_email(sample_email)
        
        stats = storage_service.get_statistics()
        
        assert stats['total_addresses'] == 1
        assert stats['total_emails'] == 1
        assert isinstance(stats['addresses'], list)
        assert 'test@test-mail.example.com' in stats['addresses']

    def test_clear_all(self, storage_service, sample_email):
        """Test clearing all emails"""
        storage_service.add_email(sample_email)
        assert len(storage_service.email_storage) == 1
        
        storage_service.clear_all()
        
        assert len(storage_service.email_storage) == 0
        assert len(storage_service.email_timestamps) == 0

    def test_thread_safety(self, storage_service, sample_email):
        """Basic test for thread safety (RLock usage)"""
        # This is a basic test - real thread safety would require concurrent testing
        with storage_service._lock:
            storage_service.add_email(sample_email)
            emails = storage_service.get_emails('test@test-mail.example.com')
            assert len(emails) == 1 