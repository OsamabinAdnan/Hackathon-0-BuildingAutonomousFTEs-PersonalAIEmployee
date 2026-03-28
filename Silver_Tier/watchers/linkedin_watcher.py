"""
LinkedIn Watcher - Monitors LinkedIn for messages and engagement.

This watcher uses LinkedIn API to monitor:
1. New messages and connection requests
2. Post engagement and comments
3. Important notifications

Creates action files in /Needs_Action/linkedin/

Requires:
- LinkedIn Developer App with appropriate permissions
- Access token (obtained via OAuth2)

Usage:
    python -m watchers.linkedin
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Set, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger('LINKEDIN')


class LinkedInWatcher:
    """
    LinkedIn API Watcher for AI Employee.

    Monitors LinkedIn for messages, engagement, and notifications.
    """

    def __init__(self, vault_path: str, check_interval: int = 300):
        """
        Initialize the LinkedIn watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 300 = 5 minutes)
        """
        self.vault_path = Path(vault_path)
        self.category = 'linkedin'
        self.needs_action = self.vault_path / 'Needs_Action' / self.category
        self.check_interval = check_interval

        # Setup logger
        self.logger = logging.getLogger('LINKEDIN')

        # Ensure output directory exists
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # LinkedIn API credentials from environment
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.refresh_token = os.getenv('LINKEDIN_REFRESH_TOKEN')
        self.org_id = os.getenv('LINKEDIN_ORG_ID')

        # API base URL
        self.api_base = 'https://api.linkedin.com/v2'

        # Track processed items
        self.processed_ids: Set[str] = set()

        # Load previously processed items from state file
        self.state_file = Path(self.vault_path).parent / ".watcher_state" / "linkedin_processed.json"
        self.load_processed_items()

        self.logger.info(f'LinkedIn Watcher initialized')
        self.logger.info(f'  Access Token: {"Configured" if self.access_token else "Not set"}')
        self.logger.info(f'  Org ID: {self.org_id or "Not set"}')
        self.logger.info(f'  Output: /Needs_Action/{self.category}/')

    def _check_token(self) -> bool:
        """
        Check if access token is configured.

        Returns:
            True if token is available
        """
        if not self.access_token:
            self.logger.error('LinkedIn access token not configured')
            self.logger.error('Set LINKEDIN_ACCESS_TOKEN in .env file')
            return False
        return True

    def _make_request(self, endpoint: str) -> Optional[dict]:
        """
        Make authenticated request to LinkedIn API.

        Args:
            endpoint: API endpoint (without base URL)

        Returns:
            JSON response or None on error
        """
        import urllib.request
        import urllib.error
        import json

        if not self._check_token():
            return None

        url = f'{self.api_base}/{endpoint}'

        try:
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'Bearer {self.access_token}')
            req.add_header('Content-Type', 'application/json')
            req.add_header('LinkedIn-Version', '202305')  # Use current API version
            req.add_header('X-Restli-Protocol-Version', '2.0.0')

            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))

        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.logger.error('LinkedIn token expired or invalid')
                self.logger.error('Please refresh your access token')
            elif e.code == 403:
                self.logger.error('LinkedIn API permission denied')
                self.logger.error('Check your app permissions')
            elif e.code == 404:
                self.logger.debug(f'LinkedIn API endpoint not found: {endpoint}')
                # Some endpoints may not be available for all apps
            else:
                self.logger.error(f'LinkedIn API HTTP error: {e.code} - {e.reason}')
            return None
        except Exception as e:
            self.logger.error(f'LinkedIn API request failed: {e}')
            return None

    def check_messages(self) -> List[dict]:
        """
        Check for new LinkedIn messages.

        Returns:
            List of new messages
        """
        # Note: LinkedIn's messaging API requires specific permissions
        # This is a simplified implementation
        messages = []

        try:
            # Get recent messages/conversations
            # Using the correct endpoint for messaging
            response = self._make_request('messaging/conversations')

            if response and 'elements' in response:
                for conv in response['elements'][:10]:  # Limit to 10
                    conv_id = conv.get('id', '')
                    if conv_id not in self.processed_ids:
                        messages.append({
                            'type': 'message',
                            'id': conv_id,
                            'data': conv
                        })

        except Exception as e:
            self.logger.debug(f'Could not check messages: {e}')
            # Try alternative endpoint
            try:
                # Alternative: Get user's network updates
                response = self._make_request('networkUpdates')
                if response and 'values' in response:
                    for update in response['values'][:10]:
                        update_id = update.get('id', '')
                        if update_id not in self.processed_ids:
                            messages.append({
                                'type': 'network_update',
                                'id': update_id,
                                'data': update
                            })
            except:
                pass

        return messages

    def check_notifications(self) -> List[dict]:
        """
        Check for LinkedIn notifications.

        Returns:
            List of notifications
        """
        notifications = []

        try:
            # Get notifications (using correct endpoint)
            response = self._make_request('notificationsV2')

            if response and 'elements' in response:
                for notif in response['elements'][:10]:
                    notif_id = notif.get('id', '')
                    if notif_id not in self.processed_ids:
                        notifications.append({
                            'type': 'notification',
                            'id': notif_id,
                            'data': notif
                        })

        except Exception as e:
            self.logger.debug(f'Could not check notifications: {e}')
            # Try alternative endpoint
            try:
                # Alternative: Get user updates
                response = self._make_request('networkUpdates')
                if response and 'values' in response:
                    for update in response['values'][:10]:
                        update_id = update.get('id', '')
                        if update_id not in self.processed_ids:
                            notifications.append({
                                'type': 'network_update',
                                'id': update_id,
                                'data': update
                            })
            except:
                pass

        return notifications

    def check_for_updates(self) -> List[dict]:
        """
        Check for all LinkedIn updates.

        Returns:
            List of new items (messages, notifications, etc.)
        """
        items = []

        # Check messages
        messages = self.check_messages()
        if messages:
            self.logger.info(f'Found {len(messages)} new messages')
            items.extend(messages)
        else:
            self.logger.debug('No new messages detected')

        # Check notifications
        notifications = self.check_notifications()
        if notifications:
            self.logger.info(f'Found {len(notifications)} new notifications')
            items.extend(notifications)
        else:
            self.logger.debug('No new notifications detected')

        if not items:
            self.logger.info('No new LinkedIn updates detected')

        return items

    def create_action_file(self, item: dict) -> Path:
        """
        Create an action file for a LinkedIn item.

        Args:
            item: Item dict with type, id, data

        Returns:
            Path to created action file
        """
        item_type = item.get('type', 'unknown')
        item_data = item.get('data', {})
        item_id = item.get('id', '')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if item_type == 'message':
            # Extract message details
            participants = item_data.get('participants', [])
            last_message = item_data.get('lastEvent', {})

            filename = f'LINKEDIN_MSG_{timestamp}.md'

            content = f'''---
type: linkedin_message
category: linkedin
conversation_id: {item_id}
created: {datetime.now().isoformat()}
priority: medium
status: pending
---

# LinkedIn Message

## Details
- **Conversation ID:** {item_id}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Message Summary
A new LinkedIn message requires your attention.

## Suggested Actions
- [ ] Read message on LinkedIn
- [ ] Reply if needed
- [ ] Archive after processing
- [ ] Move to /Done when complete

## Notes
_Add any notes here_
'''

        elif item_type == 'notification':
            notif_type = item_data.get('type', 'Unknown')

            filename = f'LINKEDIN_NOTIF_{timestamp}.md'

            content = f'''---
type: linkedin_notification
category: linkedin
notification_id: {item_id}
notification_type: {notif_type}
created: {datetime.now().isoformat()}
priority: medium
status: pending
---

# LinkedIn Notification

## Details
- **Type:** {notif_type}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Notification Summary
A LinkedIn notification requires your attention.

## Suggested Actions
- [ ] Review notification on LinkedIn
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Notes
_Add any notes here_
'''

        else:
            filename = f'LINKEDIN_{timestamp}.md'
            content = f'''---
type: linkedin
category: linkedin
item_id: {item_id}
created: {datetime.now().isoformat()}
priority: medium
status: pending
---

# LinkedIn Item

## Details
- **Type:** {item_type}
- **ID:** {item_id}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Suggested Actions
- [ ] Review on LinkedIn
- [ ] Take appropriate action
- [ ] Move to /Done when complete
'''

        action_path = self.needs_action / filename
        action_path.write_text(content, encoding='utf-8')

        # Mark as processed
        self.processed_ids.add(item_id)

        return action_path

    def load_processed_items(self):
        """Load previously processed LinkedIn items from state file."""
        try:
            if self.state_file.exists():
                import json
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'processed_ids' in data:
                        self.processed_ids.update(data['processed_ids'])
                self.logger.info(f'Loaded {len(self.processed_ids)} previously processed LinkedIn items from state file')
            else:
                self.logger.info('No state file found, starting fresh')
        except Exception as e:
            self.logger.warning(f'Could not load state file: {e}')
            self.processed_ids.clear()  # Start fresh if there's an error

    def save_processed_items(self):
        """Save processed LinkedIn items to state file."""
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
        """Main loop - continuously check for updates."""
        self.logger.info(f'Starting LinkedIn Watcher')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Output: /Needs_Action/{self.category}/')
        self.logger.info(f'Check interval: {self.check_interval}s')

        if not self._check_token():
            self.logger.error('LinkedIn access token not configured. Exiting.')
            return

        self.logger.info('Starting LinkedIn monitoring...')

        import time
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    action_file = self.create_action_file(item)
                    self.logger.info(f'Created action file: {action_file.name}')

                # Save the processed items state after each check cycle
                self.save_processed_items()
            except Exception as e:
                self.logger.error(f'Error in check cycle: {e}')

            time.sleep(self.check_interval)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='LinkedIn Watcher for AI Employee - Monitors LinkedIn'
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
        default=300,
        help='Seconds between checks (default: 300)'
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
            'LINKEDIN': Fore.LIGHTBLUE_EX,
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

    watcher = LinkedInWatcher(
        vault_path=args.vault_path,
        check_interval=args.check_interval
    )
    watcher.run()


if __name__ == '__main__':
    main()
