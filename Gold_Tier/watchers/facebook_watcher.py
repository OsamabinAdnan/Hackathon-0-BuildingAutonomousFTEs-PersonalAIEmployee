"""
Facebook Watcher - Monitors Facebook Page for messages and engagement.

This watcher uses Facebook Graph API to monitor:
1. New messages via Facebook Messenger
2. Post comments and engagement
3. Page notifications

Creates action files in /Needs_Action/facebook/

Requires:
- Facebook Developer App with appropriate permissions
- Page Access Token with pages_read_engagement, pages_manage_posts, pages_read_user_content

Usage:
    python -m watchers --watcher facebook
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

from dotenv import load_dotenv

load_dotenv()

# Logger will be configured in main()
logger = logging.getLogger('FACEBOOK')


class FacebookWatcher:
    """
    Facebook Watcher for AI Employee.
    
    Monitors Facebook Page for messages, comments, and engagement.
    Creates action files in /Needs_Action/facebook/
    """
    
    # Default keywords to watch for
    DEFAULT_KEYWORDS = [
        'urgent', 'asap', 'important', 'invoice', 'payment',
        'help', 'question', 'interested', 'pricing', 'buy',
        'contact', 'call', 'meeting', 'demo'
    ]
    
    def __init__(self, vault_path: str, check_interval: int = 659):
        """
        Initialize Facebook watcher.

        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks (default: 659)
        """
        self.vault_path = Path(vault_path)
        self.category = 'facebook'
        self.needs_action = self.vault_path / 'Needs_Action' / self.category
        self.check_interval = check_interval
        
        # Setup logger
        self.logger = logging.getLogger('FACEBOOK')
        
        # Ensure output directory exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Facebook API credentials from environment
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        
        # Track processed items to prevent duplicates
        self.processed_ids: Set[str] = set()
        
        # Load previously processed items from state file
        self.state_file = self.vault_path.parent / ".watcher_state" / "facebook_processed.json"
        self.load_processed_items()
        
        # Keywords to watch for
        keywords_env = os.getenv('FACEBOOK_KEYWORDS', '')
        self.keywords = keywords_env.split(',') if keywords_env else self.DEFAULT_KEYWORDS
        self.keywords = [k.strip().lower() for k in self.keywords if k.strip()]
        
        self.logger.info(f'Facebook Watcher initialized')
        self.logger.info(f'  Page ID: {self.page_id or "Not set"}')
        self.logger.info(f'  Access Token: {"Configured" if self.access_token else "Not set"}')
        self.logger.info(f'  Keywords: {self.keywords}')
        self.logger.info(f'  Output: /Needs_Action/{self.category}/')
        self.logger.info(f'  Check interval: {self.check_interval}s')
    
    def _check_credentials(self) -> bool:
        """Check if credentials are configured."""
        if not self.page_id:
            self.logger.error('Facebook Page ID not configured')
            self.logger.error('Set FACEBOOK_PAGE_ID in .env file')
            return False
        if not self.access_token:
            self.logger.error('Facebook Access Token not configured')
            self.logger.error('Set FACEBOOK_ACCESS_TOKEN in .env file')
            return False
        return True
    
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """
        Make request to Facebook Graph API.
        
        Args:
            endpoint: API endpoint
            params: Optional query parameters
        
        Returns:
            JSON response or error dict
        """
        import urllib.request
        import urllib.error
        import json
        
        if not self._check_credentials():
            return {'error': 'Credentials not configured'}
        
        # Build URL
        url = f'https://graph.facebook.com/v18.0/{endpoint}'
        
        # Add access token
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        # Build query string
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        if query_string:
            url += f'?{query_string}'
        
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            self.logger.error(f'Facebook API error: {e.code} - {error_body}')
            return {'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            self.logger.error(f'Facebook request failed: {e}')
            return {'error': str(e)}
    
    def check_for_messages(self) -> List[dict]:
        """
        Check for new Facebook messages.
        
        Returns:
            List of new messages
        """
        messages = []
        
        if not self._check_credentials():
            return messages
        
        try:
            # Get conversations with messages
            result = self._make_request(
                f'{self.page_id}/conversations',
                {'fields': 'messages{from,message,created_time}', 'limit': '10'}
            )
            
            if 'error' in result:
                self.logger.warning(f'Could not fetch messages: {result["error"]}')
                return messages
            
            # Process conversations
            if 'data' in result:
                for conv in result['data']:
                    if 'messages' in conv and 'data' in conv['messages']:
                        for msg in conv['messages']['data']:
                            msg_id = msg.get('id', '')
                            
                            # Skip if already processed
                            if msg_id not in self.processed_ids:
                                messages.append({
                                    'type': 'message',
                                    'id': msg_id,
                                    'from': msg.get('from', {}).get('name', 'Unknown'),
                                    'message': msg.get('message', ''),
                                    'created_time': msg.get('created_time', '')
                                })
                                self.processed_ids.add(msg_id)
            
            if messages:
                self.logger.info(f'Found {len(messages)} new messages')
            else:
                self.logger.info('No new messages detected')
            
        except Exception as e:
            self.logger.error(f'Error checking messages: {e}')
        
        return messages
    
    def check_for_comments(self) -> List[dict]:
        """
        Check for new post comments.
        
        Returns:
            List of new comments
        """
        comments = []
        
        if not self._check_credentials():
            return comments
        
        try:
            # Get recent posts with comments
            result = self._make_request(
                f'{self.page_id}/posts',
                {'fields': 'comments{from,message,created_time}', 'limit': '5'}
            )
            
            if 'error' in result:
                self.logger.warning(f'Could not fetch comments: {result["error"]}')
                return comments
            
            # Process posts
            if 'data' in result:
                for post in result['data']:
                    if 'comments' in post and 'data' in post['comments']:
                        for comment in post['comments']['data']:
                            comment_id = comment.get('id', '')
                            
                            # Skip if already processed
                            if comment_id not in self.processed_ids:
                                comments.append({
                                    'type': 'comment',
                                    'id': comment_id,
                                    'from': comment.get('from', {}).get('name', 'Unknown'),
                                    'message': comment.get('message', ''),
                                    'created_time': comment.get('created_time', '')
                                })
                                self.processed_ids.add(comment_id)
            
            if comments:
                self.logger.info(f'Found {len(comments)} new comments')
            else:
                self.logger.info('No new comments detected')
            
        except Exception as e:
            self.logger.error(f'Error checking comments: {e}')
        
        return comments
    
    def check_for_updates(self) -> List[dict]:
        """
        Check for all Facebook updates (messages + comments).
        
        Returns:
            List of new items
        """
        items = []
        
        # Check messages
        messages = self.check_for_messages()
        items.extend(messages)
        
        # Check comments
        comments = self.check_for_comments()
        items.extend(comments)
        
        # Filter by keywords
        keyword_items = []
        for item in items:
            message_text = item.get('message', '').lower()
            if any(kw in message_text for kw in self.keywords):
                keyword_items.append(item)
                self.logger.info(f"Keyword match in {item['type']}: {item['from']}")
        
        if keyword_items:
            self.logger.info(f'Found {len(keyword_items)} items matching keywords')
        
        return keyword_items if keyword_items else items
    
    def create_action_file(self, item: dict) -> Path:
        """
        Create an action file for a Facebook item.
        
        Args:
            item: Item dict with type, id, from, message, created_time
        
        Returns:
            Path to created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = ''.join(c if c.isalnum() or c in '-_' else '_' for c in item['from'])[:30]
        filename = f'FACEBOOK_{item["type"].upper()}_{timestamp}_{safe_name}.md'
        action_path = self.needs_action / filename
        
        content = f'''---
type: facebook_{item['type']}
category: facebook
item_id: {item['id']}
from_name: "{item['from']}"
created: {item.get('created_time', datetime.now().isoformat())}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

# Facebook {item['type'].title()} from {item['from']}

## {item['type'].title()} Details
- **From:** {item['from']}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Facebook ID:** {item['id']}

## {item['type'].title()} Content
{item['message']}

## Suggested Actions
- [ ] Read full {item['type']} on Facebook
- [ ] Reply if needed
- [ ] Archive after processing
- [ ] Move to /Done when complete

## Notes
_Add any notes about this {item['type']} here_
'''
        
        action_path.write_text(content, encoding='utf-8')
        self.logger.info(f'Created action file: /Needs_Action/{self.category}/{filename}')
        
        return action_path
    
    def load_processed_items(self):
        """Load previously processed items from state file."""
        try:
            if self.state_file.exists():
                import json
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'processed_ids' in data:
                        self.processed_ids.update(data['processed_ids'])
                self.logger.info(f'Loaded {len(self.processed_ids)} previously processed items from state file')
            else:
                self.logger.info('No state file found, starting fresh')
        except Exception as e:
            self.logger.warning(f'Could not load state file: {e}')
            self.processed_ids.clear()
    
    def save_processed_items(self):
        """Save processed items to state file."""
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
        self.logger.info(f'Starting Facebook Watcher')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Output: /Needs_Action/{self.category}/')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        if not self._check_credentials():
            self.logger.error('Credentials not configured. Exiting.')
            return
        
        self.logger.info('Starting Facebook monitoring...')
        
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    action_file = self.create_action_file(item)
                    self.logger.info(f'Created action file: {action_file.name}')
                
                # Save processed items state after each check cycle
                self.save_processed_items()
            except Exception as e:
                self.logger.error(f'Error in check cycle: {e}')
            
            # Sleep before next check
            time.sleep(self.check_interval)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Facebook Watcher for AI Employee - Monitors Facebook Page'
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

    # Setup logging with colors (Cyan for Facebook)
    import logging
    from colorama import init as colorama_init, Fore, Style
    colorama_init()

    # Configure root logger with colored formatter
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.setLevel(logging.INFO)

    class ColoredFormatter(logging.Formatter):
        """Custom formatter with colors for Facebook watcher."""

        COLORS = {
            logging.DEBUG: Fore.CYAN,
            logging.INFO: Fore.CYAN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.RED + Style.BRIGHT,
        }

        def format(self, record):
            level_color = self.COLORS.get(record.levelno, Fore.CYAN)
            message = super().format(record)
            return f"{level_color}[FACEBOOK] {message}{Style.RESET_ALL}"

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter('%(levelname)-8s - %(message)s'))
    root_logger.addHandler(console_handler)

    watcher = FacebookWatcher(
        vault_path=args.vault_path,
        check_interval=args.check_interval
    )
    watcher.run()


if __name__ == '__main__':
    main()
