"""
WhatsApp Service - Send WhatsApp messages via Playwright.

This service provides WhatsApp messaging capabilities via Playwright automation.
Uses persistent browser context for session storage.

Usage:
    from mcp_server.whatsapp_service import WhatsAppService

    service = WhatsAppService()
    await service.send_message(
        contact="+1234567890",
        message="Hello from AI Employee!"
    )
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('mcp_server.whatsapp')


class WhatsAppService:
    """
    WhatsApp service using Playwright automation.

    Provides message sending capabilities via WhatsApp Web.
    Uses persistent session storage to avoid repeated logins.
    """

    def __init__(self, vault_path: str = './AI_Employee_Vault_FTE'):
        """
        Initialize the WhatsApp service.

        Args:
            vault_path: Path to vault for resolving session path
        """
        self.context = None
        self.page = None
        self.playwright = None

        # Session path from environment
        self.session_path = os.getenv('WHATSAPP_SESSION_PATH', './sessions/whatsapp')
        if not Path(self.session_path).is_absolute():
            self.session_path = str(Path(vault_path).parent / self.session_path)

        # Ensure session directory exists
        Path(self.session_path).mkdir(parents=True, exist_ok=True)

        # Headless mode (WhatsApp Web often blocks headless)
        self.headless = os.getenv('WHATSAPP_HEADLESS', 'false').lower() == 'true'

        # Dry run mode
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

        # Event loop for async operations
        self._loop = None

        logger.info(f'WhatsApp Service initialized')
        logger.info(f'  Session: {self.session_path}')
        logger.info(f'  Headless: {self.headless}')

    def _run_async(self, coro):
        """Run async coroutine in persistent event loop."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop.run_until_complete(coro)

    async def _init_browser(self) -> bool:
        """
        Initialize browser with persistent context.

        Returns:
            True if successful
        """
        try:
            from playwright.async_api import async_playwright

            if self.playwright is None:
                self.playwright = await async_playwright().start()

            if self.context is None:
                logger.info('Launching browser with persistent context...')
                self.context = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=self.session_path,
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                    ],
                    viewport={'width': 1280, 'height': 720}
                )

            if self.page is None:
                if self.context.pages:
                    self.page = self.context.pages[0]
                else:
                    self.page = await self.context.new_page()

            return True

        except Exception as e:
            logger.error(f'Failed to initialize browser: {e}')
            return False

    async def _navigate_to_whatsapp(self) -> bool:
        """
        Navigate to WhatsApp Web and check login status.

        Returns:
            True if logged in
        """
        if not self.page:
            return False

        try:
            await self.page.goto('https://web.whatsapp.com', wait_until='networkidle')

            # Wait for chat list (indicates logged in)
            try:
                await self.page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                return True
            except Exception:
                logger.warning('Not logged in to WhatsApp Web')
                logger.info('Please scan QR code in the browser window')
                return False

        except Exception as e:
            logger.error(f'Error navigating to WhatsApp: {e}')
            return False

    async def _find_chat(self, contact: str) -> bool:
        """
        Find and open a chat by contact name or number.

        Args:
            contact: Contact name or phone number

        Returns:
            True if chat found and opened
        """
        if not self.page:
            return False

        try:
            # Click on search/new chat button
            search_button = await self.page.query_selector('[data-testid="chat-list-search"]')
            if search_button:
                await search_button.click()
            else:
                # Alternative: look for search input directly
                search_input = await self.page.query_selector('[data-testid="search-input"]')
                if search_input:
                    await search_input.click()

            await self.page.wait_for_timeout(500)

            # Type contact name or number
            # Use the search input that's now focused
            await self.page.keyboard.type(contact)
            await self.page.wait_for_timeout(1000)

            # Press Enter to select first result
            await self.page.keyboard.press('Enter')
            await self.page.wait_for_timeout(1000)

            return True

        except Exception as e:
            logger.error(f'Error finding chat: {e}')
            return False

    async def _send_message_to_open_chat(self, message: str) -> bool:
        """
        Send message to currently open chat.

        Args:
            message: Message text to send

        Returns:
            True if sent successfully
        """
        if not self.page:
            return False

        try:
            # Find message input
            # WhatsApp uses contenteditable div for message input
            input_selectors = [
                '[data-testid="conversation-compose-box-input"]',
                'div[contenteditable="true"][data-tab="10"]',
                'footer div[contenteditable="true"]',
            ]

            input_element = None
            for selector in input_selectors:
                input_element = await self.page.query_selector(selector)
                if input_element:
                    break

            if not input_element:
                logger.error('Message input not found')
                return False

            # Click and type message
            await input_element.click()
            await self.page.keyboard.type(message)
            await self.page.wait_for_timeout(300)

            # Press Enter to send
            await self.page.keyboard.press('Enter')
            await self.page.wait_for_timeout(500)

            return True

        except Exception as e:
            logger.error(f'Error sending message: {e}')
            return False

    async def send_message_async(
        self,
        contact: str,
        message: str
    ) -> dict:
        """
        Send a WhatsApp message asynchronously.

        Args:
            contact: Contact name or phone number
            message: Message text to send

        Returns:
            Dict with success status
        """
        if self.dry_run:
            logger.info(f'[DRY RUN] Would send WhatsApp to: {contact}')
            logger.info(f'[DRY RUN] Message: {message[:50]}...')
            return {'success': True, 'dry_run': True, 'contact': contact}

        try:
            # Initialize browser
            if not await self._init_browser():
                return {'success': False, 'error': 'Failed to initialize browser'}

            # Navigate to WhatsApp
            if not await self._navigate_to_whatsapp():
                return {'success': False, 'error': 'Not logged in to WhatsApp Web'}

            # Find chat
            if not await self._find_chat(contact):
                return {'success': False, 'error': f'Could not find contact: {contact}'}

            # Send message
            if not await self._send_message_to_open_chat(message):
                return {'success': False, 'error': 'Failed to send message'}

            logger.info(f'WhatsApp message sent to {contact}')
            return {
                'success': True,
                'contact': contact,
                'message_length': len(message)
            }

        except Exception as e:
            logger.error(f'Error sending WhatsApp message: {e}')
            return {'success': False, 'error': str(e)}

    def send_message(self, contact: str, message: str) -> dict:
        """
        Send a WhatsApp message (synchronous wrapper).

        Args:
            contact: Contact name or phone number
            message: Message text to send

        Returns:
            Dict with success status
        """
        return self._run_async(self.send_message_async(contact, message))

    async def close(self):
        """Close browser context."""
        if self.context:
            await self.context.close()
            self.context = None
            self.page = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
