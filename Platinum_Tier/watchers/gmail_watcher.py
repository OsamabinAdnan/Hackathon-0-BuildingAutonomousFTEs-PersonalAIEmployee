"""
Gmail Watcher - Monitors Gmail for unread important emails.

This watcher uses the Gmail API to monitor for new emails:
1. Authenticates via OAuth2
2. Checks for unread important emails at specified interval
3. Creates action files in /Needs_Action/email/

Requires:
- Google Cloud project with Gmail API enabled
- OAuth 2.0 credentials (credentials.json)
- Scopes: https://www.googleapis.com/auth/gmail.readonly

Usage:
    python -m watchers.gmail
    python -m watchers.gmail --setup-oauth  # First time setup
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Set

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger('GMAIL')


class GmailWatcher:
    """
    Gmail API Watcher for AI Employee.

    Monitors for unread important emails and creates action files.
    """

    def __init__(self, vault_path: str, check_interval: int = 701):
        """
        Initialize the Gmail watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 701)
        """
        from watchers.base_watcher import BaseWatcher

        # Initialize with category
        self.vault_path = Path(vault_path)
        self.category = 'email'
        self.needs_action = self.vault_path / 'Needs_Action' / self.category
        self.check_interval = check_interval

        # Setup logger
        self.logger = logging.getLogger('GMAIL')

        # Ensure output directory exists
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Gmail API setup
        self.service = None
        self.creds = None
        self.processed_ids: Set[str] = set()

        # Load previously processed emails from state file
        self.state_file = Path(self.vault_path).parent / ".watcher_state" / "gmail_processed.json"
        self.load_processed_emails()

        # Credentials paths from environment
        self.credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', './credentials/gmail_credentials.json')
        self.token_path = os.getenv('GMAIL_TOKEN_PATH', './credentials/gmail_token.json')

        # Resolve paths relative to vault
        if not Path(self.credentials_path).is_absolute():
            self.credentials_path = str(Path(vault_path).parent / self.credentials_path)
        if not Path(self.token_path).is_absolute():
            self.token_path = str(Path(vault_path).parent / self.token_path)

        self.logger.info(f'Gmail Watcher initialized')
        self.logger.info(f'  Credentials: {self.credentials_path}')
        self.logger.info(f'  Token: {self.token_path}')
        self.logger.info(f'  Output: /Needs_Action/{self.category}/')

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            # Scopes for Gmail API - BOTH read AND send permissions
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send'
            ]

            creds = None

            # Check for existing token
            if Path(self.token_path).exists():
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
                self.logger.info('Loaded existing credentials from token file')

            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    self.logger.info('Refreshing expired credentials...')
                    creds.refresh(Request())
                else:
                    # Check for credentials.json
                    if not Path(self.credentials_path).exists():
                        self.logger.error(f'Credentials file not found: {self.credentials_path}')
                        self.logger.error('Please download credentials.json from Google Cloud Console')
                        return False

                    self.logger.info('Starting OAuth flow...')
                    self.logger.info(f'Requesting scopes: {SCOPES}')
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials for future use
                Path(self.token_path).parent.mkdir(parents=True, exist_ok=True)
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                self.logger.info(f'Saved credentials to {self.token_path}')

            # Suppress the discovery cache warning by setting the logger to ERROR level
            import logging
            logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            self.creds = creds
            self.logger.info('Gmail API authenticated successfully')
            self.logger.info(f'Authenticated scopes: {creds.scopes}')
            return True

        except ImportError as e:
            self.logger.error(f'Missing required package: {e}')
            self.logger.error('Install with: pip install google-api-python-client google-auth-oauthlib')
            return False
        except Exception as e:
            self.logger.error(f'Authentication failed: {e}')
            return False

    def check_for_updates(self) -> List[dict]:
        """
        Check for new unread important emails.

        Returns:
            List of new email messages
        """
        if not self.service:
            if not self.authenticate():
                return []

        try:
            # Query for unread important emails
            # Can customize query: 'is:unread is:important', 'is:unread category:primary', etc.
            query = 'is:unread'

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=20  # Limit per check
            ).execute()

            messages = results.get('messages', [])

            # Filter out already processed messages
            new_messages = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)

            if new_messages:
                self.logger.info(f'Found {len(new_messages)} new unread emails')
            else:
                self.logger.info('No new unread emails detected')

            return new_messages

        except Exception as e:
            self.logger.error(f'Error checking emails: {e}')
            # If error is auth-related, reset service
            if '401' in str(e) or '403' in str(e):
                self.service = None
                self.creds = None
            return []

    def create_action_file(self, message: dict) -> Path:
        """
        Create an action file for an email.

        Args:
            message: Gmail message dict with 'id' and 'threadId'

        Returns:
            Path to created action file
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}

            # Get snippet
            snippet = msg.get('snippet', '')[:500]  # Limit snippet length

            # Parse sender name and email
            from_header = headers.get('From', 'Unknown <unknown@unknown.com>')
            sender_name = from_header.split('<')[0].strip() if '<' in from_header else from_header
            sender_email = from_header.split('<')[1].replace('>', '') if '<' in from_header else from_header

            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_sender = ''.join(c if c.isalnum() or c in '-_' else '_' for c in sender_name)[:30]
            filename = f'EMAIL_{timestamp}_{safe_sender}.md'
            action_path = self.needs_action / filename

            # Create frontmatter
            frontmatter = f'''---
type: email
category: email
message_id: {message['id']}
thread_id: {message.get('threadId', '')}
from_name: "{sender_name}"
from_email: {sender_email}
to: {headers.get('To', 'me')}
subject: "{headers.get('Subject', 'No Subject')}"
date: {headers.get('Date', '')}
created: {datetime.now().isoformat()}
priority: high
status: pending
---

# Email from {sender_name}

## Email Details
- **From:** {from_header}
- **To:** {headers.get('To', 'me')}
- **Subject:** {headers.get('Subject', 'No Subject')}
- **Date:** {headers.get('Date', '')}
- **Message ID:** {message['id']}

## Snippet
{snippet}

## Suggested Actions
- [ ] Read full email in Gmail
- [ ] Reply if needed
- [ ] Archive after processing
- [ ] Move to /Done when complete

## Notes
_Add any notes about this email here_
'''

            action_path.write_text(frontmatter, encoding='utf-8')

            # Mark as processed
            self.processed_ids.add(message['id'])

            return action_path

        except Exception as e:
            self.logger.error(f'Failed to create action file for message {message["id"]}: {e}')
            raise

    def load_processed_emails(self):
        """Load previously processed email IDs from state file."""
        try:
            if self.state_file.exists():
                import json
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'processed_ids' in data:
                        self.processed_ids.update(data['processed_ids'])
                self.logger.info(f'Loaded {len(self.processed_ids)} previously processed emails from state file')
            else:
                self.logger.info('No state file found, starting fresh')
        except Exception as e:
            self.logger.warning(f'Could not load state file: {e}')
            self.processed_ids.clear()  # Start fresh if there's an error

    def save_processed_emails(self):
        """Save processed email IDs to state file."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            import json
            data = {
                'processed_ids': list(self.processed_ids),
                'last_updated': datetime.now().isoformat(),
                'total_processed': len(self.processed_ids)
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f'Could not save state file: {e}')

    def run(self):
        """Main loop - continuously check for new emails."""
        self.logger.info(f'Starting Gmail Watcher')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Output: /Needs_Action/{self.category}/')
        self.logger.info(f'Check interval: {self.check_interval}s')

        # Authenticate first
        if not self.authenticate():
            self.logger.error('Failed to authenticate. Exiting.')
            return

        self.logger.info('Starting email monitoring...')

        while True:
            try:
                messages = self.check_for_updates()
                for msg in messages:
                    action_file = self.create_action_file(msg)
                    self.logger.info(f'Created action file: {action_file.name}')

                # Save the processed emails state after each check cycle
                self.save_processed_emails()
            except Exception as e:
                self.logger.error(f'Error in check cycle: {e}')

            # Sleep before next check
            import time
            time.sleep(self.check_interval)


def setup_oauth(vault_path: str):
    """
    Setup OAuth2 credentials interactively.

    Args:
        vault_path: Path to vault for resolving credentials path
    """
    print("\n" + "=" * 50)
    print("Gmail OAuth2 Setup")
    print("=" * 50)
    print("\nPrerequisites:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a project or select existing")
    print("3. Enable Gmail API")
    print("4. Create OAuth 2.0 credentials (Desktop app)")
    print("5. Download credentials.json")
    print("\n" + "=" * 50 + "\n")

    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', './credentials/gmail_credentials.json')
    if not Path(credentials_path).is_absolute():
        credentials_path = str(Path(vault_path).parent / credentials_path)

    if not Path(credentials_path).exists():
        print(f"ERROR: Credentials file not found at: {credentials_path}")
        print("Please download credentials.json and try again.")
        return False

    print(f"Found credentials at: {credentials_path}")
    print("\nStarting OAuth flow...")
    print("A browser window will open. Please authorize the application.\n")

    watcher = GmailWatcher(vault_path=vault_path)
    success = watcher.authenticate()

    if success:
        print("\n" + "=" * 50)
        print("SUCCESS! Gmail API is now authenticated.")
        print("=" * 50)
        return True
    else:
        print("\n" + "=" * 50)
        print("FAILED! Please check the error messages above.")
        print("=" * 50)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Gmail Watcher for AI Employee - Monitors for new emails'
    )
    parser.add_argument(
        '--vault-path',
        type=str,
        default='./AI_Employee_Vault_FTE',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=120,
        help='Seconds between email checks (default: 120)'
    )
    parser.add_argument(
        '--setup-oauth',
        action='store_true',
        help='Setup OAuth2 credentials interactively'
    )

    args = parser.parse_args()

    # Setup logging
    import logging
    from colorama import init as colorama_init, Fore, Style
    colorama_init()

    class ColoredFormatter(logging.Formatter):
        """Custom formatter with colors for different log levels."""

        COLORS = {
            logging.DEBUG: Fore.CYAN,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.RED + Style.BRIGHT,
        }

        COMPONENT_COLORS = {
            'GMAIL': Fore.LIGHTMAGENTA_EX,
        }

        def format(self, record):
            level_color = self.COLORS.get(record.levelno, Fore.WHITE)
            component_color = self.COMPONENT_COLORS.get(record.name, Fore.WHITE)
            message = super().format(record)
            return f"{component_color}{message}{Style.RESET_ALL}"

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

    if args.setup_oauth:
        setup_oauth(args.vault_path)
    else:
        watcher = GmailWatcher(
            vault_path=args.vault_path,
            check_interval=args.check_interval
        )
        watcher.run()


if __name__ == '__main__':
    main()
