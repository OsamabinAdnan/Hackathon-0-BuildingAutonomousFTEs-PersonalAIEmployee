"""
WhatsApp Watcher - Monitors WhatsApp Web for keyword messages.

This watcher uses Playwright to automate WhatsApp Web:
1. Uses persistent browser context for session storage
2. Monitors for unread messages containing keywords
3. Creates action files in /Needs_Action/whatsapp/

NOTE: WhatsApp Web has terms of service. Use responsibly.
Headless mode may not work - WhatsApp detects and blocks it.

Usage:
    python -m watchers.whatsapp
    python -m watchers.whatsapp --no-headless  # First time for QR scan
"""

import argparse
import logging
import os
import sys
import asyncio
import time
from pathlib import Path
from datetime import datetime
from typing import List, Set, Optional, Dict

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger('WHATSAPP')


class WhatsAppWatcher:
    """
    WhatsApp Web Watcher for AI Employee.

    Uses Playwright to monitor WhatsApp Web for messages with keywords.
    Maintains session via persistent browser context.
    """

    # Default keywords to watch for
    DEFAULT_KEYWORDS = [
        'urgent', 'asap', 'important', 'invoice', 'payment',
        'deadline', 'meeting', 'call', 'help', 'action',
        'confirm', 'approve', 'decision', 'question'
    ]

    def __init__(self, vault_path: str, check_interval: int = 571):
        """
        Initialize the WhatsApp watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 571)
        """
        self.vault_path = Path(vault_path)
        self.category = 'whatsapp'
        self.needs_action = self.vault_path / 'Needs_Action' / self.category
        self.check_interval = check_interval

        # Setup logger
        self.logger = logging.getLogger('WHATSAPP')

        # Ensure output directory exists
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Session path from environment
        self.session_path = os.getenv('WHATSAPP_SESSION_PATH', './sessions/whatsapp')
        if not Path(self.session_path).is_absolute():
            self.session_path = str(Path(vault_path).parent / self.session_path)

        # Ensure session directory exists
        Path(self.session_path).mkdir(parents=True, exist_ok=True)

        # Headless mode (WhatsApp Web blocks headless)
        self.headless = os.getenv('WHATSAPP_HEADLESS', 'false').lower() == 'true'

        # Keywords to watch for
        keywords_env = os.getenv('WHATSAPP_KEYWORDS', '')
        self.keywords = keywords_env.split(',') if keywords_env else self.DEFAULT_KEYWORDS
        self.keywords = [k.strip().lower() for k in self.keywords if k.strip()]

        # Track processed messages per chat (chat_name -> message_count)
        self.chat_message_counts: Dict[str, int] = {}

        # Load previously processed message counts from state file
        self.state_file = Path(self.vault_path).parent / ".watcher_state" / "whatsapp_processed.json"
        self.load_processed_messages()

        # Browser context
        self.context = None
        self.page = None

        self.logger.info(f'WhatsApp Watcher initialized')
        self.logger.info(f'  Session: {self.session_path}')
        self.logger.info(f'  Headless: {self.headless}')
        self.logger.info(f'  Keywords: {self.keywords}')
        self.logger.info(f'  Output: /Needs_Action/{self.category}/')

    async def init_browser(self) -> bool:
        """
        Initialize browser with persistent context.

        Returns:
            True if successful, False otherwise
        """
        try:
            from playwright.async_api import async_playwright

            self.logger.info('Initializing browser...')

            playwright = await async_playwright().start()

            # Launch with persistent context for session storage
            self.context = await playwright.chromium.launch_persistent_context(
                user_data_dir=self.session_path,
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-web-security',
                ],
                viewport={'width': 1280, 'height': 720}
            )

            # Get or create page
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()

            self.logger.info('Browser initialized successfully')
            return True

        except ImportError as e:
            self.logger.error(f'Missing required package: {e}')
            self.logger.error('Install with: pip install playwright && playwright install chromium')
            return False
        except Exception as e:
            self.logger.error(f'Failed to initialize browser: {e}')
            return False

    async def navigate_to_whatsapp(self) -> bool:
        """
        Navigate to WhatsApp Web and wait for login if needed.

        Returns:
            True if on WhatsApp Web, False otherwise
        """
        if not self.page:
            return False

        try:
            self.logger.info('Navigating to WhatsApp Web...')
            await self.page.goto('https://web.whatsapp.com', wait_until='networkidle')

            # Wait for WhatsApp Web to load completely
            await self.page.wait_for_timeout(5000)  # Give some time for page to settle

            # Check if we're logged in by looking for multiple possible indicators
            # Updated selectors for current WhatsApp Web version
            logged_in_selectors = [
                '[data-testid="chat-list"]',  # Old selector
                'div[role="navigation"] [data-testid*="drawer"]',  # Navigation drawer
                'div[tabindex="-1"][role="grid"]',  # Chat grid container
                '#pane-side',  # Side panel with chats
                'div[aria-label*="menu" i]',  # Menu elements
                '[data-testid="default-user"]',  # Profile picture/default avatar
                '._3quh._30yy._2t_']  # Alternative selector

            # QR code selectors
            qr_selectors = [
                'canvas[aria-label*="qr" i]',
                'div[data-testid*="qr" i]',
                'div[role="dialog"] canvas',  # QR code in dialog
                'div[style*="background-image"][style*="qr"]'  # QR code background
            ]

            # Check if already logged in
            for selector in logged_in_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        self.logger.info('Already logged in to WhatsApp Web')
                        return True
                except:
                    continue

            # If no logged-in indicator found, check for QR code
            qr_found = False
            for selector in qr_selectors:
                try:
                    qr_element = await self.page.query_selector(selector)
                    if qr_element:
                        qr_found = True
                        break
                except:
                    continue

            if qr_found:
                self.logger.info('QR code visible - please scan to log in')
                self.logger.info('Waiting for login...')

                # Wait for login using multiple possible selectors
                login_success = False
                timeout_time = 120000  # 2 minutes
                start_time = time.time() * 1000

                while (time.time() * 1000 - start_time) < timeout_time:
                    for selector in logged_in_selectors:
                        try:
                            element = await self.page.query_selector(selector)
                            if element:
                                self.logger.info('Login successful!')
                                return True
                        except:
                            pass
                    await self.page.wait_for_timeout(1000)  # Wait 1 second before checking again

                self.logger.error('Login timeout - please try again')
                return False
            else:
                # If neither QR code nor chat list is found, try waiting longer
                self.logger.info('Checking for login status...')
                try:
                    # Wait for either QR code or chat list with more flexible selectors
                    await self.page.wait_for_function(
                        "() => { "
                        "  const chatList = document.querySelector('#pane-side') || "
                        "    document.querySelector('[data-testid=\"chat-list\"]') || "
                        "    document.querySelector('div[role=\"navigation\"]'); "
                        "  const qrCode = document.querySelector('canvas') || "
                        "    document.querySelector('div[role=\"dialog\"] canvas'); "
                        "  return chatList || qrCode; "
                        "}",
                        timeout=30000
                    )

                    # Now check again for logged in state
                    for selector in logged_in_selectors:
                        try:
                            element = await self.page.query_selector(selector)
                            if element:
                                self.logger.info('Already logged in to WhatsApp Web')
                                return True
                        except:
                            continue

                    # If still not logged in, we must need to scan QR
                    self.logger.info('QR code visible - please scan to log in')
                    self.logger.info('Waiting for login...')

                    # Wait for login with multiple selectors
                    login_success = False
                    timeout_time = 120000  # 2 minutes
                    start_time = time.time() * 1000

                    while (time.time() * 1000 - start_time) < timeout_time:
                        for selector in logged_in_selectors:
                            try:
                                element = await self.page.query_selector(selector)
                                if element:
                                    self.logger.info('Login successful!')
                                    return True
                            except:
                                pass
                        await self.page.wait_for_timeout(1000)  # Wait 1 second before checking again

                    self.logger.error('Login timeout - please try again')
                    return False

                except Exception as e:
                    self.logger.warning(f'Could not determine login status: {e}')
                    # As fallback, assume we need to scan QR code
                    self.logger.info('Assuming QR code is needed - please scan to log in')
                    self.logger.info('Waiting for login...')

                    # Wait for login with multiple selectors
                    timeout_time = 120000  # 2 minutes
                    start_time = time.time() * 1000

                    while (time.time() * 1000 - start_time) < timeout_time:
                        for selector in logged_in_selectors:
                            try:
                                element = await self.page.query_selector(selector)
                                if element:
                                    self.logger.info('Login successful!')
                                    return True
                            except:
                                pass
                        await self.page.wait_for_timeout(1000)  # Wait 1 second before checking again

                    self.logger.error('Login timeout - please try again')
                    return False

        except Exception as e:
            self.logger.error(f'Error navigating to WhatsApp: {e}')
            return False

    async def check_for_updates(self) -> List[dict]:
        """
        Check for new messages by counting total messages per chat.
        Only processes messages if the count has increased since last check.

        Returns:
            List of new messages with keywords
        """
        if not self.page:
            return []

        try:
            messages = []

            # Find all chats
            chat_selectors = [
                '#pane-side [role="row"]',
                '#pane-side div[tabindex][data-testid]',
                '[data-testid="cell-frame-container"]',
            ]

            chat_elements = []
            for selector in chat_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        chat_elements = elements[:20]  # Limit to 20 chats
                        break
                except:
                    continue

            if not chat_elements:
                self.logger.debug('No chats found')
                return []

            self.logger.info(f'Found {len(chat_elements)} chats to check')

            # Process each chat
            for idx, chat_element in enumerate(chat_elements):
                try:
                    # Get chat name
                    chat_name = 'Unknown'
                    name_selectors = ['[title]', '[dir="auto"]', 'span[dir="auto"]']

                    for name_selector in name_selectors:
                        try:
                            chat_name_el = await chat_element.query_selector(name_selector)
                            if chat_name_el:
                                chat_name = (await chat_name_el.inner_text()).strip()
                                if chat_name:
                                    break
                        except:
                            continue

                    # Click to open the chat
                    try:
                        await chat_element.click()
                    except:
                        try:
                            clickable_child = await chat_element.query_selector('div, span, button, a')
                            if clickable_child:
                                await clickable_child.click()
                        except:
                            continue

                    await self.page.wait_for_timeout(2000)  # Wait for messages to load

                    # Count total messages in this chat
                    message_selectors = ['[data-testid="msg"]', 'div.message-in', 'div.message-out']
                    total_messages = 0
                    
                    for msg_selector in message_selectors:
                        try:
                            elements = await self.page.query_selector_all(msg_selector)
                            if elements:
                                total_messages = len(elements)
                                break
                        except:
                            continue

                    # Get previous count for this chat
                    previous_count = self.chat_message_counts.get(chat_name, 0)

                    # Check if message count increased (new messages arrived)
                    if total_messages > previous_count:
                        self.logger.info(f"[{chat_name}] New messages: {previous_count} -> {total_messages}")
                        
                        # Get only the NEW messages
                        new_message_count = total_messages - previous_count
                        all_messages = []
                        
                        for msg_selector in message_selectors:
                            try:
                                elements = await self.page.query_selector_all(msg_selector)
                                if elements:
                                    all_messages = elements
                                    break
                            except:
                                continue

                        # Process only new messages (last N messages)
                        for msg_el in all_messages[-new_message_count:]:
                            try:
                                msg_text = ''
                                msg_timestamp = ''
                                
                                try:
                                    msg_text = await msg_el.inner_text()
                                    msg_timestamp = await msg_el.get_attribute('data-pre-plain-text') or ''
                                except:
                                    try:
                                        msg_text = await msg_el.text_content()
                                    except:
                                        continue

                                if not msg_text.strip():
                                    continue

                                msg_text_lower = msg_text.lower()

                                # Check for keywords
                                if any(kw in msg_text_lower for kw in self.keywords):
                                    messages.append({
                                        'chat_name': chat_name,
                                        'message': msg_text[:500],
                                        'id': f"wa_{chat_name}_{total_messages}"
                                    })

                            except Exception as e:
                                self.logger.debug(f'Error processing message: {e}')
                                continue

                        # Update stored count
                        self.chat_message_counts[chat_name] = total_messages
                    else:
                        self.logger.debug(f"[{chat_name}] No new messages ({total_messages} total)")

                except Exception as e:
                    self.logger.debug(f'Error processing chat {idx}: {e}')
                    continue

            if messages:
                self.logger.info(f'Found {len(messages)} new keyword messages')
            else:
                self.logger.info('No new messages with keywords detected')

            return messages

        except Exception as e:
            self.logger.error(f'Error checking for updates: {e}')
            return []

    async def create_action_file(self, message: dict) -> Path:
        """
        Create an action file for a WhatsApp message.

        Args:
            message: Message dict with chat_name, message, id, timestamp

        Returns:
            Path to created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = ''.join(c if c.isalnum() or c in '-_' else '_' for c in message['chat_name'])[:30]
        filename = f'WHATSAPP_{timestamp}_{safe_name}.md'
        action_path = self.needs_action / filename

        content = f'''---
type: whatsapp
category: whatsapp
chat_name: "{message['chat_name']}"
message_id: {message['id']}
message_timestamp: {message.get('timestamp', 'N/A')}
created: {datetime.now().isoformat()}
priority: high
status: pending
---

# WhatsApp Message from {message['chat_name']}

## Message Details
- **Chat:** {message['chat_name']}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Message Timestamp:** {message.get('timestamp', 'N/A')}
- **Keywords Matched:** This message contains important keywords

## Message Content
{message['message']}

## Suggested Actions
- [ ] Read full message in WhatsApp
- [ ] Reply if needed
- [ ] Archive after processing
- [ ] Move to /Done when complete

## Notes
_Add any notes about this message here_
'''

        action_path.write_text(content, encoding='utf-8')
        return action_path

    def load_processed_messages(self):
        """Load previously processed message counts from state file."""
        try:
            if self.state_file.exists():
                import json
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'chat_message_counts' in data:
                        self.chat_message_counts.update(data['chat_message_counts'])
                self.logger.info(f'Loaded message counts for {len(self.chat_message_counts)} chats from state file')
            else:
                self.logger.info('No state file found, starting fresh')
        except Exception as e:
            self.logger.warning(f'Could not load state file: {e}')
            self.chat_message_counts.clear()

    def save_processed_messages(self):
        """Save processed message counts to state file."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            import json
            data = {
                'chat_message_counts': self.chat_message_counts,
                'last_updated': datetime.now().isoformat(),
                'total_chats_tracked': len(self.chat_message_counts)
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f'Could not save state file: {e}')

    async def send_approved_messages(self):
        """Check /Approved/whatsapp/ folder and send approved messages."""
        try:
            approved_folder = self.vault_path / 'Approved' / 'whatsapp'
            if not approved_folder.exists():
                return

            # Get all approved message files
            approved_files = list(approved_folder.glob('APPROVAL_*.md'))

            for approval_file in approved_files:
                try:
                    # Read the approval file
                    content = approval_file.read_text(encoding='utf-8', errors='replace')

                    # Extract contact and message
                    import re
                    contact_match = re.search(r'\*\*Recipient:\*\*\s*([^\n]+)', content)
                    if not contact_match:
                        contact_match = re.search(r'\|\s*\*\*Recipient\*\*\s*\|\s*([^\n]+)', content)

                    message_match = re.search(r'\*\*Message Content:\*\*([\s\S]*?)(?=\n---|\n##|\Z)', content)

                    if contact_match and message_match:
                        contact = contact_match.group(1).strip()
                        message = message_match.group(1).strip()

                        self.logger.info(f'Sending approved message to: {contact}')

                        # Send the message via WhatsApp Web
                        success = await self.send_whatsapp_message(contact, message)

                        if success:
                            self.logger.info(f'✓ Message sent to {contact}')

                            # Move approval file to Done
                            done_folder = self.vault_path / 'Done' / 'whatsapp'
                            done_folder.mkdir(parents=True, exist_ok=True)
                            approval_file.rename(done_folder / approval_file.name)

                            # Move In_Progress file to Archive
                            in_progress_folder = self.vault_path / 'In_Progress' / 'whatsapp'
                            if in_progress_folder.exists():
                                for f in in_progress_folder.glob('*.md'):
                                    archive_folder = self.vault_path / 'Archive' / 'whatsapp'
                                    archive_folder.mkdir(parents=True, exist_ok=True)
                                    f.rename(archive_folder / f.name)
                        else:
                            self.logger.error(f'✗ Failed to send message to {contact}')
                except Exception as e:
                    self.logger.error(f'Error processing approved message {approval_file.name}: {e}')
        except Exception as e:
            self.logger.error(f'Error checking approved messages: {e}')

    async def send_whatsapp_message(self, contact: str, message: str) -> bool:
        """
        Send a WhatsApp message to a contact.

        Args:
            contact: Contact name or phone number
            message: Message text to send

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.logger.error('Page not initialized')
                return False

            self.logger.info(f'Attempting to send message to {contact}')

            # Try to find search box with multiple selectors
            search_box = await self.page.query_selector('[contenteditable="true"]')
            if not search_box:
                self.logger.warning('Search box not found with contenteditable selector')
                # Try alternative selector
                search_box = await self.page.query_selector('input[type="text"]')

            if not search_box:
                self.logger.error('Could not find search box')
                return False

            self.logger.info(f'Found search box, typing contact name: {contact}')
            await search_box.click()
            await search_box.fill('')  # Clear first
            await asyncio.sleep(0.5)
            await search_box.type(contact, delay=50)  # Type slowly
            await asyncio.sleep(1.5)

            # Click on the contact from dropdown
            contact_item = await self.page.query_selector('[role="option"]')
            if not contact_item:
                self.logger.warning('Contact dropdown not found, trying alternative selector')
                # Try clicking on first list item
                contact_item = await self.page.query_selector('[role="listbox"] [role="option"]')

            if contact_item:
                self.logger.info(f'Found contact in dropdown, clicking...')
                await contact_item.click()
                await asyncio.sleep(1.5)
            else:
                self.logger.warning('Contact not found in dropdown, trying to press Enter')
                await self.page.keyboard.press('Enter')
                await asyncio.sleep(1.5)

            # Find message input box (usually the second contenteditable element)
            msg_inputs = await self.page.query_selector_all('[contenteditable="true"]')
            msg_input = None

            if len(msg_inputs) > 1:
                msg_input = msg_inputs[-1]  # Last one is usually the message box
            elif len(msg_inputs) > 0:
                msg_input = msg_inputs[0]

            if msg_input:
                self.logger.info(f'Found message input, typing message...')
                await msg_input.click()
                await msg_input.fill('')  # Clear first
                await asyncio.sleep(0.5)

                # Handle multi-line messages correctly
                # Split by newlines and type each line followed by Shift+Enter
                lines = message.split('\n')
                for i, line in enumerate(lines):
                    if line:
                        await msg_input.type(line, delay=5)

                    # If not the last line, press Shift+Enter for a new line
                    if i < len(lines) - 1:
                        await self.page.keyboard.press('Shift+Enter')

                await asyncio.sleep(0.5)

                # Send message (press Enter)
                self.logger.info('Sending message via Enter key...')
                await self.page.keyboard.press('Enter')
                await asyncio.sleep(1.5)

                self.logger.info(f'✓ Message sent successfully to {contact}')
                return True
            else:
                self.logger.error('Could not find message input box')
                return False

        except Exception as e:
            self.logger.error(f'Error sending message: {e}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    async def run_async(self):
        """Async main loop."""
        self.logger.info(f'Starting WhatsApp Watcher')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Output: /Needs_Action/{self.category}/')
        self.logger.info(f'Check interval: {self.check_interval}s')

        # Initialize browser
        if not await self.init_browser():
            self.logger.error('Failed to initialize browser. Exiting.')
            return

        # Navigate to WhatsApp
        if not await self.navigate_to_whatsapp():
            self.logger.error('Failed to connect to WhatsApp Web. Exiting.')
            return

        self.logger.info('Starting WhatsApp monitoring...')

        try:
            while True:
                try:
                    # Check for incoming messages
                    messages = await self.check_for_updates()
                    for msg in messages:
                        action_file = await self.create_action_file(msg)
                        self.logger.info(f'Created action file: {action_file.name}')

                    # Check for approved messages to send
                    await self.send_approved_messages()

                    # Save the processed messages state after each check cycle
                    self.save_processed_messages()
                except Exception as e:
                    self.logger.error(f'Error in check cycle: {e}')

                await asyncio.sleep(self.check_interval)

        except asyncio.CancelledError:
            self.logger.info('Watch cancelled')
        finally:
            if self.context:
                await self.context.close()

    def run(self):
        """Run the watcher (blocking)."""
        asyncio.run(self.run_async())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='WhatsApp Watcher for AI Employee - Monitors WhatsApp Web'
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
        default=30,
        help='Seconds between checks (default: 30)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (required for first-time QR scan)'
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
            'WHATSAPP': Fore.LIGHTGREEN_EX,
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

    # Override headless if --no-headless
    if args.no_headless:
        os.environ['WHATSAPP_HEADLESS'] = 'false'

    watcher = WhatsAppWatcher(
        vault_path=args.vault_path,
        check_interval=args.check_interval
    )
    watcher.run()


if __name__ == '__main__':
    main()
