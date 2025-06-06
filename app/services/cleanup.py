#!/usr/bin/env python3
"""
Cleanup service for scheduled email cleanup
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..config import config
from .email_storage import email_storage_service


logger = logging.getLogger(__name__)


class CleanupService:
    """Service for scheduled cleanup of old emails"""

    def __init__(self):
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.last_cleanup: Optional[datetime] = None
        self.cleanup_stats = {
            'total_cleanups': 0,
            'total_emails_cleaned': 0,
            'total_addresses_cleaned': 0,
            'last_cleanup_result': None
        }

    async def start(self) -> bool:
        """Start the cleanup service"""
        if self.is_running:
            logger.warning("Cleanup service is already running")
            return True

        try:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.is_running = True
            logger.info(
                f"Cleanup service started (interval: {config.CLEANUP_INTERVAL_MINUTES} minutes)")
            return True

        except Exception as e:
            logger.error(f"Failed to start cleanup service: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the cleanup service"""
        if not self.is_running:
            logger.warning("Cleanup service is not running")
            return True

        try:
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass

            self.is_running = False
            logger.info("Cleanup service stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop cleanup service: {e}")
            return False

    async def _cleanup_loop(self):
        """Main cleanup loop"""
        while self.is_running:
            try:
                await asyncio.sleep(config.get_cleanup_interval_seconds())

                if self.is_running:  # Check if still running after sleep
                    await self.perform_cleanup()

            except asyncio.CancelledError:
                logger.info("Cleanup loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                # Continue the loop despite errors

    async def perform_cleanup(self) -> Dict[str, Any]:
        """Perform cleanup operation"""
        try:
            logger.info("Starting scheduled cleanup...")

            # Perform cleanup
            result = email_storage_service.cleanup_old_emails()

            # Update statistics
            self.cleanup_stats['total_cleanups'] += 1
            self.cleanup_stats['total_emails_cleaned'] += result['cleaned_emails']
            self.cleanup_stats['total_addresses_cleaned'] += result['removed_addresses']
            self.cleanup_stats['last_cleanup_result'] = result
            self.last_cleanup = datetime.now()

            logger.info(
                f"Cleanup completed: {result['cleaned_emails']} emails cleaned, "
                f"{result['removed_addresses']} addresses removed, "
                f"{result['active_addresses']} addresses remaining"
            )

            return result

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {'error': str(e)}

    async def force_cleanup(self) -> Dict[str, Any]:
        """Force immediate cleanup (manual trigger)"""
        logger.info("Manual cleanup triggered")
        return await self.perform_cleanup()

    def get_status(self) -> Dict[str, Any]:
        """Get cleanup service status"""
        return {
            'running': self.is_running,
            'cleanup_interval_minutes': config.CLEANUP_INTERVAL_MINUTES,
            'retention_hours': config.RETENTION_HOURS,
            'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None,
            'stats': self.cleanup_stats
        }

    def get_next_cleanup_in_seconds(self) -> Optional[int]:
        """Get seconds until next cleanup"""
        if not self.last_cleanup or not self.is_running:
            return None

        interval_seconds = config.get_cleanup_interval_seconds()
        elapsed_seconds = (datetime.now() - self.last_cleanup).total_seconds()
        remaining_seconds = max(0, interval_seconds - elapsed_seconds)

        return int(remaining_seconds)


# Global instance
cleanup_service = CleanupService()
