#!/usr/bin/env python3
"""
SMTP server service using aiosmtpd
"""

import logging
from datetime import datetime
from email.parser import Parser
from aiosmtpd.controller import Controller
from typing import Optional, Dict, Any

from ..config import config
from .email_storage import email_storage_service


logger = logging.getLogger(__name__)


class CustomSMTPHandler:
    """SMTP message handler using aiosmtpd"""

    def __init__(self):
        self.connection_count = 0
        self.total_emails_received = 0

    async def handle_DATA(self, server, session, envelope):
        """Handle incoming email data"""
        try:
            peer = session.peer
            mailfrom = envelope.mail_from
            rcpttos = envelope.rcpt_tos
            data = envelope.content  # bytes

            logger.info(
                f"Received email from {mailfrom} to {rcpttos} from {peer}")

            # Parse email
            parser = Parser()
            msg = parser.parsestr(data.decode('utf-8', errors='ignore'))

            # Process each recipient
            timestamp = datetime.now()
            processed_count = 0

            for rcpt in rcpttos:
                if self._is_valid_recipient(rcpt):
                    email_data = self._create_email_data(
                        mailfrom, rcpt, msg, data, timestamp
                    )

                    if email_storage_service.add_email(email_data):
                        processed_count += 1
                        logger.debug(f"Stored email for {rcpt}")
                    else:
                        logger.error(f"Failed to store email for {rcpt}")
                else:
                    logger.info(f"Ignoring email for {rcpt} - not our domain")

            self.total_emails_received += processed_count

            if processed_count > 0:
                return '250 OK'
            else:
                return '550 No valid recipients in domain'

        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return '451 Requested action aborted: local error in processing'

    def _is_valid_recipient(self, recipient: str) -> bool:
        """Check if recipient is valid for our domain"""
        return recipient.lower().endswith(f'@{config.DOMAIN.lower()}')

    def _create_email_data(self, mailfrom: str, rcpt: str, msg, data: bytes, timestamp: datetime) -> Dict[str, Any]:
        """Create email data structure"""
        return {
            'id': f"{timestamp.timestamp()}_{hash(data)}",
            'from': mailfrom,
            'to': rcpt,
            'subject': msg.get('Subject', 'No Subject'),
            'body': self._get_body(msg),
            'headers': dict(msg.items()),
            'received': timestamp.isoformat(),
            'timestamp': timestamp.timestamp()
        }

    def _get_body(self, msg) -> str:
        """Extract email body from message"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            return payload.decode('utf-8', errors='ignore')
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    return payload.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Error extracting email body: {e}")

        return ""

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        """Handle RCPT TO command"""
        if self._is_valid_recipient(address):
            envelope.rcpt_tos.append(address)
            return '250 OK'
        else:
            return '550 No such user here'

    async def handle_MAIL(self, server, session, envelope, address, mail_options):
        """Handle MAIL FROM command"""
        envelope.mail_from = address
        return '250 OK'

    def get_stats(self) -> Dict[str, Any]:
        """Get SMTP handler statistics"""
        return {
            'total_emails_received': self.total_emails_received,
            'connection_count': self.connection_count
        }


class SMTPService:
    """SMTP server service"""

    def __init__(self):
        self.handler = CustomSMTPHandler()
        self.controller: Optional[Controller] = None
        self.is_running = False

    def start(self) -> bool:
        """Start SMTP server"""
        try:
            if self.is_running:
                logger.warning("SMTP server is already running")
                return True

            self.controller = Controller(
                self.handler,
                hostname=config.HOST,
                port=config.SMTP_PORT
            )

            self.controller.start()
            self.is_running = True

            logger.info(
                f"SMTP server started on {config.HOST}:{config.SMTP_PORT}")
            return True

        except Exception as e:
            logger.error(f"Failed to start SMTP server: {e}")
            return False

    def stop(self) -> bool:
        """Stop SMTP server"""
        try:
            if not self.is_running or not self.controller:
                logger.warning("SMTP server is not running")
                return True

            self.controller.stop()
            self.is_running = False

            logger.info("SMTP server stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop SMTP server: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get SMTP server status"""
        stats = self.handler.get_stats() if self.handler else {}

        return {
            'running': self.is_running,
            'host': config.HOST,
            'port': config.SMTP_PORT,
            'domain': config.DOMAIN,
            **stats
        }

    def restart(self) -> bool:
        """Restart SMTP server"""
        logger.info("Restarting SMTP server...")

        if not self.stop():
            return False

        return self.start()


# Global instance
smtp_service = SMTPService()
