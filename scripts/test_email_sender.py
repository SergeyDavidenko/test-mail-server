#!/usr/bin/env python3
"""
Enhanced Test Email Sender Script
For testing the Test Mail Server
"""

import smtplib
import time
import random
import argparse
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List


class EmailTestSuite:
    """Test suite for sending emails to the test mail server"""

    def __init__(self, smtp_host: str = 'localhost', smtp_port: int = 25):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sent_count = 0
        self.failed_count = 0

    def send_simple_email(self, from_addr: str, to_addr: str, subject: str, body: str) -> bool:
        """Send a simple text email"""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(msg)

            print(f"✓ Sent: {subject} to {to_addr}")
            self.sent_count += 1
            return True

        except Exception as e:
            print(f"✗ Failed to send to {to_addr}: {e}")
            self.failed_count += 1
            return False

    def send_multipart_email(self, from_addr: str, to_addr: str, subject: str) -> bool:
        """Send a multipart email with text and HTML"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Text part
            text = f"""
            Hello from Test Mail Server!
            
            This is a test email with both text and HTML content.
            
            Subject: {subject}
            From: {from_addr}
            To: {to_addr}
            Time: {datetime.now()}
            
            Best regards,
            Test Mail Server
            """

            # HTML part
            html = f"""
            <html>
              <body>
                <h2>Hello from Test Mail Server!</h2>
                <p>This is a test email with both <b>text</b> and <i>HTML</i> content.</p>
                <ul>
                  <li><strong>Subject:</strong> {subject}</li>
                  <li><strong>From:</strong> {from_addr}</li>
                  <li><strong>To:</strong> {to_addr}</li>
                  <li><strong>Time:</strong> {datetime.now()}</li>
                </ul>
                <p>Best regards,<br><em>Test Mail Server</em></p>
              </body>
            </html>
            """

            msg.attach(MIMEText(text, 'plain'))
            msg.attach(MIMEText(html, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(msg)

            print(f"✓ Sent multipart: {subject} to {to_addr}")
            self.sent_count += 1
            return True

        except Exception as e:
            print(f"✗ Failed to send multipart to {to_addr}: {e}")
            self.failed_count += 1
            return False

    def run_basic_test(self, recipients: List[str]) -> None:
        """Run basic email sending test"""
        print(f"📧 Running basic test to {len(recipients)} recipients...")

        for i, recipient in enumerate(recipients, 1):
            subject = f"Basic Test Email #{i}"
            body = f"This is test email #{i} sent at {datetime.now()}"
            self.send_simple_email(
                f"test{i}@example.com", recipient, subject, body)
            time.sleep(0.1)  # Small delay

    def run_multipart_test(self, recipients: List[str]) -> None:
        """Run multipart email test"""
        print(f"📧 Running multipart test to {len(recipients)} recipients...")

        for i, recipient in enumerate(recipients, 1):
            subject = f"Multipart Test Email #{i}"
            self.send_multipart_email(
                f"sender{i}@example.com", recipient, subject)
            time.sleep(0.1)

    def run_stress_test(self, recipient: str, count: int = 10) -> None:
        """Run stress test with multiple emails"""
        print(
            f"🚀 Running stress test: sending {count} emails to {recipient}...")

        subjects = [
            "Urgent: Action Required",
            "Welcome to our service!",
            "Your order confirmation",
            "Password reset request",
            "Monthly newsletter",
            "System maintenance notice",
            "Security alert",
            "Invoice attached",
            "Meeting reminder",
            "Survey invitation"
        ]

        for i in range(count):
            subject = random.choice(subjects) + f" #{i+1}"
            body = f"Stress test email #{i+1} of {count}\nSent at: {datetime.now()}\nRandom number: {random.randint(1000, 9999)}"
            sender = f"stress{i+1}@example.com"

            self.send_simple_email(sender, recipient, subject, body)

            if i < count - 1:  # Don't sleep after the last email
                time.sleep(random.uniform(0.1, 0.5))

    def print_summary(self) -> None:
        """Print test summary"""
        total = self.sent_count + self.failed_count
        success_rate = (self.sent_count / total * 100) if total > 0 else 0

        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        print(f"Total emails: {total}")
        print(f"✓ Sent successfully: {self.sent_count}")
        print(f"✗ Failed: {self.failed_count}")
        print(f"Success rate: {success_rate:.1f}%")
        print("="*50)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Test Mail Server Email Sender')
    parser.add_argument('--host', default='localhost', help='SMTP server host')
    parser.add_argument('--port', type=int, default=25,
                        help='SMTP server port')
    parser.add_argument(
        '--domain', default='test-mail.example.com', help='Email domain')
    parser.add_argument('--test', choices=['basic', 'multipart', 'stress', 'all'],
                        default='all', help='Test type to run')
    parser.add_argument('--recipients', nargs='+', help='Email recipients')
    parser.add_argument('--count', type=int, default=10,
                        help='Number of emails for stress test')

    args = parser.parse_args()

    # Default recipients if none provided
    if not args.recipients:
        args.recipients = [
            f'test1@{args.domain}',
            f'test2@{args.domain}',
            f'user@{args.domain}',
            f'admin@{args.domain}'
        ]

    # Initialize test suite
    test_suite = EmailTestSuite(args.host, args.port)

    print(f"🎯 Testing SMTP server at {args.host}:{args.port}")
    print(f"📬 Recipients: {', '.join(args.recipients)}")
    print(f"🔧 Test type: {args.test}")
    print()

    try:
        # Run tests based on selection
        if args.test in ['basic', 'all']:
            test_suite.run_basic_test(args.recipients)
            print()

        if args.test in ['multipart', 'all']:
            test_suite.run_multipart_test(args.recipients)
            print()

        if args.test in ['stress', 'all']:
            # Use first recipient for stress test
            test_suite.run_stress_test(args.recipients[0], args.count)
            print()

        test_suite.print_summary()

        # Exit with error code if any emails failed
        if test_suite.failed_count > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        test_suite.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
