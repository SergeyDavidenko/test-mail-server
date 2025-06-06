#!/usr/bin/env python3
"""
Email storage service for managing email data
"""

import time
import threading
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any
from ..config import config


class EmailStorageService:
    """Service for managing email storage and retrieval"""

    def __init__(self):
        self.email_storage: Dict[str, deque] = defaultdict(deque)
        self.email_timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def add_email(self, email_data: Dict[str, Any]) -> bool:
        """Add email to storage"""
        try:
            with self._lock:
                address = email_data['to'].lower()

                # Add email to queue
                self.email_storage[address].append(email_data)

                # Limit emails per address
                if len(self.email_storage[address]) > config.MAX_EMAILS_PER_ADDRESS:
                    self.email_storage[address].popleft()

                # Update timestamp
                self.email_timestamps[address] = email_data['timestamp']

                return True
        except Exception as e:
            print(f"Error adding email: {e}")
            return False

    def get_emails(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get emails for a specific address"""
        with self._lock:
            address = address.lower()
            emails = list(self.email_storage.get(address, []))

            # Sort by timestamp (newest first)
            emails.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

            # Apply limit
            emails = emails[:limit]

            # Remove internal timestamp field
            clean_emails = []
            for email in emails:
                clean_email = {k: v for k,
                               v in email.items() if k != 'timestamp'}
                clean_emails.append(clean_email)

            return clean_emails

    def get_all_addresses(self) -> List[Dict[str, Any]]:
        """Get all active email addresses with counts"""
        with self._lock:
            addresses = []
            for address, emails in self.email_storage.items():
                addresses.append({
                    'address': address,
                    'emailCount': len(emails)
                })
            return addresses

    def delete_emails(self, address: str) -> bool:
        """Delete all emails for a specific address"""
        with self._lock:
            address = address.lower()

            if address in self.email_storage:
                del self.email_storage[address]
                if address in self.email_timestamps:
                    del self.email_timestamps[address]
                return True

            return False

    def cleanup_old_emails(self) -> Dict[str, int]:
        """Remove old emails based on retention policy"""
        with self._lock:
            cutoff_time = time.time() - config.get_retention_seconds()

            addresses_to_remove = []
            cleaned_count = 0

            for address, emails in self.email_storage.items():
                # Count emails before cleanup
                original_count = len(emails)

                # Filter out old emails
                self.email_storage[address] = deque([
                    email for email in emails
                    if email.get('timestamp', 0) > cutoff_time
                ])

                # Count cleaned emails
                cleaned_count += original_count - \
                    len(self.email_storage[address])

                # Mark empty addresses for removal
                if not self.email_storage[address]:
                    addresses_to_remove.append(address)

            # Remove empty addresses
            for address in addresses_to_remove:
                del self.email_storage[address]
                if address in self.email_timestamps:
                    del self.email_timestamps[address]

            return {
                'cleaned_emails': cleaned_count,
                'removed_addresses': len(addresses_to_remove),
                'active_addresses': len(self.email_storage)
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        with self._lock:
            total_emails = sum(len(emails)
                               for emails in self.email_storage.values())

            return {
                'total_addresses': len(self.email_storage),
                'total_emails': total_emails,
                'addresses': list(self.email_storage.keys()),
                'oldest_email': self._get_oldest_email_timestamp(),
                'newest_email': self._get_newest_email_timestamp()
            }

    def _get_oldest_email_timestamp(self) -> Optional[float]:
        """Get timestamp of oldest email"""
        oldest = None
        for emails in self.email_storage.values():
            for email in emails:
                timestamp = email.get('timestamp', 0)
                if oldest is None or timestamp < oldest:
                    oldest = timestamp
        return oldest

    def _get_newest_email_timestamp(self) -> Optional[float]:
        """Get timestamp of newest email"""
        newest = None
        for emails in self.email_storage.values():
            for email in emails:
                timestamp = email.get('timestamp', 0)
                if newest is None or timestamp > newest:
                    newest = timestamp
        return newest

    def clear_all(self) -> None:
        """Clear all stored emails (for testing)"""
        with self._lock:
            self.email_storage.clear()
            self.email_timestamps.clear()


# Global instance
email_storage_service = EmailStorageService()
