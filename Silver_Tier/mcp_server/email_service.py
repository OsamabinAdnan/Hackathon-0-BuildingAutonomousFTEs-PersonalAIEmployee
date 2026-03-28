"""
Email Service - Send emails via Gmail API.

This service provides email sending capabilities via Gmail API.
Uses OAuth2 authentication with stored credentials.

Usage:
    from mcp_server.email_service import EmailService

    service = EmailService()
    await service.send_email(
        to="recipient@example.com",
        subject="Test Subject",
        body="Email body content"
    )
"""

import base64
import logging
import os
from email.message import EmailMessage
from typing import Optional, List
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('mcp_server.email')


class EmailService:
    """
    Email service using Gmail API.

    Provides email sending capabilities with OAuth2 authentication.
    """

    def __init__(self, vault_path: str = './AI_Employee_Vault_FTE'):
        """
        Initialize the email service.

        Args:
            vault_path: Path to vault for resolving credentials path
        """
        self.service = None
        self.credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', './credentials/gmail_credentials.json')
        self.token_path = os.getenv('GMAIL_TOKEN_PATH', './credentials/gmail_token.json')

        # Resolve paths relative to vault parent
        if not Path(self.credentials_path).is_absolute():
            self.credentials_path = str(Path(vault_path).parent / self.credentials_path)
        if not Path(self.token_path).is_absolute():
            self.token_path = str(Path(vault_path).parent / self.token_path)

        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

    def _authenticate(self) -> bool:
        """
        Authenticate with Gmail API.

        Returns:
            True if successful, False otherwise
        """
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send'
            ]

            creds = None

            # Load existing token
            if Path(self.token_path).exists():
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

            # Refresh or authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not Path(self.credentials_path).exists():
                        logger.error(f'Credentials file not found: {self.credentials_path}')
                        return False
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save token
                Path(self.token_path).parent.mkdir(parents=True, exist_ok=True)
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())

            self.service = build('gmail', 'v1', credentials=creds)
            logger.info('Gmail API authenticated successfully')
            return True

        except Exception as e:
            logger.error(f'Gmail authentication failed: {e}')
            return False

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        html: bool = False
    ) -> dict:
        """
        Send an email via Gmail API.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: Optional list of CC recipients
            bcc: Optional list of BCC recipients
            html: Whether body is HTML (default: plain text)

        Returns:
            Dict with success status and message ID or error
        """
        # Dry run check
        if self.dry_run:
            logger.info(f'[DRY RUN] Would send email to: {to}')
            logger.info(f'[DRY RUN] Subject: {subject}')
            return {'success': True, 'dry_run': True, 'to': to}

        # Authenticate if needed
        if not self.service:
            if not self._authenticate():
                return {'success': False, 'error': 'Authentication failed'}

        try:
            # Create email message
            message = EmailMessage()

            if html:
                message.set_content(body, subtype='html')
            else:
                message.set_content(body)

            message['To'] = to
            message['Subject'] = subject

            if cc:
                message['Cc'] = ', '.join(cc)
            if bcc:
                message['Bcc'] = ', '.join(bcc)

            # Encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {'raw': encoded_message}

            # Send email
            result = self.service.users().messages().send(
                userId='me',
                body=create_message
            ).execute()

            logger.info(f'Email sent successfully to {to}, Message ID: {result["id"]}')
            return {
                'success': True,
                'message_id': result['id'],
                'to': to,
                'subject': subject
            }

        except Exception as e:
            logger.error(f'Failed to send email: {e}')
            return {'success': False, 'error': str(e)}

    async def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> dict:
        """
        Create an email draft via Gmail API.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            html: Whether body is HTML

        Returns:
            Dict with success status and draft ID or error
        """
        if self.dry_run:
            logger.info(f'[DRY RUN] Would create draft to: {to}')
            return {'success': True, 'dry_run': True}

        if not self.service:
            if not self._authenticate():
                return {'success': False, 'error': 'Authentication failed'}

        try:
            message = EmailMessage()

            if html:
                message.set_content(body, subtype='html')
            else:
                message.set_content(body)

            message['To'] = to
            message['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'message': {'raw': encoded_message}}

            draft = self.service.users().drafts().create(
                userId='me',
                body=create_message
            ).execute()

            logger.info(f'Draft created: {draft["id"]}')
            return {
                'success': True,
                'draft_id': draft['id'],
                'to': to
            }

        except Exception as e:
            logger.error(f'Failed to create draft: {e}')
            return {'success': False, 'error': str(e)}
